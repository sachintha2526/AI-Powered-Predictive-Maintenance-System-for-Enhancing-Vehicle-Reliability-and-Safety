import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─── CSS ─────────────────────────────────────────────────────────────────────
REPORT_CSS = """
<style>
.report-header {
    background: #1e293b; border-bottom: 3px solid #38bdf8;
    padding: 2rem; text-align: center; border-radius: 12px 12px 0 0;
}
.report-section {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;
}
.report-label { font-size: 0.75rem; font-weight: 800; color: #475569; text-transform: uppercase; }
.report-value { font-size: 1.6rem; font-weight: 700; color: #38bdf8; }
</style>
"""

def show_report_generation(df, metrics):
    st.markdown(REPORT_CSS, unsafe_allow_html=True)

    # ── Header ──
    st.markdown(f"""
    <div class='report-header'>
        <div style='font-size: 2rem; font-weight: 800; color: #f1f5f9;'> Systems Diagnostic Report</div>
        <div style='color: #94a3b8; font-size: 0.9rem;'>Generated on: {datetime.now().strftime("%Y-%m-%d %I:%M %p")}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Executive Summary Metrics ──
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        total_v = len(df)
        st.markdown(f"<div class='report-section'><div class='report-label'>Fleet Size</div><div class='report-value'>{total_v}</div></div>", unsafe_allow_html=True)
    with m2:
        fault_rate = (df['Engine_Condition'] != 'Normal').mean()
        st.markdown(f"<div class='report-section'><div class='report-label'>Fault Rate</div><div class='report-value'>{fault_rate:.1%}</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='report-section'><div class='report-label'>Model Acc.</div><div class='report-value'>{metrics['accuracy']:.1%}</div></div>", unsafe_allow_html=True)
    with m4:
        st.markdown(f"<div class='report-section'><div class='report-label'>Criticals</div><div class='report-value' style='color:#ef4444'>{(df['Engine_Condition'] == 'Fault').sum()}</div></div>", unsafe_allow_html=True)

    # ── Analytics Row 1: Condition Distribution & Avg Readings ──
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### Engine Condition Distribution")
        fig_pie = px.pie(df, names='Engine_Condition', hole=.4,
                         color='Engine_Condition', 
                         color_discrete_map={'Normal': '#10b981', 'Warning': '#f59e0b', 'Fault': '#ef4444'})
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.markdown("#### Avg Sensor Values by Condition")
        # Extract numeric sensor columns dynamically for safety
        all_sensors = ['RPM', 'Oil_Pressure', 'Oil_Temperature', 'Coolant_Temperature', 'Fuel_Pressure']
        available_sensors = [c for c in all_sensors if c in df.columns]
        
        if not available_sensors:
            available_sensors = df.select_dtypes(include=['number']).columns.tolist()

        sensor_to_plot = st.selectbox("Select metric for analysis", available_sensors)
        avg_vals = df.groupby('Engine_Condition')[sensor_to_plot].mean().reset_index()
        fig_bar = px.bar(avg_vals, x='Engine_Condition', y=sensor_to_plot, 
                         color='Engine_Condition',
                         color_discrete_map={'Normal': '#10b981', 'Warning': '#f59e0b', 'Fault': '#ef4444'})
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Analytics Row 2: Sensor Trends ──
    st.markdown("---")
    st.markdown("#### Aggregate Sensor Trends")
    agg_df = df.reset_index().rename(columns={'index': 'Time Step'})
    fig_trend = px.line(agg_df, x='Time Step', y=sensor_to_plot, color='Engine_Condition',
                        title=f"{sensor_to_plot} Fluctuations over Diagnostic Period",
                        color_discrete_map={'Normal': '#10b981', 'Warning': '#f59e0b', 'Fault': '#ef4444'})
    fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
    st.plotly_chart(fig_trend, use_container_width=True)

    # ── Export Controls ──
    st.markdown("---")
    st.markdown("#### Export & Distribution")
    ec1, ec2 = st.columns(2)
    
    with ec1:
        st.download_button("Export as CSV Full Dataset",
                           df.to_csv(index=False).encode(),
                           "systems_report.csv", "text/csv", use_container_width=True)
    with ec2:
        st.download_button("Export as Excel Summary",
                           df.describe().to_csv().encode(),
                           "statistical_summary.csv", "text/csv", use_container_width=True)
