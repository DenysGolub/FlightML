import streamlit as st
from helpers.database import DataBase
from st_keyup import st_keyup
import pandas as pd
import shutil
import datetime
import os

st.markdown("### 📊 Датасети")
st.write("Набори даних, що використовуються в експериментах.")
db = DataBase()

def create_dirs(experiment_name):
    base_dir = "datasets"
    experiment_path = os.path.join(base_dir, experiment_name)
    os.makedirs(experiment_path, exist_ok=True)
    return experiment_path 

def insert_experiment_to_db(name, path_to_file, comment=""):
    created_at = datetime.datetime.now().strftime("%Y-%m-%d")
    query = """
    INSERT INTO datasets (name, path_to_data, description, data_type, created_at)
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (name, path_to_file, comment, "csv", created_at)
    db.run_query_params(query, params)

@st.dialog('Новий датасет')
def add_experiment():
    name_dataset = st.text_input(label="Введіть назву датасету")
    file_upload = st.file_uploader("Завантажте датасет (CSV)", type=["csv"])
    comment = st.text_area("Коментар до датасету")

    if st.button('Створити') and file_upload is not None and name_dataset.strip():
        dir_path = os.path.join("datasets", name_dataset)
        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join(dir_path, file_upload.name)

        with open(file_path, "wb") as f:
            f.write(file_upload.getbuffer())

        insert_experiment_to_db(name_dataset, file_path, comment)

        st.success("✅ Датасет успішно створено")
        st.rerun()


if(st.button('Додати датасет')):
    add_experiment()

def search_dataset(name):
    filtered = db.run_query(f"SELECT * FROM datasets WHERE name LIKE '%{name}%'")
    return filtered

search_text = st_keyup('Назва датасету')


@st.dialog(title='Ви впевнені?', )
def delete_dataset(name):
    st.warning('Дія є незворотньою.\nДатасет видалиться без можливості відновлення.')
    padding1, col1,  col2, padding2 = st.columns([2,1,1,2], vertical_alignment='bottom')
    with col1: 
        if st.button('Так'):
            query = f"DELETE FROM datasets WHERE name = '{name}'"
            shutil.rmtree(f'datasets\\{name}')
            db.run_query(query)
            st.rerun()
    with col2:
        if st.button('Ні'):
            st.rerun()

def redirect_to_dataset_page(dataset_id: int, experiment_version_id: int):
    st.session_state["modal_dataset_id"] = dataset_id
    st.session_state["modal_experiment_version_id"] = experiment_version_id

def get_dataset_by_id(dataset_id: int):
    query = f"""
    SELECT id, name, path_to_data, description, data_type, created_at
    FROM datasets
    WHERE id = {dataset_id}
    """
    result = db.run_query(query)
    print(result)
    return result
    
def show_dataset_modal():
    dataset_id = st.session_state.get("modal_dataset_id")
    if not dataset_id:
        return

    dataset = get_dataset_by_id(dataset_id)
    
    with st.container():

        if dataset[0]["path_to_data"].endswith(".csv"):
            try:
                df = pd.read_csv(dataset[0]["path_to_data"])
                print(df)
                st.dataframe(df.head(20))
            except Exception as e:
                st.error(f"⚠️ Помилка при завантаженні CSV: {e}")
        
        if st.button("❌ Закрити", key="close_modal"):
            st.session_state["modal_dataset_id"] = None
            st.session_state["modal_experiment_version_id"] = None
            st.rerun()

def redirect_to_dataset_page(dataset_id: int):
    st.session_state["modal_dataset_id"] = dataset_id

datasets = search_dataset(search_text)
max_cols = 5
current_col = 0
row = st.columns(max_cols)

for i in range(0, len(datasets), max_cols):
    row = st.columns(max_cols)  
    for j, exp in enumerate(datasets[i:i+max_cols]):  
        with row[j]:  
            with st.container(border=True):
                st.markdown(f"**{exp["name"]}**")  # exp[1] = name
                st.caption(f"{exp["description"]}")       # exp[5] = created_at

                btn_col1, btn_col2 = st.columns([1, 1])  
                with btn_col1:
                    st.button("🔍", key=f"view_{i}_{j}", help='Переглянути', use_container_width=True, on_click=redirect_to_dataset_page, args=[exp["id"]])  # exp[0] = id
                with btn_col2:
                    st.button("🗑️", key=f"del_{i}_{j}", help="Видалити", on_click=delete_dataset, args=[exp["name"]], use_container_width=True)

                if st.session_state.get("modal_dataset_id") == exp["id"]:
                    show_dataset_modal()
