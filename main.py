import re
import pandas as pd
import streamlit as st
from io import BytesIO

from sfc_quiz.utility.utils import handle_table_input, convert_to_dataframe


def convert_to_cell_reference(lookup_value, df, table_array_cols):
    for col in table_array_cols:
        matching_rows = df[df[col] == lookup_value]
        if not matching_rows.empty:
            if len(matching_rows) == 1:
                lookup_row = matching_rows.index[0]
                lookup_col = df.columns.get_loc(col)
                return get_cell_reference(lookup_row, lookup_col)
            else:
                st.write(f"Multiple occurrences found for value '{lookup_value}' in column '{col}':")
                options = []
                for idx, row in matching_rows.iterrows():
                    options.append(f"Row {idx + 1}: {', '.join(str(val) for val in row.values)}")
                selected_option = st.radio("Select the row to use:", options)
                selected_row = int(selected_option.split(":")[0].split(" ")[1]) - 1
                lookup_row = matching_rows.index[selected_row]
                lookup_col = df.columns.get_loc(col)
                return get_cell_reference(lookup_row, lookup_col)
    st.warning(f"No matching value found for '{lookup_value}'. Please enter a valid lookup value.")
    return None


if 'show_table_input' not in st.session_state:
    st.session_state['show_table_input'] = False

if 'raw_data' not in st.session_state:
    st.session_state['raw_data'] = ''

if 'df' not in st.session_state:
    st.session_state['df'] = None

show_table_input_button = st.button("Add table")

if show_table_input_button:
    st.session_state['show_table_input'] = True

if st.session_state['show_table_input']:
    st.session_state['raw_data'] = st.text_area("Table data", st.session_state['raw_data'])
    convert_button = st.button("Convert")
    if st.session_state['raw_data'] is None:
        st.error("No table has been added")

    if convert_button:
        df, columns = convert_to_dataframe(st.session_state['raw_data'])
        if df is not None:
            st.session_state['df'] = df
            st.session_state['show_table_input'] = False
        else:
            st.error("Error converting data to DataFrame.")
table_array_cols = []
if st.session_state['df'] is not None:
    st.write("Full Table:")
    st.dataframe(st.session_state['df'])
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


def evaluate_formula(formula, sheet):
    if formula.startswith("="):
        formula = formula[1:]  # Remove the leading '='

    # Replace cell references with their corresponding values
    cell_refs = re.findall(r"[A-Z]+[0-9]+", formula)
    for cell_ref in cell_refs:
        row, col = excel_to_dataframe_reference(cell_ref)
        cell_value = sheet.cell(row=row + 1, column=col + 1).value
        if isinstance(cell_value, str) and cell_value.startswith("="):
            cell_value = evaluate_formula(cell_value, sheet)
        formula = formula.replace(cell_ref, str(cell_value))

    # Evaluate the formula
    try:
        result = eval(formula)
        return result
    except Exception as e:
        raise ValueError(f"Error evaluating formula: {formula}. {str(e)}")


def get_cell_reference(row, col):
    col_name = chr(65 + col)
    return f"{col_name}{row + 1}"


def apply_formula(formula_choice, input_values, target_cell, previous_output=None):
    if previous_output is not None:
        input_values['previous_output'] = previous_output
    if formula_choice == "SUM":
        start_cell, end_cell = input_values['range'].split(':')
        start_row, start_col = excel_to_dataframe_reference(start_cell)
        end_row, end_col = excel_to_dataframe_reference(end_cell)
        formula = f"=SUM({get_cell_reference(start_row, start_col)}:{get_cell_reference(end_row, end_col)})"
    elif formula_choice == "VLOOKUP":
        lookup_value = input_values["lookup_value"]
        if isinstance(lookup_value, tuple):
            child_formula, child_target_cell = lookup_value
            lookup_value = apply_formula(child_formula, input_values[child_formula], child_target_cell)

        if table_array_cols:
            table_array_range = f"{get_cell_reference(1, df.columns.get_loc(table_array_cols[0]))}:{get_cell_reference(len(df), df.columns.get_loc(table_array_cols[-1]))}"
        else:
            table_array_range = ""
        lookup_value = convert_to_cell_reference(lookup_value, df, table_array_cols)

        col_index_num = input_values["col_index_num"]
        if lookup_value:
            formula = f'=VLOOKUP({lookup_value}, {table_array_range}, {col_index_num}, {input_values["range_lookup"]})'
        else:
            formula = ""
    elif formula_choice == "MATCH":
        lookup_value = input_values["lookup_value"]
        if isinstance(lookup_value, tuple):
            child_formula, child_target_cell = lookup_value
            lookup_value = apply_formula(child_formula, input_values[child_formula], child_target_cell)
        else:
            lookup_row, lookup_col = excel_to_dataframe_reference(lookup_value)
            lookup_value = get_cell_reference(lookup_row, lookup_col)
        lookup_array_row, lookup_array_col = excel_to_dataframe_reference(input_values["lookup_array"])
        lookup_array = get_cell_reference(lookup_array_row, lookup_array_col)
        formula = f'=MATCH({lookup_value}, {lookup_array}, {input_values["match_type"]})'
    elif formula_choice == "INDEX":
        array_row, array_col = excel_to_dataframe_reference(input_values["array"])
        array = get_cell_reference(array_row, array_col)
        row_num = input_values["row_num"]
        if isinstance(row_num, tuple):
            child_formula, child_target_cell = row_num
            row_num = apply_formula(child_formula, input_values[child_formula], child_target_cell)
        else:
            row_num_row, row_num_col = excel_to_dataframe_reference(row_num)
            row_num = get_cell_reference(row_num_row, row_num_col)
        col_num = input_values["col_num"]
        if isinstance(col_num, tuple):
            child_formula, child_target_cell = col_num
            col_num = apply_formula(child_formula, input_values[child_formula], child_target_cell)
        else:
            col_num_row, col_num_col = excel_to_dataframe_reference(col_num)
            col_num = get_cell_reference(col_num_row, col_num_col)
        formula = f'=INDEX({array}, {row_num}, {col_num})'
    elif formula_choice == "AVG":
        start_cell, end_cell = input_values['range'].split(':')
        start_row, start_col = excel_to_dataframe_reference(start_cell)
        end_row, end_col = excel_to_dataframe_reference(end_cell)
        formula = f"=AVERAGE({get_cell_reference(start_row, start_col)}:{get_cell_reference(end_row, end_col)})"
    else:
        raise ValueError(f"Unknown formula: {formula_choice}")

    # Apply the formula to the Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        workbook = writer.book
        sheet = workbook.active
        sheet[target_cell] = f'={formula}'
        writer.save()
    output.seek(0)
    df_with_formula = pd.read_excel(output)

    target_row, target_col = excel_to_dataframe_reference(target_cell)

    formula_output = df_with_formula.iat[target_row, target_col]
    st.write(f"Formula `{formula}` applied at cell {target_cell}. Output: {formula_output}")
    output.seek(0)
    st.download_button(
        label="Download Excel file",
        data=output,
        file_name="modified_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    return formula_output


# Choose the formula to apply
formula_choice = st.selectbox("Select a formula", ["SUM", "VLOOKUP", "MATCH", "INDEX", "AVG"])
input_values = {}
if formula_choice in ["SUM", "AVG"]:
    range_ = st.text_input("Enter the range (e.g., 'A1:B5'):")
    input_values['range'] = range_
elif formula_choice == "VLOOKUP":
    lookup_value_type = st.selectbox("Select lookup value type:", options=["Value", "Formula"])
    if lookup_value_type == "Value":
        lookup_value = st.text_input("Enter the lookup value:")
        input_values['lookup_value'] = lookup_value

        if table_array_cols:
            matching_rows = df[df[table_array_cols[0]] == lookup_value]
            if not matching_rows.empty:
                if len(matching_rows) == 1:
                    lookup_row = matching_rows.index[0]
                    lookup_col = df.columns.get_loc(table_array_cols[0])
                    lookup_value = get_cell_reference(lookup_row, lookup_col)
                else:
                    st.write(f"Multiple occurrences found for value '{lookup_value}':")
                    options = []
                    for idx, row in matching_rows.iterrows():
                        options.append(f"Row {idx + 1}: {', '.join(str(val) for val in row.values)}")
                    selected_option = st.radio("Select the row to use:", options)
                    selected_row = int(selected_option.split(":")[0].split(" ")[1]) - 1
                    lookup_row = matching_rows.index[selected_row]
                    lookup_col = df.columns.get_loc(table_array_cols[0])
                    lookup_value = get_cell_reference(lookup_row, lookup_col)
            else:
                st.warning(f"No matching value found for '{lookup_value}'. Please enter a valid lookup value.")
                lookup_value = None
        else:
            st.warning("Please select at least one column for the table array.")
            lookup_value = None
    else:
        child_formula = st.selectbox("Select child formula:", options=["SUM", "VLOOKUP", "MATCH", "INDEX", "AVG"])
        child_target_cell = st.text_input("Enter the target cell for child formula:")
        input_values['lookup_value'] = (child_formula, child_target_cell)
        input_values[child_formula] = {}  # Create a nested dictionary for child formula inputs

    table_array_cols = st.multiselect("Select the table array columns:", options=df.columns.tolist())
    input_values['table_array'] = table_array_cols

    col_index_num = st.number_input("Enter the column index number:", min_value=1, value=1, step=1)
    input_values['col_index_num'] = col_index_num

    range_lookup = st.selectbox("Enter the range lookup:", options=["True", "False"], index=0)
    input_values['range_lookup'] = range_lookup
elif formula_choice == "MATCH":
    lookup_value_type = st.selectbox("Select lookup value type:", options=["Cell Reference", "Formula"])
    if lookup_value_type == "Cell Reference":
        lookup_value = st.text_input("Enter the lookup value cell reference:")
        input_values['lookup_value'] = lookup_value
    else:
        child_formula = st.selectbox("Select child formula:", options=["SUM", "VLOOKUP", "MATCH", "INDEX", "AVG"])
        child_target_cell = st.text_input("Enter the target cell for child formula:")
        input_values['lookup_value'] = (child_formula, child_target_cell)
        input_values[child_formula] = {}  # Create a nested dictionary for child formula inputs

    lookup_array = st.text_input("Enter the lookup array cell reference:")
    input_values['lookup_array'] = lookup_array
    match_type = st.selectbox("Enter the match type:", options=[0, -1, 1])
    input_values['match_type'] = match_type
elif formula_choice == "INDEX":
    array = st.text_input("Enter the array cell reference:")
    input_values['array'] = array

    row_num_type = st.selectbox("Select row number type:", options=["Cell Reference", "Formula"])
    if row_num_type == "Cell Reference":
        row_num = st.text_input("Enter the row number cell reference:")
        input_values['row_num'] = row_num
    else:
        child_formula = st.selectbox("Select child formula for row number:",
                                     options=["SUM", "VLOOKUP", "MATCH", "INDEX", "AVG"])
        child_target_cell = st.text_input("Enter the target cell for row number child formula:")
        input_values['row_num'] = (child_formula, child_target_cell)
        input_values[child_formula] = {}  # Create a nested dictionary for child formula inputs

    col_num_type = st.selectbox("Select column number type:", options=["Cell Reference", "Formula"])
    if col_num_type == "Cell Reference":
        col_num = st.text_input("Enter the column number cell reference:")
        input_values['col_num'] = col_num
    else:
        child_formula = st.selectbox("Select child formula for column number:",
                                     options=["SUM", "VLOOKUP", "MATCH", "INDEX", "AVG"])
        child_target_cell = st.text_input("Enter the target cell for column number child formula:")
        input_values['col_num'] = (child_formula, child_target_cell)
        input_values[child_formula] = {}  # Create a nested dictionary for child formula inputs child formula inputs
# Ask the user for the target cell
target_cell = st.text_input("Enter the target cell (e.g., 'D1')")

# Ask the user for the target cell

# When the "Apply Formula" button is clicked
if st.button("Apply Formula"):
    apply_formula(formula_choice, input_values, target_cell)
