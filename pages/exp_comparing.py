import streamlit as st
from helpers.database import DataBase
import pandas as pd
import matplotlib.pyplot as plt


def generate_query(experiment, params, metrics):
    columns_sql = []
    
    for m in metrics:
        columns_sql.append(f"MAX(CASE WHEN m.name = '{m}' THEN em.metric_value END) AS {m}")
        
    for p in params:
        columns_sql.append(f"MAX(CASE WHEN p.name = '{p}' THEN ep.param_value END) AS {p}")

    full_query = f'''
    SELECT eh.experiment_version AS version,
    {',\n'.join(columns_sql)}
    FROM experiments_history eh

    JOIN experiments e ON eh.experiment_id = e.id

    LEFT JOIN experiment_metrics em ON eh.id = em.experiment_history_id
    LEFT JOIN metrics m ON em.metric_id = m.id

    LEFT JOIN experiment_params ep ON eh.id = ep.experiment_history_id
    LEFT JOIN params p ON ep.param_id = p.id

    WHERE e.name = '{experiment}'

    GROUP BY eh.id
    ORDER BY eh.id;
        '''
    
    return full_query

def generate_query_selected_versions(exp_versions: dict, params, metrics):
    columns_sql = []

    for m in metrics:
        columns_sql.append(
            f"MAX(CASE WHEN m.name = '{m}' THEN em.metric_value END) AS \"{m}\""
        )
    for p in params:
        columns_sql.append(
            f"MAX(CASE WHEN p.name = '{p}' THEN ep.param_value END) AS \"{p}\""
        )

    conditions = [
        f"(e.name = '{exp_name}' AND eh.experiment_version = '{version}')"
        for exp_name, version in exp_versions.items()
    ]

    where_clause = " OR ".join(conditions)

    full_query = f'''
    SELECT e.name AS experiment,
           eh.experiment_version AS version,
           {',\n           '.join(columns_sql)}
    FROM experiments_history eh
    JOIN experiments e ON eh.experiment_id = e.id
    LEFT JOIN experiment_metrics em ON eh.id = em.experiment_history_id
    LEFT JOIN metrics m ON em.metric_id = m.id
    LEFT JOIN experiment_params ep ON eh.id = ep.experiment_history_id
    LEFT JOIN params p ON ep.param_id = p.id
    WHERE {where_clause}
    GROUP BY eh.id, e.name, eh.experiment_version
    ORDER BY e.name;
    '''
    return full_query



st.markdown("### ⚖️ Порівняння")
st.write("Порівняння версій експерименту за обраними параметрами та метриками.")



db = DataBase()

tab1, = st.tabs(["🔁 Порівняння версій"])

with tab1:
    exp_options = db.run_query("SELECT name FROM experiments")

    temp_exp_options = [e["name"] for e in db.run_query("SELECT name FROM experiments")]

    exp_options = temp_exp_options
    experiment = st.selectbox("Оберіть експеримент з наявних", exp_options)


    params_options = [p["name"] for p in db.run_query("SELECT name FROM params")]
    selected_params = st.multiselect("Оберіть параметри моделі", params_options)


    metrics_options = [p["name"] for p in db.run_query("SELECT name FROM metrics")]
    selected_metrics = st.multiselect("Оберіть метрики", metrics_options)

    if(len(selected_metrics) > 0 and len(selected_params) > 0):
        table_query = generate_query(experiment, selected_params, selected_metrics)
        print(table_query)
        df = db.run_query_with_column_names(table_query)
        st.table(df.set_index("version"))
        st.markdown("<br>", unsafe_allow_html=True)
        st.line_chart(data=df[['version']+selected_metrics], x='version', height=650)


# with tab2:

#     available_experiments = [e["name"] for e in db.run_query("SELECT name FROM experiments")]
#     selected_experiments = st.multiselect("Оберіть експерименти", available_experiments)

#     exp_versions = {}
#     for exp in selected_experiments:
#         versions = [v["experiment_version"] for v in db.run_query_params(
#             "SELECT experiment_version FROM experiments_history eh JOIN experiments e ON e.id = eh.experiment_id WHERE e.name = %s",
#             (exp,)
#         )]
#         if versions:
#             selected_version = st.selectbox(f"Оберіть версію для {exp}", versions, key=f"{exp}_version")
#             exp_versions[exp] = selected_version

#     params = st.multiselect("Параметри", [p["name"] for p in db.run_query("SELECT name FROM params")])
#     metrics = st.multiselect("Метрики", [m["name"] for m in db.run_query("SELECT name FROM metrics")])

#     if exp_versions and (params or metrics):
#         query = generate_query_selected_versions(exp_versions, params, metrics)
#         df = db.run_query_with_column_names(query)

#         st.table(df.set_index("experiment"))
#         if metrics:
#             st.line_chart(df.set_index("experiment")[metrics])
