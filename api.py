  # main.py (FastAPI Backend)
from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI(title="AutoBio-X API")

# ------------------- DATA LOADING -------------------
def load_csv(file: str):
    if os.path.exists(file):
        try:
            return pd.read_csv(file)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            return pd.DataFrame()
    else:
        print(f"Warning: {file} not found!")
        return pd.DataFrame()

expression_df = load_csv("expression.csv")
mutation_df = load_csv("mutations.csv")
drug_df = load_csv("dgidb_drugs.csv")

# ------------------- ENDPOINTS -------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to the AutoBio-X API!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/expression/{gene}")
def get_expression(gene: str):
    if expression_df.empty:
        return {"error": "Expression dataset not available."}
    gene = gene.upper()
    result = expression_df[expression_df["Gene"].str.upper() == gene]
    if result.empty:
        return {"gene": gene, "expression": "Not found"}
    return {"gene": gene, "expression": result.iloc[0][1:].to_dict()}

@app.get("/mutation/{gene}")
def get_mutation(gene: str):
    if mutation_df.empty:
        return {"error": "Mutation dataset not available."}
    gene = gene.upper()
    result = mutation_df[mutation_df["Gene"].str.upper() == gene]
    if result.empty:
        return {"gene": gene, "mutation": "Not found"}
    return result.to_dict(orient="records")

@app.get("/drugs/{gene}")
def get_drugs(gene: str):
    if drug_df.empty:
        return {"error": "Drug dataset not available."}
    gene = gene.upper()
    result = drug_df[drug_df["Gene"].str.upper() == gene]
    if result.empty:
        return {"gene": gene, "drugs": "Not found"}
    return result[["Drug", "Interaction"]].to_dict(orient="records")

# ------------------- REQUIREMENTS -------------------
# Save the following as requirements.txt:
# fastapi==0.111.0
# uvicorn==0.30.0
# pandas==2.2.2
