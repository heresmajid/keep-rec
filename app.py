import hmac
import streamlit as st
import pandas as pd
from datetime import datetime

# Function to write data to Excel
def write_to_excel(expense_data):
    df = pd.DataFrame([expense_data])
    file_path = 'expenses.xlsx'

    try:
        existing_df = pd.read_excel(file_path)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass  # Create a new file if it doesn't exist

    df.to_excel(file_path, index=False)

def check_password():
    """Returns `True` if the user had a correct password."""
    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            st.session_state["logged_in_user"] = st.session_state["username"]
            del st.session_state["password"]  # Don't store the password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

# Check if the user is logged in
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# If the user is not logged in, check password
if not check_password():
    st.stop()

# Main Streamlit app starts here
st.title("Household Expense Tracker")
st.write(f"Welcome, {st.session_state['logged_in_user']}!")

# Input fields for adding expenses
label = st.text_input("Expense Label")
cost = st.number_input("Cost", min_value=0.0)

if st.button("Add Expense"):
    if label and cost:
        expense_data = {
            'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Username': st.session_state['logged_in_user'],
            'Label': label,
            'Cost': cost
        }
        write_to_excel(expense_data)
        st.success("Expense recorded successfully!")
    else:
        st.error("Please fill in all fields.")

# Optional: Display total expenses for the logged-in user
if st.button("Show My Expenses"):
    try:
        df = pd.read_excel('expenses.xlsx')
        user_expenses = df[df['Username'] == st.session_state['logged_in_user']]
        st.write(user_expenses)
    except FileNotFoundError:
        st.error("No expenses recorded yet.")