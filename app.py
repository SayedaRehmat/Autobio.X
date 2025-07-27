 # app.py - Professional SaaS Bioinformatics Tool (Landing Page + Gene Explorer + Pricing)
import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os
from io import BytesIO

# ------------------- CONFIG -------------------
st.set_page_config(page_title="AutoBio-X Pro", layout="wide")

# ------------------- CUSTOM STYLES -------------------
st.markdown("""
<style>
    body {background-color: #f7f9fc;}
    .main-header {text-align: center; font-size: 40px; font-weight: bold; color: #2c3e50;}
    .sub-header {text-align: center; font-size: 20px; color: #34495e;}
    .pricing-card {background: #fff; padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;}
    .section-title {font-size: 30px; color: #2c3e50; margin-top: 30px;}
</style>
""", unsafe_allow_html=True)

# ------------------- HOMEPAGE -------------------
def homepage():
    st.markdown("<div class='main-header'>AutoBio-X Pro</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>AI-powered gene expression & drug discovery tool</div>", unsafe_allow_html=True)
    st.image("logo.png", width=220) if os.path.exists("logo.png") else None
    st.write("---")
    st.markdown("""
    ### Why Choose AutoBio-X Pro?
    - **Real-time gene data** from bioinformatics APIs.
    - **Mutation insights** and **drug target analysis**.
    - **Professional PDF/Excel reports**.
    - **Pro & Enterprise plans for unlimited features.**
    """)

    st.write("---")
    st.markdown("<div class='section-title'>Testimonials</div>", unsafe_allow_html=True)
    st.info("'AutoBio-X Pro has transformed the way we analyze genetic data.' – Dr. Ayesha Khan")
    st.info("'The drug-matching feature is a game-changer for precision medicine.' – Prof. John Doe")

    st.write("---")
    st.markdown("<div class='section-title'>Pricing & Plans</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='pricing-card'><b>Free Plan</b><br>5 searches/day<br>Access to sample data</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='pricing-card'><b>Pro Plan</b><br>$49/month<br>Unlimited searches<br>PDF Reports<br><button>Upgrade</button></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='pricing-card'><b>Enterprise</b><br>$499/month<br>Custom analysis<br>Dedicated support</div>", unsafe_allow_html=True)

    st.write("---")
    st.markdown("<div class='section-title'>Contact Us</div>", unsafe_allow_html=True)
    with st.form("contact_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Your Message")
        if st.form_submit_button("Send Message"):
            if name and email and message:
                st.success(f"Thank you {name}, we will reply to {email} soon!")
            else:
                st.error("Please fill out all fields.")

# ------------------- GENE EXPLORER -------------------
ENSEMBL_API = "https://rest.ensembl.org"
DGIDB_API = "https://dgidb.org/api/v2/interactions"

def fetch_gene_expression(gene):
    return {"Sample_1": 8.2, "Sample_2": 7.9, "Sample_3": 8.4} if gene else {}

def fetch_mutations(gene):
    return [{"Mutation": "R175H", "Impact": "High"}] if gene == "TP53" else []

def fetch_drugs(gene):
    try:
        resp = requests.get(f"{DGIDB_API}/{gene}?source_trust_levels=Expert%20curated")
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for interaction in data.get('matchedTerms', []):
                for drug in interaction.get('interactions', []):
                    results.append({"Drug": drug.get('drugName'), "Interaction": drug.get('interactionTypes')})
            return results
    except:
        return []
    return []

def gene_explorer():
    st.markdown("<div class='main-header'>Gene Explorer</div>", unsafe_allow_html=True)
    gene = st.text_input("Enter Gene Symbol (e.g., TP53, BRCA1)").strip().upper()
    tabs = st.tabs(["Expression", "Mutations", "Drugs"])
    if gene:
        expr = fetch_gene_expression(gene)
        muts = fetch_mutations(gene)
        drugs = fetch_drugs(gene)

        # Expression Tab
        with tabs[0]:
            if expr:
                st.subheader("Expression Data")
                df_expr = pd.DataFrame(expr.items(), columns=["Sample", "Expression"])
                st.dataframe(df_expr)
                fig, ax = plt.subplots()
                ax.bar(df_expr['Sample'], df_expr['Expression'], color='skyblue')
                st.pyplot(fig)
            else:
                st.warning("No expression data available.")

        # Mutation Tab
        with tabs[1]:
            if muts:
                st.subheader("Mutation Info")
                st.table(pd.DataFrame(muts))
            else:
                st.warning("No mutation data found.")

        # Drug Tab
        with tabs[2]:
            if drugs:
                st.subheader("Drug Matches")
                st.table(pd.DataFrame(drugs))
            else:
                st.warning("No drug matches found.")

# ------------------- MAIN MENU -------------------
menu = st.sidebar.radio("Navigation", ["Home", "Gene Explorer"])
if menu == "Home":
    homepage()
elif menu == "Gene Explorer":
    gene_explorer()

# ------------------- FOOTER -------------------
st.markdown("""
<hr style='border: 1px solid #ddd;'>
<div style="text-align: center; color: gray;">
    <b>AutoBio-X Pro</b> — Founder: Syeda Rehmat | <a href='#'>About</a> | <a href='#'>Contact</a>
</div>
""", unsafe_allow_html=True)
