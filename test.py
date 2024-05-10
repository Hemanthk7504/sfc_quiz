import re

import pandas as pd
import openpyxl
import streamlit as st
from io import BytesIO

from sfc_quiz.utility.utils import handle_table_input

# Sample DataFrame for demonstration
handle_table_input()
df = st.session_state['df']


def excel_to_dataframe_reference(cell):
    match = re.match(r"([A-Z]+)([0-9]+)", cell)
    if match:
        col, row = match.groups()
        row = int(row) - 1  # Convert to zero-based index
        col = ord(col) - 65  # Convert 'A' to 0, 'B' to 1, etc.
        return row, col
    else:
        raise ValueError(f"Invalid cell reference '{cell}'. Cell reference must contain a column and a row number.")


# Choose the formula to apply
formula_choice = st.selectbox("Select a formula", ["SUM", "VLOOKUP", "CONCATENATE"])

# Handling SUM formula input
if formula_choice == "SUM":
    st.write("The SUM function adds the values in a range of cells.")

    # Convert DataFrame columns to a list and specify default columns
    columns_list = df.columns.tolist()
    default_columns = columns_list[:2]  # Default to first two columns

    # Let the user select multiple columns to sum, ensuring default values are properly set
    selected_columns = st.multiselect("Select columns to sum:", options=columns_list, default=default_columns)

    if selected_columns:

        cell_ranges = [f"{chr(65 + df.columns.get_loc(col))}2:{chr(65 + df.columns.get_loc(col))}{len(df) + 1}"
                       for col in selected_columns]
        combined_range = ','.join(cell_ranges)  # Combine all selected column ranges

        # Where to apply the formula
        target_cell = st.text_input("Enter the cell to apply formula (e.g., 'D1')")
        apply_button = st.button("Apply Formula")

        if apply_button and target_cell:
            # Apply formula in Excel
            output = BytesIO()
            st.write(output.read())
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
                workbook = writer.book
                sheet = workbook.active
                formula = f"=SUM({combined_range})"
                sheet[target_cell] = formula
                writer.save()
            output.seek(0)
            df_with_formula = pd.read_excel(output)

            target_row, target_col = excel_to_dataframe_reference(target_cell)

            formula_output = df_with_formula.iat[target_row, target_col]

            st.success(f"Formula `{formula}` applied at cell {target_cell}. Output: {formula_output}")

            st.write(f"Formula =SUM({combined_range}) applied at cell {target_cell}. Output: {formula_output}")
            st.download_button(
                "Download Excel file with formulas",
                output,
                "dynamic_formulas_excel.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
