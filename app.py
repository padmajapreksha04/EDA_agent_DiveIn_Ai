"""
AI Research Assistant - Web Interface
Built by: Data Science Graduate Student @ Pace University
"""
import streamlit as st
import google.generativeai as genai
from tools import create_tools
import os
import re
import json
from datetime import datetime
import pandas as pd
import openpyxl  # For Excel file reading
import plotly.express as px
import plotly.graph_objects as go
import io
import numpy as np


# Report Generation and Visualization Imports
from report_generator import ReportGenerator, create_download_button
from pdf_report_generator import PDFReportGenerator
from eda_module import EDAAnalyzer, MissingValueHandler




# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="DiveIn AI - Research Companion",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .welcome-wrapper {
        background: linear-gradient(135deg, 
            rgba(255, 107, 107, 0.15) 0%, 
            rgba(255, 168, 0, 0.15) 25%,
            rgba(52, 211, 153, 0.15) 50%,
            rgba(96, 165, 250, 0.15) 75%,
            rgba(167, 139, 250, 0.15) 100%);
        background-size: 200% 200%;
        animation: gradientShift 8s ease infinite, fadeInUp 0.6s ease-out;
        border-radius: 20px;
        padding: 3rem 2.5rem;
        border: 2px solid rgba(255, 168, 0, 0.4);
        box-shadow: 0 8px 32px rgba(255, 168, 0, 0.2);
    }
    
    .title-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .robot-icon {
        font-size: 3rem;
        animation: pulse 2s infinite;
        filter: drop-shadow(0 0 10px rgba(255, 168, 0, 0.6));
    }
    
    .main-heading {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FFD93D 0%, #FF6B6B 50%, #4ECDC4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }
    
    .divider {
        height: 3px;
        background: linear-gradient(90deg, 
            #FFD93D 0%, 
            #FF6B6B 25%, 
            #4ECDC4 50%, 
            #6A5ACD 75%, 
            #FFD93D 100%);
        margin: 1.5rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(255, 217, 61, 0.4);
    }
    
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #FFD93D;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-shadow: 0 2px 10px rgba(255, 217, 61, 0.5);
    }
    
    .feature-list {
        list-style: none;
        padding: 0;
    }
    
    .feature-item {
        padding: 1rem 1.5rem;
        margin: 0.8rem 0;
        background: linear-gradient(90deg, 
            rgba(255, 107, 107, 0.2) 0%, 
            rgba(255, 168, 0, 0.2) 50%,
            rgba(52, 211, 153, 0.2) 100%);
        border-radius: 12px;
        color: #ffffff;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.3s ease;
        border-left: 4px solid #FFD93D;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .feature-item:hover {
        background: linear-gradient(90deg, 
            rgba(255, 107, 107, 0.35) 0%, 
            rgba(255, 168, 0, 0.35) 50%,
            rgba(52, 211, 153, 0.35) 100%);
        padding-left: 2rem;
        transform: translateX(5px);
        border-left-color: #FF6B6B;
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
    }
    
    .feature-item:nth-child(2) {
        border-left-color: #FFA500;
    }
    
    .feature-item:nth-child(2):hover {
        border-left-color: #FFD93D;
        box-shadow: 0 6px 20px rgba(255, 168, 0, 0.4);
    }
    
    .feature-item:nth-child(3) {
        border-left-color: #4ECDC4;
    }
    
    .feature-item:nth-child(3):hover {
        border-left-color: #34D399;
        box-shadow: 0 6px 20px rgba(52, 211, 153, 0.4);
    }
    
    .feature-item:nth-child(4) {
        border-left-color: #A78BFA;
    }
    
    .feature-item:nth-child(4):hover {
        border-left-color: #818CF8;
        box-shadow: 0 6px 20px rgba(129, 140, 248, 0.4);
    }
    
    .feature-emoji {
        font-size: 1.5rem;
        min-width: 1.5rem;
        filter: drop-shadow(0 2px 5px rgba(255, 217, 61, 0.3));
    }
    
    .cta-container {
        margin-top: 2.5rem;
        padding: 2rem;
        background: linear-gradient(135deg, 
            rgba(255, 107, 107, 0.25) 0%, 
            rgba(255, 168, 0, 0.25) 50%,
            rgba(52, 211, 153, 0.25) 100%);
        border-radius: 15px;
        border: 2px solid rgba(255, 217, 61, 0.4);
        text-align: center;
        box-shadow: 0 8px 25px rgba(255, 168, 0, 0.3);
    }
    
    .cta-title {
        font-size: 1.4rem;
        font-weight: 600;
        background: linear-gradient(135deg, #FFD93D 0%, #FF6B6B 50%, #4ECDC4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        text-shadow: 0 0 20px rgba(255, 217, 61, 0.5);
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# LOAD API KEYS FROM SECRETS
# ============================================================================
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    SERPER_API_KEY = st.secrets["SERPER_API_KEY"]
except Exception as e:
    st.error("⚠️ API keys not configured. Please set up secrets.")
    st.info("Add GOOGLE_API_KEY and SERPER_API_KEY to .streamlit/secrets.toml")
    st.stop()


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent_initialized' not in st.session_state:
    st.session_state.agent_initialized = False
if 'tools' not in st.session_state:
    st.session_state.tools = None
if 'tool_dict' not in st.session_state:
    st.session_state.tool_dict = {}
if 'model' not in st.session_state:
    st.session_state.model = None
if 'research_agent' not in st.session_state:
    st.session_state.research_agent = None
if 'ml_analyzer' not in st.session_state:
    st.session_state.ml_analyzer = None

# Initialize Report Generator and Visualizer
if 'report_generator' not in st.session_state:
    st.session_state.report_generator = ReportGenerator()


# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================
with st.sidebar:
    st.header("⚙️ Settings")
    
    
    
    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1
    )
    
    if st.button("🔄 Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    st.markdown("### 📚 About")
    st.markdown("""

    
    Capabilities:
    - 📚 Data Preprocessing
    - 📈 Data Visualization
    
    """)

# ============================================================================
# MAIN HEADER
# ============================================================================
st.markdown("""
    <div style='text-align: center; padding: 2rem 0 3rem 0;'>
        <h1 style='font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem; 
                   background: linear-gradient(135deg, #ffffff 0%, #d4af37 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;'>
            🔬 DiveIn AI
        </h1>
        <p style='font-size: 1.2rem; color: #888; font-weight: 300; margin: 0;'>
            Executive Research Companion
        </p>
    </div>
""", unsafe_allow_html=True)


# ============================================================================
# AGENT INITIALIZATION
# ============================================================================
if not st.session_state.agent_initialized:
    with st.spinner("🚀 Initializing AI Assistant..."):
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            
            available_models = []
            try:
                all_models = genai.list_models()
                for model in all_models:
                    if 'generateContent' in model.supported_generation_methods:
                        model_name_str = model.name.split('/')[-1]
                        available_models.append(model_name_str)
            except:
                available_models = ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest", "gemini-pro"]
            
            model_created = False
            for try_model in available_models:
                try:
                    test_model = genai.GenerativeModel(
                        model_name=try_model,
                        generation_config={
                            "temperature": temperature,
                            "top_p": 0.95,
                            "top_k": 40,
                            "max_output_tokens": 8192,
                        }
                    )
                    test_response = test_model.generate_content("Hi")
                    st.session_state.model = test_model
                    model_created = True
                    break
                except:
                    continue
            
            if not model_created:
                st.error("⚠️ Could not initialize AI model.")
                st.stop()
            
            os.environ['SERPER_API_KEY'] = SERPER_API_KEY
            st.session_state.tools = create_tools()
            st.session_state.tool_dict = {
                tool.name: tool for tool in st.session_state.tools
            }
            
            st.session_state.agent_initialized = True
            
        except Exception as e:
            st.error(f"❌ Initialization error: {e}")
            st.stop()




# ============================================
# DATA UPLOAD SECTION - ON MAIN PAGE
# ============================================
def eda_analysis_page():
    """Complete EDA Analysis Page with Visualizations, Cleaning, and Reports"""
    st.title("🔍 Exploratory Data Analysis")
    
    uploaded_file = st.file_uploader(
        "Upload your dataset to begin the EDA analysis",
        type=['xlsx', 'xls', 'csv'],
        help="Limit 200MB per file • XLSX, XLS, CSV"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File uploaded successfully! Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
            # Add this line
            st.session_state.uploaded_data = df.copy()


            # ========= AUTO PREPROCESSING =========
            auto_df = df.copy()

            # Missing values: simple strategy – you can tune this later
            num_cols = auto_df.select_dtypes(include=[np.number]).columns
            cat_cols = auto_df.select_dtypes(exclude=[np.number]).columns

            # Numeric: median imputation
            for col in num_cols:
                auto_df[col].fillna(auto_df[col].median(), inplace=True)

            # Categorical: mode imputation
            for col in cat_cols:
                if not auto_df[col].mode().empty:
                   auto_df[col].fillna(auto_df[col].mode()[0], inplace=True)

            # Outlier handling (IQR capping)
            for col in num_cols:
                q1 = auto_df[col].quantile(0.25)
                q3 = auto_df[col].quantile(0.75)
                iqr = q3 - q1
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                auto_df[col] = auto_df[col].clip(lower=lower, upper=upper)

            # Normalization example (optional – keep a copy)
            from sklearn.preprocessing import StandardScaler
            scaled_df = auto_df.copy()
            if len(num_cols) > 0:
                scaler = StandardScaler()
                scaled_df[num_cols] = scaler.fit_transform(scaled_df[num_cols])

            # Save to session for later tabs / download
            st.session_state["preprocessed_df"] = auto_df
            st.session_state["scaled_df"] = scaled_df

            # Basic EDA objects to reuse
            eda = EDAAnalyzer(auto_df)
            basic_info = eda.get_basic_info()
            stat_summary = eda.get_statistical_summary() if len(eda.numeric_cols) > 0 else None
            corr_matrix = eda.get_correlation_matrix() if len(eda.numeric_cols) > 1 else None


            # Store original data
            if 'original_df' not in st.session_state:
                st.session_state['original_df'] = df.copy()
            
            # Initialize EDA Analyzer
            eda = EDAAnalyzer(df)
            
            # Create tabs for different analyses
            (overview_tab,) = st.tabs([ "📋 EDA and Report"])

            
            # TAB 1: Overview
            with overview_tab:
                st.header("📋 Dataset Overview (Narrative)")

                st.write(f"**Shape:** {auto_df.shape[0]:,} rows × {auto_df.shape[1]} columns")

                

                # Generate a textual description with the LLM
                if "model" in st.session_state and st.session_state.model:
                    if st.button("🧠 Generate Theoretical Description", key="overview_llm_btn"):
                        sample_rows = auto_df.head(5).to_dict(orient="records")
                        overview_prompt = f"""
You are a senior data analyst.
Given this tabular dataset (summary + sample), write a clear, executive-level overview
of what this dataset represents and what kind of analysis it supports.

Summary:
- Shape: {auto_df.shape[0]} rows × {auto_df.shape[1]} columns
- Columns and dtypes: {auto_df.dtypes.to_dict()}
- First 5 rows (JSON): {json.dumps(sample_rows, default=str)[:4000]}

Explain:
1. What the dataset appears to be about.
2. Types of variables (numeric vs categorical).
3. Potential business questions or analyses it enables.
4. Any immediate data quality considerations (high-level).

Write 3–6 short paragraphs.
"""
                        response = st.session_state.model.generate_content(overview_prompt)
                        st.markdown(response.text)

            

            # ==============================
            # 1. Data Type & Summary Stats
            # ==============================
                st.subheader("📌 Data Types & Summary Statistics")

                num_cols = df.select_dtypes(include=[np.number]).columns
                cat_cols = df.select_dtypes(exclude=[np.number]).columns

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Column Type Overview**")
                    type_info = pd.DataFrame({
                        "Column": df.columns,
                        "Data Type": df.dtypes.values,
                        "Numeric?": [c in num_cols for c in df.columns],
                        "Unique Values": [df[c].nunique() for c in df.columns],
                    })
                    st.dataframe(type_info, use_container_width=True, height=350)

                with col2:
                    if len(num_cols) > 0:
                        st.markdown("**Numeric Columns – Summary Stats**")
                        st.dataframe(df[num_cols].describe().T, use_container_width=True, height=350)
                    if len(cat_cols) > 0:
                        st.markdown("**Categorical Columns – Summary Stats**")
                        st.dataframe(
                            df[cat_cols].describe(include="all").T,
                            use_container_width=True,
                            height=350,
                        )

                st.markdown("---")

            # ==============================
            # 2. Missing Values Analysis
            # ==============================
            st.subheader("🔍 Missing Values Analysis")

            missing = df.isnull().sum()
            missing = missing[missing > 0]

            if len(missing) > 0:
                st.warning(f"⚠️ Found missing values in {len(missing)} columns")

                col1, col2 = st.columns([2, 1])
                with col1:
                    fig_missing = px.bar(
                        x=missing.index,
                        y=missing.values,
                        title="Missing Values by Column",
                        labels={"x": "Column", "y": "Missing Count"},
                        color_discrete_sequence=["#FFA15A"],
                    )
                    st.plotly_chart(fig_missing, use_container_width=True, key="adv_missing_bar")

                with col2:
                    missing_df = pd.DataFrame({
                        "Column": missing.index,
                        "Missing Count": missing.values,
                        "Missing %": (missing.values / len(df) * 100).round(2),
                    })
                    st.dataframe(missing_df, use_container_width=True, height=300)

                st.subheader("🎯 Handle Missing Values")
                col1, col2 = st.columns(2)

                with col1:
                    imputation_method = st.selectbox(
                        "Select Imputation Method",
                        [
                            "Mean (Numeric columns)",
                            "Median (Numeric columns)",
                            "Mode (All columns)",
                            "Forward Fill",
                            "Backward Fill",
                            "Drop Rows with Missing Values",
                            "Drop Columns with >50% Missing",
                        ],
                    )

                with col2:
                    st.write("")
                    st.write("")
                    if st.button("🔧 Apply Imputation", type="primary", use_container_width=True):
                       with st.spinner("Cleaning data..."):
                            if imputation_method == "Mean (Numeric columns)":
                                for col in num_cols:
                                   df[col].fillna(df[col].mean(), inplace=True)
                                st.success("✅ Mean imputation applied to numeric columns!")

                            elif imputation_method == "Median (Numeric columns)":
                                for col in num_cols:
                                    df[col].fillna(df[col].median(), inplace=True)
                                st.success("✅ Median imputation applied to numeric columns!")

                            elif imputation_method == "Mode (All columns)":
                                for col in df.columns:
                                    if not df[col].mode().empty:
                                        df[col].fillna(df[col].mode()[0], inplace=True)
                                st.success("✅ Mode imputation applied to all columns!")

                            elif imputation_method == "Forward Fill":
                                df.fillna(method="ffill", inplace=True)
                                st.success("✅ Forward fill applied!")

                            elif imputation_method == "Backward Fill":
                                df.fillna(method="bfill", inplace=True)
                                st.success("✅ Backward fill applied!")

                            elif imputation_method == "Drop Rows with Missing Values":
                                rows_before = len(df)
                                df.dropna(inplace=True)
                                st.success(f"✅ Dropped {rows_before - len(df)} rows with missing values!")

                            elif imputation_method == "Drop Columns with >50% Missing":
                                thresh = len(df) * 0.5
                                cols_before = len(df.columns)
                                df.dropna(axis=1, thresh=thresh, inplace=True)
                                st.success(f"✅ Dropped {cols_before - len(df.columns)} columns with >50% missing values!")

                      
                            # Preview after handling missing values
                            st.subheader("🔍 Data After Handling Missing Values")
                            st.dataframe(df.head(20), use_container_width=True)

                            st.subheader("📉 Remaining Missing Values (After Imputation)")
                            remaining = df.isnull().sum()
                            remaining = remaining[remaining > 0]
                            if len(remaining) == 0:
                                st.success("🎉 No missing values remain in the dataset.")
                            else:
                                remaining_df = pd.DataFrame({
                                    "Column": remaining.index,
                                    "Missing Count": remaining.values,
                                    "Missing %": (remaining.values / len(df) * 100).round(2),
                                })
                                st.dataframe(remaining_df, use_container_width=True)

                            # Store cleaned data for use in other tabs
                            st.session_state["cleaned_df"] = df.copy()
            else:
               st.success("✅ No missing values detected in the dataset!")

               st.markdown("---")


            
            # ==============================
            # 3. Outlier Detection & Visuals
            # ==============================
            st.subheader("🚨 Outlier Detection (IQR)")

            if len(num_cols) > 0:
                outlier_summary = []
                for col in num_cols:
                    q1 = df[col].quantile(0.25)
                    q3 = df[col].quantile(0.75)
                    iqr = q3 - q1
                    lower = q1 - 1.5 * iqr
                    upper = q3 + 1.5 * iqr
                    mask = (df[col] < lower) | (df[col] > upper)
                    count = mask.sum()
                    if count > 0:
                        outlier_summary.append({
                            "Column": col,
                            "Outlier Count": int(count),
                            "Outlier %": round(count / len(df) * 100, 2),
                            "Lower Bound": round(lower, 3),
                            "Upper Bound": round(upper, 3),
                        })

                if outlier_summary:
                    outlier_df = pd.DataFrame(outlier_summary)
                    st.dataframe(outlier_df, use_container_width=True)

                    sel_col = st.selectbox(
                        "Select numeric column for outlier visualization",
                        outlier_df["Column"],
                        key="adv_outlier_col",
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Box Plot (With Outliers)**")
                        fig_box = px.box(df, y=sel_col, points="all",
                                 title=f"{sel_col} – Box Plot with Outliers")
                        st.plotly_chart(fig_box, use_container_width=True)

                        with col2:
                            st.markdown("**Histogram (With Outliers)**")
                        fig_hist = px.histogram(df, x=sel_col, marginal="box",
                                        title=f"{sel_col} – Distribution with Outliers")
                        st.plotly_chart(fig_hist, use_container_width=True)

                else:
                    st.success("✅ No significant numeric outliers detected by the IQR rule.")
            else:
              st.info("No numeric columns available for outlier analysis.")

            st.markdown("---")

            # ==============================
            # 4. Duplicate Rows
            # ==============================
            st.subheader("🔄 Duplicate Rows")

            duplicates = df.duplicated().sum()
            if duplicates > 0:
                st.warning(f"⚠️ Found {duplicates} duplicate rows")
                if st.button("🗑️ Remove Duplicates", type="primary"):
                    df.drop_duplicates(inplace=True)
                    st.session_state["cleaned_df"] = df.copy()
                    st.success(f"✅ Removed {duplicates} duplicate rows!")
                    st.rerun()
            else:
                st.success("✅ No duplicate rows found!")

            st.markdown("---")

            # ==============================
            # 5. Data Type Optimization
            # ==============================
            st.subheader("🔢 Data Type Optimization")

            type_opt = pd.DataFrame({
                "Column": df.columns,
                "Current Type": df.dtypes.values,
                "Memory Usage (MB)": [df[c].memory_usage(deep=True) / 1024**2 for c in df.columns],
            })
            st.dataframe(type_opt, use_container_width=True)

            st.info("""
**💡 Tips for Data Type Optimization:**
- Convert object columns with few unique values to `'category'`.
- Use smaller integer types (int8, int16) when possible.
- Convert date strings to proper `datetime` format.
""")
            # ==============================
            # 6. Correlation Analysis
            # ==============================
            st.markdown("---")
            st.subheader("📈 Correlation Analysis (Numeric Features)")

            if len(num_cols) > 1:
                # Correlation matrix
                corr_matrix = df[num_cols].corr()

                fig_corr = px.imshow(
                    corr_matrix,
                    text_auto=".2f",
                    color_continuous_scale="RdBu",
                    origin="lower",
                    x=num_cols,
                    y=num_cols,
                    title="Correlation Heatmap (Numeric Columns)",
                )
                fig_corr.update_xaxes(side="top")
                st.plotly_chart(fig_corr, use_container_width=True)
                # Optional: let user pick two features for scatter
                col_x, col_y = st.columns(2)
                with col_x:
                    corr_x = st.selectbox("X‑axis numeric feature", num_cols, key="corr_x")
                with col_y:
                    corr_y = st.selectbox("Y‑axis numeric feature", num_cols, key="corr_y")

                if corr_x != corr_y:
                   fig_scatter = px.scatter(
                       df,
                       x=corr_x,
                       y=corr_y,
                       trendline="ols",
                       title=f"{corr_y} vs {corr_x}",
                   )
                   st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.info("Select two different numeric features to view the scatter plot.")
            else:
                st.info("Need at least two numeric columns for correlation analysis.")


    

            # ==============================
            # 7. Feature Visualizations
            # ==============================
            st.markdown("---")
            st.subheader("📊 Feature Visualizations")

            # Numerical feature visuals (histogram + violin)
            if len(num_cols) > 0:
                st.markdown("**Numerical Feature**")
                num_feature = st.selectbox("Select numeric feature", num_cols, key="adv_num_viz")

                col1, col2 = st.columns(2)
                with col1:
                    fig_num_hist = px.histogram(
                    df,
                    x=num_feature,
                    marginal="box",
                    title=f"{num_feature} – Histogram",
                    )
                    st.plotly_chart(fig_num_hist, use_container_width=True)

                with col2:
                    fig_num_violin = px.violin(
                    df,
                    y=num_feature,
                    box=True,
                    points="all",
                    title=f"{num_feature} – Violin Plot",
                    )
                    st.plotly_chart(fig_num_violin, use_container_width=True)

            # Categorical feature visuals (bar + pie)
            if len(cat_cols) > 0:
                st.markdown("**Categorical Feature**")
                cat_feature = st.selectbox("Select categorical feature", cat_cols, key="adv_cat_viz")

                value_counts = df[cat_feature].value_counts().reset_index()
                value_counts.columns = [cat_feature, "Count"]

                col1, col2 = st.columns(2)
                with col1:
                    fig_cat_bar = px.bar(
                    value_counts,
                    x=cat_feature,
                    y="Count",
                    title=f"{cat_feature} – Category Counts",
                    )
                    st.plotly_chart(fig_cat_bar, use_container_width=True)

                with col2:
                    fig_cat_pie = px.pie(
                    value_counts,
                    names=cat_feature,
                    values="Count",
                    title=f"{cat_feature} – Proportions",
                    )
                    st.plotly_chart(fig_cat_pie, use_container_width=True)
                    st.markdown("---")
               
# TAB 5: Export Reports
            
                st.header("📤 Export Analysis Reports")

                # Ensure we have a cleaned version; fall back to original
                cleaned_df = st.session_state.get("cleaned_df", df)

                col1, col2 = st.columns(2)

                
                # -------- PDF Report --------
                with col1:
                    st.subheader("📄 PDF Report")
                    st.markdown("Generate a concise PDF report summarizing the EDA and data quality.")

                    
                # Create / reuse PDFReportGenerator
                    if st.button("📥 Generate PDF Report", type="primary", use_container_width=True):
                        with st.spinner("Generating PDF report..."):
                            try:
                                # pass df and eda as required by __init__
                                pdf_gen = PDFReportGenerator(df, eda)
                                pdf_buffer = pdf_gen.generate_report()

                                st.download_button(
                                label="📑 Download PDF Report",
                                data=pdf_buffer,
                    file_name=f"EDA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                )
                                st.success("✅ PDF report generated successfully!")
                            except Exception as e:
                              st.error(f"❌ Error generating PDF report: {str(e)}")
                              st.info("💡 Make sure PDFReportGenerator is properly configured.")


            

            
            
            
            
            
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Please ensure your file is a valid Excel or CSV file with proper formatting.")
            
            # Show detailed error for debugging
            with st.expander("🔍 Show detailed error"):
                st.code(str(e))
    
    else:
        # Landing page when no file is uploaded
        
        
        st.markdown("")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### 
            
            """)
        
        with col2:
            st.markdown("""
          
           
            """)
        
        with col3:
            st.markdown("""
           
            """)
        
    




# Add this to your main app navigation
def main():
    st.set_page_config(
        page_title="DiveIn AI - Data Analysis (EDA)",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Directly load the EDA analysis page
    eda_analysis_page()

    
   

def research_assistant_page():
    """Your existing research assistant functionality"""
    

    
    st.markdown("""
    ### Welcome! Let's turn curiosity into intelligence.
    
    #### What I do best:
    
    - 💡 Transform vague questions into structured, multi-source research
    - 🧠 Connect insights across academic papers, articles, and real-time data
    - 📊 Deliver executive-ready analysis, not just search results
    - ⚡ Generate research reports in seconds, not hours
    
    #### Let's dive in—what would you like to explore?
    """)
    
    # Your existing chat interface code here
    # ...

    
if __name__ == "__main__":
    main()

# ============================================================================
# CHAT HISTORY DISPLAY
# ============================================================================
# Show previous conversation
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================================
# CHAT INPUT AND DATASET-ONLY ANSWER
# ============================================================================
prompt = st.chat_input("Ask me anything about your uploaded dataset...", key="eda_chat")

if prompt:
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Analyzing your dataset and question..."):
            try:
                df = st.session_state.uploaded_data  # set this when file is loaded
                num_cols = df.select_dtypes(include=["number"]).columns.tolist()
                cat_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

                sample_rows = df.head(5).to_dict(orient="records")

                data_context = f"""
You are a senior data analyst and ML engineer.
You have access to a pandas DataFrame called df that represents the uploaded dataset.

Dataset summary:
- Shape: {df.shape[0]} rows × {df.shape[1]} columns
- Numeric columns: {num_cols}
- Categorical columns: {cat_cols}
- Column dtypes: {df.dtypes.to_dict()}
- First 5 rows (JSON): {json.dumps(sample_rows, default=str)[:4000]}
"""

                full_prompt = f"""{data_context}

User question:
{prompt}

Your task:
1. ALWAYS answer in the context of this dataset. Use column names and their types explicitly.
2. If the question is about data quality (e.g., missing values, outliers), explain:
   - How to detect them in this dataframe.
   - Concrete strategies that could be applied here (mean/median/mode, IQR capping, etc.).
3. If the question is about modeling (e.g., "build a model", "predict", "classification", "regression"):
   - Propose suitable targets and feature sets from the existing columns.
   - Suggest appropriate algorithms and preprocessing for THIS dataset.
   - Provide example Python code snippets using scikit‑learn that assume df is available.
4. If the question is vague, interpret it in the most useful way for this dataset and suggest next steps.
5. Do NOT say "the dataset does not contain information about X". Instead, infer what can be done with the available columns and describe a sensible approach.

Answer with clear sections and bullet points where helpful.
"""

                response = st.session_state.model.generate_content(full_prompt)
                answer = response.text
                st.markdown(answer)

                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(f"❌ Error: {e}")




        
                



# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 2rem 0; color: #666;'>
        <div style='font-size: 0.9rem; margin-bottom: 0.5rem;'>
            <span style='color: #d4af37; font-weight: 600;'>DiveIn AI</span> 
            <span style='color: #444;'>|</span> 
            Executive Research Engine
        </div>
        <div style='font-size: 0.85rem; color: #555;'>
        </div>
    </div>
""", unsafe_allow_html=True)

                 