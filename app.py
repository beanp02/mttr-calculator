import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os
import warnings
from datetime import timedelta

# Silence the openpyxl style warning in logs
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# --- 1. SECURE GATEKEEPER ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True
    st.title("🔐 Secure Access Required")
    password_input = st.text_input("Enter Access Password", type="password")
    if password_input:
        correct_pw = os.getenv("APP_PASSWORD", "TemporaryFallback123").strip()
        if password_input.strip() == correct_pw:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("😕 Password incorrect")
    return False

# --- PAGE CONFIG ---
st.set_page_config(page_title="ServiceNow MTTR Dashboard", layout="wide")

st.markdown("""
    <style>
    .stButton > button { height: 60px; width: 100%; font-size: 18px; font-weight: bold; background-color: #007bff; color: white; border-radius: 8px; }
    .summary-card { padding: 25px; border-radius: 12px; border: 2px solid #007bff; background-color: rgba(128, 128, 128, 0.05); margin-bottom: 25px; }
    .metric-line { font-size: 1.25rem; margin-bottom: 12px; }
    </style>
""", unsafe_allow_html=True)

def calculate_mttr_data(df, start_col, end_col):
    df[start_col] = pd.to_datetime(df[start_col], errors='coerce')
    df[end_col] = pd.to_datetime(df[end_col], errors='coerce')
    clean_df = df.dropna(subset=[start_col, end_col]).copy()
    
    def apply_8hr_logic(row):
        duration = row[end_col] - row[start_col]
        total_hours = (duration.days * 24) + (duration.seconds / 3600)
        days = total_hours // 24
        if (total_hours % 24) > 8: days += 1
        return max(0, days)

    clean_df['Calculated_Days'] = clean_df.apply(apply_8hr_logic, axis=1)
    return clean_df

if check_password():
    CONFIG = {
        "Incident": {"start": "Created", "end": "Resolved at", "icon": "🚨"},
        "Request": {"start": "Created", "end": "Closed", "icon": "📦"},
        "Change": {"start": "Actual start date", "end": "Actual end date", "icon": "⚙️"},
        "Feedback": {"start": "Start", "end": "End", "icon": "💬"},
        "Survey": {"start": "Taken on", "end": "Action completed", "icon": "📝"}
    }

    if 'app_mode' not in st.session_state:
        st.session_state.app_mode = None

    if st.session_state.app_mode is None:
        st.title("What MTTR are you calculating today?")
        cols = st.columns(5)
        for i, cat in enumerate(CONFIG.keys()):
            if cols[i].button(f"{CONFIG[cat]['icon']}\n{cat}"):
                st.session_state.app_mode = cat
                st.rerun()
    else:
        mode = st.session_state.app_mode
        st.button("← Back to Selection", on_click=lambda: st.session_state.update({"app_mode": None, "processed_df": None}))
        st.title(f"{CONFIG[mode]['icon']} {mode} Analysis")
        
        uploaded_file = st.file_uploader(f"Upload {mode} File", type=["xlsx"])

        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            
            with st.expander("Column Mapping Settings"):
                start_col = st.selectbox("Start Date Column", df.columns, index=df.columns.get_loc(CONFIG[mode]['start']) if CONFIG[mode]['start'] in df.columns else 0)
                end_col = st.selectbox("End Date Column", df.columns, index=df.columns.get_loc(CONFIG[mode]['end']) if CONFIG[mode]['end'] in df.columns else 0)
                grp_kw = ['assignment group', 'workgroup', 'issue owner', 'group', 'definition', 'assigned to', 'department']
                found_grp = next((c for c in df.columns if any(kw in c.lower() for kw in grp_kw)), df.columns[0])
                actual_grp_col = st.selectbox("Group/Category Column", df.columns, index=df.columns.get_loc(found_grp))

            c1, c2 = st.columns(2)
            with c1:
                time_filter = st.selectbox("Timeframe", ["All Data", "Today", "Yesterday", "Last 7 Days", "Last 30 Days", "Last 90 Days"])
            with c2:
                kpi_target = st.number_input("KPI Target (Days)", min_value=1, value=5)

            if st.button("🚀 UPDATE REPORT"):
                df[start_col] = pd.to_datetime(df[start_col], errors='coerce')
                ref_date = df[start_col].max()
                f_df = df.copy()
                if time_filter != "All Data":
                    days_map = {"Today": 0, "Yesterday": 1, "Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
                    cutoff = ref_date - timedelta(days=days_map[time_filter])
                    f_df = df[df[start_col] >= cutoff] if time_filter != "Yesterday" else df[df[start_col].dt.date == cutoff.date()]
                st.session_state.processed_df = calculate_mttr_data(f_df, start_col, end_col)
                st.session_state.current_period = time_filter
                st.session_state.mapped_grp = actual_grp_col

            if st.session_state.get("processed_df") is not None:
                res = st.session_state.processed_df
                actual_grp = st.session_state.mapped_grp
                
                if not res.empty:
                    avg_val = res['Calculated_Days'].mean()
                    total = len(res)
                    perf_pct = (len(res[res['Calculated_Days'] <= kpi_target]) / total) * 100
                    id_kw = ['id', 'number', 'incident id', 'task', 'inc #', 'sys_id']
                    actual_id = next((c for c in res.columns if any(kw in c.lower() for kw in id_kw)), res.columns[0])
                    
                    if actual_grp in res.columns:
                        stats = res.groupby(actual_grp)['Calculated_Days'].agg(['mean','count']).rename(columns={'mean': 'Avg Days', 'count': 'Volume'})
                        slow_gs = stats.round(0).astype(int).sort_values('Avg Days', ascending=False).head(5)
                        min_vol = 3
                        fast_gs = stats[stats['Volume'] >= min_vol].round(0).astype(int).sort_values('Avg Days', ascending=True).head(5)
                        if fast_gs.empty: fast_gs = stats.round(0).astype(int).sort_values('Avg Days', ascending=True).head(5)
                        slowest_name = slow_gs.index[0] if not slow_gs.empty else "N/A"
                    else:
                        slow_gs, fast_gs, slowest_name = pd.DataFrame(), pd.DataFrame(), "N/A"

                    st.markdown(f"""<div class="summary-card"><h2>📊 Overview: {st.session_state.current_period}</h2><div class="metric-line">✅ <b>SLA Compliance:</b> {perf_pct:.1f}%</div><div class="metric-line">⏱️ <b>Avg MTTR:</b> {int(round(avg_val))} Days</div><div class="metric-line">⚠️ <b>Bottleneck:</b> {slowest_name}</div></div>""", unsafe_allow_html=True)

                    status_label = "ON TARGET" if avg_val <= kpi_target else "ABOVE TARGET"
                    status_color = "#28a745" if avg_val <= kpi_target else "#dc3545"
                    
                    bottleneck_rows = "".join([f"<tr><td style='text-align:left;'>{n}</td><td>{int(r['Avg Days'])}</td><td>{int(r['Volume'])}</td></tr>" for n, r in slow_gs.iterrows()]) if not slow_gs.empty else "<tr><td colspan='3'>No data</td></tr>"
                    performer_rows = "".join([f"<tr><td style='text-align:left;'>{n}</td><td>{int(r['Avg Days'])}</td><td>{int(r['Volume'])}</td></tr>" for n, r in fast_gs.iterrows()]) if not fast_gs.empty else "<tr><td colspan='3'>No data</td></tr>"

                    trend_data = res.sort_values(start_col)['Calculated_Days'].tolist()
                    points = "".join([f"{(i * 40) + 10},{150 - (min(val, 14) * 10)} " for i, val in enumerate(trend_data[-20:])])
                    target_y = 150 - (min(kpi_target, 14) * 10)

                    report_html = f"""<html><head><style>body {{ font-family: Arial, sans-serif; padding: 40px; max-width: 900px; margin: auto; }} .badge {{ background: {status_color}; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; }} .card-container {{ display: flex; gap: 15px; margin: 25px 0; }} .card {{ flex: 1; background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #ddd; text-align: center; }} table {{ border-collapse: collapse; width: 100%; margin: 20px 0; table-layout: fixed; }} th, td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }} .red-th {{ background: #dc3545; color: white; }} .green-th {{ background: #28a745; color: white; }}</style></head><body><h1>{mode} Performance Report <span class="badge">{status_label}</span></h1><div class="card-container"><div class="card"><h2>{perf_pct:.1f}%</h2><p>Compliance</p></div><div class="card"><h2>{int(round(avg_val))}</h2><p>Avg Days</p></div><div class="card"><h2>{total}</h2><p>Volume</p></div></div><h2>📈 Performance Trend</h2><svg width="800" height="180" style="background:#fff; border:1px solid #eee;"><line x1="0" y1="{target_y}" x2="800" y2="{target_y}" stroke="red" stroke-width="2" stroke-dasharray="5,5" /><polyline fill="none" stroke="#007bff" stroke-width="3" points="{points}" /></svg><h2 style="color:#dc3545;">🚨 Slowest Performers</h2><table><colgroup><col style="width: 60%;"><col style="width: 20%;"><col style="width: 20%;"></colgroup><tr class="red-th"><th style="text-align:left;">Group Name</th><th>Avg Days</th><th>Volume</th></tr>{bottleneck_rows}</table><h2 style="color:#28a745;">⭐ Best Performers</h2><table><colgroup><col style="width: 60%;"><col style="width: 20%;"><col style="width: 20%;"></colgroup><tr class="green-th"><th style="text-align:left;">Group Name</th><th>Avg Days</th><th>Volume</th></tr>{performer_rows}</table></body></html>"""

                    st.download_button("📥 Download Executive Report", data=report_html, file_name=f"{mode}_Report.html", mime="text/html")
                    
                    c_slow, c_fast = st.columns(2)
                    with c_slow:
                        st.subheader("🚨 Slowest Groups")
                        st.dataframe(slow_gs, width="stretch") # FIX
                    with c_fast:
                        st.subheader("⭐ Best Performers")
                        st.dataframe(fast_gs, width="stretch") # FIX
                    
                    st.subheader("📈 Investigative Trend Map")
                    fig = px.line(res.sort_values(start_col), x=start_col, y='Calculated_Days', markers=True, hover_data=[actual_id, actual_grp], labels={'Calculated_Days': 'Resolution Time (Days)', start_col: 'Date Created'}, title="Resolution Timeline (Days) vs. KPI Target")
                    fig.add_scatter(x=[res[start_col].min(), res[start_col].max()], y=[kpi_target, kpi_target], mode="lines", line=dict(color="red", dash="dash"), name=f"KPI Target ({kpi_target} Days)")
                    fig.update_layout(showlegend=True, legend_title_text='Metrics')
                    st.plotly_chart(fig, width="stretch") # FIX
                    
                    st.subheader("📄 Raw Calculation Data")
                    st.dataframe(res, width="stretch") # FIX
