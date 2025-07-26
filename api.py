from fastapi import FastAPI
import pandas as pd

app = FastAPI(title="AutoBio-X API")

# Load data
expression_df = pd.read_csv("expression.csv")
mutation_df = pd.read_csv("mutations.csv")
drug_df = pd.read_csv("dgidb_drugs.csv")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AutoBio-X API!"}

@app.get("/expression/{gene}")
def get_expression(gene: str):
    gene = gene.upper()
    result = expression_df[expression_df["Gene"].str.upper() == gene]
    if result.empty:
        return {"gene": gene, "expression": "Not found"}
    return {"gene": gene, "expression": result.iloc[0][1:].to_dict()}

@app.get("/mutation/{gene}")
def get_mutation(gene: str):
    gene = gene.upper()
    result = mutation_df[mutation_df["Gene"].str.upper() == gene]
    if result.empty:
        return {"gene": gene, "mutation": "Not found"}
    return result.to_dict(orient="records")

@app.get("/drugs/{gene}")
def get_drugs(gene: str):
    gene = gene.upper()
    result = drug_df[drug_df["Gene"].str.upper() == gene]
    if result.empty:
        return {"gene": gene, "drugs": "Not found"}
    return result[["Drug", "Interaction"]].to_dict(orient="records")
