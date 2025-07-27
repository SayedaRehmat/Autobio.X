 # app.py
import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
import tempfile
import os

# ------------------- CONFIG -------------------
st.set_page_config(page_title="AutoBio-X", layout="wide")
BASE_API = "https://autobio-x.onrender.com"

# ------------------- HEADER -------------------
st.image("logo.png", width=220)
st.title("AutoBio-X: Gene Explorer & Drug Matcher")

st.markdown("""
### A real-time AI-powered tool to explore gene expression, mutation impact, and targeted drug matches in breast cancer.
**Sign up for early updates and exclusive reports!**
""")

# ------------------- LANDING PAGE -------------------
with st.expander("Join our email list for premium features"):
    email = st.text_input("Your email")
    if st.button("Subscribe"):
        st.success(f"Thanks for subscribing, {email}! We'll keep you posted.")

# ------------------- API HELPERS WITH FALLBACK -------------------
def get_expression_data(gene: str):
    url = f"{BASE_API}/expression/{gene}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json().get("expression", {})
        else:
            return {"error": f"API returned {r.status_code}"}
    except Exception as e:
        st.warning(f"Using sample expression data due to: {e}")
        return {"Sample_1": 8.2, "Sample_2": 7.9, "Sample_3": 8.4}


def get_mutation_data(gene: str):
    url = f"{BASE_API}/mutation/{gene}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            return [{"error": f"API returned {r.status_code}"}]
    except Exception as e:
        st.warning(f"Using sample mutation data due to: {e}")
        return [
            {"Mutation": "p.R175H", "Impact": "High"},
            {"Mutation": "p.R248Q", "Impact": "Medium"}
        ]


def get_drug_data(gene: str):
    url = f"{BASE_API}/drugs/{gene}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            return [{"error": f"API returned {r.status_code}"}]
    except Exception as e:
        st.warning(f"Using sample drug data due to: {e}")
        return [
            {"Drug": "Olaparib", "Status": "Approved"},
            {"Drug": "Talazoparib", "Status": "Clinical Trial"}
        ]


def safe_text(text):
    return str(text).encode('latin1', 'ignore').decode('latin1')

# ------------------- GENE INPUT -------------------
gene = st.text_input("Enter Gene Symbol (e.g., TP53, BRCA1)").strip().upper()

expr, muts, drugs = {}, [], []

if gene:
    with st.spinner("Fetching data..."):
        expr = get_expression_data(gene)
        muts = get_mutation_data(gene)
        drugs = get_drug_data(gene)

    # ------------------- DISPLAY DATA -------------------
    if expr and isinstance(expr, dict) and "error" not in expr:
        st.subheader("Expression Data")
        expr_df = pd.DataFrame(expr.items(), columns=["Sample", "Expression"])
        st.dataframe(expr_df)
    else:
        st.warning(expr.get("error", "No expression data available."))

    if muts and isinstance(muts, list) and "error" not in muts[0]:
        st.subheader("Mutation Info")
        st.table(pd.DataFrame(muts))
    else:
        st.warning(muts[0].get("error", "No mutation data found."))

    if drugs and isinstance(drugs, list) and "error" not in drugs[0]:
        st.subheader("Drug Matches")
        st.table(pd.DataFrame(drugs))
    else:
        st.warning(drugs[0].get("error", "No drug matches found."))

    # ------------------- PDF REPORT -------------------
    expression_ok = expr and isinstance(expr, dict) and "error" not in expr
    mutation_ok = muts and isinstance(muts, list) and "error" not in muts[0]
    drug_ok = drugs and isinstance(drugs, list) and "error" not in drugs[0]

    if expression_ok and mutation_ok and drug_ok:
        if st.button("Download Report as PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=14)
            pdf.set_text_color(33, 33, 33)
            pdf.cell(200, 10, txt=safe_text(f"Gene Report: {gene}"), ln=True, align='C')
            pdf.ln(10)

            # Expression Data
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt=safe_text("Expression Data"), ln=True)
            pdf.set_font("Arial", '', 12)
            for sample, value in expr.items():
                pdf.cell(0, 10, txt=safe_text(f"{sample}: {value}"), ln=True)

            pdf.ln(5)

            # Mutation Info
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt=safe_text("Mutation Info"), ln=True)
            pdf.set_font("Arial", '', 12)
            for mut in muts:
                for k, v in mut.items():
                    pdf.cell(0, 10, txt=safe_text(f"{k}: {v}"), ln=True)
                pdf.ln(3)

            # Drug Matches
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt=safe_text("Drug Matches"), ln=True)
            pdf.set_font("Arial", '', 12)
            for drug in drugs:
                for k, v in drug.items():
                    pdf.cell(0, 10, txt=safe_text(f"{k}: {v}"), ln=True)
                pdf.ln(3)

            # Footer
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 10)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(200, 10, txt=safe_text("Generated by Syeda Rehmat — Founder, BioZero"), ln=True, align='C')

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                pdf.output(tmpfile.name)
                with open(tmpfile.name, "rb") as f:
                    st.download_button(
                        label="Download PDF Report",
                        data=f,
                        file_name=f"{gene}_AutoBioX_Report.pdf",
                        mime="application/pdf"
                    )
                os.unlink(tmpfile.name)

# ------------------- FOOTER -------------------
st.markdown("""
<hr style='border: 1px solid #ddd;'>
<div style="text-align: center; color: gray;">
    Created by <b>Syeda Rehmat</b> — Founder, <i>BioZero</i>
</div>
""", unsafe_allow_html=True)
