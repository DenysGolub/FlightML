import streamlit as st
import pandas as pd
import seaborn as sns
import time
import matplotlib.pyplot as plt
from helpers.database import DataBase
import json
from datetime import datetime
import plotly.express as px


db = DataBase()
ds_id = 0

if "selected_exp" not in st.session_state:
    st.session_state.selected_exp = None

if st.session_state.selected_exp is None:
    st.warning("Оберіть експеримент з наявних або створіть новий!")
    st.stop()

if st.button("На головну"):
    st.session_state.selected_exp = None
    st.switch_page("pages/dashboard.py")


def get_or_create_param_id(name):
    row = db.run_query_params("SELECT id FROM params WHERE name = %s", (name,))
    if row:
        return row[0]["id"]
    db.run_query_params("INSERT INTO params (name) VALUES (%s)", (name,))
    return db.run_query_params("SELECT id FROM params WHERE name = %s", (name,))[0]["id"]

def get_or_create_metric_id(name):
    row = db.run_query_params("SELECT id FROM metrics WHERE name = %s", (name,))
    if row:
        return row[0]["id"]
    db.run_query_params("INSERT INTO metrics (name) VALUES (%s)", (name,))
    return db.run_query_params("SELECT id FROM metrics WHERE name = %s", (name,))[0]["id"]


def remove_items_from_db(removed_param_names: set, removed_metric_names: set, experiment_history_id):
    for param_name in removed_param_names:
        param_id = get_or_create_param_id(param_name)
        db.run_query_params("""
            DELETE FROM experiment_params
            WHERE experiment_history_id = %s AND param_id = %s
        """, (experiment_history_id, param_id))

    for metric_name in removed_metric_names:
        metric_id = get_or_create_metric_id(metric_name)
        db.run_query_params("""
            DELETE FROM experiment_metrics
            WHERE experiment_history_id = %s AND metric_id = %s
        """, (experiment_history_id, metric_id))


st.title(f"Експеримент: {st.session_state.selected_exp}")

# Версії
query_versions = '''SELECT experiment_version FROM experiments_history WHERE experiment_id = %s'''
results = db.run_query_params(query_versions, (st.session_state.selected_exp_id,))
versions = [result["experiment_version"] for result in results]

if not versions:
    st.info('У цього експерименту немає версій.')

st.markdown("### 🧬 Керування версіями експерименту")
st.markdown("Додайте нову версію експерименту або виберіть існуючу зі списку нижче.")

with st.container(border=True):
    col1, col2 = st.columns([3, 1])
    version_input = col1.text_input("Назва нової версії", key="vers_input", placeholder="v1.0, baseline, tuned_model")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
    if col2.button("➕ Додати версію"):
        version = version_input.strip()
        if version:
            try:
                db.run_query_params(
                    '''INSERT INTO experiments_history (experiment_id, experiment_version) VALUES (%s, %s)''',
                    (st.session_state.selected_exp_id, version)
                )
                versions.append(version)
                st.success(f"✅ Версію **{version}** додано успішно.")

                del st.session_state["vers_input"]
                st.rerun()

            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    st.warning("⚠️ Ім'я версії не повинно повторюватись в межах експерименту.")
                else:
                    st.error(f"❌ Помилка: {e}")
        else:
            st.warning("⚠️ Введіть назву версії перед додаванням.")


data, eda, info = st.tabs(['📄 Дані', '🔬 EDA', '⚙️ Конфігурація та результати'])

# Вибір версії експерименту
with st.sidebar:
    st.markdown("### 🔢 Вибір версії експерименту")
    versions = [row["experiment_version"] for row in db.run_query_params(
        "SELECT experiment_version FROM experiments_history WHERE experiment_id = %s",
        (st.session_state.selected_exp_id,)
    )]
    selected_version = st.selectbox("Оберіть версію:", options=versions)

# Дані
with data:
    st.subheader("📎 Прив’язка датасету до версії експерименту")

    datasets = db.run_query('SELECT id, name FROM datasets')
    dataset_options = {f"{row["name"]} (ID: {row["id"]})": row["id"] for row in datasets}

    if len(dataset_options) == 0:
        st.error("❌ В базі відсутні датасети.")
        st.stop()

    query_current = '''
    SELECT d.name, d.id 
    FROM experiment_data ed
    JOIN datasets d ON ed.dataset_id = d.id
    JOIN experiments_history eh ON ed.experiment_version_id = eh.id
    WHERE eh.experiment_id = %s AND eh.experiment_version = %s
    '''
    result_current = db.run_query_params(query_current, (st.session_state.selected_exp_id, selected_version))
    print(result_current)
    if result_current:
        name, ds_id = result_current[0]["name"], result_current[0]["id"]
        # print(name, ds_id)
        st.markdown(f"🔗 Поточний прив’язаний датасет: **{name}** (ID: {ds_id})")
    else:
        st.info("🔒 Поки що не прив’язано жодного датасету до цієї версії.")
        ds_id = None

    selected_dataset = st.selectbox("Оберіть новий датасет для цієї версії:", options=list(dataset_options.keys()))
    selected_dataset_id = dataset_options[selected_dataset]

    if st.button("🔗 Прив'язати датасет"):
        query = "SELECT id FROM experiments_history WHERE experiment_id = %s AND experiment_version = %s"
        result = db.run_query_params(query, (st.session_state.selected_exp_id, selected_version))

        if result:
            version_id = result[0]["id"]
            try:
                db.run_query_params(
                    '''
                    INSERT INTO experiment_data (experiment_version_id, dataset_id)
                    VALUES (%s, %s)
                    ON CONFLICT(experiment_version_id)
                    DO UPDATE SET dataset_id = excluded.dataset_id
                    ''',
                    (version_id, selected_dataset_id)
                )
                st.success("✅ Датасет успішно оновлено або прив’язано до версії!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Помилка при збереженні: {e}")
        else:
            st.error("❌ Не вдалося знайти ID обраної версії експерименту.")

# EDA
with eda:
    st.subheader("📊 Автоматичний аналіз")
    if ds_id is not None:
        query = "SELECT path_to_data FROM datasets WHERE id = %s"
        res = db.run_query_params(query, (ds_id,))
    else:
        res = []

    if res:
        print(res)
        try:
            df = pd.read_csv(res[0]["path_to_data"])
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Info", "Head", "Describe", "Nulls", "Plots"])

            with tab1:
                st.text(df.info())

            with tab2:
                st.dataframe(df.head(), use_container_width=True)

            with tab3:
                st.dataframe(df.describe(), use_container_width=True)

            with tab4:
                st.dataframe(
                    df.isnull().sum().reset_index().rename(
                        columns={0: "Nulls", "index": "Column"}
                    ),
                    use_container_width=True
                )

            with tab5:
                num_cols = df.select_dtypes(include='number').columns
                cat_cols = df.select_dtypes(include='object').columns

        
                if len(num_cols) > 0:
                    with st.expander("📊 Розподіли числових колонок", expanded=False):
                        for col in num_cols:
                            fig = px.histogram(df, x=col, nbins=30, title=f"Розподіл: {col}", opacity=0.75)
                            fig.update_layout(height=500)
                            st.plotly_chart(fig, use_container_width=True)

                if len(cat_cols) > 0:
                    with st.expander("📊 Частоти категоріальних колонок", expanded=False):
                        for col in cat_cols:
                            vc = df[col].value_counts().reset_index()
                            vc.columns = [col, 'Кількість']
                            fig = px.bar(vc, x=col, y='Кількість', title=f"Категорії: {col}")
                            fig.update_layout(height=500)
                            st.plotly_chart(fig, use_container_width=True)

                if len(num_cols) >= 2:
                    with st.expander("🔗 Кореляційна матриця", expanded=False):
                        corr = df[num_cols].corr()
                        fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", title="Кореляція між числовими змінними")
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Не вдалося прочитати файл: {e}")
    else:
        st.warning("Цей датасет не має шляху до CSV або не вибрано датасет.")

# Конфігурація
with info:
    st.subheader("⚙️ Конфігурація та результати")

    try:
        experiment_history_id = db.run_query_params(
            "SELECT id FROM experiments_history WHERE experiment_version = %s", 
            (selected_version,)
        )[0]["id"]
    except IndexError:
        st.info("Експеримент повинен мати хоча б одну версію!")
        st.stop()

    possible_params = [row["name"] for row in db.run_query("SELECT name FROM params")]
    possible_metrics = [row["name"] for row in db.run_query("SELECT name FROM metrics")]

    rows = db.run_query_params("""
        SELECT p.name, ep.param_value
        FROM experiment_params ep
        JOIN params p ON ep.param_id = p.id
        WHERE ep.experiment_history_id = %s
    """, (experiment_history_id,))
    print(rows)
    params_data = {r["name"]: r["param_value"] for r in rows}

    rows = db.run_query_params("""
        SELECT m.name, em.metric_value
        FROM experiment_metrics em
        JOIN metrics m ON em.metric_id = m.id
        WHERE em.experiment_history_id = %s
    """, (experiment_history_id,))
    metric_data = {r["name"]: r["metric_value"] for r in rows}

    if "last_experiment_id" not in st.session_state or st.session_state.last_experiment_id != experiment_history_id:
        st.session_state.last_experiment_id = experiment_history_id
        st.session_state.param_values = params_data.copy()
        st.session_state.metric_values = {k: float(v) for k, v in metric_data.items()}

    param_values = st.session_state.param_values
    metric_values = st.session_state.metric_values
    
    st.markdown("### 📥 Імпорт з JSON")

    with st.expander("🔽 Завантажити з файлів"):
        param_file = st.file_uploader("Завантаж файл параметрів (params.json)", type=["json"], key="param_file")
        metric_file = st.file_uploader("Завантаж файл метрик (metrics.json)", type=["json"], key="metric_file")

        if st.button("📤 Імпортувати з файлів"):
            if param_file:
                try:
                    params_json = json.load(param_file)
                    for k, v in params_json.items():
                        st.session_state.param_values[k] = str(v)
                    st.success("✅ Параметри імпортовано!")
                    time.sleep(1)
                except Exception as e:
                    st.error(f"❌ Помилка у файлі параметрів: {e}")
                    time.sleep(1)
            
            if metric_file:
                try:
                    metrics_json = json.load(metric_file)
                    for k, v in metrics_json.items():
                        st.session_state.metric_values[k] = float(v)
                    st.success("✅ Метрики імпортовано!")
                except Exception as e:
                    st.error(f"❌ Помилка у файлі метрик: {e}")
            st.rerun()

    with st.expander("📝 Вставити JSON вручну"):
        param_text = st.text_area("Встав JSON для параметрів", height=150, key="param_text")
        metric_text = st.text_area("Встав JSON для метрик", height=150, key="metric_text")

        if st.button("📥 Імпортувати з тексту"):
            if param_text:
                try:
                    params_json = json.loads(param_text)
                    for k, v in params_json.items():
                        st.session_state.param_values[k] = str(v)
                    st.success("✅ Параметри імпортовано з тексту!")
                    time.sleep(1)
                except Exception as e:
                    st.error(f"❌ Помилка у тексті параметрів: {e}")
                    time.sleep(1)

            if metric_text:
                try:
                    metrics_json = json.loads(metric_text)
                    for k, v in metrics_json.items():
                        st.session_state.metric_values[k] = float(v)
                    st.success("✅ Метрики імпортовано з тексту!")
                    time.sleep(1)
                except Exception as e:
                    st.error(f"❌ Помилка у тексті метрик: {e}")
                    time.sleep(1)
            st.rerun()


    # Параметри
    st.markdown("### 🛠️ Гіперпараметри")

    for idx, old_name in enumerate(list(param_values.keys())):
        col1, col2, col3 = st.columns([1, 2, 0.3])

        sel = col1.selectbox(
            f"Назва параметра {idx+1}",
            options=possible_params + ["Інше…"],
            index=(possible_params.index(old_name) 
                   if old_name in possible_params else len(possible_params)),
            key=f"param_select_{idx}"
        )
        if sel == "Інше…":
            new_name = col1.text_input(
                f"Введи нову назву параметра {idx+1}",
                value=old_name if old_name not in possible_params else "",
                key=f"param_input_{idx}"
            )
        else:
            new_name = sel

        new_val = col2.text_input(
            f"Значення параметра {idx+1}",
            value=param_values.get(old_name, ""),
            key=f"param_val_{idx}"
        )

        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
                
        if col3.button("❌", key=f"remove_param_{idx}"):
            param_values.pop(old_name)
            st.rerun()
        if new_name and new_name != old_name:
            if new_name not in param_values:  
                param_values[new_name] = new_val
                param_values.pop(old_name)
                st.rerun()
        else:
            param_values[old_name] = new_val
    if st.button("➕ Додати параметр"):
        param_values[""] = ""
        st.rerun()

    # Метрики
    st.markdown("### 📊 Результати експерименту")

    for idx, old_name in enumerate(list(metric_values.keys())):
        col1, col2, col3 = st.columns([1, 2, 0.3])

        sel = col1.selectbox(
            f"Назва метрики {idx+1}",
            options=possible_metrics + ["Інше…"],
            index=(possible_metrics.index(old_name) 
                   if old_name in possible_metrics else len(possible_metrics)),
            key=f"metric_select_{idx}"
        )
        if sel == "Інше…":
            new_name = col1.text_input(
                f"Введи нову назву метрики {idx+1}",
                value=old_name if old_name not in possible_metrics else "",
                key=f"metric_input_{idx}"
            )
        else:
            new_name = sel

        new_val = col2.number_input(
            f"Значення метрики {idx+1}",
            value=metric_values.get(old_name, 0.0),
            format="%.4f",
            key=f"metric_val_{idx}"
        )

        with col3:
            st.markdown("<br>", unsafe_allow_html=True)

        if col3.button("❌", key=f"remove_metric_{idx}"):
            metric_values.pop(old_name)
            st.rerun()

        if new_name and new_name != old_name:
            if new_name not in metric_values:
                metric_values[new_name] = new_val
                metric_values.pop(old_name)
                st.rerun()
        else:
            metric_values[old_name] = new_val

    if st.button("➕ Додати метрику"):
        metric_values[""] = 0.0
        st.rerun()

    # Збереження в БД
    if st.button("💾 Зберегти конфігурацію та результати"):
        rem_p = set(params_data) - set(param_values)
        rem_m = set(metric_data) - set(metric_values)
        remove_items_from_db(rem_p, rem_m, experiment_history_id)

        for name, val in param_values.items():
            pid = get_or_create_param_id(name)
            if db.run_query_params("SELECT 1 FROM experiment_params WHERE experiment_history_id=%s AND param_id=%s", (experiment_history_id, pid)):
                db.run_query_params("UPDATE experiment_params SET param_value=%s WHERE experiment_history_id=%s AND param_id=%s", (val, experiment_history_id, pid))
            else:
                db.run_query_params("INSERT INTO experiment_params (experiment_history_id,param_id,param_value) VALUES (%s,%s,%s)", (experiment_history_id, pid, val))

        for name, val in metric_values.items():
            mid = get_or_create_metric_id(name)
            if db.run_query_params("SELECT 1 FROM experiment_metrics WHERE experiment_history_id=%s AND metric_id=%s", (experiment_history_id, mid)):
                db.run_query_params("UPDATE experiment_metrics SET metric_value=%s WHERE experiment_history_id=%s AND metric_id=%s", (val, experiment_history_id, mid))
            else:
                db.run_query_params("INSERT INTO experiment_metrics (experiment_history_id,metric_id,metric_value) VALUES (%s,%s,%s)", (experiment_history_id, mid, val))

        st.success("✅ Збережено!")
        time.sleep(1)
        st.rerun()
        
    st.markdown("### 📥 Експорт в JSON")

    param_json_str = json.dumps(param_values, indent=4)
    st.download_button(
        label="📤 Експортувати параметри (JSON)",
        data=param_json_str,
        file_name="params.json",
        mime="application/json"
    )

    # Експорт метрик
    metric_json_str = json.dumps(metric_values, indent=4)
    st.download_button(
        label="📤 Експортувати метрики (JSON)",
        data=metric_json_str,
        file_name="metrics.json",
        mime="application/json"
    )

