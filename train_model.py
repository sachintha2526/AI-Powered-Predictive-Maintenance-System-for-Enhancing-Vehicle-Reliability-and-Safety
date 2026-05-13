import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def generate_sample_data(n_samples=500):
    """
    Generates synthetic vehicle engine data for demonstration.
    """
    np.random.seed(42)
    
    # Normal operating conditions
    rpm_normal = np.random.normal(2500, 300, n_samples // 2)
    oil_pressure_normal = np.random.normal(50, 5, n_samples // 2) # PSI
    oil_temp_normal = np.random.normal(190, 10, n_samples // 2) # Fahrenheit
    coolant_temp_normal = np.random.normal(190, 10, n_samples // 2) # Fahrenheit
    fuel_pressure_normal = np.random.normal(45, 2, n_samples // 2) # PSI
    
    # Faulty conditions
    rpm_fault = np.random.normal(3500, 500, n_samples // 2)
    oil_pressure_fault = np.random.normal(25, 10, n_samples // 2) # Low oil pressure
    oil_temp_fault = np.random.normal(240, 20, n_samples // 2) # High oil temp
    coolant_temp_fault = np.random.normal(230, 20, n_samples // 2) # Overheating
    fuel_pressure_fault = np.random.normal(35, 10, n_samples // 2) # Irregular fuel pressure
    
    # Combine
    rpm = np.concatenate([rpm_normal, rpm_fault])
    oil_pressure = np.concatenate([oil_pressure_normal, oil_pressure_fault])
    oil_temp = np.concatenate([oil_temp_normal, oil_temp_fault])
    coolant_temp = np.concatenate([coolant_temp_normal, coolant_temp_fault])
    fuel_pressure = np.concatenate([fuel_pressure_normal, fuel_pressure_fault])
    
    # Create DataFrame
    df = pd.DataFrame({
        'RPM': rpm,
        'Oil_Pressure': oil_pressure,
        'Oil_Temperature': oil_temp,
        'Coolant_Temperature': coolant_temp,
        'Fuel_Pressure': fuel_pressure
    })
    
    # Assign labels
    conditions = []
    for i in range(n_samples):
        if (df['Oil_Pressure'].iloc[i] < 30) or (df['Coolant_Temperature'].iloc[i] > 220):
            conditions.append('Fault')
        elif (df['Oil_Pressure'].iloc[i] < 40) or (df['Coolant_Temperature'].iloc[i] > 210):
            conditions.append('Warning')
        else:
            conditions.append('Normal')
            
    df['Engine_Condition'] = conditions
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df

def preprocess_data(df):
    # Standardize column mappings so various uploaded datasets resolve to identical features
    rename_map = {
        'Engine rpm': 'RPM', 'engine_rpm': 'RPM',
        'Lub oil pressure': 'Oil_Pressure', 'lub_oil_pressure': 'Oil_Pressure',
        'Lub oil temp': 'Oil_Temperature', 'lub_oil_temperature': 'Oil_Temperature', 'Oil temp': 'Oil_Temperature',
        'Coolant temp': 'Coolant_Temperature', 'coolant_temperature': 'Coolant_Temperature',
        'Coolant pressure': 'Coolant_Pressure', 'coolant_pressure': 'Coolant_Pressure',
        'Fuel pressure': 'Fuel_Pressure', 'fuel_pressure': 'Fuel_Pressure',
        'Engine Condition': 'Engine_Condition', 'engine_condition': 'Engine_Condition'
    }
    df = df.rename(columns=rename_map)
    df = df.dropna()
    return df

def detect_anomalies(df):
    """
    Detects anomalies using Isolation Forest on numerical features.
    Returns the dataframe with Anomaly_Score and Anomaly_Status columns.
    """
    df_numeric = df.select_dtypes(include=[np.number])
    if df_numeric.empty:
        return df
        
    iso = IsolationForest(contamination=0.05, random_state=42)
    preds = iso.fit_predict(df_numeric)
    scores = iso.decision_function(df_numeric)
    
    df_out = df.copy()
    df_out['Anomaly_Score'] = scores
    df_out['Anomaly_Status'] = ['Anomaly' if p == -1 else 'Normal' for p in preds]
    return df_out

def train_model(df):
    X = df.drop(columns=['Engine_Condition'], errors='ignore')
    X = X.select_dtypes(include=[np.number])
    y = df['Engine_Condition']
    
    # Split data to evaluate the model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Calculate evaluation metrics
    y_pred = model.predict(X_test_scaled)
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
        'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
        'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0),
        'conf_matrix': confusion_matrix(y_test, y_pred, labels=model.classes_),
        'classes': model.classes_,
        'feature_names': list(X_train.columns)
    }
    
    return model, scaler, metrics

def predict_condition(model, scaler, input_data):
    input_scaled = scaler.transform(input_data)
    prediction = model.predict(input_scaled)
    probabilities = model.predict_proba(input_scaled)
    classes = model.classes_
    return prediction, probabilities, classes
