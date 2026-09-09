import os
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

def generate_synthetic_training_data(n_samples=1000):
    """
    Generates synthetic feature table based on historical monsoon landslide data for NER corridors:
    - rainfall_24h (mm)
    - slope_deg
    - soil_saturation (%)
    - historical_incident_count
    - road_class_code (1=NH, 2=SH, 3=District)
    - Target: disruption_occurred (0 or 1)
    """
    np.random.seed(42)
    rainfall = np.random.exponential(scale=35.0, size=n_samples)
    slope = np.random.uniform(5.0, 45.0, size=n_samples)
    saturation = np.minimum(100.0, rainfall * 0.8 + np.random.normal(20, 10, size=n_samples))
    incidents = np.random.poisson(lam=1.5, size=n_samples)
    road_class = np.random.choice([1, 2, 3], size=n_samples, p=[0.5, 0.3, 0.2])

    # Logit probability equation simulating slope * rainfall risk
    logit = -3.5 + 0.04 * rainfall + 0.05 * slope + 0.02 * saturation + 0.3 * incidents - 0.2 * road_class
    prob = 1 / (1 + np.exp(-logit))
    disruption = (prob > 0.45).astype(int)

    df = pd.DataFrame({
        'rainfall_24h': rainfall,
        'slope_deg': slope,
        'soil_saturation': saturation,
        'historical_incidents': incidents,
        'road_class': road_class,
        'disruption_occurred': disruption
    })
    return df

def train_model():
    print("=== Training Baseline Risk Model ===")
    df = generate_synthetic_training_data()
    
    X = df[['rainfall_24h', 'slope_deg', 'soil_saturation', 'historical_incidents', 'road_class']]
    y = df['disruption_occurred']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    rf.fit(X_train, y_train)

    preds = rf.predict(X_test)
    probs = rf.predict_proba(X_test)[:, 1]

    print("Model Evaluation:")
    print(classification_report(y_test, preds))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, probs):.4f}")

    # Feature Importance (SHAP surrogate)
    importances = dict(zip(X.columns, [round(float(v), 4) for v in rf.feature_importances_]))
    print("\nFeature Importances:")
    for feature, val in importances.items():
        print(f"  - {feature}: {val * 100:.1f}%")

    os.makedirs("./ml/artifacts", exist_ok=True)
    with open("./ml/artifacts/feature_importance.json", "w") as f:
        json.dump(importances, f, indent=2)

    print("\nModel training complete. Artifacts saved to ./ml/artifacts/")

if __name__ == "__main__":
    train_model()
