 # app.py (Full Professional Tool with CSV/Excel/PDF Downloads and Pricing)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os
from io import BytesIO

# ------------------- CONFIG -------------------
st.set_page_config(page_title="AutoBio-X", layout="wide")

# ------------------- STYLES -------------------
st.markdown("""
<style>
    .reportview-container { background: #f7f9fc; }
    .stButton>button {
        background-color: #007BFF; color: white; border-radius: 8px; padding: 6px 18px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------- LOAD DATA -------------------
@st.cache_data
def load_csv(file, default_data):
    if os.path.exists(file):
        try:
            return pd.read_csv(file)
        except Exception as e:
            st.warning(f"Error loading {file}: {e}. Using default data.")
            return default_data
    else:
        st.warning(f"{file} not found. Using default sample data.")
        return default_data

# Default sample data
sample_expression = pd.DataFrame({
    "Gene": ["TP53", "BRCA1"],
    "Sample1": [8.2, 6.3],
    "Sample2": [7.9, 5.8]
})

sample_mutations = pd.DataFrame({
    "Gene": ["TP53", "BRCA1"],
    "Impact": ["High", "Moderate"],
    "Mutation": ["R175H", "5382insC"]
})

sample_drugs = pd.DataFrame({
    "Gene": ["TP53", "BRCA1"],
    "Drug": ["DrugA", "DrugB"],
    "Interaction": ["Inhibitor", "Activator"]
})

expression_df = load_csv("expression.csv", sample_expression)
mutation_df = load_csv("mutations.csv", sample_mutations)
drug_df = load_csv("dgidb_drugs.csv", sample_drugs)

# ------------------- HERO SECTION -------------------
if os.path.exists("logo.png"):
    st.image("logo.png", width=220)
st.title("AutoBio-X: Gene Explorer & Drug Matcher")

st.markdown("""
<div style='background-color:#e3f2fd;padding:20px;border-radius:10px;'>
    <h2>Welcome to AutoBio-X</h2>
    <p>A powerful AI-driven platform for gene expression analysis, mutation insights, and targeted drug matches.</p>
    <p><b>Created by Syeda Rehmat — Founder, BioZero</b></p>
</div>
""", unsafe_allow_html=True)

# ------------------- PRICING -------------------
st.markdown("""
## Pricing & Plans
**Free Plan** — 5 searches/day, sample data only.
**Pro Plan ($49/month)** — Unlimited searches, extended datasets, priority support.
**Enterprise Plan ($499/month)** — Custom analysis, dedicated manager, API access.
""")
if st.button("Upgrade to Pro Plan ($49/month)"):
    st.info("[Redirecting to Stripe Checkout (placeholder)...](https://stripe.com)")

# ------------------- UTILS -------------------
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def generate_pdf(gene, expr, muts, drugs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt=f"Gene Report: {gene}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Expression Data", ln=True)
    pdf.set_font("Arial", '', 12)
    for sample, value in expr.items():
        pdf.cell(0, 10, txt=f"{sample}: {value}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Mutation Info", ln=True)
    pdf.set_font("Arial", '', 12)
    for mut in muts:
        for k, v in mut.items():
            pdf.cell(0, 10, txt=f"{k}: {v}", ln=True)
        pdf.ln(3)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Drug Matches", ln=True)
    pdf.set_font("Arial", '', 12)
    for drug in drugs:
        for k, v in drug.items():
            pdf.cell(0, 10, txt=f"{k}: {v}", ln=True)
        pdf.ln(3)
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmpfile.name)
    return tmpfile.name

# ------------------- SEARCH -------------------
all_genes = sorted(set(expression_df["Gene"]) | set(mutation_df["Gene"]) | set(drug_df["Gene"]))
gene = st.text_input("Search Gene Symbol:", "").strip().upper()

# ------------------- TABS -------------------
tabs = st.tabs(["Expression", "Mutations", "Drugs"])
expr, muts, drugs = {}, [], []

if gene:
    expr_df = expression_df[expression_df["Gene"].str.upper() == gene]
    expr = expr_df.iloc[0][1:].to_dict() if not expr_df.empty else {"error": "No expression data found."}
    muts_df = mutation_df[mutation_df["Gene"].str.upper() == gene]
    muts = muts_df.to_dict(orient="records") if not muts_df.empty else [{"error": "No mutation data found."}]
    drugs_df = drug_df[drug_df["Gene"].str.upper() == gene]
    drugs = drugs_df[["Drug", "Interaction"]].to_dict(orient="records") if not drugs_df.empty else [{"error": "No drug matches found."}]

    # Expression Tab
    with tabs[0]:
        if "error" not in expr:
            st.subheader("Expression Data")
            df = pd.DataFrame(expr.items(), columns=["Sample", "Expression"])
            st.dataframe(df)
            fig, ax = plt.subplots()
            ax.bar(df['Sample'], df['Expression'], color='skyblue')
            st.pyplot(fig)
            st.download_button("Download Expression CSV", df.to_csv(index=False).encode('utf-8'), f"{gene}_expression.csv")
            st.download_button("Download Expression Excel", to_excel(df), f"{gene}_expression.xlsx")
        else:
            st.warning(expr["error"])

    # Mutation Tab
    with tabs[1]:
        if "error" not in muts[0]:
            df = pd.DataFrame(muts)
            st.subheader("Mutation Info")
            st.table(df)
            st.download_button("Download Mutations CSV", df.to_csv(index=False).encode('utf-8'), f"{gene}_mutations.csv")
            st.download_button("Download Mutations Excel", to_excel(df), f"{gene}_mutations.xlsx")
        else:
            st.warning(muts[0]["error"])

    # Drug Tab
    with tabs[2]:
        if "error" not in drugs[0]:
            df = pd.DataFrame(drugs)
            st.subheader("Drug Matches")
            st.table(df)
            st.download_button("Download Drugs CSV", df.to_csv(index=False).encode('utf-8'), f"{gene}_drugs.csv")
            st.download_button("Download Drugs Excel", to_excel(df), f"{gene}_drugs.xlsx")
        else:
            st.warning(drugs[0]["error"])

    # PDF Download
    if "error" not in expr and "error" not in muts[0] and "error" not in drugs[0]:
        if st.button("Download Full Report (PDF)"):
            pdf_path = generate_pdf(gene, expr, muts, drugs)
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF Report", f, f"{gene}_report.pdf")
            os.unlink(pdf_path)

# ------------------- CONTACT FORM -------------------
st.markdown("---")
st.markdown("## Contact Us")
with st.form("contact_form"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Your Message")
    if st.form_submit_button("Send Message"):
        if name and email and message:
            st.success(f"Thank you {name}, we will reply to {email} soon!")
        else:
            st.error("Please fill out all fields.")

# ------------------- FOOTER -------------------
st.markdown("""
<hr style='border: 1px solid #ddd;'>
<div style="text-align: center; color: gray;">
    <b>Syeda Rehmat</b> — Founder, <i>BioZero</i> | <a href='#'>About</a> | <a href='#'>Contact</a>
</div>
""", unsafe_allow_html=True)
