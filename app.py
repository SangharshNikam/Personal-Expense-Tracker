import streamlit as st
import pandas as pd
from datetime import date, datetime
from supabase import create_client, Client

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="centered")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

CATEGORIES = ["Food", "Household", "Transport", "Bills & Utilities", "Entertainment", "Other"]
PAYMENT_METHODS = ["Cash", "UPI", "Credit Card", "Debit Card", "Other"]

# ----------------------------
# DATA FUNCTIONS
# ----------------------------
def add_expense(exp_date, amount, category, payment_method, description):
    supabase.table("expenses").insert({
        "date": str(exp_date),
        "amount": float(amount),
        "category": category,
        "payment_method": payment_method,
        "description": description,
    }).execute()

@st.cache_data(ttl=30)
def get_all_expenses():
    response = supabase.table("expenses").select("*").order("date", desc=True).execute()
    df = pd.DataFrame(response.data)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)
        df["day_name"] = df["date"].dt.day_name()
    return df

def delete_expense(expense_id):
    supabase.table("expenses").delete().eq("id", expense_id).execute()

# ----------------------------
# UI
# ----------------------------
st.title("💰 Personal Expense Tracker")

tab1, tab2, tab3 = st.tabs(["➕ Add Expense", "📊 Analysis", "📋 History"])

# --- TAB 1: ADD EXPENSE ---
with tab1:
    st.subheader("Add a new expense")
    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            exp_date = st.date_input("Date", value=date.today())
            amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
        with col2:
            category = st.selectbox("Category", CATEGORIES)
            payment_method = st.selectbox("Payment Method", PAYMENT_METHODS)
        description = st.text_input("Description (optional)")

        submitted = st.form_submit_button("Add Expense", use_container_width=True)
        if submitted:
            if amount <= 0:
                st.error("Amount must be greater than 0.")
            else:
                add_expense(exp_date, amount, category, payment_method, description)
                st.cache_data.clear()
                st.success(f"Added ₹{amount:.2f} under {category}")

    st.divider()
    st.caption("Quick add — common categories")
    qcols = st.columns(len(CATEGORIES))
    for i, cat in enumerate(CATEGORIES):
        if qcols[i].button(cat, use_container_width=True):
            st.session_state["quick_category"] = cat
            st.info(f"Selected '{cat}' — enter the amount below and submit.")

# --- TAB 2: ANALYSIS ---
with tab2:
    df = get_all_expenses()
    if df.empty:
        st.info("No expenses logged yet. Add your first one in the 'Add Expense' tab.")
    else:
        st.subheader("Overview")

        view = st.radio("View by", ["Daily", "Monthly"], horizontal=True)

        if view == "Monthly":
            monthly = df.groupby("month")["amount"].sum().sort_index()
            st.metric("This month's spend", f"₹{monthly.iloc[-1]:,.2f}" if len(monthly) else "₹0")
            st.bar_chart(monthly)
        else:
            daily = df.groupby(df["date"].dt.date)["amount"].sum().sort_index()
            st.metric("Today's spend", f"₹{daily.get(date.today(), 0):,.2f}")
            st.line_chart(daily)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Category-wise spending**")
            cat_spend = df.groupby("category")["amount"].sum().sort_values(ascending=False)
            st.bar_chart(cat_spend)
        with col2:
            st.markdown("**Payment method breakdown**")
            pm_spend = df.groupby("payment_method")["amount"].sum().sort_values(ascending=False)
            st.bar_chart(pm_spend)

        st.markdown("**Top 5 highest expenses**")
        top5 = df.nlargest(5, "amount")[["date", "amount", "category", "description"]]
        st.dataframe(top5, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Budget tracking")
        budget = st.number_input("Set your monthly budget (₹)", min_value=0.0, value=15000.0, step=500.0)
        current_month = pd.Timestamp.today().to_period("M").strftime("%Y-%m")
        spent_this_month = df[df["month"] == current_month]["amount"].sum()
        remaining = budget - spent_this_month
        pct = min(spent_this_month / budget, 1.0) if budget > 0 else 0
        st.progress(pct, text=f"₹{spent_this_month:,.2f} spent of ₹{budget:,.2f} ({pct*100:.0f}%)")
        if remaining < 0:
            st.error(f"Over budget by ₹{abs(remaining):,.2f}")
        else:
            st.success(f"₹{remaining:,.2f} remaining this month")

# --- TAB 3: HISTORY ---
with tab3:
    st.subheader("All expenses")
    df = get_all_expenses()
    if df.empty:
        st.info("No expenses yet.")
    else:
        month_filter = st.selectbox("Filter by month", ["All"] + sorted(df["month"].unique(), reverse=True))
        display_df = df if month_filter == "All" else df[df["month"] == month_filter]
        display_df = display_df[["id", "date", "amount", "category", "payment_method", "description"]]
        st.dataframe(display_df.drop(columns=["id"]), use_container_width=True, hide_index=True)

        st.caption("Delete an entry")
        del_id = st.selectbox("Select entry ID to delete", display_df["id"].tolist() if not display_df.empty else [])
        if st.button("Delete selected entry", type="secondary"):
            delete_expense(del_id)
            st.cache_data.clear()
            st.success("Deleted.")
            st.rerun()
