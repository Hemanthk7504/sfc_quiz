import json
import pandas as pd
import streamlit as st


def load_formulas():
    with open('../operations/formulas.json', 'r') as file:
        formulas = json.load(file)
    return formulas


def apply_formula(dataframe, formula, variables):
    # Execute the formula safely using eval()
    try:
        result = eval(formula, {"dataframe": dataframe, **variables})
        return result
    except Exception as e:
        return str(e)


def formula_interface():
    formulas = load_formulas()
    formula_names = [formula['name'] for formula in formulas]
    st.title("Apply Formulas")
    selected_formula_name = st.selectbox("Choose a formula:", formula_names)
    selected_formula = next((item for item in formulas if item['name'] == selected_formula_name), None)

    if selected_formula:
        st.write(selected_formula['description'])
        # Create input fields based on required parameters in the formula string
        variables = {}
        params = ['lookup_column', 'lookup_value', 'result_column', 'column_name']  # Common params in formula
        for param in params:
            if param in selected_formula['formula']:
                if 'column' in param:
                    variables[param] = st.selectbox(f"Select {param}:", df.columns, key=param)  # Assuming df is your DataFrame loaded
                else:
                    variables[param] = st.text_input(f"Enter {param}:", key=param)

        # Button to execute formula
        if st.button("Apply Formula"):
            # Attempt to safely evaluate the formula using eval
            try:
                # Prepare the local environment for eval()
                local_env = {'dataframe': df}
                local_env.update(variables)
                result = eval(selected_formula['formula'], {}, local_env)
                st.write("Result:", result)
            except Exception as e:
                st.error(f"Error applying formula: {str(e)}")

df = pd.DataFrame({
    'Column1': [10, 20, 30, 40, 50],
    'Column2': [100, 200, 300, 400, 500]
})

formula_interface()