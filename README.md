# EDA_agent_DiveIn_Ai
Automated EDA Agent (Streamlit + LLM)
This project is an interactive Exploratory Data Analysis (EDA) web app that combines classical data‑science workflows with an LLM‑powered assistant. Users can upload CSV or Excel files, automatically clean and profile their data, generate visualizations, and export ready‑to‑share reports.

The app is built with Streamlit for the UI and uses pandas, NumPy, Plotly, and scikit‑learn for statistics and visualization. An integrated Gemini‑based assistant summarizes the dataset, explains missing values and outliers, suggests preprocessing steps, and proposes baseline ML models. The tool produces both Excel and PDF reports, enabling a reproducible, end‑to‑end pipeline from raw data upload to cleaned analytics outputs.

# Key capabilities
* Automatic detection and treatment of missing values and outliers using configurable strategies (imputation, dropping, capping).
* Rich visual EDA, including histograms, boxplots, bar charts, and correlation heatmaps, with “before vs after cleaning” comparisons.
* Session‑aware design using st.session_state, allowing users to toggle between original and cleaned datasets while exploring plots and statistics.
* LLM chat interface grounded on the uploaded dataset that answers domain questions, recommends features, and sketches example ML pipelines.​
* One‑click export of multi‑sheet Excel files and PDF summaries, making it easy to share insights with non‑technical stakeholders.
