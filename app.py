 # app.py (Clean & Validated Version with Sample Data Fallback)
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
    .reportview-container {
        background: #f7f9fc;
    }
    .stButton>button {
        background-color: #007BFF;
        color: white;
        border-radius: 8px;
        padding: 6px 18px;
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

# Default fallback data
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

# ------------------- ABOUT SECTION -------------------
st.markdown("""
## About AutoBio-X
AutoBio-X is designed for researchers and clinicians to simplify complex bioinformatics workflows:
- **Gene Expression Analysis** — Compare gene activity across samples.
- **Mutation Insights** — Identify impactful gene mutations.
- **Drug Matches** — Explore drugs targeting specific genes.
""")

# ------------------- TEAM SECTION -------------------
st.markdown("""
## Meet the Team
**Syeda Rehmat** — Founder & Bioinformatics Specialist  
**Your Name Here** — Software Engineer  
**Advisors** — Scientists and healthcare experts guiding the project.
""")

# ------------------- TESTIMONIALS -------------------
st.markdown("""
## Testimonials
> *"AutoBio-X has transformed the way we analyze genetic data."* — **Dr. Ayesha Khan**

> *"The drug-matching feature is a game-changer for precision medicine."* — **Prof. John Doe**
""")

# ------------------- GENE SEARCH -------------------
all_genes = sorted(set(expression_df["Gene"]) | set(mutation_df["Gene"]) | set(drug_df["Gene"]))
search_gene = st.text_input("Search Gene Symbol:", "")
gene = search_gene.strip().upper() if search_gene else ""

# ------------------- TABS -------------------
tabs = st.tabs(["Expression", "Mutations", "Drugs"])
expr, muts, drugs = {}, [], []

# ------------------- UTILS -------------------
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# ------------------- GENE DATA -------------------
if gene:
    # Expression
    result = expression_df[expression_df["Gene"].str.upper() == gene]
    expr = result.iloc[0][1:].to_dict() if not result.empty else {"error": "No expression data found."}

    # Mutations
    muts_df = mutation_df[mutation_df["Gene"].str.upper() == gene]
    muts = muts_df.to_dict(orient="records") if not muts_df.empty else [{"error": "No mutation data found."}]

    # Drugs
    drugs_df = drug_df[drug_df["Gene"].str.upper() == gene]
    drugs = drugs_df[["Drug", "Interaction"]].to_dict(orient="records") if not drugs_df.empty else [{"error": "No drug matches found."}]

    # Display Expression
    with tabs[0]:
        if "error" not in expr:
            st.subheader("Expression Data")
            expr_df = pd.DataFrame(expr.items(), columns=["Sample", "Expression"])
            st.dataframe(expr_df)
            fig, ax = plt.subplots()
            ax.bar(expr_df['Sample'], expr_df['Expression'], color='skyblue')
            st.pyplot(fig)
        else:
            st.warning(expr["error"])

    # Display Mutations
    with tabs[1]:
        if "error" not in muts[0]:
            st.subheader("Mutation Info")
            st.table(pd.DataFrame(muts))
        else:
            st.warning(muts[0]["error"])

    # Display Drugs
    with tabs[2]:
        if "error" not in drugs[0]:
            st.subheader("Drug Matches")
            st.table(pd.DataFrame(drugs))
        else:
            st.warning(drugs[0]["error"])

# ------------------- CONTACT FORM -------------------
st.markdown("---")
st.markdown("## Contact Us")
with st.form("contact_form"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Your Message")
    submitted = st.form_submit_button("Send Message")
    if submitted:
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
