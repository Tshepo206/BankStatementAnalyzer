
# streamlit_app.py — BankStatementAnalyzer UI
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.cleaner import (
    canonicalize,
    run_anomaly_iforest,
    vendor_clusters_kmeans,
    to_excel_bytes,
)

st.set_page_config(page_title="Bank Statement Analyzer", layout="wide")
st.title("🏦 Bank Statement Analyzer")
st.caption("Upload a bank statement (CSV/XLSX) → normalize → analyze → download cleaned file.")

with st.sidebar:
    st.header("⚙️ Options")
    contamination = st.slider("Anomaly sensitivity (IsolationForest)", 0.005, 0.10, 0.02, 0.005)
    do_clusters = st.checkbox("Vendor clusters (KMeans)", value=False)
    n_clusters = st.slider("Number of clusters", 3, 12, 6, 1, disabled=not do_clusters)
    st.markdown("---")
    st.info("Tip: Commas as decimals & (negatives) are handled automatically.")

uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
if not uploaded:
    st.stop()

name = getattr(uploaded, "name", "").lower()
if name.endswith(".csv"):
    raw_df = pd.read_csv(uploaded, dtype=str, encoding="utf-8", engine="python")
else:
    raw_df = pd.read_excel(uploaded, dtype=str)

st.subheader("Raw preview")
st.dataframe(raw_df.head(20), use_container_width=True)

clean_df = canonicalize(raw_df)

with st.spinner("Running anomaly detection..."):
    clean_df["anomaly"] = run_anomaly_iforest(clean_df, contamination=contamination)

if do_clusters:
    with st.spinner("Building vendor clusters..."):
        clean_df["vendor_cluster"] = vendor_clusters_kmeans(clean_df, n_clusters=n_clusters)

st.markdown("### Summary")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Debits (Out)", f"{clean_df.loc[clean_df['amount']<0,'abs_amount'].sum():,.2f}")
with col2:
    st.metric("Total Credits (In)", f"{clean_df.loc[clean_df['amount']>0,'abs_amount'].sum():,.2f}")
with col3:
    st.metric("Transactions", f"{len(clean_df):,}")
with col4:
    st.metric("Anomalies flagged", int(clean_df['anomaly'].sum()))

st.markdown("### Charts")
daily = clean_df.groupby("date_only")["amount"].sum().reset_index()
fig1 = plt.figure()
plt.plot(daily["date_only"], daily["amount"])
plt.title("Daily Net Cashflow")
plt.xlabel("Date")
plt.ylabel("Net Amount")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig1)

cat = (
    clean_df.loc[clean_df["amount"] < 0]
    .groupby("category")["abs_amount"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
    .reset_index()
)
fig2 = plt.figure()
plt.bar(cat["category"], cat["abs_amount"])
plt.title("Top Categories (Debits)")
plt.xlabel("Category")
plt.ylabel("Total Spent")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
st.pyplot(fig2)

dc = pd.Series(
    {
        "Debits": clean_df.loc[clean_df["amount"] < 0, "abs_amount"].sum(),
        "Credits": clean_df.loc[clean_df["amount"] > 0, "abs_amount"].sum(),
    }
)
fig3 = plt.figure()
plt.pie(dc.values, labels=dc.index, autopct="%1.1f%%", startangle=90)
plt.title("Debits vs Credits (Abs)")
plt.tight_layout()
st.pyplot(fig3)

st.markdown("### Cleaned Transactions")
st.dataframe(clean_df, use_container_width=True)

st.markdown("### Download")
st.download_button("⬇️ CSV", data=clean_df.to_csv(index=False).encode("utf-8"),
                   file_name="cleaned_statement.csv", mime="text/csv")
st.download_button("⬇️ Excel (.xlsx)", data=to_excel_bytes(clean_df),
                   file_name="cleaned_statement.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
st.success("Ready. Edit keyword rules in src/cleaner.py → rule_based_category().")
