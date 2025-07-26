import streamlit as st
import requests

# ----------------- Page Setup -----------------
st.set_page_config(page_title="AutoBio-X", layout="centered")

st.image("logo.png", width=220)
st.title("🧬 AutoBio-X: Gene Explorer & Drug Matcher")
st.markdown(
    """
    A real-time AI-powered tool to explore gene expression, mutation impact, and targeted drug matches in breast cancer.
    """
)

# ----------------- API Helper Functions -----------------

BASE_API = "https://autobio-x.onrender.com"

def get_expression_data(gene):
    try:
        r = requests.get(f"{BASE_API}/expression/{gene}")
        return r.json().get("expression", {})
    except:
        return {"error": "Failed to fetch expression data."}

def get_mutation_data(gene):
    try:
        r = requests.get(f"{BASE_API}/mutation/{gene}")
        return r.json()
    except:
        return [{"error": "Failed to fetch mutation data."}]

def get_drug_data(gene):
    try:
        r = requests.get(f"{BASE_API}/drugs/{gene}")
        return r.json()
    except:
        return [{"error": "Failed to fetch drug data."}]

# ----------------- Gene Input Section -----------------

gene = st.text_input("🔍 Enter Gene Symbol (e.g., TP53, BRCA1)").strip().upper()

if gene:
    # ----------------- Expression -----------------
    st.subheader("📊 Expression Data")
    expr = get_expression_data(gene)
    if "error" in expr:
        st.warning(expr["error"])
    else:
        st.json(expr)

    # ----------------- Mutation -----------------
    st.subheader("🧬 Mutation Info")
    muts = get_mutation_data(gene)
    if isinstance(muts, list) and "error" in muts[0]:
        st.warning(muts[0]["error"])
    else:
        st.json(muts)

    # ----------------- Drug Matches -----------------
    st.subheader("💊 Drug Matches")
    drugs = get_drug_data(gene)
    if isinstance(drugs, list) and "error" in drugs[0]:
        st.warning(drugs[0]["error"])
    else:
        st.json(drugs)

# ----------------- Footer -----------------
st.markdown(
    """
    <hr style='border: 1px solid #ddd;'>
    <div style="text-align: center; color: gray;">
        Created by <b>Syeda Rehmat</b> — Founder, <i>BioZero</i>
    </div>
    """,
    unsafe_allow_html=True
)
