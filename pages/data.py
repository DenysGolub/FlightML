import streamlit as st
from helpers import database as db
from st_keyup import st_keyup
import shutil
st.file_uploader("Завантажте датасет")

def search_experiment(name):
    filtered = db.run_query(f'SELECT * FROM datasets WHERE name LIKE "%{name}%"')
    # st.write(12)
    # st.write(filtered)
    return filtered

search_text = st_keyup('Назва датасету')


def edit_experiment(name):
    pass
@st.dialog(title='Ви впевнені?', )
def delete_experiment(name):
    st.warning('Дія є незворотньою.\nДатасет видалиться без можливості відновлення.')
    padding1, col1,  col2, padding2 = st.columns([2,1,1,2], vertical_alignment='bottom')
    with col1: 
        if st.button('Так'):
            query = f'DELETE FROM datasets WHERE name = "{name}"'
            shutil.rmtree(f'datasets\\{name}')
            db.run_query(query)
            st.rerun()
    with col2:
        if st.button('Ні'):
            st.rerun()



experiments = search_experiment(search_text)
max_cols = 5
current_col = 0
row = st.columns(max_cols)

for i in range(0, len(experiments), max_cols):
    row = st.columns(max_cols)  
    for j, exp in enumerate(experiments[i:i+max_cols]):  
        with row[j]:  
            with st.container(border=True):
                st.markdown(f"**{exp[1]}**")
                st.caption(f"{exp[5]}") 

                btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])  
                with btn_col1:
                    st.button("🔍", key=f"view_{i}_{j}", help='Переглянути', use_container_width=True, on_click=redirect_to_experiment_page, args=[exp[1], exp[0]])
                with btn_col2:
                    st.button("🖊️", key=f"edit_{i}_{j}", help="Змінити", use_container_width=True, on_click = edit_experiment, args=[exp[0]])
                with btn_col3:
                    st.button("🗑️", key=f"del_{i}_{j}", help="Видалити", on_click=delete_experiment, args=[exp[1], exp[2]], use_container_width=True)
                    
                    
                    
                    

