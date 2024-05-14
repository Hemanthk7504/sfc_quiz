import re

from PIL import Image

from main import formula_inputs
from ocr.tesseract_ocr import ocr_image
import streamlit as st
from db.db_operations import update_question_with_table, process_question_insertion, match_question, update_question, \
    insert_question
import json
import pandas as pd
import ast
from db.db import session, create_tables
from db.models import *
from operations.operation import run_excel_formula_app
from utility.utils import extract_numbers_with_variable_names, apply_solution, handle_table_input
from sqlalchemy import select

module_selection = st.sidebar.radio("Choose a module", ("Master Question", "Solutions"), key="choose_module")


def view_solution(question_id, session):
    """
    Fetch and display solution details for a given question ID
    :param question_id: the ID of the question
    :param session: the Session object
    """

    try:
        question = session.query(Question).filter(Question.id == question_id).first()
        if question:
            variable_values = question.variable_values
            solution_params = question.solution_params
            solution_formulas = question.solution_formulas
            combined_data = []
            for param, formula in zip(solution_params, solution_formulas):
                combined_data.append([param, formula])
            if variable_values:
                try:
                    variable_values = ast.literal_eval(variable_values)
                except Exception as e:
                    print(f"Failed to parse variable values: {e}")
                    return
                for key, value in variable_values.items():
                    combined_data.append([key, str(value)])
            results_df = pd.DataFrame(combined_data, columns=['Parameter/Variable', 'Value/Formula'])
            print("Raw question data:", question)
        else:
            print("No data found for the selected question ID.")

    except Exception as e:
        print(f"An error occurred: {e}")


def edit_question_interface(similar_questions):
    """Interface for editing an existing question."""
    if 'question_init' not in st.session_state or st.session_state.question_init not in [q.id for q in
                                                                                         similar_questions]:
        # Default selection for first run
        st.session_state.question_init = similar_questions[0].id  # Initialize with the first question's ID

    question_options = {q.id: q.question_text for q in similar_questions}
    question_id = st.selectbox(
        "Select a question to edit:",
        options=[q.id for q in similar_questions],
        format_func=lambda x: next(q.question_text for q in similar_questions if q.id == x),
        index=[q.id for q in similar_questions].index(st.session_state.question_init),
        key='question_select'
    )
    st.session_state.question_init = question_id
    # Get the selected question details
    selected_question = next(q for q in similar_questions if q.id == question_id)

    # Allow editing of question text and other attributes
    edited_text = st.text_area("Edit the question text:", value=selected_question.question_text,
                               key=f"edit_{question_id}")

    edited_variable_values = st.text_area("Edit variable values:", value=selected_question.variable_values,
                                          key=f"vars_{question_id}")
    edited_solution_params = st.text_area("Edit solution parameters:", value=selected_question.solution_params,
                                          key=f"params_{question_id}")
    edited_solution_formulas = st.text_area("Edit solution formulas:", value=selected_question.solution_formulas,
                                            key=f"formulas_{question_id}")

    if st.button("Update Question", key=f"update_{question_id}"):
        # Function to update the question in the database
        update_question(question_id, edited_text, edited_variable_values, edited_solution_params,
                        edited_solution_formulas)
        st.success("Question updated successfully.")
        # Optionally reset or clear the form here
        st.experimental_rerun()


if 'no_solution_steps' not in st.session_state:
    st.session_state['no_solution_steps'] = 0
st.session_state['df'] = None
if 'solution_details_saved' not in st.session_state:
    st.session_state['solution_details_saved'] = False
if 'last_question_id' not in st.session_state:
    st.session_state['last_question_id'] = None
if 'question_init' not in st.session_state:
    st.session_state['question_init'] = None
if 'selected_formula' not in st.session_state:
    st.session_state['selected_formula'] = None
if 'formula_type' not in st.session_state:
    st.session_state['formula_type'] = None

def master_question_module():
    """
    This function handles user interaction for creating and editing master questions with solutions.
    """
    st.title('Prepare Master Question')
    user_input_mode = st.radio("Do you want to upload an image or paste text?", ('Upload Image', 'Paste Text'),
                               key="master_input")

    user_question = ""
    if user_input_mode == 'Paste Text':
        user_question = st.text_area("Paste your question or new template here:")
    elif user_input_mode == 'Upload Image':
        uploaded_image = st.file_uploader("Upload an image...", type=["png", "jpg", "jpeg"])
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            user_question = ocr_image(image)
            user_question = st.text_area("Edit the extracted text if necessary:", user_question, height=300)
    if user_question:
        if st.button("Add New Question"):
            match_found, similar_questions = match_question(user_question, session)
            if not match_found:
                process_question_insertion(session, user_question,
                                           need_table=False)

            if match_found:
                st.warning("A similar question already exists in the database.")
                edit_or_new = st.radio("Select an option", ("Edit Existing Question", "Create New Question"),
                                       key="create")
                if edit_or_new == "Edit Existing Question":
                    edit_question_interface(similar_questions)
                numbers, variable_names = extract_numbers_with_variable_names(user_question)
                modified_question = re.sub(r'\d+(?:,\d{3})*(?:\.\d+)?', 'X', user_question)
                variable_values_str = str(dict(zip(variable_names, numbers)))
                no_variables = len(numbers)
                question_id = insert_question(session, modified_question, no_variables, variable_values_str)
                st.session_state['last_question_id'] = question_id
                st.success(f"New question added with ID {question_id}:")
                st.write(f"Number of variables identified: {no_variables}")
                st.write("Variables list:")
                for variable, value in zip(variable_names, numbers):
                    st.write(f"{variable}: {value}")
                st.session_state['no_solution_steps'] = 0
                st.session_state['solution_details_saved'] = False
        else:
            st.warning("A similar question already exists in the database.")
    if 'last_question_id' in st.session_state and st.session_state['last_question_id'] is not None:
        st.write("Upload or input the table data associated with this question:")
        handle_table_input()
        if 'df' in st.session_state and st.session_state['df'] is not None:
            df = st.session_state['df']
            run_excel_formula_app(df)
            df_json = df.to_json()
            update_question_with_table(session, st.session_state['last_question_id'], df_json)
            st.success("Table data linked to the question successfully.")
            if st.session_state.get('selected_formula'):
                selected_formula = st.session_state.get('selected_formula')
                if selected_formula:
                    question_to_update = session.query(Question).filter_by(
                        id=st.session_state['last_question_id']).first()
                    question_to_update.excel_formula = selected_formula['formula']
                    session.flush()
                    st.success("Formula saved successfully!")
            else:
                st.info("No table data has been added yet.")
        else:
            st.info("No table data has been added yet.")

    no_solution_steps = st.number_input("Enter the number of solution steps",
                                        value=st.session_state['no_solution_steps'], min_value=0, step=1,
                                        key='no_solution_steps')
    use_statistical_functions = st.checkbox("Use statistical functions")
    if no_solution_steps > 0 and st.session_state.get('last_question_id') is not None:
        solution_params = []
        solution_formulas = []

        for i in range(no_solution_steps):
            col1, col2 = st.columns(2)
            with col1:
                param_name = st.text_input(f"Enter solution parameter name for step {i + 1}", key=f"param_name_{i + 1}")
            with col2:
                if use_statistical_functions:
                    statistical_function = st.selectbox(f"Select statistical function for {param_name}",
                                                        ["None", "margin_of_error"], key=f"stat_func_{i + 1}")
                    if statistical_function == "margin_of_error":
                        alpha_var = st.text_input(f"Enter variable name for alpha (default: 0.05)",
                                                  key=f"alpha_var_{i + 1}")
                        std_var = st.text_input(f"Enter variable name for standard deviation", key=f"std_var_{i + 1}")
                        size_var = st.text_input(f"Enter variable name for sample size", key=f"size_var_{i + 1}")
                        formula = f"margin_of_error({alpha_var}, {std_var}, {size_var})"
                    else:
                        formula = st.text_input(f"Enter formula for {param_name}", key=f"formula_{i + 1}")
                else:
                    formula = st.text_input(f"Enter formula for {param_name}", key=f"formula_{i + 1}")
            solution_params.append(param_name)
            solution_formulas.append(formula)

        if st.button("Save Solution Details"):
            solution_params_json = json.dumps(solution_params)
            solution_formulas_json = json.dumps(solution_formulas)
            question_to_update = session.query(Question).filter_by(id=st.session_state['last_question_id']).first()
            question_to_update.no_solution_steps = no_solution_steps
            question_to_update.solution_params = solution_params_json
            question_to_update.solution_formulas = solution_formulas_json
            session.flush()
            st.session_state['solution_details_saved'] = True
            st.success("Solution details saved successfully!")
    if st.session_state.get('solution_details_saved') and st.button('View Solution'):
        view_solution(st.session_state['last_question_id'], session)
    if st.session_state.get('solution_details_saved') and st.button('Apply Solution'):
        question_data = session.query(Question).filter_by(id=st.session_state['last_question_id']).first()

        if question_data:
            try:
                variable_values = ast.literal_eval(question_data.variable_values)
            except Exception as e:
                st.error(f"Failed to parse variable values: {e}")

            solution_params = json.loads(question_data.solution_params)
            solution_formulas = json.loads(question_data.solution_formulas)
            computed_results = apply_solution(solution_params, solution_formulas, variable_values)
            results_df = pd.DataFrame(computed_results, columns=['Parameter', 'Computed Value'])
            st.table(results_df)


def solutions_module():
    """
    This function handles user interaction for solution retrieval and displays results.
    """
    st.title('Solutions')
    user_input_mode = st.radio("How would you like to input the question?", ('Upload Image', 'Paste Text'),
                               key="upload")
    user_question = ""
    if user_input_mode == 'Paste Text':
        user_question = st.text_area("Paste your question here:")
    elif user_input_mode == 'Upload Image':
        uploaded_image = st.file_uploader("Upload an image...", type=["png", "jpg", "jpeg"])
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            user_question = ocr_image(image)
            user_question = st.text_area("Review the extracted text:", user_question, height=300)

    if user_question and st.button("Show Solution"):
        match_found, similar_questions = match_question(user_question, session)
        if match_found:
            selected_question = similar_questions[0]
            input_numbers, _ = extract_numbers_with_variable_names(user_question)
            query = select(Question).from_(Question).where(Question.question_text == selected_question)
            question_data = session.exec(query).first()

            if question_data:
                question_id = question_data.id
                stored_variable_values_str = question_data.variable_values
                solution_params_str = question_data.solution_params
                solution_formulas_str = question_data.solution_formulas
                stored_variable_values = ast.literal_eval(stored_variable_values_str)
                solution_params = json.loads(solution_params_str)
                solution_formulas = json.loads(solution_formulas_str)
                variable_values = dict(zip(stored_variable_values.keys(), input_numbers))
                computed_results = apply_solution(solution_params, solution_formulas, variable_values)
                results_df = pd.DataFrame(computed_results, columns=['Parameter', 'Computed Value'])
                st.table(results_df)
        else:
            st.error("No matching question found in the database.")




if module_selection == "Master Question":
    create_tables(database_url="sqlite:///quiz_stats.db")
    master_question_module()


elif module_selection == "Solutions":
    create_tables(database_url="sqlite:///quiz_stats.db")
    solutions_module()

