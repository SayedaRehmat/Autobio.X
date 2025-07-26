import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
from fpdf import FPDF

# Load data
expression_df = pd.read_csv("expression.csv")
mutation_df = pd.read_csv("mutations.csv")
drug_df = pd.read_csv("dgidb_drugs.csv")

st.set_page_config(page_title="AutoBio-X", layout="wide")

# Sidebar
st.sidebar.image("logo.png", width=200)
lang = st.sidebar.radio("🌐 Language", ["English", "Urdu"])
st.sidebar.markdown("Created by **Syeda Rehmat** — Founder, BioZero 💛")

st.title("🧬 AutoBio-X: AI-Powered Gene Analysis Platform")

# Input genes
genes_input = st.text_area("🔍 Enter gene names (comma-separated):", "TP53, BRCA1, EGFR")
genes = [g.strip().upper() for g in genes_input.split(",") if g.strip()]

if genes:
    st.subheader("📊 Gene Expression & Mutation Results")
    report_data = []

    for gene in genes:
        exp = expression_df[expression_df['Gene'].str.upper() == gene]
        mut = mutation_df[mutation_df['Gene'].str.upper() == gene]
        drugs = drug_df[drug_df['Gene'].str.upper() == gene]

        st.markdown(f"### 🔬 {gene}")

        # Expression
        if not exp.empty:
            st.write("**Expression Data:**")
            st.dataframe(exp)
            fig, ax = plt.subplots()
            ax.bar(exp.columns[1:], exp.values[0][1:], color="orchid")
            ax.set_ylabel("Expression Level")
            st.pyplot(fig)
        else:
            st.warning("No expression data found.")

        # Mutation
        if not mut.empty:
            st.write("**Mutation Found:**")
            st.dataframe(mut)
        else:
            st.info("No mutation found.")

        # Drugs
        if not drugs.empty:
            st.write("💊 **Potential Drug Matches:**")
            st.dataframe(drugs[['Drug', 'Interaction']])
        else:
            st.error("No drug match found.")

        report_data.append((gene, not exp.empty, not mut.empty, not drugs.empty))

    # PDF Generator
    if st.button("📄 Download Gene Report PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="AutoBio-X Gene Analysis Report", ln=True, align="C")
        pdf.ln(10)
        for gene, has_exp, has_mut, has_drug in report_data:
            pdf.cell(200, 10, txt=f"Gene: {gene}", ln=True)
            pdf.cell(200, 10, txt=f"- Expression Data: {'Yes' if has_exp else 'No'}", ln=True)
            pdf.cell(200, 10, txt=f"- Mutation Data: {'Yes' if has_mut else 'No'}", ln=True)
            pdf.cell(200, 10, txt=f"- Drug Match: {'Yes' if has_drug else 'No'}", ln=True)
            pdf.ln(5)
        pdf_file = "gene_report.pdf"
        pdf.output(pdf_file)
        with open(pdf_file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{pdf_file}">📥 Download PDF Report</a>'
            st.markdown(href, unsafe_allow_html=True)

else:
    st.info("Please enter at least one gene to analyze.")
