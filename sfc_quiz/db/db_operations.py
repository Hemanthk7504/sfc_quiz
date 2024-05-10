import json
import re
from sqlalchemy import select
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utility.utils import extract_numbers_with_variable_names
from .models import *

from sqlalchemy import select


def update_question(session, question_id, edited_question, edited_variable_values, edited_solution_params,
                    edited_solution_formulas):
    """
    Update a question's text, variable values, solution parameters, and solution formulas in the database.

    :param session: the Session object
    :param question_id: the ID of the question
    :param edited_question: the edited question text
    :param edited_variable_values: the edited variable values
    :param edited_solution_params: the edited solution parameters
    :param edited_solution_formulas: the edited solution formulas
    """
    question = session.query(Question).filter(Question.id == question_id).first()
    if question:
        question.question_text = edited_question
        question.variable_values = edited_variable_values
        question.solution_params = json.dumps(edited_solution_params)
        question.solution_formulas = json.dumps(edited_solution_formulas)
        session.commit()


def get_question_ids_from_db(session):
    """
    Fetch all question IDs from the database
    :param session: the Session object
    :return: a list of all question IDs in the database
    """

    query = select(Question.id).from_(Question)
    results = session.exec(query).all()
    question_ids = [result.id for result in results]  # Extract IDs from question objects
    return question_ids


def update_question_with_table(session, question_id, df_json):
    """
    Update a question in the database with its associated table data (creating a new table_data entry if needed)
    :param session: the Session object
    :param question_id: the ID of the question
    :param df_json: JSON representation of the DataFrame containing the table data
    """

    question = session.query(Question).filter(Question.id == question_id).first()
    if question:
        table_data = session.query(TableData).filter(TableData.question_id == question_id).first()
        if not table_data:
            new_table_data = TableData(data=df_json, question_id=question.id)
            session.add(new_table_data)
            session.commit()
            # question.table_data_id = new_table_data.id
        else:
            table_data.data = df_json
            session.commit()
        session.commit()


def insert_question(session, modified_question, no_variables, variable_values_str):
    """
    Insert a new question into the database
    :param session: the Session object
    :param modified_question: the question text with variables replaced by 'X'
    :param no_variables: the number of variables identified
    :param variable_values_str: a string representation of the variable values dictionary
    :return: the ID of the inserted question
    """

    new_question = Question(
        question_text=modified_question,
        no_variables=no_variables,
        variable_values=variable_values_str,
    )

    session.add(new_question)
    session.commit()
    session.refresh(new_question)

    return new_question.id


def match_question(input_question, session):
    """
    Compare input question with all questions in the database
    :param input_question: the question text to compare
    :param session: the Session object
    :return: (match_found, list_of_similar_questions)
    """

    questions = session.query(Question).all()

    similar_questions = []
    if questions:
        vectorizer = TfidfVectorizer().fit([input_question] + [q.question_text for q in questions])
        vectors = vectorizer.transform([input_question] + [q.question_text for q in questions])
        cosine_sim = cosine_similarity(vectors[0:1], vectors[1:])

        for idx, score in enumerate(cosine_sim[0]):
            if score > 0.8:
                similar_questions.append(questions[idx])
    return len(similar_questions) > 0, similar_questions


from sqlalchemy.exc import IntegrityError


def process_question_insertion(session, user_question, need_table):
    """Inserts question and handles table data if needed."""
    numbers, variable_names = extract_numbers_with_variable_names(user_question)
    modified_question = re.sub(r'\d+(?:,\d{3})*(?:\.\d+)?', 'X', user_question)
    variable_values_str = json.dumps(dict(zip(variable_names, numbers)))
    no_variables = len(numbers)

    if need_table:
        if 'df' in st.session_state:
            df_json = st.session_state['df'].to_json(orient='split')
            try:
                question_id = insert_question(session, modified_question, no_variables, variable_values_str, df_json)
                session.commit()
            except IntegrityError as e:
                st.error(f"Failed to insert question: {e}")
                return
        else:
            st.error("No table data found. Please upload and verify table data.")
            return
    else:
        try:
            question_id = insert_question(session, modified_question, no_variables, variable_values_str)
            session.commit()
        except IntegrityError as e:
            st.error(f"Failed to insert question: {e}")
            return

    if question_id:
        st.session_state['last_question_id'] = question_id
        st.success(f"New question added with ID {question_id}:")
        st.write(f"Number of variables identified: {no_variables}")
        st.write("Variables list:")
        for variable, value in zip(variable_names, numbers):
            st.write(f"{variable}: {value}")


def fetch_all_questions(session):
    """
    Fetch all questions from the database for comparison
    :param engine: the SQLAlchemy engine object
    :return: a list of all questions in the database
    """
    questions = session.query(Question).all()
    return [question.question_text for question in questions]
