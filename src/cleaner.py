
import io
import re
from dateutil import parser as dateparser
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)
        .str.strip("_")
    )
    return df

def detect_schema(df: pd.DataFrame) -> dict:
    cols = df.columns.tolist()
    mapping = {}
    candidates = {
        "date": [
            "date","txn_date","transaction_date","posting_date","value_date","post_date"
        ],
        "description": [
            "description","narration","details","detail","transaction_details",
            "reference","ref","memo","particulars","beneficiary","payee"
        ],
        "amount": ["amount","amt","transaction_amount","value","debit_credit"],
        "debit": ["debit","withdrawal","debits"],
        "credit": ["credit","deposit","credits"],
        "balance": ["balance","bal","running_balance","closing_balance"],
    }
    for target, names in candidates.items():
        for n in names:
            if n in cols:
                mapping[target] = n
                break
        if target not in mapping:
            for c in cols:
                if target in c:
                    mapping[target] = c
                    break
    return mapping

def coerce_date(x):
    if pd.isna(x):
        return pd.NaT
    try:
        return dateparser.parse(str(x), dayfirst=False, yearfirst=False)
    except Exception:
        return pd.NaT

def coerce_number(x):
    if pd.isna(x):
        return np.nan
    s = str(x).strip()
    if re.match(r"^\(.*\)$", s):
        s = "-" + s[1:-1]
    s = s.replace(" ", "")
    if s.count(",") == 1 and s.count(".") == 0:
        s = s.replace(",", ".")
    s = s.replace(",", "")
    try:
        return float(s)
    except Exception:
        return np.nan

def rule_based_category(desc: str) -> str:
    if not isinstance(desc, str):
        return "Uncategorized"
    d = desc.lower()
    rules = [
        ("Groceries", ["shoprite","checkers","pick n pay","spar","woolworths"]),
        ("Fuel", ["engeni","engen","bp","shell","total","sasol","caltex"]),
        ("Food & Drink", ["uber eats","mr d","restaurant","kfc","mcd","nando"]),
        ("Transport", ["uber","bolt","taxi","autopax","bus","gautrain"]),
        ("Utilities", ["eskom","municipality","telkom","vodacom","mtn","cell c"]),
        ("Rent/Mortgage", ["lease","rent","bond","mortgage"]),
        ("Fees", ["fee","charges","charge","commission","service fee"]),
        ("Salary/Income", ["salary","payroll","credit interest","dividend"]),
        ("Transfers", ["transfer","tfr","inter-account","ift"]),
        ("ATM Cash", ["atm","cash withdrawal"]),
        ("Insurance", ["insurance","premium","sanlam","old mutual","discovery"]),
        ("Healthcare", ["pharmacy","dischem","clicks","medical"]),
        ("Entertainment", ["netflix","spotify","dstv","movie"]),
        ("Travel", ["airways","saa","flysafair","kulula","airline","hotel"]),
        ("Education", ["udemy","coursera","edx"]),
        ("Bank Charges", ["bank charge","monthly account fee"]),
    ]
    for cat, keys in rules:
        if any(k in d for k in keys):
            return cat
    return "Uncategorized"

def canonicalize(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    m = detect_schema(df)
    out = pd.DataFrame(index=df.index)
    date_col = m.get("date")
    if date_col and date_col in df:
        out["date"] = df[date_col].map(coerce_date)
    else:
        out["date"] = pd.NaT
    desc_col = m.get("description")
    out["description"] = df[desc_col] if desc_col in df else ""
    amt = df[m["amount"]].map(coerce_number) if m.get("amount") in df else None
    debit = df[m["debit"]].map(coerce_number) if m.get("debit") in df else None
    credit = df[m["credit"]].map(coerce_number) if m.get("credit") in df else None
    if amt is not None:
        if debit is not None or credit is not None:
            signed = pd.Series(0.0, index=df.index, dtype=float)
            if debit is not None:
                signed = signed.where(~debit.notna(), -debit.fillna(0))
            if credit is not None:
                signed = signed.where(~credit.notna(), credit.fillna(0))
            out["amount"] = signed.where(signed != 0, amt)
        else:
            out["amount"] = amt
    elif debit is not None or credit is not None:
        signed = pd.Series(0.0, index=df.index, dtype=float)
        if debit is not None:
            signed = signed.where(~debit.notna(), -debit.fillna(0))
        if credit is not None:
            signed = signed.where(~credit.notna(), credit.fillna(0))
        out["amount"] = signed
    else:
        out["amount"] = np.nan
    bal_col = m.get("balance")
    out["balance"] = df[bal_col].map(coerce_number) if bal_col in df else np.nan
    out["type"] = np.where(out["amount"] < 0, "Debit", np.where(out["amount"] > 0, "Credit", "Zero"))
    out["abs_amount"] = out["amount"].abs()
    out["category"] = out["description"].astype(str).map(rule_based_category)
    out["date_only"] = pd.to_datetime(out["date"]).dt.date
    out["month"] = pd.to_datetime(out["date"]).dt.to_period("M").astype(str)
    out = out.dropna(how="all")
    return out

def run_anomaly_iforest(df: pd.DataFrame, contamination: float = 0.02) -> pd.Series:
    x = df[["abs_amount"]].fillna(0.0).values
    iforest = IsolationForest(random_state=42, contamination=contamination)
    y = iforest.fit_predict(x)  # -1 = anomaly
    return pd.Series(np.where(y == -1, True, False), index=df.index, name="anomaly")

def vendor_clusters_kmeans(df: pd.DataFrame, n_clusters: int = 6) -> pd.Series:
    texts = df["description"].astype(str).fillna("")
    if texts.str.len().sum() == 0:
        return pd.Series(["Cluster_0"] * len(df), index=df.index, name="vendor_cluster")
    vec = TfidfVectorizer(max_features=4000, ngram_range=(1, 2), min_df=1)
    X = vec.fit_transform(texts)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    labels = km.fit_predict(X)
    return pd.Series([f"Cluster_{i}" for i in labels], index=df.index, name="vendor_cluster")

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="cleaned")
    return output.getvalue()
