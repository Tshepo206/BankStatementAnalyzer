
import pandas as pd
from src.cleaner import coerce_number, canonicalize, rule_based_category

def test_coerce_number_parentheses_negative():
    assert coerce_number("(123.45)") == -123.45

def test_canonicalize_basic_amount_signs():
    df = pd.DataFrame({
        "Date": ["2024-01-01","2024-01-02"],
        "Description": ["Salary","ATM Withdrawal"],
        "Credit": [1000, None],
        "Debit": [None, 200],
        "Balance": [1000, 800]
    })
    out = canonicalize(df)
    assert out.loc[out["description"].str.contains("salary"), "amount"].iloc[0] == 1000
    assert out.loc[out["description"].str.contains("atm"), "amount"].iloc[0] == -200

def test_rule_based_category_matches():
    assert rule_based_category("Paid to Checkers Hyper") == "Groceries"
