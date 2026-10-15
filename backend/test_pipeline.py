"""Verification test script for MuryaAI FastAPI app."""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_and_samples():
    response = client.get("/api/samples")
    assert response.status_code == 200, f"Samples failed: {response.text}"
    samples = response.json()
    assert len(samples) >= 4, "Should have at least 4 language samples"
    print(f"PASS: Samples endpoint returned {len(samples)} benchmark prompts.")

def test_text_resolution_hausa():
    payload = {
        "text": "An cire min kudi naira dubu goma sha biyar a POS amma ban samu kudi ba",
        "language": "hausa",
        "channel": "ivr_phone",
        "caller_id": "08031234567"
    }
    response = client.post("/api/resolve/text", json=payload)
    assert response.status_code == 200, f"Hausa resolution failed: {response.text}"
    data = response.json()
    assert data["detected_language"] == "hausa"
    assert data["entities"]["domain"] == "banking_pos"
    assert data["entities"]["intent"] == "failed_pos_debit"
    assert "DIS-BNK" in data["resolution_action"]["ticket_id"]
    print("PASS: Hausa POS grievance resolved with auto-reversal ticket:", data["resolution_action"]["ticket_id"])

def test_text_resolution_yoruba():
    payload = {
        "text": "Mo ra owo ina naira egberun marun lori mita mi 01482910394 sugbon mi o ri token gba",
        "language": "yoruba",
        "channel": "web",
        "caller_id": "08031234567"
    }
    response = client.post("/api/resolve/text", json=payload)
    assert response.status_code == 200, f"Yoruba resolution failed: {response.text}"
    data = response.json()
    assert data["detected_language"] == "yoruba"
    assert data["entities"]["domain"] == "electricity_disco"
    assert data["entities"]["meter_number"] == "01482910394"
    assert "token" in data["resolution_action"]["details"]
    print("PASS: Yoruba DisCo token query resolved. Token delivered:", data["resolution_action"]["details"]["token"])

def test_telemetry():
    response = client.get("/api/telemetry")
    assert response.status_code == 200
    telemetry = response.json()
    assert telemetry["total_calls"] > 0
    assert telemetry["resolution_rate_percent"] > 90
    print(f"PASS: Telemetry endpoint returned {telemetry['total_calls']} calls, resolution rate: {telemetry['resolution_rate_percent']}%.")

if __name__ == "__main__":
    test_health_and_samples()
    test_text_resolution_hausa()
    test_text_resolution_yoruba()
    test_telemetry()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
