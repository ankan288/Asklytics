"""Production integration test suite for FastAPI REST API endpoints using TestClient."""

import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_session_lifecycle_api():
    # 1. Create session
    create_res = client.post("/sessions", json={"datasource_id": "default"})
    assert create_res.status_code == 200
    data = create_res.json()
    assert "session_id" in data
    sid = data["session_id"]

    # 2. Delete session
    del_res = client.delete(f"/sessions/{sid}")
    assert del_res.status_code == 200
    assert del_res.json() == {"status": "deleted"}


def test_upload_csv_endpoint_valid():
    csv_content = b"department,budget\nSales,50000\nEngineering,120000"
    files = {"file": ("departments.csv", io.BytesIO(csv_content), "text/csv")}
    response = client.post("/upload/csv", files=files)

    assert response.status_code == 200
    json_data = response.json()
    assert "datasource_id" in json_data
    assert json_data["table_name"] == "uploaded_data"
    assert "department" in json_data["columns"]
    assert "budget" in json_data["columns"]


def test_upload_csv_endpoint_rejects_non_csv():
    txt_content = b"Just plain text"
    files = {"file": ("notes.txt", io.BytesIO(txt_content), "text/plain")}
    response = client.post("/upload/csv", files=files)
    assert response.status_code == 400
    assert "Only .csv files are accepted" in response.json()["detail"]


@patch("app.services.gemini_service.generate_dashboard")
@patch("app.services.gemini_service.generate_insight")
def test_query_endpoint_e2e_mocked_ai(mock_insight, mock_dashboard):
    # Mock AI stage 1 response
    mock_dashboard.return_value = {
        "dashboard_title": "Product Revenue Overview",
        "sql": "SELECT product_category, SUM(total_revenue) AS revenue FROM amazon_sales GROUP BY product_category",
        "charts": [
            {
                "id": "chart-1",
                "type": "bar",
                "title": "Revenue by Category",
                "x_key": "product_category",
                "y_keys": ["revenue"],
                "color_palette": ["#4f46e5"],
            }
        ],
        "follow_up_suggestions": ["Filter by region"],
    }

    # Mock AI stage 2 response
    mock_insight.return_value = {
        "insight_summary": "Top category generated strong revenue across all segments.",
        "data_limitations": None,
    }

    # Create session
    session_res = client.post("/sessions", json={"datasource_id": "default"})
    sid = session_res.json()["session_id"]

    # Run query
    query_payload = {
        "session_id": sid,
        "prompt": "Show total revenue by product category",
        "datasource_id": "default",
    }
    response = client.post("/query", json=query_payload)
    assert response.status_code == 200

    res_data = response.json()
    assert res_data["dashboard_title"] == "Product Revenue Overview"
    assert "SELECT" in res_data["sql"]
    assert len(res_data["charts"]) == 1
    assert res_data["charts"][0]["type"] == "bar"

    # Verify Wave 1 audit metadata exists
    assert "audit" in res_data
    assert res_data["audit"] is not None
    assert res_data["audit"]["is_read_only"] is True
    assert res_data["audit"]["execution_time_ms"] >= 0
    assert "verification" in res_data["audit"]


@patch("app.services.gemini_service.generate_dashboard")
def test_query_endpoint_handles_unanswerable_query(mock_dashboard):
    mock_dashboard.return_value = {
        "error": "The dataset does not contain weather data."
    }

    session_res = client.post("/sessions", json={"datasource_id": "default"})
    sid = session_res.json()["session_id"]

    response = client.post("/query", json={
        "session_id": sid,
        "prompt": "What was the weather during each purchase?",
        "datasource_id": "default",
    })
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["error"] == "The dataset does not contain weather data."
