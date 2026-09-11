from app.services import ml_risk_service


def test_model_loads_from_artifact():
    ml_risk_service.load_model()
    assert ml_risk_service.is_model_loaded() is True


def test_predict_returns_probability_and_importances():
    ml_risk_service.load_model()
    prob, importances = ml_risk_service.predict_disruption_probability(
        {
            "rainfall_1h": 12.0,
            "rainfall_6h": 45.0,
            "rainfall_24h": 85.0,
            "forecast_24h_rain": 100.0,
            "landslide_susceptibility": 0.9,
            "base_risk_score": 70.0,
            "historical_incident_count": 2,
        }
    )
    assert 0.0 <= prob <= 1.0
    assert isinstance(importances, dict)
    assert len(importances) > 0


def test_high_risk_inputs_score_higher_than_low_risk_inputs():
    ml_risk_service.load_model()
    low_prob, _ = ml_risk_service.predict_disruption_probability(
        {
            "rainfall_1h": 0.5, "rainfall_6h": 1.0, "rainfall_24h": 2.0,
            "forecast_24h_rain": 2.0, "landslide_susceptibility": 0.1,
            "base_risk_score": 15.0, "historical_incident_count": 0,
        }
    )
    high_prob, _ = ml_risk_service.predict_disruption_probability(
        {
            "rainfall_1h": 20.0, "rainfall_6h": 90.0, "rainfall_24h": 150.0,
            "forecast_24h_rain": 160.0, "landslide_susceptibility": 0.95,
            "base_risk_score": 85.0, "historical_incident_count": 4,
        }
    )
    assert high_prob > low_prob
