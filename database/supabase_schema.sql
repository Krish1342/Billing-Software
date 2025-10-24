-- Supabase Postgres Schema for Jewelry Billing & Stock Management
-- Production-ready schema with serialized inventory and category_item_no reuse
-- Run this in Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Core Tables
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Serialized inventory items (one row per physical piece)
-- Each item has a category_item_no that gets reused when items are sold
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES categories(id),
    category_item_no INTEGER NOT NULL, -- Per-category sequential number (reused when items sold)
    product_name TEXT NOT NULL,
    description TEXT,
    hsn_code TEXT,
    gross_weight DECIMAL(10,3) NOT NULL CHECK (gross_weight > 0),
    net_weight DECIMAL(10,3) NOT NULL CHECK (net_weight > 0 AND net_weight <= gross_weight),
    supplier_id UUID REFERENCES suppliers(id),
    melting_percentage DECIMAL(5,2) DEFAULT 0.00,
    status TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK (status IN ('AVAILABLE', 'SOLD', 'RESERVED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_category_item_no UNIQUE (category_id, category_item_no)
);

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    gstin TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE bills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bill_number TEXT UNIQUE NOT NULL,
    customer_id UUID REFERENCES customers(id),
    customer_name TEXT NOT NULL, -- Denormalized for bills without customer_id
    customer_phone TEXT,
    customer_gstin TEXT,
    bill_date DATE NOT NULL DEFAULT CURRENT_DATE,
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    cgst_rate DECIMAL(5,2) NOT NULL DEFAULT 1.50,
    sgst_rate DECIMAL(5,2) NOT NULL DEFAULT 1.50,
    cgst_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    sgst_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    rounded_off DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    status TEXT NOT NULL DEFAULT 'GENERATED' CHECK (status IN ('GENERATED', 'REVERSED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE bill_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bill_id UUID NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
    inventory_id UUID REFERENCES inventory(id), -- NULL for custom orders
    product_name TEXT NOT NULL,
    description TEXT,
    hsn_code TEXT,
    quantity DECIMAL(10,3) NOT NULL DEFAULT 1.000,
    rate DECIMAL(12,2) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Immutable stock movements ledger
CREATE TABLE stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventory_id UUID REFERENCES inventory(id),
    movement_type TEXT NOT NULL CHECK (movement_type IN ('ADDED', 'SOLD', 'REVERSED', 'ADJUSTED')),
    reference_id UUID, -- bill_id for sales/reversals
    reference_type TEXT, -- 'BILL', 'ADJUSTMENT', etc.
    quantity DECIMAL(10,3) NOT NULL DEFAULT 1.000,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_inventory_category_status ON inventory(category_id, status);
CREATE INDEX idx_inventory_status ON inventory(status);
CREATE INDEX idx_bill_items_bill_id ON bill_items(bill_id);
CREATE INDEX idx_bill_items_inventory_id ON bill_items(inventory_id);
CREATE INDEX idx_stock_movements_inventory_id ON stock_movements(inventory_id);
CREATE INDEX idx_stock_movements_reference ON stock_movements(reference_id, reference_type);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_inventory_updated_at BEFORE UPDATE ON inventory FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bills_updated_at BEFORE UPDATE ON bills FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Safety trigger: prevent direct modification of sold inventory
CREATE OR REPLACE FUNCTION prevent_sold_inventory_modification()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status = 'SOLD' AND (NEW.status != OLD.status OR NEW.category_item_no != OLD.category_item_no) THEN
        RAISE EXCEPTION 'Cannot modify sold inventory item. Use bill reversal instead.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_sold_inventory_update 
    BEFORE UPDATE ON inventory 
    FOR EACH ROW 
    EXECUTE FUNCTION prevent_sold_inventory_modification();

-- Views
CREATE VIEW current_stock_view AS
SELECT 
    i.id,
    i.category_id,
    c.name as category_name,
    i.category_item_no,
    i.product_name,
    i.description,
    i.hsn_code,
    i.gross_weight,
    i.net_weight,
    s.name as supplier_name,
    s.code as supplier_code,
    i.melting_percentage,
    i.status,
    i.created_at
FROM inventory i
JOIN categories c ON i.category_id = c.id
LEFT JOIN suppliers s ON i.supplier_id = s.id
WHERE i.status = 'AVAILABLE'
ORDER BY c.name, i.category_item_no;

CREATE VIEW category_summary_view AS
SELECT 
    c.id as category_id,
    c.name as category_name,
    COUNT(i.id) as total_items,
    COUNT(CASE WHEN i.status = 'AVAILABLE' THEN 1 END) as available_items,
    COUNT(CASE WHEN i.status = 'SOLD' THEN 1 END) as sold_items,
    COALESCE(SUM(CASE WHEN i.status = 'AVAILABLE' THEN i.gross_weight END), 0) as available_gross_weight,
    COALESCE(SUM(CASE WHEN i.status = 'AVAILABLE' THEN i.net_weight END), 0) as available_net_weight
FROM categories c
LEFT JOIN inventory i ON c.id = i.category_id
GROUP BY c.id, c.name
ORDER BY c.name;

CREATE VIEW total_summary_view AS
SELECT 
    COUNT(CASE WHEN i.status = 'AVAILABLE' THEN 1 END) as total_available_items,
    COUNT(CASE WHEN i.status = 'SOLD' THEN 1 END) as total_sold_items,
    COALESCE(SUM(CASE WHEN i.status = 'AVAILABLE' THEN i.gross_weight END), 0) as total_available_gross_weight,
    COALESCE(SUM(CASE WHEN i.status = 'AVAILABLE' THEN i.net_weight END), 0) as total_available_net_weight
FROM inventory i;

CREATE VIEW sold_items_view AS
SELECT 
    i.id,
    i.category_id,
    c.name as category_name,
    i.category_item_no,
    i.product_name,
    i.gross_weight,
    i.net_weight,
    b.bill_number,
    b.bill_date,
    b.customer_name,
    bi.amount as sale_amount,
    i.updated_at as sold_at
FROM inventory i
JOIN categories c ON i.category_id = c.id
JOIN bill_items bi ON i.id = bi.inventory_id
JOIN bills b ON bi.bill_id = b.id
WHERE i.status = 'SOLD' AND b.status = 'GENERATED'
ORDER BY i.updated_at DESC;

CREATE VIEW stock_ledger_view AS
SELECT 
    sm.id,
    sm.inventory_id,
    i.category_id,
    c.name as category_name,
    i.category_item_no,
    i.product_name,
    sm.movement_type,
    sm.reference_id,
    sm.reference_type,
    sm.quantity,
    sm.notes,
    sm.created_at
FROM stock_movements sm
LEFT JOIN inventory i ON sm.inventory_id = i.id
LEFT JOIN categories c ON i.category_id = c.id
ORDER BY sm.created_at DESC;

-- RPC Functions

-- Get next available category_item_no for a category (reuses sold item slots)
CREATE OR REPLACE FUNCTION get_next_category_item_no(p_category_id UUID)
RETURNS INTEGER AS $$
DECLARE
    next_no INTEGER;
BEGIN
    -- Find the lowest available number (reuse sold item slots)
    SELECT COALESCE(MIN(gaps.gap), 1) INTO next_no
    FROM (
        SELECT generate_series(1, COALESCE(MAX(category_item_no), 0) + 1) AS gap
        FROM inventory 
        WHERE category_id = p_category_id
    ) gaps
    WHERE gaps.gap NOT IN (
        SELECT category_item_no 
        FROM inventory 
        WHERE category_id = p_category_id 
        AND status IN ('AVAILABLE', 'RESERVED')
    );
    
    RETURN next_no;
END;
$$ LANGUAGE plpgsql;

-- Add inventory item
CREATE OR REPLACE FUNCTION add_inventory_item(
    p_category_id UUID,
    p_product_name TEXT,
    p_gross_weight DECIMAL(10,3),
    p_net_weight DECIMAL(10,3),
    p_description TEXT DEFAULT NULL,
    p_hsn_code TEXT DEFAULT NULL,
    p_supplier_id UUID DEFAULT NULL,
    p_melting_percentage DECIMAL(5,2) DEFAULT 0.00
)
RETURNS UUID AS $$
DECLARE
    v_item_id UUID;
    v_category_item_no INTEGER;
BEGIN
    -- Validate weights
    IF p_gross_weight <= 0 OR p_net_weight <= 0 OR p_net_weight > p_gross_weight THEN
        RAISE EXCEPTION 'Invalid weights: gross_weight must be > 0, net_weight must be > 0 and <= gross_weight';
    END IF;
    
    -- Get next available category item number
    SELECT get_next_category_item_no(p_category_id) INTO v_category_item_no;
    
    -- Insert inventory item
    INSERT INTO inventory (
        category_id, category_item_no, product_name, description, hsn_code,
        gross_weight, net_weight, supplier_id, melting_percentage, status
    ) VALUES (
        p_category_id, v_category_item_no, p_product_name, p_description, p_hsn_code,
        p_gross_weight, p_net_weight, p_supplier_id, p_melting_percentage, 'AVAILABLE'
    ) RETURNING id INTO v_item_id;
    
    -- Create stock movement record
    INSERT INTO stock_movements (inventory_id, movement_type, quantity, notes)
    VALUES (v_item_id, 'ADDED', 1.000, 'Initial inventory addition');
    
    RETURN v_item_id;
END;
$$ LANGUAGE plpgsql;

-- Create bill with automatic stock deduction
CREATE OR REPLACE FUNCTION create_bill_with_items(
    p_bill_number TEXT,
    p_customer_name TEXT,
    p_items JSONB, -- Array of {inventory_id, rate, product_name, description, hsn_code}
    p_customer_phone TEXT DEFAULT NULL,
    p_customer_gstin TEXT DEFAULT NULL,
    p_bill_date DATE DEFAULT CURRENT_DATE,
    p_cgst_rate DECIMAL(5,2) DEFAULT 1.50,
    p_sgst_rate DECIMAL(5,2) DEFAULT 1.50
)
RETURNS UUID AS $$
DECLARE
    v_bill_id UUID;
    v_item JSONB;
    v_inventory_id UUID;
    v_subtotal DECIMAL(12,2) := 0;
    v_cgst_amount DECIMAL(12,2);
    v_sgst_amount DECIMAL(12,2);
    v_total_amount DECIMAL(12,2);
    v_rounded_off DECIMAL(12,2);
    v_final_total DECIMAL(12,2);
BEGIN
    -- Create bill
    INSERT INTO bills (
        bill_number, customer_name, customer_phone, customer_gstin, 
        bill_date, cgst_rate, sgst_rate
    ) VALUES (
        p_bill_number, p_customer_name, p_customer_phone, p_customer_gstin,
        p_bill_date, p_cgst_rate, p_sgst_rate
    ) RETURNING id INTO v_bill_id;
    
    -- Process each item
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
    LOOP
        v_inventory_id := (v_item->>'inventory_id')::UUID;
        
        -- Check if inventory item is available for sale
        IF v_inventory_id IS NOT NULL THEN
            PERFORM 1 FROM inventory 
            WHERE id = v_inventory_id AND status = 'AVAILABLE'
            FOR UPDATE; -- Lock the row
            
            IF NOT FOUND THEN
                RAISE EXCEPTION 'Inventory item % is not available for sale', v_inventory_id;
            END IF;
            
            -- Mark item as sold
            UPDATE inventory 
            SET status = 'SOLD', updated_at = NOW()
            WHERE id = v_inventory_id;
            
            -- Create stock movement
            INSERT INTO stock_movements (
                inventory_id, movement_type, reference_id, reference_type, 
                quantity, notes
            ) VALUES (
                v_inventory_id, 'SOLD', v_bill_id, 'BILL', 
                1.000, 'Sold via bill ' || p_bill_number
            );
        END IF;
        
        -- Add bill item
        INSERT INTO bill_items (
            bill_id, inventory_id, product_name, description, hsn_code,
            quantity, rate, amount
        ) VALUES (
            v_bill_id, v_inventory_id, 
            v_item->>'product_name', v_item->>'description', v_item->>'hsn_code',
            (v_item->>'quantity')::DECIMAL(10,3),
            (v_item->>'rate')::DECIMAL(12,2),
            (v_item->>'amount')::DECIMAL(12,2)
        );
        
        -- Add to subtotal
        v_subtotal := v_subtotal + (v_item->>'amount')::DECIMAL(12,2);
    END LOOP;
    
    -- Calculate tax amounts
    v_cgst_amount := ROUND(v_subtotal * p_cgst_rate / 100, 2);
    v_sgst_amount := ROUND(v_subtotal * p_sgst_rate / 100, 2);
    v_total_amount := v_subtotal + v_cgst_amount + v_sgst_amount;
    
    -- Calculate rounding
    v_final_total := ROUND(v_total_amount);
    v_rounded_off := v_final_total - v_total_amount;
    
    -- Update bill totals
    UPDATE bills SET
        subtotal = v_subtotal,
        cgst_amount = v_cgst_amount,
        sgst_amount = v_sgst_amount,
        total_amount = v_final_total,
        rounded_off = v_rounded_off
    WHERE id = v_bill_id;
    
    RETURN v_bill_id;
END;
$$ LANGUAGE plpgsql;

-- Reverse a bill (idempotent)
CREATE OR REPLACE FUNCTION reverse_bill(p_bill_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_bill_number TEXT;
    v_item RECORD;
BEGIN
    -- Check if bill exists and is not already reversed
    SELECT bill_number INTO v_bill_number
    FROM bills 
    WHERE id = p_bill_id AND status = 'GENERATED'
    FOR UPDATE;
    
    IF NOT FOUND THEN
        -- Bill already reversed or doesn't exist - idempotent operation
        RETURN TRUE;
    END IF;
    
    -- Restore inventory items and create reversal movements
    FOR v_item IN 
        SELECT bi.inventory_id
        FROM bill_items bi
        WHERE bi.bill_id = p_bill_id AND bi.inventory_id IS NOT NULL
    LOOP
        -- Restore item to available status
        UPDATE inventory 
        SET status = 'AVAILABLE', updated_at = NOW()
        WHERE id = v_item.inventory_id;
        
        -- Create reversal stock movement
        INSERT INTO stock_movements (
            inventory_id, movement_type, reference_id, reference_type,
            quantity, notes
        ) VALUES (
            v_item.inventory_id, 'REVERSED', p_bill_id, 'BILL',
            1.000, 'Bill reversal for ' || v_bill_number
        );
    END LOOP;
    
    -- Mark bill as reversed
    UPDATE bills 
    SET status = 'REVERSED', updated_at = NOW()
    WHERE id = p_bill_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Get category CSV data
CREATE OR REPLACE FUNCTION get_category_csv_data(p_category_id UUID)
RETURNS TABLE (
    category_item_no INTEGER,
    product_name TEXT,
    gross_weight DECIMAL(10,3),
    net_weight DECIMAL(10,3),
    supplier_code TEXT,
    added_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        i.category_item_no,
        i.product_name,
        i.gross_weight,
        i.net_weight,
        COALESCE(s.code, '') as supplier_code,
        i.created_at as added_at
    FROM inventory i
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    WHERE i.category_id = p_category_id AND i.status = 'AVAILABLE'
    ORDER BY i.category_item_no;
END;
$$ LANGUAGE plpgsql;

-- Get summary CSV data
CREATE OR REPLACE FUNCTION get_summary_csv_data()
RETURNS TABLE (
    category_name TEXT,
    total_items BIGINT,
    available_items BIGINT,
    sold_items BIGINT,
    available_gross_weight DECIMAL,
    available_net_weight DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM category_summary_view;
END;
$$ LANGUAGE plpgsql;

-- Seed Data
INSERT INTO categories (name, description) VALUES
('Ring', 'Gold and silver rings'),
('Chain', 'Gold and silver chains'),
('Necklace', 'Traditional and modern necklaces'),
('Earrings', 'Stud and drop earrings'),
('Bangles', 'Gold and silver bangles');

INSERT INTO suppliers (name, code, contact_person, phone, email) VALUES
('Golden Crafts Ltd', 'GCL001', 'Rajesh Kumar', '+91-9876543210', 'rajesh@goldencrafts.com'),
('Silver Palace', 'SP002', 'Priya Sharma', '+91-9876543211', 'priya@silverpalace.com'),
('Diamond Delights', 'DD003', 'Amit Singh', '+91-9876543212', 'amit@diamonddelights.com');

-- Sample inventory items
DO $$
DECLARE
    v_ring_cat_id UUID;
    v_chain_cat_id UUID;
    v_supplier_id UUID;
BEGIN
    -- Get category IDs
    SELECT id INTO v_ring_cat_id FROM categories WHERE name = 'Ring';
    SELECT id INTO v_chain_cat_id FROM categories WHERE name = 'Chain';
    SELECT id INTO v_supplier_id FROM suppliers WHERE code = 'GCL001';
    
    -- Add sample rings
    PERFORM add_inventory_item(v_ring_cat_id, 'Ring', 5.450, 5.200, 'Gold ring with design', '7113', v_supplier_id, 85.5);
    PERFORM add_inventory_item(v_ring_cat_id, 'Ring', 3.250, 3.100, 'Silver ring plain', '7113', v_supplier_id, 92.0);
    PERFORM add_inventory_item(v_ring_cat_id, 'Ring', 6.750, 6.400, 'Gold ring with stones', '7113', v_supplier_id, 87.2);
    
    -- Add sample chains
    PERFORM add_inventory_item(v_chain_cat_id, 'Chain', 12.350, 11.800, 'Gold chain 18 inch', '7113', v_supplier_id, 88.5);
    PERFORM add_inventory_item(v_chain_cat_id, 'Chain', 8.450, 8.200, 'Silver chain 20 inch', '7113', v_supplier_id, 90.1);
END $$;

-- Sample bill
DO $$
DECLARE
    v_bill_id UUID;
    v_ring_id UUID;
    v_items JSONB;
BEGIN
    -- Get first available ring
    SELECT id INTO v_ring_id FROM inventory WHERE status = 'AVAILABLE' LIMIT 1;
    
    -- Create items array
    v_items := jsonb_build_array(
        jsonb_build_object(
            'inventory_id', v_ring_id,
            'product_name', 'Gold Ring',
            'description', 'Beautiful gold ring',
            'hsn_code', '7113',
            'quantity', 1,
            'rate', 25000.00,
            'amount', 25000.00
        )
    );
    
    -- Create sample bill
    SELECT create_bill_with_items(
        'RK-2024-001',
        'John Doe',
        v_items,
        '+91-9876543210',
        NULL,
        CURRENT_DATE,
        1.50,
        1.50
    ) INTO v_bill_id;
END $$;