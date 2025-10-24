-- Test SQL Cases for Jewelry Management System
-- Run these in Supabase SQL Editor to test functionality

-- Test 1: Selling a serialized item
DO $$
DECLARE
    v_bill_id UUID;
    v_ring_id UUID;
    v_items JSONB;
    v_category_item_no INTEGER;
BEGIN
    -- Get first available ring
    SELECT id, category_item_no INTO v_ring_id, v_category_item_no 
    FROM inventory 
    WHERE status = 'AVAILABLE' 
    AND category_id = (SELECT id FROM categories WHERE name = 'Ring' LIMIT 1)
    LIMIT 1;
    
    RAISE NOTICE 'Testing sale of Ring item % with category_item_no %', v_ring_id, v_category_item_no;
    
    -- Create items array
    v_items := jsonb_build_array(
        jsonb_build_object(
            'inventory_id', v_ring_id,
            'product_name', 'Gold Ring',
            'description', 'Test sale ring',
            'hsn_code', '7113',
            'quantity', 1,
            'rate', 25000.00,
            'amount', 25000.00
        )
    );
    
    -- Create test bill
    SELECT create_bill_with_items(
        'TEST-001',
        'Test Customer',
        '+91-9876543210',
        NULL,
        CURRENT_DATE,
        1.50,
        1.50,
        v_items
    ) INTO v_bill_id;
    
    RAISE NOTICE 'Bill created with ID: %', v_bill_id;
    
    -- Verify item is marked as sold
    IF EXISTS (SELECT 1 FROM inventory WHERE id = v_ring_id AND status = 'SOLD') THEN
        RAISE NOTICE '✅ Test 1 PASSED: Item correctly marked as SOLD';
    ELSE
        RAISE NOTICE '❌ Test 1 FAILED: Item not marked as SOLD';
    END IF;
    
    -- Verify stock movement was created
    IF EXISTS (SELECT 1 FROM stock_movements WHERE inventory_id = v_ring_id AND movement_type = 'SOLD') THEN
        RAISE NOTICE '✅ Test 1 PASSED: Stock movement created';
    ELSE
        RAISE NOTICE '❌ Test 1 FAILED: Stock movement not created';
    END IF;
    
END $$;

-- Test 2: Try to sell already sold item (should fail)
DO $$
DECLARE
    v_sold_item_id UUID;
    v_items JSONB;
BEGIN
    -- Get a sold item
    SELECT id INTO v_sold_item_id 
    FROM inventory 
    WHERE status = 'SOLD' 
    LIMIT 1;
    
    IF v_sold_item_id IS NULL THEN
        RAISE NOTICE 'No sold items found, skipping Test 2';
        RETURN;
    END IF;
    
    RAISE NOTICE 'Testing attempt to sell already sold item %', v_sold_item_id;
    
    -- Try to create bill with sold item
    v_items := jsonb_build_array(
        jsonb_build_object(
            'inventory_id', v_sold_item_id,
            'product_name', 'Already Sold Item',
            'quantity', 1,
            'rate', 10000.00,
            'amount', 10000.00
        )
    );
    
    BEGIN
        PERFORM create_bill_with_items(
            'TEST-002',
            'Test Customer 2',
            NULL,
            NULL,
            CURRENT_DATE,
            1.50,
            1.50,
            v_items
        );
        
        RAISE NOTICE '❌ Test 2 FAILED: Should not be able to sell sold item';
    EXCEPTION 
        WHEN OTHERS THEN
            RAISE NOTICE '✅ Test 2 PASSED: Correctly prevented sale of sold item - %', SQLERRM;
    END;
    
END $$;

-- Test 3: Add item after sale reuses slot
DO $$
DECLARE
    v_ring_category_id UUID;
    v_sold_item_no INTEGER;
    v_new_item_id UUID;
    v_new_item_no INTEGER;
BEGIN
    -- Get ring category ID
    SELECT id INTO v_ring_category_id FROM categories WHERE name = 'Ring';
    
    -- Find a sold item's category_item_no
    SELECT category_item_no INTO v_sold_item_no
    FROM inventory 
    WHERE category_id = v_ring_category_id 
    AND status = 'SOLD'
    LIMIT 1;
    
    IF v_sold_item_no IS NULL THEN
        RAISE NOTICE 'No sold rings found, skipping Test 3';
        RETURN;
    END IF;
    
    RAISE NOTICE 'Testing reuse of category_item_no % after sale', v_sold_item_no;
    
    -- Add new ring item
    SELECT add_inventory_item(
        v_ring_category_id,
        'Ring',
        'Test reuse ring',
        '7113',
        4.500,
        4.200,
        NULL,
        85.0
    ) INTO v_new_item_id;
    
    -- Check if it reused the sold item's number
    SELECT category_item_no INTO v_new_item_no
    FROM inventory 
    WHERE id = v_new_item_id;
    
    -- Find the lowest available slot that should be reused
    DECLARE
        expected_slot INTEGER;
    BEGIN
        SELECT COALESCE(MIN(gaps.gap), 1) INTO expected_slot
        FROM (
            SELECT generate_series(1, COALESCE(MAX(category_item_no), 0) + 1) AS gap
            FROM inventory 
            WHERE category_id = v_ring_category_id
        ) gaps
        WHERE gaps.gap NOT IN (
            SELECT category_item_no 
            FROM inventory 
            WHERE category_id = v_ring_category_id 
            AND status IN ('AVAILABLE', 'RESERVED')
        );
        
        IF v_new_item_no = expected_slot THEN
            RAISE NOTICE '✅ Test 3 PASSED: New item correctly reused slot % (expected %)', v_new_item_no, expected_slot;
        ELSE
            RAISE NOTICE '❌ Test 3 FAILED: New item got slot %, expected %', v_new_item_no, expected_slot;
        END IF;
    END;
    
END $$;

-- Test 4: Bill reversal restores slot
DO $$
DECLARE
    v_bill_id UUID;
    v_item_id UUID;
    v_category_item_no INTEGER;
    v_reversal_success BOOLEAN;
BEGIN
    -- Find a generated bill with inventory items
    SELECT b.id, bi.inventory_id INTO v_bill_id, v_item_id
    FROM bills b
    JOIN bill_items bi ON b.id = bi.bill_id
    WHERE b.status = 'GENERATED' 
    AND bi.inventory_id IS NOT NULL
    LIMIT 1;
    
    IF v_bill_id IS NULL THEN
        RAISE NOTICE 'No bills found to reverse, skipping Test 4';
        RETURN;
    END IF;
    
    -- Get the item's category_item_no before reversal
    SELECT category_item_no INTO v_category_item_no
    FROM inventory 
    WHERE id = v_item_id;
    
    RAISE NOTICE 'Testing reversal of bill % with item % (category_item_no %)', v_bill_id, v_item_id, v_category_item_no;
    
    -- Reverse the bill
    SELECT reverse_bill(v_bill_id) INTO v_reversal_success;
    
    IF v_reversal_success THEN
        RAISE NOTICE '✅ Test 4 PASSED: Bill reversal succeeded';
    ELSE
        RAISE NOTICE '❌ Test 4 FAILED: Bill reversal failed';
        RETURN;
    END IF;
    
    -- Check if item is restored to available
    IF EXISTS (SELECT 1 FROM inventory WHERE id = v_item_id AND status = 'AVAILABLE') THEN
        RAISE NOTICE '✅ Test 4 PASSED: Item restored to AVAILABLE status';
    ELSE
        RAISE NOTICE '❌ Test 4 FAILED: Item not restored to AVAILABLE status';
    END IF;
    
    -- Check if bill is marked as reversed
    IF EXISTS (SELECT 1 FROM bills WHERE id = v_bill_id AND status = 'REVERSED') THEN
        RAISE NOTICE '✅ Test 4 PASSED: Bill marked as REVERSED';
    ELSE
        RAISE NOTICE '❌ Test 4 FAILED: Bill not marked as REVERSED';
    END IF;
    
    -- Check if reversal stock movement was created
    IF EXISTS (SELECT 1 FROM stock_movements WHERE inventory_id = v_item_id AND movement_type = 'REVERSED') THEN
        RAISE NOTICE '✅ Test 4 PASSED: Reversal stock movement created';
    ELSE
        RAISE NOTICE '❌ Test 4 FAILED: Reversal stock movement not created';
    END IF;
    
END $$;

-- Test 5: Category CSV download
DO $$
DECLARE
    v_category_id UUID;
    v_csv_data RECORD;
    v_count INTEGER := 0;
BEGIN
    -- Get ring category ID
    SELECT id INTO v_category_id FROM categories WHERE name = 'Ring';
    
    RAISE NOTICE 'Testing CSV download for Ring category %', v_category_id;
    
    -- Test CSV data retrieval
    FOR v_csv_data IN 
        SELECT * FROM get_category_csv_data(v_category_id)
    LOOP
        v_count := v_count + 1;
        RAISE NOTICE 'CSV Row %: Item % - % - %g gross, %g net, supplier %', 
            v_count, 
            v_csv_data.category_item_no,
            v_csv_data.product_name,
            v_csv_data.gross_weight,
            v_csv_data.net_weight,
            v_csv_data.supplier_code;
    END LOOP;
    
    IF v_count > 0 THEN
        RAISE NOTICE '✅ Test 5 PASSED: CSV data retrieved - % rows', v_count;
    ELSE
        RAISE NOTICE '⚠️  Test 5 WARNING: No CSV data found for Ring category';
    END IF;
    
END $$;

-- Test 6: Summary CSV download
DO $$
DECLARE
    v_summary_data RECORD;
    v_count INTEGER := 0;
    v_total_available INTEGER := 0;
BEGIN
    RAISE NOTICE 'Testing summary CSV download';
    
    -- Test summary CSV data retrieval
    FOR v_summary_data IN 
        SELECT * FROM get_summary_csv_data()
    LOOP
        v_count := v_count + 1;
        v_total_available := v_total_available + v_summary_data.available_items;
        RAISE NOTICE 'Summary Row %: % - % total, % available, % sold, %g net weight', 
            v_count,
            v_summary_data.category_name,
            v_summary_data.total_items,
            v_summary_data.available_items,
            v_summary_data.sold_items,
            v_summary_data.available_net_weight;
    END LOOP;
    
    IF v_count > 0 THEN
        RAISE NOTICE '✅ Test 6 PASSED: Summary CSV data retrieved - % categories, % total available items', v_count, v_total_available;
    ELSE
        RAISE NOTICE '❌ Test 6 FAILED: No summary data found';
    END IF;
    
END $$;

-- Test 7: Verify uniqueness constraints
DO $$
DECLARE
    v_category_id UUID;
    v_duplicate_attempt_failed BOOLEAN := FALSE;
BEGIN
    -- Get ring category ID
    SELECT id INTO v_category_id FROM categories WHERE name = 'Ring';
    
    RAISE NOTICE 'Testing uniqueness constraints for category_item_no';
    
    -- Try to create duplicate category_item_no (should fail)
    BEGIN
        INSERT INTO inventory (category_id, category_item_no, product_name, gross_weight, net_weight)
        VALUES (v_category_id, 1, 'Duplicate Test', 1.000, 1.000);
        
        RAISE NOTICE '❌ Test 7 FAILED: Duplicate category_item_no was allowed';
    EXCEPTION 
        WHEN unique_violation THEN
            v_duplicate_attempt_failed := TRUE;
            RAISE NOTICE '✅ Test 7 PASSED: Duplicate category_item_no correctly prevented';
        WHEN OTHERS THEN
            RAISE NOTICE '❌ Test 7 FAILED: Unexpected error - %', SQLERRM;
    END;
    
END $$;

-- Test 8: View consistency check
DO $$
DECLARE
    v_view_count INTEGER;
    v_direct_count INTEGER;
BEGIN
    RAISE NOTICE 'Testing view consistency';
    
    -- Check current_stock_view vs direct query
    SELECT COUNT(*) INTO v_view_count FROM current_stock_view;
    SELECT COUNT(*) INTO v_direct_count FROM inventory WHERE status = 'AVAILABLE';
    
    IF v_view_count = v_direct_count THEN
        RAISE NOTICE '✅ Test 8 PASSED: current_stock_view consistent - % items', v_view_count;
    ELSE
        RAISE NOTICE '❌ Test 8 FAILED: current_stock_view inconsistent - view: %, direct: %', v_view_count, v_direct_count;
    END IF;
    
END $$;

-- Summary of all test results
SELECT 
    'Test Summary' as test_type,
    COUNT(*) as total_available_items,
    (SELECT COUNT(*) FROM inventory WHERE status = 'SOLD') as total_sold_items,
    (SELECT COUNT(*) FROM bills WHERE status = 'GENERATED') as active_bills,
    (SELECT COUNT(*) FROM bills WHERE status = 'REVERSED') as reversed_bills,
    (SELECT COUNT(*) FROM stock_movements) as total_movements;

-- Show current inventory state
SELECT 
    c.name as category,
    COUNT(*) as items,
    COUNT(CASE WHEN i.status = 'AVAILABLE' THEN 1 END) as available,
    COUNT(CASE WHEN i.status = 'SOLD' THEN 1 END) as sold,
    MIN(CASE WHEN i.status = 'AVAILABLE' THEN i.category_item_no END) as min_available_no,
    MAX(CASE WHEN i.status = 'AVAILABLE' THEN i.category_item_no END) as max_available_no
FROM categories c
LEFT JOIN inventory i ON c.id = i.category_id
GROUP BY c.id, c.name
ORDER BY c.name;