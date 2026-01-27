from fastapi.testclient import TestClient
from service_a import app as app_a
from service_b import app as app_b
from unittest.mock import patch

# Klient testowy dla Serwisu A
client_a = TestClient(app_a)
# Klient testowy dla Serwisu B
client_b = TestClient(app_b)

def test_service_a_save():
    """Test czy Serwis A poprawnie zapisuje dane"""
    response = client_a.post("/results", json={"url": "http://test.com", "count": 5})
    assert response.status_code == 200
    assert response.json()["status"] == "saved"
    
    get_res = client_a.get("/results")
    assert len(get_res.json()) > 0

@patch("service_b.pika.BlockingConnection") 
def test_service_b_endpoint(mock_pika):
    """Test czy Serwis B przyjmuje zgłoszenie"""
    mock_channel = mock_pika.return_value.channel.return_value
    
    response = client_b.post("/analyze", json={"url": "http://image.com/photo.jpg"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Accepted"

    mock_channel.basic_publish.assert_called_once()