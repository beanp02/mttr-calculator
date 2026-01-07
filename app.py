import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os  

# --- 1. NEW SECURE GATEKEEPER ---
def check_password():
    """Returns True if the user had the correct password."""
    # Initialize state
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # If already logged in, just return True
    if st.session_state["password_correct"]:
        return True

    # Show login form
    st.title("🔐 Secure Access Required")
    password_input = st.text_input("Enter Access Password", type="password")
    
    if password_input:
        # Get correct password from ENV or Fallback
        correct_pw = os.getenv("APP_PASSWORD", "TemporaryFallback123").strip()
        
        if password_input.strip() == correct_pw:
            st.session_state["password_correct"] = True
            st.rerun() # Refresh the page to show the dashboard
        else:
            st.error("😕 Password incorrect")
            
    return False

if not check_password():
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(page_title="ServiceNow MTTR Dashboard", layout="wide")

# --- CUSTOM CSS FOR BUTTONS ---
st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 100px;
        width: 100%;
        font-size: 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE FOR NAVIGATION ---
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = None

# --- MAPPING CONFIGURATION ---
# This dictionary maps your selection to the expected Excel column names
CONFIG = {
    "Incident": {"start": "Created", "end": "Resolved at", "icon": "🚨"},
    "Request": {"start": "Created", "end": "Closed", "icon": "📦"},
    "Change": {"start": "Actual start date", "end": "Actual end date", "icon": "⚙️"},
    "Feedback": {"start": "Start", "end": "End", "icon": "💬"},
    "Survey": {"start": "Taken on", "end": "Action completed", "icon": "📝"}
}

# --- BUSINESS LOGIC FUNCTION ---
def calculate_mttr_data(df, start_col, end_col):
    df[start_col] = pd.to_datetime(df[start_col], errors='coerce')
    df[end_col] = pd.to_datetime(df[end_col], errors='coerce')
    
    # Clean invalid rows
    clean_df = df.dropna(subset=[start_col, end_col]).copy()
    
    def apply_8hr_logic(row):
        duration = row[end_col] - row[start_col]
        total_hours = (duration.days * 24) + (duration.seconds / 3600)
        days = total_hours // 24
        if (total_hours % 24) > 8:
            days += 1
        return max(0, days)

    clean_df['Calculated_Days'] = clean_df.apply(apply_8hr_logic, axis=1)
    # Also keep raw hours for the trendline
    clean_df['Raw_Hours'] = (clean_df[end_col] - clean_df[start_col]).dt.total_seconds() / 3600
    
    return clean_df

# --- UI: LANDING PAGE ---
if st.session_state.app_mode is None:
    st.title("What MTTR are you calculating today?")
    st.write("Select a category to begin your analysis.")
    
    cols = st.columns(5)
    categories = list(CONFIG.keys())
    
    for i, cat in enumerate(categories):
        if cols[i].button(f"{CONFIG[cat]['icon']}\n{cat}"):
            st.session_state.app_mode = cat
            st.rerun()

# --- UI: ANALYSIS PAGE ---
else:
    mode = st.session_state.app_mode
    st.button("← Back to Selection", on_click=lambda: st.session_state.update({"app_mode": None}))
    
    st.title(f"{CONFIG[mode]['icon']} {mode} MTTR Calculator")
    
    uploaded_file = st.file_uploader(f"Upload {mode} Excel File", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            cols = df.columns.tolist()
            
            # Auto-detect headers from config
            expected_start = CONFIG[mode]['start']
            expected_end = CONFIG[mode]['end']
            
            # Allow manual override if headers don't match exactly
            with st.expander("Column Mapping (Adjust if needed)"):
                start_col = st.selectbox("Start Date Column", cols, index=cols.index(expected_start) if expected_start in cols else 0)
                end_col = st.selectbox("End Date Column", cols, index=cols.index(expected_end) if expected_end in cols else 0)

            if st.button("Generate Report"):
                processed_df = calculate_mttr_data(df, start_col, end_col)
                
                if not processed_df.empty:
                    # Metrics
                    avg_days = processed_df['Calculated_Days'].mean()
                    m1, m2 = st.columns(2)
                    m1.metric(f"Mean Time To Resolve ({mode})", f"{avg_days:.2f} Days")
                    m2.metric("Total Records", len(processed_df))
                    
                    # Trendline
                    st.subheader(f"📈 {mode} Resolution Trend")
                    processed_df = processed_df.sort_values(start_col)
                    fig = px.line(
                        processed_df, 
                        x=start_col, 
                        y='Raw_Hours',
                        title=f"Resolution Time (Hours) over Time",
                        labels={start_col: 'Date Created/Started', 'Raw_Hours': 'Hours to Resolve'},
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Data Preview
                    with st.expander("View Calculation Details"):
                        st.dataframe(processed_df[[start_col, end_col, 'Calculated_Days']])
                        
                else:
                    st.error("No valid date data found in the selected columns.")
        except Exception as e:
            st.error(f"Error: {e}. Please ensure the Excel file matches the {mode} format.")

