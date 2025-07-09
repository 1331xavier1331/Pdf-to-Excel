from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import pdfplumber
import pandas as pd
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "PDF to Excel API is running"}

@app.post("/convert")
async def convert_pdf_to_excel(file: UploadFile = File(...)):
    input_path = f"temp_{file.filename}"
    output_path = f"{file.filename}.xlsx"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    with pdfplumber.open(input_path) as pdf:
        all_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_tables.append(df)

    if all_tables:
        final_df = pd.concat(all_tables, ignore_index=True)
        final_df.to_excel(output_path, index=False)
    else:
        return {"error": "No tables found in PDF"}

    os.remove(input_path)
    return FileResponse(output_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=output_path)
