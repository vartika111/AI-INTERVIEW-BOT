import os
# Configure the test environment to use an in-memory SQLite database
os.environ["DB_PATH"] = ":memory:"

import pytest
from fastapi.testclient import TestClient
from src.api.main import app, storage

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    """Ensures each test gets a clean, re-initialized in-memory SQLite schema."""
    storage._init_db()
    yield

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}

def test_create_and_get_candidate():
    # 1. Create candidate
    candidate_data = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "skills": ["Python", "SQL"]
    }
    response = client.post("/candidate", json=candidate_data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["name"] == "Jane Doe"
    assert res_data["email"] == "jane.doe@example.com"
    assert res_data["skills"] == ["Python", "SQL"]
    assert "id" in res_data
    candidate_id = res_data["id"]

    # 2. Retrieve candidate details
    get_response = client.get(f"/candidate/{candidate_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == candidate_id
    assert get_data["name"] == "Jane Doe"
    assert get_data["email"] == "jane.doe@example.com"
    assert get_data["skills"] == ["Python", "SQL"]

def test_get_nonexistent_candidate():
    response = client.get("/candidate/CAN-NONEXISTENT")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_start_interview_new_candidate():
    req_data = {
        "topic": "Python",
        "difficulty": "Easy",
        "count": 2,
        "name": "New Candidate",
        "email": "new.cand@example.com"
    }
    response = client.post("/interview/start", json=req_data)
    assert response.status_code == 201
    res_data = response.json()
    assert "interview_id" in res_data
    assert "candidate_id" in res_data
    assert res_data["topic"] == "Python"
    assert res_data["difficulty"] == "Easy"
    assert res_data["question_count"] == 2
    assert res_data["status"] == "IN_PROGRESS"

def test_start_interview_existing_candidate():
    # Register candidate first
    candidate_response = client.post("/candidate", json={
        "name": "Arthur Dent",
        "email": "arthur@galaxy.org",
        "skills": ["OOP"]
    })
    candidate_id = candidate_response.json()["id"]

    # Start interview (OOP Medium has only 2 questions in the bank pool)
    req_data = {
        "topic": "OOP",
        "difficulty": "Medium",
        "count": 2,
        "candidate_id": candidate_id
    }
    response = client.post("/interview/start", json=req_data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["candidate_id"] == candidate_id
    assert res_data["topic"] == "OOP"
    assert res_data["question_count"] == 2

def test_full_interview_workflow():
    # 1. Register candidate and start interview
    start_response = client.post("/interview/start", json={
        "topic": "SQL",
        "difficulty": "Easy",
        "count": 2,
        "name": "Bruce Wayne",
        "email": "bruce@batman.com"
    })
    assert start_response.status_code == 201
    start_data = start_response.json()
    interview_id = start_data["interview_id"]
    candidate_id = start_data["candidate_id"]

    # 2. Get first question
    next_response = client.post("/interview/next", json={"interview_id": interview_id})
    assert next_response.status_code == 200
    next_data = next_response.json()
    assert next_data["is_finished"] is False
    assert next_data["status"] == "IN_PROGRESS"
    assert "question" in next_data
    q1 = next_data["question"]
    assert q1["topic"] == "SQL"
    assert q1["difficulty"] == "Easy"

    # 3. Submit answer to first question
    ans_response = client.post("/interview/answer", json={
        "interview_id": interview_id,
        "question_id": q1["id"],
        "answer": "Primary keys uniquely identify rows."
    })
    assert ans_response.status_code == 200
    ans_data = ans_response.json()
    assert ans_data["status"] == "SUCCESS"
    assert ans_data["question_id"] == q1["id"]

    # 4. Get second question (could be dynamic follow-up or main question)
    # The default MockLLMClient evaluates score as 8.0, so dynamic follow-up is generated.
    # Therefore, next question will be Q1-followup.
    next_response2 = client.post("/interview/next", json={"interview_id": interview_id})
    assert next_response2.status_code == 200
    next_data2 = next_response2.json()
    assert next_data2["is_finished"] is False
    q2 = next_data2["question"]
    assert q2["id"] == f"{q1['id']}-followup"

    # 5. Answer follow-up question (omitting question_id to test default active question resolution)
    ans_response2 = client.post("/interview/answer", json={
        "interview_id": interview_id,
        "answer": "Yes, standard indexing speeds up queries."
    })
    assert ans_response2.status_code == 200
    ans_data2 = ans_response2.json()
    assert ans_data2["question_id"] == q2["id"]

    # 6. Fetch next question (original second main question)
    next_response3 = client.post("/interview/next", json={"interview_id": interview_id})
    assert next_response3.status_code == 200
    next_data3 = next_response3.json()
    assert next_data3["is_finished"] is False
    q3 = next_data3["question"]
    assert q3["id"] != q2["id"]

    # Submit answer (this will trigger follow-up Q-SQL-02-followup)
    ans_response3 = client.post("/interview/answer", json={
        "interview_id": interview_id,
        "answer": "A foreign key creates relational mappings."
    })
    assert ans_response3.status_code == 200

    # 7. Get second follow-up question
    next_response4 = client.post("/interview/next", json={"interview_id": interview_id})
    assert next_response4.status_code == 200
    next_data4 = next_response4.json()
    assert next_data4["is_finished"] is False
    q4 = next_data4["question"]
    assert q4["id"] == f"{q3['id']}-followup"

    # Submit answer for the second follow-up
    ans_response4 = client.post("/interview/answer", json={
        "interview_id": interview_id,
        "answer": "Yes, referential integrity matches keys."
    })
    assert ans_response4.status_code == 200

    # 8. Advancing past final question should auto-evaluate and complete interview
    next_response_final = client.post("/interview/next", json={"interview_id": interview_id})
    assert next_response_final.status_code == 200
    assert next_response_final.json() == {"question": None, "status": "COMPLETED", "is_finished": True}

    # 8. Query interview results
    result_response = client.get(f"/interview/result/{interview_id}")
    assert result_response.status_code == 200
    result_data = result_response.json()
    assert result_data["status"] == "COMPLETED"
    assert result_data["score"] == 8.0  # MockLLMClient evaluates non-empty answers to 8.0
    assert len(result_data["detailed_evaluations"]) > 0

    # 9. Query candidate history
    history_response = client.get(f"/history/{candidate_id}")
    assert history_response.status_code == 200
    history_data = history_response.json()
    assert history_data["candidate_id"] == candidate_id
    assert len(history_data["interviews"]) == 1
    assert history_data["interviews"][0]["interview_id"] == interview_id
    assert history_data["interviews"][0]["score"] == 8.0
    assert history_data["interviews"][0]["status"] == "COMPLETED"
