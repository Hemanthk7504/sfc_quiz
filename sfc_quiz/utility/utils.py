import re
import string
import numexpr as ne
import pandas as pd
import streamlit as st
from scipy.stats import t
import numpy as np


def extract_numbers_with_variable_names(question):
    matches = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', question)
    numbers = [float(match.replace(',', '')) for match in matches]
    variable_names = list(string.ascii_uppercase)[:len(numbers)]
    return numbers, variable_names


def evaluate_formula(formula, variables_dict):
    try:
        return ne.evaluate(formula, local_dict=variables_dict)
    except Exception as e:
        return str(e)


def convert_to_dataframe(raw_data):
    try:
        if 'df' not in st.session_state:
            st.session_state['df'] = None
        df = pd.read_csv(pd.io.common.StringIO(raw_data), sep='\t', engine='python')
        for col in df.columns:
            if df[col].dtype == object:
                try:
                    df[col] = df[col].replace('[\$,]', '', regex=True).replace(',', '', regex=True).astype(float)
                    st.session_state['df'] = df
                except ValueError:
                    pass
        return df, list(df.columns)
    except Exception as e:
        st.error(f"Error parsing CSV data: {e}")
        return None, None


def sanitize_formula(formula):
    cleaned_formula = re.sub(r'[\r\n\t]+', '', formula)
    cleaned_formula = re.sub(r'(\d+\.\d+)([A-Za-z]+)', r'\1*\2', cleaned_formula)
    return cleaned_formula


def parse_and_compute(formula, computed_values):
    sanitized_formula = sanitize_formula(formula)
    # Continue with the replacement of variables with their numeric values
    for var, value in computed_values.items():
        if var in sanitized_formula:
            sanitized_formula = sanitized_formula.replace(var, str(value))

    sanitized_formula = sanitized_formula.replace('%', '/100')

    try:
        result = ne.evaluate(sanitized_formula)
    except Exception as e:
        print(f"Error evaluating formula: {e}")
        result = None

    if result is not None:
        try:
            result = float(result)
        except ValueError:
            print("Conversion to float failed, setting result to None")
            result = None

    return result

    variables_in_formula = re.findall(r'[A-Za-z]+', formula)

    # Replace each variable in the formula with its value from computed_values
    for var in variables_in_formula:
        if var in computed_values:
            # Replace the variable name with its value, ensure it's cast to str for replacement
            formula = formula.replace(var, str(computed_values[var]))

    # Evaluate the formula using numexpr for safety
    try:
        # Use ne.evaluate to compute the result of the formula
        return ne.evaluate(formula)
    except Exception as e:
        # If there's an error in evaluation, return the error message
        return str(e)


def apply_solution(params, formulas, variable_values):
    # Initialize a dictionary to store computed results
    computed_values = variable_values.copy()
    results = []

    # Iterate over each solution parameter and its formula
    for param, formula in zip(params, formulas):
        if formula.startswith("margin_of_error"):
            # If the formula starts with "margin_of_error", extract the variable names
            alpha_var, std_var, size_var = re.findall(r'\((.*?)\)', formula)[0].split(', ')

            # Get the values for the variables from variable_values or use default values
            alpha = float(variable_values.get(alpha_var, 0.05))
            std = float(variable_values.get(std_var, 0))
            size = int(variable_values.get(size_var, 0))

            if std != 0 and size != 0:
                df = size - 1
                t_critical = t.ppf(1 - alpha / 2, df)
                result = t_critical * (std / np.sqrt(size))
            else:
                result = None
        else:
            # Compute the result of the formula
            result = parse_and_compute(formula, computed_values)

        # Update the computed values with the result
        computed_values[param] = result
        # Append the result to the results list
        results.append((param, result))

    # Return the results as a list of tuples
    return results


def handle_table_input():
    if 'show_table_input' not in st.session_state:
        st.session_state['show_table_input'] = False

    if 'raw_data' not in st.session_state:
        st.session_state['raw_data'] = ''

    if 'df' not in st.session_state:
        st.session_state['df'] = None

    show_table_input_button = st.button("Add table",key="show_table_input_button")

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

    if st.session_state['df'] is not None:
        st.write("Full Table:")
        st.dataframe(st.session_state['df'])
