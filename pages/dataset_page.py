import streamlit as st
import pandas as pd
def dataset_view_page():
    dataset_id = st.session_state.get("view_dataset_id")
    experiment_version_id = st.session_state.get("experiment_version_id")

    if not dataset_id:
        st.warning("❗ Датасет не обраний.")
        return

    dataset = get_dataset_by_id(dataset_id)  # Твоя функція для витягування з БД

    st.header(f"📁 Датасет: {dataset['name']}")
    st.markdown(f"**Тип даних:** {dataset.get('data_type', '—')}")
    st.markdown(f"**Опис:** {dataset.get('description', '—')}")
    st.markdown(f"**Шлях до файлу:** `{dataset['path_to_data']}`")
    st.markdown(f"**Дата створення:** {dataset['created_at']}")

    # Візуалізація даних, якщо CSV
    if dataset["path_to_data"].endswith(".csv"):
        try:
            df = pd.read_csv(dataset["path_to_data"])
            st.subheader("🧾 Попередній перегляд даних:")
            st.dataframe(df.head(20))
        except Exception as e:
            st.error(f"Не вдалося завантажити CSV: {e}")
    
    # Додатково: покажемо, з яким експериментом зв'язаний
    if experiment_version_id:
        st.markdown(f"🔗 Пов’язано з експеримент версією: `{experiment_version_id}`")
