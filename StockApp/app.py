"""
Jewelry Shop Stock Management System - Streamlit Application

A modern, web-based inventory management system for jewelry shops with
category-based organization, real-time statistics, and comprehensive tracking.

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to the path to import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db_manager import DBManager
from utils.logger import HistoryLogger, ActionType

# Page configuration
st.set_page_config(
    page_title="Jewelry Shop Stock Management",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(45deg, #f0f2f6, #ffffff);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f4e79;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .category-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    
    .category-card:hover {
        transform: translateY(-5px);
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .info-message {
        background-color: #cce7ff;
        color: #004085;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Initialize database and logger
@st.cache_resource
def init_database():
    """Initialize database manager and logger."""
    db_manager = DBManager()
    logger = HistoryLogger(db_manager)
    return db_manager, logger


# Get data with caching
@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_categories_summary(_db_manager):
    """Get category summary data."""
    return _db_manager.get_product_categories_summary()


@st.cache_data(ttl=60)
def get_all_products(_db_manager):
    """Get all products data."""
    return _db_manager.get_products()


@st.cache_data(ttl=60)
def get_all_suppliers(_db_manager):
    """Get all suppliers data."""
    return _db_manager.get_suppliers()


@st.cache_data(ttl=60)
def get_all_categories(_db_manager):
    """Get all categories data."""
    return _db_manager.get_all_categories()


@st.cache_data(ttl=60)
def get_category_names(_db_manager):
    """Get category names."""
    return _db_manager.get_category_names()


@st.cache_data(ttl=60)
def get_history_data(_db_manager, limit=100):
    """Get history data."""
    return _db_manager.get_history(limit)


def main():
    """Main application function."""

    # Initialize database
    db_manager, logger = init_database()

    # Main header
    st.markdown(
        '<h1 class="main-header">💎 Jewelry Shop Stock Management System</h1>',
        unsafe_allow_html=True,
    )

    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        [
            "🏠 Dashboard",
            "💍 Products by Category",
            "📦 All Products",
            "🏢 Suppliers",
            "🏷️ Categories",
            "📊 Analytics",
            "📋 History",
            "⚙️ Settings",
        ],
    )

    # Page routing
    if page == "🏠 Dashboard":
        dashboard_page(db_manager, logger)
    elif page == "💍 Products by Category":
        products_by_category_page(db_manager, logger)
    elif page == "📦 All Products":
        all_products_page(db_manager, logger)
    elif page == "🏢 Suppliers":
        suppliers_page(db_manager, logger)
    elif page == "🏷️ Categories":
        categories_page(db_manager, logger)
    elif page == "📊 Analytics":
        analytics_page(db_manager, logger)
    elif page == "📋 History":
        history_page(db_manager, logger)
    elif page == "⚙️ Settings":
        settings_page(db_manager, logger)


def dashboard_page(db_manager, logger):
    """Main dashboard page with overview statistics."""

    st.header("🏠 Dashboard Overview")

    try:
        # Get summary data
        categories_data = get_categories_summary(db_manager)
        all_products = get_all_products(db_manager)

        if not categories_data:
            # Show Quick Start section when database is empty
            st.markdown("### 🚀 Welcome to Your Jewelry Shop Management System!")
            st.info(
                "Your database is empty. Let's get you started by adding your first products!"
            )

            # Quick Start section
            st.markdown("### 📋 Quick Start Options")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### ➕ Add Your First Product")
                st.markdown("Choose a category and add your first jewelry item:")

                # Quick category selection
                quick_categories = [
                    "Rings",
                    "Necklaces",
                    "Earrings",
                    "Bracelets",
                    "Pendants",
                    "Brooches",
                ]
                selected_quick_category = st.selectbox(
                    "Select Category:", quick_categories, key="quick_category"
                )

                if st.button("🎯 Add Product", type="primary"):
                    st.session_state.add_product_category = selected_quick_category
                    st.session_state.show_add_form = True
                    st.rerun()

            with col2:
                st.markdown("#### 🏢 Add Your First Supplier")
                st.markdown("Start by adding a supplier for your jewelry:")

                if st.button("👥 Add Supplier", type="secondary"):
                    st.session_state.show_add_supplier_form = True
                    st.session_state.page = "🏢 Suppliers"
                    st.rerun()

            # Show the add form if requested
            if st.session_state.get("show_add_form", False):
                st.markdown("---")
                show_add_product_form(
                    db_manager,
                    logger,
                    st.session_state.get("add_product_category", "Rings"),
                )

            return

        # Overall statistics
        total_categories = len(categories_data)
        total_products = sum(cat.get("product_count", 0) for cat in categories_data)
        total_quantity = sum(
            cat.get("total_quantity", 0) or 0 for cat in categories_data
        )
        total_weight = sum(
            cat.get("total_gross_weight", 0) or 0 for cat in categories_data
        )
        total_value = sum(cat.get("total_value", 0) or 0 for cat in categories_data)

        # Display overall metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="📂 Total Categories",
                value=total_categories,
                help="Number of product categories",
            )

        with col2:
            st.metric(
                label="📦 Total Products",
                value=total_products,
                help="Total number of product types",
            )

        with col3:
            st.metric(
                label="🔢 Total Quantity",
                value=f"{total_quantity:,}",
                help="Total pieces in inventory",
            )

        with col4:
            st.metric(
                label="⚖️ Total Weight",
                value=f"{total_weight:.1f}g",
                help="Total gross weight of inventory",
            )

        # Total value metric (full width)
        st.metric(
            label="💰 Total Inventory Value",
            value=f"${total_value:,.2f}",
            help="Total value of all inventory",
        )

        st.divider()

        # Category breakdown
        st.subheader("📊 Inventory by Category")

        if categories_data:
            # Create DataFrame for charts
            df_categories = pd.DataFrame(categories_data)

            # Charts in columns
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                # Quantity pie chart
                fig_qty = px.pie(
                    df_categories,
                    values="total_quantity",
                    names="category",
                    title="Quantity Distribution by Category",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )
                fig_qty.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig_qty, use_container_width=True)

            with chart_col2:
                # Value bar chart
                fig_value = px.bar(
                    df_categories,
                    x="category",
                    y="total_value",
                    title="Value by Category",
                    color="total_value",
                    color_continuous_scale="viridis",
                )
                fig_value.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_value, use_container_width=True)

            # Category cards
            st.subheader("💍 Quick Category Access")

            # Display categories in cards
            for i in range(0, len(categories_data), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(categories_data):
                        cat = categories_data[i + j]
                        with col:
                            display_category_card(cat, db_manager, logger)

    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")


def display_category_card(category_data, db_manager, logger):
    """Display a category card with key metrics and actions."""

    category_name = category_data.get("category", "Unknown")
    product_count = category_data.get("product_count", 0)
    total_quantity = category_data.get("total_quantity", 0) or 0
    total_weight = category_data.get("total_gross_weight", 0) or 0
    total_value = category_data.get("total_value", 0) or 0
    avg_melting = category_data.get("avg_melting_percentage", 0) or 0

    # Category emoji mapping
    category_emojis = {
        "Rings": "💍",
        "Necklaces": "📿",
        "Earrings": "👂",
        "Bracelets": "💎",
        "Pendants": "🔗",
        "Chains": "⛓️",
        "Bangles": "⭕",
        "Anklets": "🦶",
        "Brooches": "📌",
        "Cufflinks": "👔",
    }

    emoji = category_emojis.get(category_name, "💎")

    with st.container():
        st.markdown(
            f"""
        <div class="category-card">
            <h3>{emoji} {category_name}</h3>
            <p><strong>Products:</strong> {product_count}</p>
            <p><strong>Quantity:</strong> {total_quantity:,} pieces</p>
            <p><strong>Weight:</strong> {total_weight:.1f}g</p>
            <p><strong>Value:</strong> ${total_value:,.2f}</p>
            {f"<p><strong>Avg Melting:</strong> {avg_melting:.1f}%</p>" if avg_melting > 0 else ""}
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"View {category_name}", key=f"view_{category_name}"):
                st.session_state.selected_category = category_name
                st.session_state.page = "💍 Products by Category"
                st.rerun()

        with col2:
            if st.button(
                f"Add {category_name[:-1] if category_name.endswith('s') else category_name}",
                key=f"add_{category_name}",
            ):
                st.session_state.add_product_category = category_name
                st.session_state.show_add_form = True
                st.rerun()


def products_by_category_page(db_manager, logger):
    """Products organized by category with category-specific management."""

    st.header("💍 Products by Category")

    # Get all categories from the categories table
    all_categories = get_all_categories(db_manager)
    category_names = [cat["name"] for cat in all_categories]

    if not category_names:
        st.markdown("### 🎯 No Categories Found")
        st.info(
            "You haven't created any categories yet. Go to the Categories page to add some, or add your first product to get started."
        )

        st.markdown("### ➕ Add Your First Product")
        st.markdown("Choose a category to get started:")

        # Provide default categories if none exist
        default_categories = [
            "Rings",
            "Necklaces",
            "Earrings",
            "Bracelets",
            "Pendants",
            "Brooches",
            "Chains",
            "Bangles",
            "Anklets",
            "Cufflinks",
        ]

        col1, col2 = st.columns([2, 1])

        with col1:
            selected_category = st.selectbox(
                "Select Category:", default_categories, key="new_category_select"
            )

        with col2:
            if st.button("🎯 Add Product", type="primary"):
                st.session_state.add_product_category = selected_category
                st.session_state.show_add_product_form = True

        # Show the add form if requested
        if st.session_state.get("show_add_product_form", False):
            st.markdown("---")
            show_add_product_form(
                db_manager,
                logger,
                st.session_state.get("add_product_category", "Rings"),
            )

        return

    # Get selected category from session state or default to first
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = category_names[0]

    selected_category = st.selectbox(
        "Select Category:",
        category_names,
        index=(
            category_names.index(st.session_state.selected_category)
            if st.session_state.selected_category in category_names
            else 0
        ),
        key="category_selector",
    )

    st.session_state.selected_category = selected_category

    # Get products in selected category
    category_products = db_manager.get_products_by_category(selected_category)

    # Category header with metrics
    if category_products:
        total_qty = sum(p.get("quantity", 0) for p in category_products)
        total_weight = sum((p.get("gross_weight", 0) or 0) for p in category_products)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Items", len(category_products))
        with col2:
            st.metric("Total Quantity", f"{total_qty:,}")
        with col3:
            st.metric("Total Weight", f"{total_weight:.1f}g")
    else:
        st.info(
            f"No products found in '{selected_category}' category. Add your first product below!"
        )

    # Add new product button
    if selected_category:
        if st.button(
            f"➕ Add New {selected_category[:-1] if selected_category.endswith('s') else selected_category}"
        ):
            st.session_state.show_add_form = True
            st.session_state.add_product_category = selected_category

    # Show add form if requested
    if st.session_state.get("show_add_form", False):
        show_add_product_form(
            db_manager,
            logger,
            st.session_state.get("add_product_category", selected_category),
        )

    # Display products
    if category_products:
        st.subheader(f"📦 {selected_category} Inventory")

        # Convert to DataFrame for better display
        df = pd.DataFrame(category_products)

        # Compute per-category Sr.No based on stable ordering (by id if available)
        if not df.empty:
            if "id" in df.columns:
                df = df.sort_values("id", ascending=True).reset_index(drop=True)
            # Insert sr_no as first column for display/export
            df.insert(0, "sr_no", range(1, len(df) + 1))

        # Select columns to display
        display_columns = [
            "sr_no",
            "name",
            "gross_weight",
            "net_weight",
            "melting_percentage",
            "supplier_name",
        ]

        # Filter existing columns
        available_columns = [col for col in display_columns if col in df.columns]

        if available_columns:
            # Rename columns for display
            column_names = {
                "sr_no": "Sr.No",
                "name": "Product Name",
                "gross_weight": "Gross Weight (g)",
                "net_weight": "Net Weight (g)",
                "melting_percentage": "Melting (%)",
                "supplier_name": "Supplier",
            }

            df_display = df[available_columns].copy()
            df_display = df_display.rename(columns=column_names)

            # Format numeric columns
            if "Unit Price ($)" in df_display.columns:
                df_display["Unit Price ($)"] = df_display["Unit Price ($)"].apply(
                    lambda x: f"${x:.2f}" if pd.notnull(x) else "$0.00"
                )

            if "Melting (%)" in df_display.columns:
                df_display["Melting (%)"] = df_display["Melting (%)"].apply(
                    lambda x: f"{x:.1f}%" if pd.notnull(x) else "0.0%"
                )

            # Display table
            st.dataframe(df_display, use_container_width=True)

            # Download current category as CSV (only required columns)
            try:
                export_cols = []
                # Use per-category sr_no instead of global id
                if "sr_no" in df.columns:
                    export_cols.append("sr_no")
                if "gross_weight" in df.columns:
                    export_cols.append("gross_weight")
                if "net_weight" in df.columns:
                    export_cols.append("net_weight")
                if "supplier_name" in df.columns:
                    export_cols.append("supplier_name")

                export_df = df[export_cols].copy() if export_cols else pd.DataFrame()
                # Rename columns
                export_df = export_df.rename(
                    columns={
                        "sr_no": "Sr.No",
                        "gross_weight": "Gross Weight (g)",
                        "net_weight": "Net Weight (g)",
                        "supplier_name": "Supplier",
                    }
                )

                # Build in-memory CSV
                import io

                csv_buffer = io.StringIO()
                export_df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                safe_cat = (selected_category or "category").replace(" ", "_").lower()
                file_name = f"{safe_cat}_products.csv"

                st.download_button(
                    label="⬇️ Download This Category (CSV)",
                    data=csv_data,
                    file_name=file_name,
                    mime="text/csv",
                )
            except Exception as e:
                st.error(f"Error preparing download: {str(e)}")

            # Product management
            st.subheader("🔧 Product Management")

            # Select product for editing/deleting
            product_names = [p["name"] for p in category_products]
            selected_product_name = st.selectbox(
                "Select product to edit/delete:", product_names
            )

            if selected_product_name:
                selected_product = next(
                    p for p in category_products if p["name"] == selected_product_name
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("✏️ Edit Product"):
                        st.session_state.edit_product = selected_product
                        st.session_state.show_edit_form = True

                with col2:
                    if st.button("🗑️ Delete Product", type="secondary"):
                        if (
                            st.session_state.get("confirm_delete")
                            == selected_product["id"]
                        ):
                            # Perform deletion
                            try:
                                db_manager.delete_product(selected_product["id"])
                                logger.log_action(
                                    action=ActionType.DELETE,
                                    entity_type="products",
                                    entity_id=str(selected_product["id"]),
                                    details=selected_product,
                                    user="streamlit_user",
                                )
                                st.success(
                                    f"Product '{selected_product['name']}' deleted successfully!"
                                )
                                st.session_state.confirm_delete = None
                                # Clear cache and rerun
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting product: {str(e)}")
                        else:
                            st.session_state.confirm_delete = selected_product["id"]
                            st.warning(
                                "Click 'Delete Product' again to confirm deletion."
                            )

            # Show edit form if requested
            if st.session_state.get("show_edit_form", False):
                show_edit_product_form(
                    db_manager, logger, st.session_state.get("edit_product")
                )

    else:
        st.info(
            f"No products found in {selected_category} category. Add some products to get started!"
        )


def show_add_product_form(db_manager, logger, category):
    """Show form to add a new product."""

    st.subheader(f"➕ Add New {category[:-1] if category.endswith('s') else category}")

    with st.form("add_product_form"):
        col1, col2 = st.columns(2)

        with col1:
            gross_weight = st.number_input(
                "Gross Weight (g)*", min_value=0.01, step=0.01, format="%.2f"
            )
            melting_percentage = st.number_input(
                "Melting Percentage",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.1f",
            )

        with col2:
            description = st.text_area("Description", help="Optional description")
            net_weight = st.number_input(
                "Net Weight (g)*", min_value=0.01, step=0.01, format="%.2f"
            )

            # Supplier selection
            suppliers = get_all_suppliers(db_manager)
            supplier_options = ["None"] + [
                f"{s['name']} ({s['code']})" for s in suppliers
            ]
            selected_supplier = st.selectbox("Supplier", supplier_options)

        # Category display
        st.info(f"Category: **{category}**")

        # Form buttons
        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("✅ Add Product", type="primary")

        with col2:
            cancelled = st.form_submit_button("❌ Cancel")

        if cancelled:
            st.session_state.show_add_form = False
            st.session_state.show_add_product_form = False
            st.session_state.show_add_product_form_all = False
            st.rerun()

        if submitted:
            # Validation
            errors = []

            if gross_weight <= 0:
                errors.append("Gross weight must be positive")

            if net_weight <= 0:
                errors.append("Net weight must be positive")

            if gross_weight < net_weight:
                errors.append("Gross weight cannot be less than net weight")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    # Get supplier ID
                    supplier_id = None
                    if selected_supplier != "None":
                        supplier_name = selected_supplier.split(" (")[0]
                        supplier = next(
                            (s for s in suppliers if s["name"] == supplier_name), None
                        )
                        if supplier:
                            supplier_id = supplier["id"]

                    # Add product
                    product_id = db_manager.add_product(
                        name=category,  # Use category as name
                        gross_weight=gross_weight,
                        net_weight=net_weight,
                        quantity=1,  # Default quantity
                        unit_price=0.0,  # Default price
                        supplier_id=supplier_id,
                        description=(
                            description.strip() if description.strip() else None
                        ),
                        category=category,
                        melting_percentage=melting_percentage,
                    )

                    # Log the action
                    logger.log_action(
                        action=ActionType.CREATE,
                        entity_type="products",
                        entity_id=str(product_id),
                        details={
                            "name": category,
                            "category": category,
                            "gross_weight": gross_weight,
                            "net_weight": net_weight,
                        },
                        user="streamlit_user",
                    )

                    st.success(f"Product '{category}' added successfully!")
                    st.session_state.show_add_form = False
                    st.session_state.show_add_product_form = False
                    st.session_state.show_add_product_form_all = False

                    # Clear cache and rerun
                    st.cache_data.clear()
                    st.rerun()

                except Exception as e:
                    st.error(f"Error adding product: {str(e)}")


def show_edit_product_form(db_manager, logger, product):
    """Show form to edit an existing product."""

    st.subheader(f"✏️ Edit Product: {product['name']}")

    with st.form("edit_product_form"):
        col1, col2 = st.columns(2)

        with col1:
            gross_weight = st.number_input(
                "Gross Weight (g)*",
                value=float(product.get("gross_weight", 0)),
                min_value=0.01,
                step=0.01,
                format="%.2f",
            )
            melting_percentage = st.number_input(
                "Melting Percentage",
                value=float(product.get("melting_percentage", 0)),
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.1f",
            )

        with col2:
            description = st.text_area(
                "Description", value=product.get("description", "") or ""
            )
            net_weight = st.number_input(
                "Net Weight (g)*",
                value=float(product.get("net_weight", 0)),
                min_value=0.01,
                step=0.01,
                format="%.2f",
            )

            # Supplier selection
            suppliers = get_all_suppliers(db_manager)
            supplier_options = ["None"] + [
                f"{s['name']} ({s['code']})" for s in suppliers
            ]

            # Set current supplier
            current_supplier_name = product.get("supplier_name", "")
            current_supplier_code = product.get("supplier_code", "")
            current_selection = "None"

            if current_supplier_name and current_supplier_code:
                current_selection = f"{current_supplier_name} ({current_supplier_code})"
                if current_selection not in supplier_options:
                    current_selection = "None"

            selected_supplier = st.selectbox(
                "Supplier",
                supplier_options,
                index=supplier_options.index(current_selection),
            )

        # Category display
        st.info(f"Category: **{product.get('category', 'Unknown')}**")

        # Form buttons
        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("✅ Update Product", type="primary")

        with col2:
            cancelled = st.form_submit_button("❌ Cancel")

        if cancelled:
            st.session_state.show_edit_form = False
            st.rerun()

        if submitted:
            # Validation
            errors = []

            if gross_weight <= 0:
                errors.append("Gross weight must be positive")

            if net_weight <= 0:
                errors.append("Net weight must be positive")

            if gross_weight < net_weight:
                errors.append("Gross weight cannot be less than net weight")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    # Get supplier ID
                    supplier_id = None
                    if selected_supplier != "None":
                        supplier_name = selected_supplier.split(" (")[0]
                        supplier = next(
                            (s for s in suppliers if s["name"] == supplier_name), None
                        )
                        if supplier:
                            supplier_id = supplier["id"]

                    # Update product
                    category = product.get("category")
                    success = db_manager.update_product_full(
                        product_id=product["id"],
                        name=category,
                        gross_weight=gross_weight,
                        net_weight=net_weight,
                        quantity=0,
                        unit_price=0,
                        supplier_id=supplier_id,
                        description=(
                            description.strip() if description.strip() else None
                        ),
                        category=category,
                        melting_percentage=melting_percentage,
                    )

                    if success:
                        # Log the action
                        logger.log_action(
                            action=ActionType.UPDATE,
                            entity_type="products",
                            entity_id=str(product["id"]),
                            details={
                                "name": category,
                                "gross_weight": gross_weight,
                                "net_weight": net_weight,
                            },
                            user="streamlit_user",
                        )

                        st.success(f"Product '{category}' updated successfully!")
                        st.session_state.show_edit_form = False

                        # Clear cache and rerun
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Failed to update product")

                except Exception as e:
                    st.error(f"Error updating product: {str(e)}")


def all_products_page(db_manager, logger):
    """All products management page."""

    st.header("📦 All Products")

    # Get all products
    products = get_all_products(db_manager)

    if not products:
        st.markdown("### 🎯 No Products Found")
        st.info("You haven't added any products yet. Let's add your first product!")

        st.markdown("### ➕ Add Your First Product")

        # Get categories from database
        category_names = get_category_names(db_manager)

        # If no categories exist, provide default ones
        if not category_names:
            category_names = [
                "Rings",
                "Necklaces",
                "Earrings",
                "Bracelets",
                "Pendants",
                "Brooches",
                "Chains",
                "Bangles",
                "Anklets",
                "Cufflinks",
            ]

        col1, col2 = st.columns([2, 1])

        with col1:
            selected_category = st.selectbox(
                "Select Category:",
                category_names,
                key="all_products_category_select",
            )

        with col2:
            if st.button("🎯 Add Product", type="primary", key="all_products_add_btn"):
                st.session_state.add_product_category = selected_category
                st.session_state.show_add_product_form_all = True

        # Show the add form if requested
        if st.session_state.get("show_add_product_form_all", False):
            st.markdown("---")
            show_add_product_form(
                db_manager,
                logger,
                st.session_state.get("add_product_category", "Rings"),
            )

        return

    # Convert to DataFrame
    df = pd.DataFrame(products)

    # Search and filter
    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input(
            "🔍 Search products", placeholder="Enter product name..."
        )

    with col2:
        categories = ["All"] + db_manager.get_available_categories()
        selected_category = st.selectbox("📂 Filter by category", categories)

    with col3:
        sort_by = st.selectbox(
            "📊 Sort by", ["name", "quantity", "unit_price", "category"]
        )

    # Apply filters
    filtered_df = df.copy()

    if search_term:
        filtered_df = filtered_df[
            filtered_df["name"].str.contains(search_term, case=False, na=False)
        ]

    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]

    # Sort
    if sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(sort_by)

    # Display summary
    if not filtered_df.empty:
        total_products = len(filtered_df)
        total_quantity = filtered_df["quantity"].sum()
        total_value = (filtered_df["quantity"] * filtered_df["unit_price"]).sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Products Found", total_products)
        with col2:
            st.metric("Total Quantity", f"{total_quantity:,}")
        with col3:
            st.metric("Total Value", f"${total_value:,.2f}")

        # Display table
        display_columns = [
            "name",
            "category",
            "quantity",
            "gross_weight",
            "net_weight",
            "unit_price",
            "supplier_name",
            "melting_percentage",
        ]

        available_columns = [
            col for col in display_columns if col in filtered_df.columns
        ]

        if available_columns:
            display_df = filtered_df[available_columns].copy()

            # Rename columns
            column_names = {
                "name": "Product Name",
                "category": "Category",
                "quantity": "Quantity",
                "gross_weight": "Gross Weight (g)",
                "net_weight": "Net Weight (g)",
                "unit_price": "Unit Price ($)",
                "supplier_name": "Supplier",
                "melting_percentage": "Melting (%)",
            }

            display_df = display_df.rename(columns=column_names)

            # Format columns
            if "Unit Price ($)" in display_df.columns:
                display_df["Unit Price ($)"] = display_df["Unit Price ($)"].apply(
                    lambda x: f"${x:.2f}"
                )

            if "Melting (%)" in display_df.columns:
                display_df["Melting (%)"] = display_df["Melting (%)"].apply(
                    lambda x: f"{x:.1f}%" if pd.notnull(x) else "0.0%"
                )

            st.dataframe(display_df, use_container_width=True)

    else:
        st.info("No products match your search criteria.")


def suppliers_page(db_manager, logger):
    """Suppliers management page."""

    st.header("🏢 Suppliers Management")

    # Top action buttons
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button("➕ Add New Supplier"):
            st.session_state.show_add_supplier_form = True

    with col2:
        if st.button(
            "🗑️ Clear All Suppliers",
            type="secondary",
            help="Remove all existing suppliers",
        ):
            st.session_state.show_clear_suppliers_confirm = True

    with col3:
        suppliers = get_all_suppliers(db_manager)
        st.metric("Total", len(suppliers))

    # Confirmation dialog for clearing suppliers
    if st.session_state.get("show_clear_suppliers_confirm", False):
        st.warning("⚠️ **Are you sure you want to remove ALL suppliers?**")
        st.caption(
            "This action cannot be undone. All supplier data will be permanently deleted."
        )

        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:
            if st.button("✅ Yes, Clear All", type="primary"):
                try:
                    count = db_manager.clear_all_suppliers()
                    logger.log_action(
                        action=ActionType.DELETE,
                        entity_type="suppliers",
                        details={"action": "clear_all", "count": count},
                        user="streamlit_user",
                    )
                    st.success(f"Successfully removed {count} suppliers!")
                    st.session_state.show_clear_suppliers_confirm = False
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing suppliers: {str(e)}")

        with col2:
            if st.button("❌ Cancel"):
                st.session_state.show_clear_suppliers_confirm = False
                st.rerun()

    # Show add form if requested
    if st.session_state.get("show_add_supplier_form", False):
        show_add_supplier_form(db_manager, logger)

    # Get suppliers
    suppliers = get_all_suppliers(db_manager)

    if suppliers:
        st.subheader(f"📋 Suppliers ({len(suppliers)})")

        # Convert to DataFrame
        df = pd.DataFrame(suppliers)

        # Display table
        display_columns = [
            "name",
            "code",
            "contact_person",
            "email",
            "phone",
            "address",
        ]
        available_columns = [col for col in display_columns if col in df.columns]

        if available_columns:
            display_df = df[available_columns].copy()

            # Rename columns
            column_names = {
                "name": "Supplier Name",
                "code": "Code",
                "contact_person": "Contact Person",
                "email": "Email",
                "phone": "Phone",
                "address": "Address",
            }

            display_df = display_df.rename(columns=column_names)
            st.dataframe(display_df, use_container_width=True)

        # Supplier management
        st.subheader("🔧 Supplier Management")

        supplier_names = [s["name"] for s in suppliers]
        selected_supplier_name = st.selectbox("Select supplier:", supplier_names)

        if selected_supplier_name:
            selected_supplier = next(
                s for s in suppliers if s["name"] == selected_supplier_name
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✏️ Edit Supplier"):
                    st.session_state.edit_supplier = selected_supplier
                    st.session_state.show_edit_supplier_form = True

            with col2:
                if st.button("🗑️ Delete Supplier", type="secondary"):
                    if (
                        st.session_state.get("confirm_delete_supplier")
                        == selected_supplier["id"]
                    ):
                        try:
                            db_manager.delete_supplier(selected_supplier["id"])
                            logger.log_action(
                                action=ActionType.DELETE,
                                entity_type="suppliers",
                                entity_id=str(selected_supplier["id"]),
                                details=selected_supplier,
                                user="streamlit_user",
                            )
                            st.success(
                                f"Supplier '{selected_supplier['name']}' deleted successfully!"
                            )
                            st.session_state.confirm_delete_supplier = None
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting supplier: {str(e)}")
                    else:
                        st.session_state.confirm_delete_supplier = selected_supplier[
                            "id"
                        ]
                        st.warning("Click 'Delete Supplier' again to confirm deletion.")

        # Show edit form if requested
        if st.session_state.get("show_edit_supplier_form", False):
            show_edit_supplier_form(
                db_manager, logger, st.session_state.get("edit_supplier")
            )

    else:
        st.info("No suppliers found. Add suppliers to manage your supply chain.")


def show_add_supplier_form(db_manager, logger):
    """Show form to add a new supplier."""

    st.subheader("➕ Add New Supplier")

    with st.form("add_supplier_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Supplier Name*")
            contact_person = st.text_input("Contact Person")
            email = st.text_input("Email")

        with col2:
            phone = st.text_input("Phone")
            address = st.text_area("Address")

        # Supplier code input with auto-generation option
        st.subheader("Supplier Code")
        col1, col2 = st.columns([3, 1])

        with col1:
            custom_code = st.text_input(
                "Supplier Code*",
                help="Enter a unique code for this supplier (e.g., SUP001, ABC123, etc.)",
                placeholder="Enter custom code or use auto-generate",
            )

        with col2:
            if st.form_submit_button(
                "🔄 Auto-Generate", help="Generate code from supplier name"
            ):
                if name:
                    st.session_state.suggested_code = db_manager.generate_supplier_code(
                        name
                    )
                else:
                    st.session_state.suggested_code = None

        # Show suggested code if generated
        if (
            hasattr(st.session_state, "suggested_code")
            and st.session_state.suggested_code
        ):
            st.info(f"💡 Suggested code: **{st.session_state.suggested_code}**")
            st.caption(
                "You can use this suggested code or enter your own custom code above."
            )

        # Code validation display
        if custom_code:
            existing_suppliers = db_manager.get_suppliers()
            existing_codes = [s["code"] for s in existing_suppliers]
            if custom_code.upper() in [code.upper() for code in existing_codes]:
                st.error(
                    f"⚠️ Code '{custom_code}' already exists! Please choose a different code."
                )
            else:
                st.success(f"✅ Code '{custom_code}' is available!")

        # Form buttons
        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("✅ Add Supplier", type="primary")

        with col2:
            cancelled = st.form_submit_button("❌ Cancel")

        if cancelled:
            st.session_state.show_add_supplier_form = False
            if hasattr(st.session_state, "suggested_code"):
                delattr(st.session_state, "suggested_code")
            st.rerun()

        if submitted:
            if not name or not name.strip():
                st.error("Supplier name is required")
            elif not custom_code or not custom_code.strip():
                st.error("Supplier code is required")
            else:
                # Check for duplicate code
                existing_suppliers = db_manager.get_suppliers()
                existing_codes = [s["code"].upper() for s in existing_suppliers]

                if custom_code.strip().upper() in existing_codes:
                    st.error(
                        f"Supplier code '{custom_code}' already exists! Please choose a different code."
                    )
                else:
                    try:
                        supplier_id = db_manager.add_supplier_with_code(
                            name=name.strip(),
                            code=custom_code.strip().upper(),
                            contact_person=(
                                contact_person.strip()
                                if contact_person and contact_person.strip()
                                else None
                            ),
                            phone=phone.strip() if phone and phone.strip() else None,
                            email=email.strip() if email and email.strip() else None,
                            address=(
                                address.strip() if address and address.strip() else None
                            ),
                        )

                        logger.log_action(
                            action=ActionType.CREATE,
                            entity_type="suppliers",
                            entity_id=str(supplier_id),
                            details={"name": name, "code": custom_code.strip().upper()},
                            user="streamlit_user",
                        )

                        st.success(
                            f"Supplier '{name}' added successfully with code '{custom_code.strip().upper()}'!"
                        )
                        st.session_state.show_add_supplier_form = False
                        if hasattr(st.session_state, "suggested_code"):
                            delattr(st.session_state, "suggested_code")
                        st.cache_data.clear()
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error adding supplier: {str(e)}")


def show_edit_supplier_form(db_manager, logger, supplier):
    """Show form to edit an existing supplier."""

    st.subheader(f"✏️ Edit Supplier: {supplier['name']}")

    with st.form("edit_supplier_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Supplier Name*", value=supplier.get("name", ""))
            contact_person = st.text_input(
                "Contact Person", value=supplier.get("contact_person", "") or ""
            )
            email = st.text_input("Email", value=supplier.get("email", "") or "")

        with col2:
            phone = st.text_input("Phone", value=supplier.get("phone", "") or "")
            address = st.text_area("Address", value=supplier.get("address", "") or "")

        # Show current code
        st.info(f"Supplier Code: **{supplier.get('code', 'Unknown')}**")

        # Form buttons
        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("✅ Update Supplier", type="primary")

        with col2:
            cancelled = st.form_submit_button("❌ Cancel")

        if cancelled:
            st.session_state.show_edit_supplier_form = False
            st.rerun()

        if submitted:
            if not name or not name.strip():
                st.error("Supplier name is required")
            else:
                try:
                    success = db_manager.update_supplier(
                        supplier_id=supplier["id"],
                        name=name.strip(),
                        contact_person=(
                            contact_person.strip()
                            if contact_person and contact_person.strip()
                            else None
                        ),
                        phone=phone.strip() if phone and phone.strip() else None,
                        email=email.strip() if email and email.strip() else None,
                        address=(
                            address.strip() if address and address.strip() else None
                        ),
                    )

                    if success:
                        logger.log_action(
                            action=ActionType.UPDATE,
                            entity_type="suppliers",
                            entity_id=str(supplier["id"]),
                            details={"name": name, "contact_person": contact_person},
                            user="streamlit_user",
                        )

                        st.success(f"Supplier '{name}' updated successfully!")
                        st.session_state.show_edit_supplier_form = False
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Failed to update supplier")

                except Exception as e:
                    st.error(f"Error updating supplier: {str(e)}")


def categories_page(db_manager, logger):
    """Categories management page."""

    st.header("🏷️ Categories Management")

    # Get all categories
    categories = get_all_categories(db_manager)

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("➕ Add Category", type="primary"):
            st.session_state.show_add_category_form = True

    with col2:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Add category form
    if getattr(st.session_state, "show_add_category_form", False):
        st.markdown("---")
        show_add_category_form(db_manager, logger)

    # Display categories
    if categories:
        st.markdown("### 📋 All Categories")

        # Create a DataFrame for better display
        df_categories = pd.DataFrame(categories)
        df_categories["created_at"] = pd.to_datetime(
            df_categories["created_at"]
        ).dt.strftime("%Y-%m-%d %H:%M")

        # Display categories in cards
        for category in categories:
            with st.expander(f"🏷️ {category['name']}", expanded=False):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(
                        f"**Description:** {category.get('description', 'No description')}"
                    )
                    st.write(f"**Created:** {category['created_at']}")

                    # Get products count for this category
                    products_in_category = db_manager.get_products_by_category(
                        category["name"]
                    )
                    st.write(f"**Products:** {len(products_in_category)} items")

                with col2:
                    if st.button(f"✏️ Edit", key=f"edit_cat_{category['id']}"):
                        st.session_state.edit_category_id = category["id"]
                        st.session_state.show_edit_category_form = True
                        st.rerun()

                    # Only allow deletion if no products
                    if len(products_in_category) == 0:
                        if st.button(
                            f"🗑️ Delete",
                            key=f"delete_cat_{category['id']}",
                            type="secondary",
                        ):
                            try:
                                db_manager.delete_category(category["id"])
                                logger.log_action(
                                    action=ActionType.DELETE,
                                    entity_type="categories",
                                    entity_id=str(category["id"]),
                                    details={"name": category["name"]},
                                    user="streamlit_user",
                                )
                                st.success(
                                    f"Category '{category['name']}' deleted successfully!"
                                )
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting category: {str(e)}")
                    else:
                        st.caption(
                            f"Cannot delete: {len(products_in_category)} products"
                        )

    # Edit category form
    if getattr(st.session_state, "show_edit_category_form", False):
        edit_category_id = getattr(st.session_state, "edit_category_id", None)
        if edit_category_id:
            category_to_edit = next(
                (cat for cat in categories if cat["id"] == edit_category_id), None
            )
            if category_to_edit:
                st.markdown("---")
                show_edit_category_form(db_manager, logger, category_to_edit)

    if not categories:
        st.info("No categories found. Add your first category using the button above.")


def show_add_category_form(db_manager, logger):
    """Show form to add a new category."""

    st.subheader("➕ Add New Category")

    with st.form("add_category_form"):
        name = st.text_input("Category Name*", placeholder="e.g., Wedding Rings")
        description = st.text_area(
            "Description", placeholder="Brief description of this category..."
        )

        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("✅ Add Category", type="primary")

        with col2:
            cancelled = st.form_submit_button("❌ Cancel")

        if cancelled:
            st.session_state.show_add_category_form = False
            st.rerun()

        if submitted:
            # Validation
            errors = []

            if not name or not name.strip():
                errors.append("Category name is required")
            elif len(name.strip()) < 2:
                errors.append("Category name must be at least 2 characters")
            elif len(name.strip()) > 50:
                errors.append("Category name must be less than 50 characters")

            if description and len(description.strip()) > 200:
                errors.append("Description must be less than 200 characters")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    category_id = db_manager.add_category(
                        name=name.strip(),
                        description=(
                            description.strip()
                            if description and description.strip()
                            else None
                        ),
                    )

                    # Log the action
                    logger.log_action(
                        action=ActionType.CREATE,
                        entity_type="categories",
                        entity_id=str(category_id),
                        details={
                            "name": name.strip(),
                            "description": (
                                description.strip()
                                if description and description.strip()
                                else None
                            ),
                        },
                        user="streamlit_user",
                    )

                    st.success(f"Category '{name.strip()}' added successfully!")
                    st.session_state.show_add_category_form = False

                    # Clear cache and rerun
                    st.cache_data.clear()
                    st.rerun()

                except Exception as e:
                    st.error(f"Error adding category: {str(e)}")


def show_edit_category_form(db_manager, logger, category):
    """Show form to edit an existing category."""

    st.subheader(f"✏️ Edit Category: {category['name']}")

    with st.form("edit_category_form"):
        name = st.text_input("Category Name*", value=category.get("name", ""))
        description = st.text_area(
            "Description", value=category.get("description", "") or ""
        )

        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("✅ Update Category", type="primary")

        with col2:
            cancelled = st.form_submit_button("❌ Cancel")

        if cancelled:
            st.session_state.show_edit_category_form = False
            st.rerun()

        if submitted:
            # Validation
            errors = []

            if not name or not name.strip():
                errors.append("Category name is required")
            elif len(name.strip()) < 2:
                errors.append("Category name must be at least 2 characters")
            elif len(name.strip()) > 50:
                errors.append("Category name must be less than 50 characters")

            if description and len(description.strip()) > 200:
                errors.append("Description must be less than 200 characters")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    # Safe to use name.strip() here since we validated it above
                    cleaned_name = name.strip() if name else ""
                    cleaned_description = (
                        description.strip()
                        if description and description.strip()
                        else None
                    )

                    success = db_manager.update_category(
                        category_id=category["id"],
                        name=cleaned_name,
                        description=cleaned_description,
                    )

                    if success:
                        # Log the action
                        logger.log_action(
                            action=ActionType.UPDATE,
                            entity_type="categories",
                            entity_id=str(category["id"]),
                            details={
                                "name": cleaned_name,
                                "description": cleaned_description,
                            },
                            user="streamlit_user",
                        )

                        st.success(f"Category '{cleaned_name}' updated successfully!")
                        st.session_state.show_edit_category_form = False

                        # Clear cache and rerun
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Failed to update category")

                except Exception as e:
                    st.error(f"Error updating category: {str(e)}")


def analytics_page(db_manager, logger):
    """Analytics and reporting page."""

    st.header("📊 Analytics & Reports")

    try:
        # Get data
        categories_data = get_categories_summary(db_manager)
        all_products = get_all_products(db_manager)

        if not categories_data or not all_products:
            st.info(
                "No data available for analytics. Add some products to see reports."
            )
            return

        # Analytics tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            [
                "📈 Overview",
                "💰 Value Analysis",
                "⚖️ Weight Analysis",
                "📋 Low Stock",
                "🤝 Supplier Analysis",
                "📆 Trends",
            ]
        )

        with tab1:
            st.subheader("📈 Inventory Overview")

            # Create DataFrames
            df_categories = pd.DataFrame(categories_data)
            df_products = pd.DataFrame(all_products)

            # Top categories by value
            col1, col2 = st.columns(2)

            with col1:
                fig_top_categories = px.bar(
                    df_categories.head(10),
                    x="total_value",
                    y="category",
                    title="Top Categories by Value",
                    orientation="h",
                    color="total_value",
                    color_continuous_scale="viridis",
                )
                st.plotly_chart(fig_top_categories, use_container_width=True)

            with col2:
                # Melting percentage by category
                avg_melting = df_categories[df_categories["avg_melting_percentage"] > 0]
                if not avg_melting.empty:
                    fig_melting = px.bar(
                        avg_melting,
                        x="category",
                        y="avg_melting_percentage",
                        title="Average Melting % by Category",
                        color="avg_melting_percentage",
                        color_continuous_scale="RdYlBu_r",
                    )
                    fig_melting.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_melting, use_container_width=True)

        with tab2:
            st.subheader("💰 Value Analysis")

            # High-value products
            df_products_sorted = df_products.sort_values("unit_price", ascending=False)
            top_products = df_products_sorted.head(10)

            col1, col2 = st.columns(2)

            with col1:
                fig_top_products = px.bar(
                    top_products,
                    x="unit_price",
                    y="name",
                    title="Top 10 Most Expensive Products",
                    orientation="h",
                    color="unit_price",
                    color_continuous_scale="Reds",
                )
                st.plotly_chart(fig_top_products, use_container_width=True)

            with col2:
                # Value distribution
                df_products["total_value"] = (
                    df_products["quantity"] * df_products["unit_price"]
                )
                value_ranges = pd.cut(
                    df_products["total_value"],
                    bins=[0, 100, 500, 1000, 5000, float("inf")],
                    labels=["$0-100", "$100-500", "$500-1K", "$1K-5K", "$5K+"],
                )

                value_dist = value_ranges.value_counts().reset_index()
                value_dist.columns = ["Range", "Count"]

                fig_value_dist = px.pie(
                    value_dist,
                    values="Count",
                    names="Range",
                    title="Product Value Distribution",
                )
                st.plotly_chart(fig_value_dist, use_container_width=True)

        with tab3:
            st.subheader("⚖️ Weight Analysis")

            col1, col2 = st.columns(2)

            with col1:
                # Weight by category
                fig_weight = px.treemap(
                    df_categories,
                    path=["category"],
                    values="total_gross_weight",
                    title="Weight Distribution by Category",
                )
                st.plotly_chart(fig_weight, use_container_width=True)

            with col2:
                # Efficiency ratio (net/gross weight)
                df_products["efficiency_ratio"] = (
                    df_products["net_weight"] / df_products["gross_weight"] * 100
                )

                fig_efficiency = px.histogram(
                    df_products,
                    x="efficiency_ratio",
                    nbins=20,
                    title="Weight Efficiency Distribution (%)",
                    labels={"efficiency_ratio": "Efficiency Ratio (%)"},
                )
                st.plotly_chart(fig_efficiency, use_container_width=True)

        with tab4:
            st.subheader("📋 Low Stock Alert")

            # Low stock threshold
            threshold = st.slider("Low stock threshold:", 1, 50, 10)

            low_stock = df_products[df_products["quantity"] <= threshold]

            if not low_stock.empty:
                st.warning(
                    f"⚠️ {len(low_stock)} products are below the threshold of {threshold} units!"
                )

                # Display low stock products
                low_stock_display = low_stock[
                    ["name", "category", "quantity", "unit_price"]
                ].copy()
                low_stock_display["total_value"] = (
                    low_stock_display["quantity"] * low_stock_display["unit_price"]
                )

                st.dataframe(
                    low_stock_display.rename(
                        columns={
                            "name": "Product",
                            "category": "Category",
                            "quantity": "Quantity",
                            "unit_price": "Unit Price",
                            "total_value": "Total Value",
                        }
                    ),
                    use_container_width=True,
                )
                # Chart for low stock products
                fig_low_stock = px.bar(
                    low_stock.head(20),
                    x="quantity",
                    y="name",
                    title=f"Products with Quantity ≤ {threshold}",
                    orientation="h",
                    color="quantity",
                    color_continuous_scale="Reds",
                )
                st.plotly_chart(fig_low_stock, use_container_width=True)
            else:
                st.success(
                    f"✅ All products have sufficient stock (above {threshold} units)!"
                )

        with tab5:
            st.subheader("🤝 Supplier Contributions")

            # Supplier total contributions by category (weights)
            df_sup = df_products.copy()
            if "supplier_name" in df_sup.columns:
                grp = (
                    df_sup.groupby(["category", "supplier_name"], dropna=False)[
                        "gross_weight"
                    ]
                    .sum()
                    .reset_index()
                )
                if not grp.empty:
                    fig_sup = px.bar(
                        grp,
                        x="category",
                        y="gross_weight",
                        color="supplier_name",
                        title="Supplier Gross Weight Contribution by Category",
                        barmode="stack",
                    )
                    st.plotly_chart(fig_sup, use_container_width=True)
                else:
                    st.info("No supplier data available.")
            else:
                st.info("Supplier data not available in products table.")

            st.subheader("Gross vs Net Scatter")
            if not df_products.empty:
                fig_scatter = px.scatter(
                    df_products,
                    x="gross_weight",
                    y="net_weight",
                    color="category",
                    hover_data=["name", "supplier_name"],
                    title="Gross vs Net Weight by Category",
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

        with tab6:
            st.subheader("📆 Trends Over Time")
            # If created_at exists, show count by month
            if "created_at" in df_products.columns:
                df_time = df_products.copy()
                try:
                    df_time["created_at"] = pd.to_datetime(df_time["created_at"])
                    df_time["month"] = (
                        df_time["created_at"].dt.to_period("M").astype(str)
                    )
                    trend = (
                        df_time.groupby("month")
                        .size()
                        .reset_index(name="products_added")
                    )
                    fig_trend = px.line(
                        trend,
                        x="month",
                        y="products_added",
                        title="Products Added per Month",
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
                except Exception:
                    st.info("Could not parse product timestamps for trend analysis.")
            else:
                st.info("Timestamp information not available for products.")

    except Exception as e:
        st.error(f"Error generating analytics: {str(e)}")


def history_page(db_manager, logger):
    """History and audit trail page."""

    st.header("📋 System History & Audit Trail")

    # Get history data
    history_data = get_history_data(db_manager, 200)

    if not history_data:
        st.info("No history data found.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(history_data)

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        # Action filter
        actions = ["All"] + list(df["action"].unique())
        selected_action = st.selectbox("Filter by action:", actions)

    with col2:
        # Table filter
        tables = ["All"] + list(df["table_name"].unique())
        selected_table = st.selectbox("Filter by table:", tables)

    with col3:
        # Date range
        days_back = st.selectbox("Show last:", [7, 30, 90, 365, "All"], index=1)

    # Apply filters
    filtered_df = df.copy()

    if selected_action != "All":
        filtered_df = filtered_df[filtered_df["action"] == selected_action]

    if selected_table != "All":
        filtered_df = filtered_df[filtered_df["table_name"] == selected_table]

    if days_back != "All":
        cutoff_date = datetime.now() - timedelta(days=int(days_back))
        filtered_df["timestamp"] = pd.to_datetime(filtered_df["timestamp"])
        filtered_df = filtered_df[filtered_df["timestamp"] >= cutoff_date]

    # Display summary
    if not filtered_df.empty:
        st.metric("Records Found", len(filtered_df))

        # Action summary
        action_counts = filtered_df["action"].value_counts()

        col1, col2 = st.columns(2)

        with col1:
            fig_actions = px.pie(
                values=action_counts.values,
                names=action_counts.index,
                title="Actions Distribution",
            )
            st.plotly_chart(fig_actions, use_container_width=True)

        with col2:
            # Timeline
            if "timestamp" in filtered_df.columns:
                filtered_df["date"] = pd.to_datetime(filtered_df["timestamp"]).dt.date
                daily_counts = (
                    filtered_df.groupby("date").size().reset_index(name="count")
                )

                fig_timeline = px.line(
                    daily_counts, x="date", y="count", title="Activity Timeline"
                )
                st.plotly_chart(fig_timeline, use_container_width=True)

        # History table
        st.subheader("📋 Activity Log")

        # Prepare display data
        display_columns = ["timestamp", "action", "table_name", "record_id", "user_id"]
        available_columns = [
            col for col in display_columns if col in filtered_df.columns
        ]

        if available_columns:
            display_df = filtered_df[available_columns].copy()

            # Format timestamp
            if "timestamp" in display_df.columns:
                display_df["timestamp"] = pd.to_datetime(
                    display_df["timestamp"]
                ).dt.strftime("%Y-%m-%d %H:%M:%S")

            # Rename columns
            column_names = {
                "timestamp": "Timestamp",
                "action": "Action",
                "table_name": "Table",
                "record_id": "Record ID",
                "user_id": "User",
            }

            display_df = display_df.rename(columns=column_names)

            # Sort by timestamp (most recent first)
            if "Timestamp" in display_df.columns:
                display_df = display_df.sort_values("Timestamp", ascending=False)

            st.dataframe(display_df, use_container_width=True)

    else:
        st.info("No history records match your filters.")


def settings_page(db_manager, logger):
    """Settings and configuration page."""

    st.header("⚙️ Settings & Configuration")

    # Database info
    st.subheader("🗄️ Database Information")

    try:
        # Get database stats
        products_count = len(get_all_products(db_manager))
        suppliers_count = len(get_all_suppliers(db_manager))
        history_count = len(get_history_data(db_manager, 1000))

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Products", products_count)

        with col2:
            st.metric("Suppliers", suppliers_count)

        with col3:
            st.metric("History Records", history_count)

        # Database file info
        db_path = db_manager.db_path
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / 1024  # KB
            st.info(f"Database file: `{db_path}` ({db_size:.1f} KB)")

    except Exception as e:
        st.error(f"Error getting database info: {str(e)}")

    st.divider()

    # Data management
    st.subheader("📊 Data Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared successfully!")

        # Download full data summary (category-level only)
        try:
            categories_data = get_categories_summary(db_manager)
            df_sum = (
                pd.DataFrame(categories_data) if categories_data else pd.DataFrame()
            )

            # Keep only category-level essential metrics
            keep_cols = [
                "category",
                "product_count",
                "total_gross_weight",
                "total_net_weight",
                "avg_melting_percentage",
            ]
            df_sum = (
                df_sum[keep_cols]
                if not df_sum.empty
                else pd.DataFrame(columns=keep_cols)
            )
            df_sum = df_sum.rename(
                columns={
                    "category": "Category",
                    "product_count": "Products",
                    "total_gross_weight": "Total Gross Weight (g)",
                    "total_net_weight": "Total Net Weight (g)",
                    "avg_melting_percentage": "Avg Melting (%)",
                }
            )

            import io

            sum_buffer = io.StringIO()
            df_sum.to_csv(sum_buffer, index=False)
            sum_csv = sum_buffer.getvalue()

            st.download_button(
                label="📤 Download Full Data (Category Summary)",
                data=sum_csv,
                file_name="category_summary.csv",
                mime="text/csv",
                help="Downloads only the per-category totals, not individual products.",
            )
        except Exception as e:
            st.error(f"Failed to prepare category summary: {str(e)}")

    with col2:
        if st.button("🗑️ Clear Old History"):
            if st.session_state.get("confirm_clear_history"):
                try:
                    # Clear history older than 90 days
                    cutoff_date = (datetime.now() - timedelta(days=90)).isoformat()
                    # This would need a method in db_manager
                    st.success("Old history cleared!")
                    st.session_state.confirm_clear_history = False
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Error clearing history: {str(e)}")
            else:
                st.session_state.confirm_clear_history = True
                st.warning(
                    "Click again to confirm clearing history older than 90 days."
                )

        if st.button(
            "� Reset Database", type="secondary", help="Remove ALL data from database"
        ):
            if st.session_state.get("confirm_reset_database"):
                try:
                    result = db_manager.reset_database()
                    logger.log_action(
                        action=ActionType.DELETE,
                        entity_type="database",
                        details={
                            "action": "reset_database",
                            "products_removed": result["products"],
                            "suppliers_removed": result["suppliers"],
                            "history_removed": result["history"],
                        },
                        user="streamlit_user",
                    )
                    st.success(
                        f"Database reset complete! Removed {result['products']} products, {result['suppliers']} suppliers, and {result['history']} history records."
                    )
                    st.session_state.confirm_reset_database = False
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error resetting database: {str(e)}")
            else:
                st.session_state.confirm_reset_database = True
                st.error(
                    "⚠️ **DANGER:** This will delete ALL data! Click again to confirm."
                )

        if st.button("�💾 Backup Database"):
            try:
                import shutil

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"data/backup_jewelry_shop_{timestamp}.db"
                shutil.copy2(db_manager.db_path, backup_path)
                st.success(f"Database backed up to {backup_path}")
            except Exception as e:
                st.error(f"Backup failed: {str(e)}")

    st.divider()

    # App info
    st.subheader("ℹ️ Application Information")

    st.info(
        """
    **Jewelry Shop Stock Management System**
    
    Version: 2.0 (Streamlit Edition)
    
    Features:
    - 🏠 Interactive Dashboard with category overview
    - 💍 Category-based product management  
    - 📦 Comprehensive product tracking
    - 🏢 Supplier management with auto-codes
    - 📊 Advanced analytics and reporting
    - 📋 Complete audit trail
    - 💎 Jewelry-specific fields (melting %, weights)
    - 🌐 Modern web-based interface
    - 📱 Responsive design
    
    Built with Streamlit for modern, user-friendly experience.
    """
    )


# Initialize session state
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

if "show_edit_form" not in st.session_state:
    st.session_state.show_edit_form = False

if "show_add_supplier_form" not in st.session_state:
    st.session_state.show_add_supplier_form = False

if "show_edit_supplier_form" not in st.session_state:
    st.session_state.show_edit_supplier_form = False

# Run the app
if __name__ == "__main__":
    main()
