import datetime
from app.services.status_engine import evaluate_segment_state


class FakeSegment:
    def __init__(self, base_risk_score=20.0, last_updated=None):
        self.base_risk_score = base_risk_score
        self.last_updated = last_updated or datetime.datetime.utcnow()


def test_fresh_segment_no_incidents_stays_open():
    seg = FakeSegment(base_risk_score=15.0)
    status, risk, confidence = evaluate_segment_state(seg, [], computed_risk_score=15.0)
    assert status == "Open"
    assert confidence >= 0.90


def test_stale_segment_confidence_decays():
    old_time = datetime.datetime.utcnow() - datetime.timedelta(hours=36)
    seg = FakeSegment(base_risk_score=15.0, last_updated=old_time)
    status, risk, confidence = evaluate_segment_state(seg, [], computed_risk_score=15.0)
    assert confidence < 0.95


def test_uses_the_passed_in_risk_score_not_its_own():
    seg = FakeSegment(base_risk_score=15.0)
    status, risk, confidence = evaluate_segment_state(seg, [], computed_risk_score=72.0)
    assert risk == 72.0
    assert status == "Caution"
