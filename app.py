 # app.py (Streamlit App with Homepage, About, and Contact Form)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os
from io import BytesIO

# ------------------- CONFIG -------------------
st.set_page_config(page_title="AutoBio-X", layout="wide")

# Custom style
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
def load_csv(file):
    try:
        return pd.read_csv(file)
    except Exception as e:
        st.error(f"Failed to load {file}: {e}")
        return pd.DataFrame()

expression_df = load_csv("expression.csv")
mutation_df = load_csv("mutations.csv")
drug_df = load_csv("dgidb_drugs.csv")

# ------------------- HERO SECTION -------------------
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

This tool was created by **Syeda Rehmat**, Founder of **BioZero**, with a mission to make precision medicine accessible to everyone.
""")

# ------------------- SEARCH BOX -------------------
all_genes = sorted(set(expression_df["Gene"]) | set(mutation_df["Gene"]) | set(drug_df["Gene"])) if not expression_df.empty else []
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

if gene:
    # Expression
    result = expression_df[expression_df["Gene"].str.upper() == gene]
    if not result.empty:
        expr = result.iloc[0][1:].to_dict()
    else:
        expr = {"error": "No expression data found."}

    # Mutations
    muts_df = mutation_df[mutation_df["Gene"].str.upper() == gene]
    if muts_df.empty:
        muts = [{"error": "No mutation data found."}]
    else:
        with tabs[1]:
            if "Impact" in muts_df.columns:
                impact_filter = st.multiselect("Filter Mutations by Impact:", sorted(muts_df["Impact"].unique()), default=list(muts_df["Impact"].unique()))
                muts_df = muts_df[muts_df["Impact"].isin(impact_filter)]
        muts = muts_df.to_dict(orient="records")

    # Drugs
    drugs_df = drug_df[drug_df["Gene"].str.upper() == gene]
    if drugs_df.empty:
        drugs = [{"error": "No drug matches found."}]
    else:
        with tabs[2]:
            if "Interaction" in drugs_df.columns:
                interaction_filter = st.multiselect("Filter Drugs by Interaction:", sorted(drugs_df["Interaction"].unique()), default=list(drugs_df["Interaction"].unique()))
                drugs_df = drugs_df[drugs_df["Interaction"].isin(interaction_filter)]
        drugs = drugs_df[["Drug", "Interaction"]].to_dict(orient="records")

    # ------------------- DISPLAY DATA -------------------
    with tabs[0]:
        if expr and "error" not in expr:
            st.subheader("Expression Data")
            expr_df = pd.DataFrame(expr.items(), columns=["Sample", "Expression"])
            st.dataframe(expr_df)
            fig, ax = plt.subplots()
            ax.bar(expr_df['Sample'], expr_df['Expression'], color='skyblue')
            ax.set_xlabel('Sample')
            ax.set_ylabel('Expression Level')
            ax.set_title(f'Gene Expression for {gene}')
            st.pyplot(fig)
            st.download_button("Download Expression CSV", expr_df.to_csv(index=False).encode('utf-8'), file_name=f"{gene}_expression.csv", mime="text/csv")
            st.download_button("Download Expression Excel", to_excel(expr_df), file_name=f"{gene}_expression.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning(expr.get("error", "No expression data available."))

    with tabs[1]:
        if muts and "error" not in muts[0]:
            st.subheader("Mutation Info")
            muts_data = pd.DataFrame(muts)
            st.table(muts_data)
            st.download_button("Download Mutations CSV", muts_data.to_csv(index=False).encode('utf-8'), file_name=f"{gene}_mutations.csv", mime="text/csv")
            st.download_button("Download Mutations Excel", to_excel(muts_data), file_name=f"{gene}_mutations.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning(muts[0].get("error", "No mutation data found."))

    with tabs[2]:
        if drugs and "error" not in drugs[0]:
            st.subheader("Drug Matches")
            drugs_data = pd.DataFrame(drugs)
            st.table(drugs_data)
            st.download_button("Download Drugs CSV", drugs_data.to_csv(index=False).encode('utf-8'), file_name=f"{gene}_drugs.csv", mime="text/csv")
            st.download_button("Download Drugs Excel", to_excel(drugs_data), file_name=f"{gene}_drugs.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning(drugs[0].get("error", "No drug matches found."))

    # ------------------- PDF REPORT -------------------
    def safe_text(text):
        return str(text).encode('latin1', 'ignore').decode('latin1')

    if "error" not in expr and "error" not in muts[0] and "error" not in drugs[0]:
        if st.button("Download Report as PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=14)
            pdf.set_text_color(33, 33, 33)
            pdf.cell(200, 10, txt=safe_text(f"Gene Report: {gene}"), ln=True, align='C')
            pdf.ln(10)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt=safe_text("Expression Data"), ln=True)
            pdf.set_font("Arial", '', 12)
            for sample, value in expr.items():
                pdf.cell(0, 10, txt=safe_text(f"{sample}: {value}"), ln=True)

            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt=safe_text("Mutation Info"), ln=True)
            pdf.set_font("Arial", '', 12)
            for mut in muts:
                for k, v in mut.items():
                    pdf.cell(0, 10, txt=safe_text(f"{k}: {v}"), ln=True)
                pdf.ln(3)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt=safe_text("Drug Matches"), ln=True)
            pdf.set_font("Arial", '', 12)
            for drug in drugs:
                for k, v in drug.items():
                    pdf.cell(0, 10, txt=safe_text(f"{k}: {v}"), ln=True)
                pdf.ln(3)

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
            st.success(f"Thank you {name}, your message has been received!")
        else:
            st.error("Please fill out all fields.")

# ------------------- FOOTER -------------------
st.markdown("""
<hr style='border: 1px solid #ddd;'>
<div style="text-align: center; color: gray;">
    <b>Syeda Rehmat</b> — Founder, <i>BioZero</i> | <a href='#'>About</a> | <a href='#'>Contact</a>
</div>
""", unsafe_allow_html=True)
