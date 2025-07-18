#region Libraries
import streamlit as st
import re
import os
from datetime import datetime
from st_keyup import st_keyup
import shutil
#endregion

#region Variables
BASE_PATH = os.path.abspath("experiments")
#endregion


#region DataBase Initizalization
from helpers.database import DataBase

db = DataBase()
#endregion

#region Functions
def generate_folder_name(experiment_name):
    folder_name = re.sub(r'\s+', '-', experiment_name).lower()
    return folder_name

def create_dirs(experiment_name):
    os.mkdir(f'{BASE_PATH}\\{experiment_name}')
    os.mkdir(f'{BASE_PATH}\\{experiment_name}\\data')
    
def insert_experiment_to_db(name, comment):
    folder_path = f'/{name}'
    created_at = datetime.now()
    edited_at = datetime.now()
    print(created_at)
    query = '''
    INSERT INTO experiments (name, folder_path, created_at, edited_at, comment) 
    VALUES (%s, %s, %s, %s, %s)
'''
    params = (name, folder_path, str(created_at), str(edited_at), comment)

    db.run_query_params(query, params)
  
    
    
def search_experiment(name):
    filtered = db.run_query(f"SELECT * FROM experiments WHERE name LIKE '%{name}%'")
    return filtered


@st.dialog(title='Ви впевнені?', )
def delete_experiment(name):
    st.warning('Дія є незворотньою.\nЕксперимент видалиться без можливості відновлення.')
    padding1, col1,  col2, padding2 = st.columns([2,1,1,2], vertical_alignment='bottom')
    with col1: 
        if st.button('Так'):
            query = f"DELETE FROM experiments WHERE name = '{name}'"
            shutil.rmtree(f'experiments\\{name}')
            db.run_query(query)
            st.rerun()
    with col2:
        if st.button('Ні'):
            st.rerun()

#endregion  

cot = st.container()
cot.markdown('### 📄Головна')
st.write("Управління експериментами.")

@st.dialog('Новий експеримент')
def add_experiment():
    name = st.text_input(label='Назва')
    comment = st.text_input(label='Коментар')
    if st.button('Створити'):
        # st.session_state.experiment = {"item": item, "name": name}
        create_dirs(name)
        insert_experiment_to_db(name, comment)
        st.rerun()



if(st.button('Додати експеримент')):
    add_experiment()


def redirect_to_experiment_page(name_exp, id_exp):
    st.session_state.selected_exp = name_exp
    st.session_state.selected_exp_id = id_exp

if "selected_exp" in st.session_state and st.session_state.selected_exp is not None:
    st.switch_page('pages/exp_page.py')
    
search_text = st_keyup('Пошук за назвою експерименту')


experiments = search_experiment(search_text)
max_cols = 5
current_col = 0
row = st.columns(max_cols)

for i in range(0, len(experiments), max_cols):
    row = st.columns(max_cols)  
    for j, exp in enumerate(experiments[i:i+max_cols]):  
        with row[j]:  
            with st.container(border=True):
                print(exp)
                st.markdown(f"**{exp["name"]}**")
                st.caption(f"{exp["comment"]}") 

                btn_col1, btn_col2 = st.columns([1, 1])  
                with btn_col1:
                    st.button("🔍", key=f"view_{i}_{j}", help='Переглянути', use_container_width=True, on_click=redirect_to_experiment_page, args=[exp["name"], exp["id"]])
                with btn_col2:
                    st.button("🗑️", key=f"del_{i}_{j}", help="Видалити", on_click=delete_experiment, args=[exp["name"]], use_container_width=True)
                    
                    
                    
                    

