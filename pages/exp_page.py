import streamlit as st
import numpy as np
import pandas as pd
from helpers.database import DataBase


def insert_version_to_db(version_name):
    query = f'''
    INSERT INTO experiments_history (experiment_id, experiment_version)
    VALUES ({st.session_state.selected_exp_id}, '{version_name}')
    
    '''
    st.write(query)
    db.run_query(query)

if "selected_exp" not in st.session_state:
    st.session_state.selected_exp = None
    

if st.session_state.selected_exp is None:
    st.write("Оберіть експеримент з наявних або створіть новий!")
else:
    st.title(f"{st.session_state.selected_exp}")
    if st.button("Повернутися на головну"):
        st.session_state.selected_exp = None
        st.switch_page("pages/dashboard.py")
        


        
    import streamlit as st

    db = DataBase()

    # Fetch existing versions for the selected experiment
    query = '''SELECT experiment_version FROM experiments_history WHERE experiment_id = ?'''
    results = db.run_query_params(query, (st.session_state.selected_exp_id,))
    versions = [result[0] for result in results]

    if len(versions) == 0:
        st.info('В базі даних не існує версій для цього експерименту.')

    def insert_version_to_db():
        version = st.session_state.vers_input 
        if version:
            try:
                db.run_query_params(
                    '''INSERT INTO experiments_history (experiment_id, experiment_version) VALUES (?, ?)''',
                    (st.session_state.selected_exp_id, version)
                )
                st.session_state.vers_input = "" 
            except Exception as e:
                if(f'{e}' == 'UNIQUE constraint failed: experiments_history.experiment_version'):
                    st.error('Назви версій повинні бути унікальні!')
                else:
                    st.error(f"Помилка при додаванні версії: {e}")

    st.text_input(label='Назва версії', key='vers_input', on_change=insert_version_to_db)

    st.selectbox(label='Версії', options=versions)

    data, info, eda = st.tabs(['Дані', 'Загальні відомості', 'EDA'])
    
    data.file_uploader('Завантажити файл')
    
    
    
    eda.write('Exploratory Data Analysis')
    eda.dataframe(pd.DataFrame([12, 124]))
    
        
