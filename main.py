import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# --- Path Handling ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "student_data.csv")
STYLE_PATH = os.path.join(BASE_DIR, "style.css")

# ====== Load custom CSS ======
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found. Ensure 'style.css' is in the root folder.")

local_css(STYLE_PATH)

st.title("Student Performance Analyzer :bar_chart:")
st.write(
    "Analyze student data with cleaned scores, key metrics, and visualizations."
)

# ====== Load data ======
@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path)
        # Strip whitespace from column headers
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error(f"Data file not found at {path}. Please ensure 'student_data.csv' is inside a 'data' folder.")
        return None

df = load_data(DATA_PATH)

if df is not None:
    st.subheader("Raw Data")
    st.dataframe(df)

    # Check if score columns exist
    score_cols = ["MathScore", "ReadingScore", "WritingScore"]
    missing_cols = [col for col in score_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required score columns: {missing_cols}")
        st.stop()

    # Convert score columns to numeric, coercing errors to NaN
    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Create the AverageScore column as mean of the three scores
    df['AverageScore'] = df[score_cols].mean(axis=1)

    # Data Cleaning: fill missing AverageScore with median, drop duplicates
    df['AverageScore'].fillna(df['AverageScore'].median(), inplace=True)
    df.drop_duplicates(inplace=True)

    st.subheader("Cleaned Data (filled missing average scores, removed duplicates)")
    st.dataframe(df)

    # Sidebar filter - filter by Gender (example)
    st.sidebar.markdown("## Student Performance Analyzer")
    st.sidebar.markdown("---")

    genders = df["Gender"].dropna().unique().tolist()
    selected_genders = st.sidebar.multiselect("Filter by Gender", genders, default=genders)
    
    if not selected_genders:
        st.warning("Please select at least one gender in the sidebar.")
        st.stop()

    filtered_df = df[df["Gender"].isin(selected_genders)]

    # Key Metrics
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Students", int(filtered_df.shape[0]))
    with col2:
        st.metric("Average Score", round(np.mean(filtered_df["AverageScore"]), 2))
    with col3:
        st.metric("Highest Score", int(np.max(filtered_df["AverageScore"])))
    with col4:
        st.metric("Lowest Score", int(np.min(filtered_df["AverageScore"])))

    # Visualization - Average Score by Gender
    st.subheader("Average Score by Gender")
    avg_scores_gender = (
        filtered_df.groupby("Gender")["AverageScore"].mean().reset_index()
    )
    bar_fig = px.bar(avg_scores_gender, x="Gender", y="AverageScore", color="Gender",
                     labels={"AverageScore": "Average Score"}, title="Average Scores by Gender")
    st.plotly_chart(bar_fig, use_container_width=True)

    # Visualization - Distribution of Students by Ethnic Group
    st.subheader("Student Distribution by Ethnic Group")
    ethnic_counts = filtered_df["EthnicGroup"].fillna("Unknown").value_counts().reset_index()
    ethnic_counts.columns = ["EthnicGroup", "Count"]
    pie_fig = px.pie(ethnic_counts, names="EthnicGroup", values="Count", title="Distribution of Students by Ethnic Group")
    st.plotly_chart(pie_fig, use_container_width=True)
