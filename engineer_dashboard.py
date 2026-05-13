import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from train_model import predict_condition
from notifications import show_alerts_panel

# ─── CSS ─────────────────────────────────────────────────────────────────────
ENG_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700;800&display=swap');

.eng-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.eng-label { font-size: 0.7rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.8px; }
.eng-value { font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 700; color: #38bdf8; }

/* ── Metrics ── */
.metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.metric-item { flex: 1; border-left: 2px solid #38bdf8; padding-left: 0.8rem; }

/* ── Section Title ── */
.sec-title {
    font-size: 0.9rem; font-weight: 800; color: #f1f5f9;
    background: #1e293b; padding: 0.5rem 1rem; border-radius: 6px;
    margin: 1.5rem 0 1rem; display: flex; align-items: center; gap: 0.5rem;
}
</style>
"""

def show_engineer_dashboard(df, model, scaler, metrics):
    if df is None or model is None:
        st.warning("Please load or generate data first.")
        return

    st.markdown(ENG_CSS, unsafe_allow_html=True)
    
    # ── Sidebar Navigation ────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:1rem 0;'>
            <div style='font-size:2.5rem'></div>
            <div style='font-weight:800;font-size:1.1rem;color:#f1f5f9;'>Automotive Engineer</div>
            <div style='font-size:0.7rem;color:#475569;font-family:monospace;'>Diagnostic Console v2.4</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        if st.button("Back to Login / Logout", key="engineer_logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # ── Top Diagnostic Metrics ───────────────────────────────────────────────
    st.markdown("<div class='sec-title'> AI Model Performance & Diagnostics</div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"<div class='metric-item'><div class='eng-label'>Accuracy</div><div class='eng-value'>{metrics['accuracy']:.2%}</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-item'><div class='eng-label'>F1-Score</div><div class='eng-value'>{metrics['f1']:.2%}</div></div>", unsafe_allow_html=True)
    with m3:
        n_anom = (st.session_state.df_with_anomalies['Anomaly_Status'] == 'Anomaly').sum() if 'df_with_anomalies' in st.session_state else 0
        st.markdown(f"<div class='metric-item'><div class='eng-label'>Anomaly Freq</div><div class='eng-value'>{n_anom} events</div></div>", unsafe_allow_html=True)
    with m4:
        st.markdown(f"<div class='metric-item'><div class='eng-label'>Active Features</div><div class='eng-value'>{len(metrics['feature_names'])}</div></div>", unsafe_allow_html=True)

    # ── Feature Importance & Heatmap ──────────────────────────────────────────
    c1, c2 = st.columns([3, 2])
    
    with c1:
        st.markdown("<div class='sec-title'> Feature Importance Analysis</div>", unsafe_allow_html=True)
        feat_imp = pd.Series(model.feature_importances_, index=metrics['feature_names']).sort_values(ascending=True)
        fig_imp = px.bar(x=feat_imp.values, y=feat_imp.index, orientation='h', 
                         color=feat_imp.values, color_continuous_scale='Blues')
        fig_imp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8",
                               xaxis_title="Importance Weight", yaxis_title="")
        st.plotly_chart(fig_imp, use_container_width=True)

    with c2:
        st.markdown("<div class='sec-title'> Sensor Correlation</div>", unsafe_allow_html=True)
        df_num = df.select_dtypes(include=[np.number])
        fig_corr, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(df_num.corr(), annot=True, cmap='RdBu_r', center=0, ax=ax, cbar=False, annot_kws={"size": 8})
        fig_corr.patch.set_facecolor('none')
        ax.set_facecolor('none')
        plt.xticks(fontsize=8, rotation=45)
        plt.yticks(fontsize=8)
        st.pyplot(fig_corr)

    # ── Sensor Trends & Anomalies ────────────────────────────────────────────
    st.markdown("<div class='sec-title'> Real-time Sensor Decomposition</div>", unsafe_allow_html=True)
    selected_sensor = st.selectbox("Select Sensor for In-depth Analysis", metrics['feature_names'])
    
    fig_trend = px.line(df.reset_index(), x='index', y=selected_sensor, title=f"{selected_sensor} Trend Analysis")
    # Highlight anomalies if available
    if 'df_with_anomalies' in st.session_state:
        anom_df = st.session_state.df_with_anomalies[st.session_state.df_with_anomalies['Anomaly_Status'] == 'Anomaly']
        fig_trend.add_scatter(x=anom_df.index, y=anom_df[selected_sensor], mode='markers', 
                               marker=dict(color='red', size=8), name='Anomalies')
    
    fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
    st.plotly_chart(fig_trend, use_container_width=True)

    # ── Simulation Lab ────────────────────────────────────────────────────────
    st.markdown("<div class='sec-title'> Systems Simulation Lab (What-if Analysis)</div>", unsafe_allow_html=True)
    input_dict = {}
    cols = st.columns(3)
    for idx, col_name in enumerate(metrics['feature_names']):
        col_min = int(df[col_name].min())
        col_max = int(df[col_name].max())
        col_mean = int(df[col_name].mean())
        with cols[idx % 3]:
            val = st.slider(f"Simulate {col_name}", min_value=col_min, max_value=col_max, value=col_mean)
            input_dict[col_name] = [val]
    
    if st.button("🔌 Compute Simulation Predicton", use_container_width=True):
        input_data = pd.DataFrame(input_dict)[metrics['feature_names']]
        pred, prob, classes = predict_condition(model, scaler, input_data)
        
        c3, c4 = st.columns([1, 2])
        with c3:
            st.metric("Simulated Status", pred[0])
            st.progress(max(prob[0]))
        with c4:
            prob_df = pd.DataFrame({'Class': classes, 'Probability': prob[0]})
            st.bar_chart(prob_df.set_index('Class'))


    # ── Alerts Section ────────────────────────────────────────────────────────
    st.markdown("<div class='sec-title'> Active Diagnosed Faults</div>", unsafe_allow_html=True)
    show_alerts_panel(compact=True)

    # ── Data Registry ────────────────────────────────────────────────────────
    st.markdown("<div class='sec-title'> High-Density Data Registry</div>", unsafe_allow_html=True)
    st.dataframe(df.style.background_gradient(cmap='Blues'), use_container_width=True)
