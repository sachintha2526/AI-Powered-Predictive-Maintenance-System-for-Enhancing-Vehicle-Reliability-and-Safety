import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from train_model import generate_sample_data, preprocess_data, train_model, predict_condition, detect_anomalies
from login import show_login_page, ROLE_PERMISSIONS
from admin_dashboard import show_admin_dashboard
from payment_page import show_payment_page
from service_booking import show_service_booking
from fleet_manager_dashboard import show_manager_dashboard
from engineer_dashboard import show_engineer_dashboard
from technician_dashboard import show_technician_dashboard

st.set_page_config(page_title="AI Predictive Maintenance", page_icon="", layout="wide")

# ─── Auth Gate ───────────────────────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login_page()
    st.stop()

# ─── Route Admin to Admin Dashboard ──────────────────────────────────────────
if st.session_state.get('role') == 'Admin':
    show_admin_dashboard()
    st.stop()

# ─── Route Manager to Fleet Manager Dashboard ────────────────────────────────
if st.session_state.get('role') == 'Manager':
    show_manager_dashboard()
    st.stop()

# ─── Route Technician to Technician Dashboard ────────────────────────────────
if st.session_state.get('role') == 'Technician':
    show_technician_dashboard()
    st.stop()

# ─── Sidebar: User Badge + Logout (for roles without specialized dashboards) ───
if st.session_state.get('role') not in ['Admin', 'Manager', 'Engineer', 'Technician']:
    role      = st.session_state.get('role', 'User')
    username  = st.session_state.get('username', 'user')
    role_info = ROLE_PERMISSIONS.get(role, {'icon': '👤', 'color': '#94a3b8', 'description': 'System User'})
    
    st.sidebar.markdown(f"""
    <div style='background:linear-gradient(135deg,#1e293b,#0f172a);
                border:1px solid #334155; border-radius:12px;
                padding:.9rem 1rem; margin-bottom:1rem;'>
        <div style='font-size:1.5rem'>{role_info['icon']}</div>
        <div style='font-weight:700; color:#f1f5f9; font-size:.95rem'>{username.capitalize()}</div>
        <div style='font-size:.75rem; color:{role_info["color"]}; font-weight:600'>{role}</div>
        <div style='font-size:.7rem; color:#94a3b8; margin-top:.3rem'>{role_info["description"]}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Back to Login / Logout", key="app_logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.title("AI-Powered Predictive Maintenance System for Enhancing Vehicle Reliability and Safety")
st.markdown("Monitor vehicle health and predict faults using AI.")

st.sidebar.header("Configuration")
data_source = st.sidebar.radio("Data Source", ["Use Sample Data", "Upload CSV"])

if 'model' not in st.session_state:
    st.session_state.model = None
if 'scaler' not in st.session_state:
    st.session_state.scaler = None

df = None
if data_source == "Use Sample Data":
    df = generate_sample_data(n_samples=500)
    st.sidebar.success("Loaded Sample Data")
else:
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("Uploaded Successfully")

if df is not None:
    df = preprocess_data(df)
    
    # Calculate anomaly scores for the dataset
    df_with_anomalies = detect_anomalies(df)
    
    if 'Engine_Condition' in df.columns:
        model, scaler, metrics = train_model(df)
        st.session_state.model = model
        st.session_state.scaler = scaler
        st.session_state.metrics = metrics
        st.sidebar.info("Model Trained")
        st.session_state.df_with_anomalies = df_with_anomalies

    # ─── Route Engineer to Technical Dashboard ──────────────────────────────
    if st.session_state.get('role') == 'Engineer':
        show_engineer_dashboard(df, st.session_state.model, st.session_state.scaler, st.session_state.metrics)
        st.stop()

    # ─── Default Dashboard (for any roles not routed above) ───────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Sensor Data", "Visuals", "AI Prediction", "Model Performance", "💳 Payments", "📅 Booking"])
    
    with tab1:
        st.subheader("Dataset Overview & Anomaly Detection")
        
        col1, col2 = st.columns(2)
        col1.metric("Total Records", len(df_with_anomalies))
        
        anomaly_count = (df_with_anomalies['Anomaly_Status'] == 'Anomaly').sum()
        col2.metric("Total Anomalies Detected", anomaly_count, help="Anomalies flagged using Isolation Forest")
        
        st.markdown("### Data View")
        view_mode = st.radio("Filter Data:", ["All Data", "Anomalies Only", "Normal Only"], horizontal=True)
        
        display_df = df_with_anomalies
        if view_mode == "Anomalies Only":
            display_df = df_with_anomalies[df_with_anomalies['Anomaly_Status'] == 'Anomaly']
        elif view_mode == "Normal Only":
            display_df = df_with_anomalies[df_with_anomalies['Anomaly_Status'] == 'Normal']
            
        def highlight_anomalies(val):
            return 'background-color: #ff4b4b; color: white' if val == 'Anomaly' else ''
            
        st.dataframe(display_df.style.map(highlight_anomalies, subset=['Anomaly_Status']), use_container_width=True)
        
    with tab2:
        st.subheader("Sensor Trend Analysis")
        sensors = [c for c in df.columns if c != 'Engine_Condition']
        sel = st.selectbox("Select Sensor", sensors)
        st.plotly_chart(px.line(df.reset_index(), x=df.index, y=sel, title=f"{sel} Trend"), use_container_width=True)
        
        st.divider()
        st.subheader("Sensor Correlation Heatmap")
        st.markdown("Displays the linear relationship between different numeric sensors.")
        
        # Calculate correlation matrix
        corr_matrix = df.corr(numeric_only=True)
        
        # Generate heatmap using Seaborn
        fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax_corr, 
                    linewidths=0.5, cbar_kws={"shrink": .8})
        plt.title("Correlation Heatmap of Sensor Data")
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        st.pyplot(fig_corr)
        
    with tab3:
        if st.session_state.model:
            st.write("Adjust the parameters to simulate a reading:")
            
            # dynamically create sliders based on the features the model actually trained on
            feature_cols = st.session_state.metrics['feature_names']
            
            input_dict = {}
            cols = st.columns(3)
            for idx, col_name in enumerate(feature_cols):
                if col_name in df.columns:
                    col_min = int(df[col_name].min())
                    col_max = int(df[col_name].max())
                    col_mean = int(df[col_name].mean())
                else:
                    col_min, col_max, col_mean = 0.0, 1000.0, 50.0
                    
                if col_min == col_max:
                    col_min, col_max = 0.0, col_max + 10.0
                
                with cols[idx % 3]:
                    val = st.slider(col_name, min_value=col_min, max_value=col_max, value=col_mean)
                    input_dict[col_name] = [val]

            if st.button("Predict"):
                input_data = pd.DataFrame(input_dict)
                # Ensure input exactly matches training feature order
                input_data = input_data[feature_cols]
                pred, prob, classes = predict_condition(st.session_state.model, st.session_state.scaler, input_data)
                
                if pred[0] == "Normal": 
                    st.success("✅ **Status: Normal** - Engine is operating within optimal parameters.")
                elif pred[0] == "Warning": 
                    st.warning("⚠️ **Status: Warning** - Suboptimal conditions detected. Check readings closely.")
                else: 
                    st.error("🚨 **Status: Fault** - Critical conditions detected! Immediate maintenance recommended.")
                
                # Calculate and display Failure Risk
                # Calculate and display Failure Risk regardless of specific class naming conventions
                fault_prob = 0.0
                if 'Normal' in classes:
                    normal_idx = list(classes).index('Normal')
                    fault_prob = 1.0 - float(prob[0][normal_idx])
                elif 'Fault' in classes:
                    fault_idx = list(classes).index('Fault')
                    fault_prob = float(prob[0][fault_idx])
                elif len(classes) > 1:
                    fault_prob = float(prob[0][-1])
                    
                st.metric("Failure Risk (Risk of non-Normal state)", f"{fault_prob:.0%}")
                
                # Visual Risk Gauges
                if fault_prob < 0.4:
                    st.success(f"🟢 **Low Risk Level:** {fault_prob:.0%} confidence of failure.")
                elif fault_prob < 0.75:
                    st.warning(f"🟡 **Medium Risk Level:** {fault_prob:.0%} confidence of failure.")
                else:
                    st.error(f"🔴 **High Risk Level:** {fault_prob:.0%} confidence of failure.")
                    
                st.progress(fault_prob)
                st.divider()
                
                st.bar_chart(pd.DataFrame(prob, columns=classes).T)
                
                # Check for feature importances and display plot if available
                if hasattr(st.session_state.model, 'feature_importances_'):
                    st.divider()
                    st.subheader("Model Feature Importance")
                    feature_names = input_data.columns
                    importances = st.session_state.model.feature_importances_
                    
                    # Create DataFrame and sort
                    imp_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
                    imp_df = imp_df.sort_values(by='Importance', ascending=True)
                    
                    # Create plotly bar chart
                    fig_imp = px.bar(imp_df, x='Importance', y='Feature', orientation='h',
                                     title='Which sensors matter most for this prediction?',
                                     color='Importance',
                                     color_continuous_scale=px.colors.sequential.Teal)
                    st.plotly_chart(fig_imp, use_container_width=True)
                    
            st.divider()
            st.subheader("Batch Dataset Predictions")
            st.markdown("Run the AI model across the entire loaded dataset and export the results.")
            
            # Predict over the entire original datast
            features_df = df.drop(columns=['Engine_Condition'], errors='ignore')
            feature_cols = st.session_state.metrics['feature_names']
            
            # Ensure all required columns exist and match order
            for mc in feature_cols:
                if mc not in features_df.columns:
                    features_df[mc] = 0.0
                    
            features_df = features_df[feature_cols]
            batch_preds, _, _ = predict_condition(st.session_state.model, st.session_state.scaler, features_df)
            
            # Form final output by binding predictions to features
            out_df = features_df.copy()
            out_df['Predicted_Condition'] = batch_preds
            
            st.write("Preview of the Augmented Dataset:")
            st.dataframe(out_df.head(), use_container_width=True)
            
            # Convert to CSV and create Download Button
            @st.cache_data
            def convert_df(df_to_convert):
                return df_to_convert.to_csv(index=False).encode('utf-8')
                
            csv_export = convert_df(out_df)
            
            st.download_button(
                label="Download Predictions as CSV",
                data=csv_export,
                file_name="engine_predictive_maintenance_results.csv",
                mime="text/csv",
            )
            
        else:
            st.warning("Model not trained.")
            
    with tab4:
        if 'metrics' in st.session_state and st.session_state.metrics:
            st.subheader("Model Evaluation Metrics")
            metrics = st.session_state.metrics
            
            # Display metrics as KPIs
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Accuracy", f"{metrics['accuracy']:.1%}")
            c2.metric("Precision", f"{metrics['precision']:.1%}")
            c3.metric("Recall", f"{metrics['recall']:.1%}")
            c4.metric("F1-Score", f"{metrics['f1']:.1%}")
            
            st.divider()
            st.subheader("Confusion Matrix")
            st.markdown("Shows how many predictions were correct vs. incorrect for each health condition.")
            
            # Display Confusion Matrix Heatmap
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(metrics['conf_matrix'], annot=True, fmt='d', cmap='Blues',
                        xticklabels=metrics['classes'], yticklabels=metrics['classes'], ax=ax)
            plt.ylabel('Actual Condition')
            plt.xlabel('Predicted Condition')
            # Adjust layout
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("Metrics not available. Model needs to be trained on data with 'Engine_Condition'.")

    with tab5:
        show_payment_page()

    with tab6:
        show_service_booking()
