import openpyxl
import pandas as pd
from io import StringIO
import streamlit as st


def convert_to_excel(df):
    """Convert a DataFrame to an in-memory Excel file object."""
    output = StringIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='dataframe')
    writer.save()
    output.seek(0)
    return output


def apply_excel_formula(dataframe):
    excel_file = convert_to_excel(dataframe)

    wb = openpyxl.load_workbook(excel_file)
    ws = wb["dataframe"]
    st.dataframe(ws)


def convert_to_dataframe(raw_data):
    """Parses raw CSV data with the first line as column names into a Pandas DataFrame."""
    try:
        df = pd.read_csv(pd.io.common.StringIO(raw_data), sep='\t', engine='python')
        for col in df.columns:
            if df[col].dtype == object:
                try:
                    df[col] = df[col].replace('[\$,]', '', regex=True).replace(',', '', regex=True).astype(float)
                except ValueError:
                    pass
        return df, list(df.columns)
    except Exception as e:
        st.error(f"Error parsing CSV data: {e}")
        return None, None
