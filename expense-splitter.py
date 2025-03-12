import streamlit as st
import pandas as pd
import numpy as np

def calculate_splits(expenses):
    total_spent = expenses.groupby('Name')['Amount'].sum()
    avg_spent = total_spent.mean()
    balance = total_spent - avg_spent
    return balance

def update_paid_status(name, balance, creditors, debtors):
    if name in balance:
        paid_amount = balance[name]
        balance[name] = 0
        
        creditors_to_update = creditors[creditors > 0]
        total_credit = creditors_to_update.sum()
        
        if total_credit > 0:
            for creditor in creditors_to_update.index:
                creditors[creditor] -= (paid_amount * (creditors[creditor] / total_credit))
                if creditors[creditor] < 0:
                    creditors[creditor] = 0
    
    return balance, creditors

st.markdown(
    """
    <style>
        .stApp { background-color: #FFF5B5; }
        .title { font-size: 36px; font-weight: bold; color: white; background-color: #6B613A; padding: 15px; border-radius: 8px; text-align: left; margin-bottom: 20px; }
        .input-box { border-radius: 10px !important; padding: 10px; width: 100%; }
        .button { background-color: white; border: 1px solid black; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='title'>Expense Splitter</div>", unsafe_allow_html=True)

st.markdown("<div class='container'>", unsafe_allow_html=True)
st.subheader("Enter names (comma-separated)")
names = st.text_area("", "Ali, Jack, Bob", key="name_input")
names = [name.strip() for name in names.split(',') if name.strip()]

data = []
removed_people = []
payments_checked = {}

for name in names:
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        amount = st.number_input(f"Amount paid by {name}", min_value=0.0, step=10.00, key=name)
    with col2:
        remove = st.checkbox(f"Remove {name}", key=f"remove_{name}")
    with col3:
        paid = st.checkbox(f"Paid", key=f"paid_{name}")
    
    if remove:
        removed_people.append(name)
    else:
        data.append({"Name": name, "Amount": amount})
        payments_checked[name] = paid

if st.button("Split", key="split_button", help="Calculate who owes what"):
    df = pd.DataFrame(data)
    balance = calculate_splits(df)
    
    creditors = balance[balance > 0]
    debtors = balance[balance < 0].abs()
    
    for name, paid in payments_checked.items():
        if paid:
            balance, creditors = update_paid_status(name, balance, creditors, debtors)
    
    st.subheader("Results")
    st.write("Positive means they should receive money, negative means they owe.")
    st.dataframe(balance.to_frame(name="Balance"))
    
    transactions = []
    
    for debtor, debt_amount in debtors.items():
        for creditor, credit_amount in creditors.items():
            amount = min(debt_amount, credit_amount)
            if payments_checked.get(debtor, False):
                transactions.append(f"{debtor} has already paid {creditor}.")
            else:
                transactions.append(f"{debtor} pays {creditor} ${amount:.2f}")
            creditors[creditor] -= amount
            debtors[debtor] -= amount
            if creditors[creditor] == 0: break
        
    st.subheader("Who Pays Whom?")
    for t in transactions:
        st.write(t)

st.markdown("</div>", unsafe_allow_html=True)