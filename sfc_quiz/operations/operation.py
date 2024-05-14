import streamlit as st

from utility.utils import handle_table_input

handle_table_input()
def run_excel_formula_app(df):
    st.title("Excel Formula Generator")

    if 'selected_formula' not in st.session_state:
        st.session_state['selected_formula'] = None

    if 'formula_type' not in st.session_state:
        st.session_state['formula_type'] = None

    formula_type = st.selectbox("Select a formula type:", ["SUM","HLOOKUP","FILTER", "SUMIF", "VLOOKUP", "MATCH", "INDEX", "AVG"])

    column = None
    lookup_value = None
    range_columns = None
    col_index_num = None
    range_lookup = None
    condition = None

    if formula_type == "SUM" or formula_type == "AVG":
        column = st.selectbox("Select the column for the operation:", df.columns)
    elif formula_type == "SUMIF":
        column = st.selectbox("Select the column for SUMIF:", df.columns)
        condition = st.text_input("Enter condition for SUMIF (e.g., '>150'):")
    elif formula_type == "FILTER":
        column = st.selectbox("Select the column for the condition:", df.columns)
        condition = st.text_input("Enter the condition for FILTER (e.g., '>=20'):")
    elif formula_type == "HLOOKUP":
        lookup_value = st.text_input("Enter the lookup value for HLOOKUP:")
        range_columns = st.multiselect("Select the range of rows to search within:", df.columns,
                                       default=df.columns.tolist())
        col_index_num = st.number_input("Enter the row index for the result (starting from 1):", min_value=1,
                                        max_value=len(df.columns), value=1)
        range_lookup = st.radio("Choose the type of match for HLOOKUP:", ['True', 'False'], index=1)

    elif formula_type == "VLOOKUP":
        lookup_column = st.selectbox("Select the lookup column:", df.columns)
        lookup_value = st.text_input("Enter the lookup value:")
        range_columns = st.multiselect("Select the range of columns to search within:", df.columns,
                                       default=df.columns.tolist())
        col_index_num = st.number_input("Enter the column index for the result (starting from 1):", min_value=1,
                                        max_value=len(df.columns), value=1)
        range_lookup = st.radio("Choose the type of match:", ['True', 'False'], index=1)
    elif formula_type == "MATCH":
        column = st.selectbox("Select the column for MATCH:", df.columns)
        lookup_value = st.text_input("Enter lookup value for MATCH:")
    elif formula_type == "INDEX":
        column = st.selectbox("Select the column for INDEX:", df.columns)
        lookup_value = st.text_input("Enter the index position (row number):")

    if st.button(f"Generate {formula_type} Formula"):
        formula = ""
        if formula_type == "SUM":
            formula = f"=SUM({chr(ord('A') + df.columns.get_loc(column))}2:{chr(ord('A') + df.columns.get_loc(column))}{len(df) + 1})"
        elif formula_type == "SUMIF":
            formula = f"=SUMIF({chr(ord('A') + df.columns.get_loc(column))}2:{chr(ord('A') + df.columns.get_loc(column))}{len(df) + 1}, \"{condition}\")"
        elif formula_type == "FILTER":
            formula = f"=FILTER({chr(ord('A') + df.columns.get_loc(column))}2:{chr(ord('A') + df.columns.get_loc(column))}{len(df) + 1}, {chr(ord('A') + df.columns.get_loc(column))}2:{chr(ord('A') + df.columns.get_loc(column))}{len(df) + 1} {condition})"
        elif formula_type == "VLOOKUP":
            row_index = df[df[lookup_column].astype(str) == lookup_value].index[0] + 2
            lookup_value_cell = f'{chr(ord("A") + df.columns.get_loc(lookup_column))}{row_index}'
            start_col = chr(ord('A') + df.columns.get_loc(range_columns[0]))
            end_col = chr(ord('A') + df.columns.get_loc(range_columns[-1]))
            table_range = f"{start_col}2:{end_col}{len(df) + 1}"
            formula = f"=VLOOKUP({lookup_value_cell}, {table_range}, {col_index_num}, {range_lookup})"
        elif formula_type == "MATCH":
            row_index = df[df[column].astype(str) == lookup_value].index[0] + 2
            lookup_value = f'{chr(ord("A") + df.columns.get_loc(column))}{row_index}'
            formula = f"=MATCH({lookup_value}, {chr(ord('A') + df.columns.get_loc(column))}2:{chr(ord('A') + df.columns.get_loc(column))}{len(df) + 1}, 0)"
        elif formula_type == "FILTER":
            col_letter = chr(ord('A') + df.columns.get_loc(column))
            formula = f"=FILTER({col_letter}2:{col_letter}{len(df) + 1}, {col_letter}2:{col_letter}{len(df) + 1}{condition})"
        elif formula_type == "HLOOKUP":
            start_col = chr(ord('A') + df.columns.get_loc(range_columns[0]))
            end_col = chr(ord('A') + df.columns.get_loc(range_columns[-1]))
            range_lookup_val = "TRUE" if range_lookup == "True" else "FALSE"
            formula = f"=HLOOKUP({lookup_value}, {start_col}1:{end_col}{len(df) + 1}, {col_index_num}, {range_lookup_val})"
        elif formula_type == "INDEX":
            formula = f"=INDEX({chr(ord('A') + df.columns.get_loc(column))}2:{chr(ord('A') + df.columns.get_loc(column))}{len(df) + 1}, {lookup_value})"
        elif formula_type == "AVG":
            formula = f"=AVERAGE({chr(ord('A') + df.columns.get_loc(column))}2:{chr(ord('A') + df.columns.get_loc(column))}{len(df) + 1})"

        st.session_state['selected_formula'] = formula
        st.session_state['formula_type'] = formula_type

    if st.session_state['selected_formula']:
        st.text("Generated Excel Formula:")
        st.code(st.session_state['selected_formula'])

if st.session_state['df'] is not None:
    df = st.session_state['df']
    run_excel_formula_app(df)