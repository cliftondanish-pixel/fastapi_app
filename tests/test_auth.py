from tests.conftest import client, TestingSessionLocal

from models.user import User
from services.password_service import hash_password

def test_health_check():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }
    
def test_login_invalid_credentials():

    response = client.post(
        "/auth/login",
        json={
            "email": "fake@gmail.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Invalid email or password"
    }
    
def test_forgot_password():

    db = TestingSessionLocal()

    user = User(
        full_name="Test User",
        email="test@example.com",
        password_hash=hash_password("Password123"),
        account_type="Individual",
        is_active=True
    )

    db.add(user)
    db.commit()
    db.close()

    response = client.post(
        "/auth/forgot-password",
        json={
            "email": "test@example.com"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "OTP sent successfully"
    
def test_me_without_login():

    response = client.get("/auth/me")

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Not authenticated"
    }
    
def test_register_individual():

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "Password123",
            "confirm_password": "Password123",
            "account_type": "Individual"
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "OTP sent successfully"
    }
    
def test_duplicate_email():

    data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "Password123",
        "confirm_password": "Password123",
        "account_type": "Individual"
    }

    client.post("/auth/register", json=data)

    response = client.post("/auth/register", json=data)

    assert response.status_code == 400

    assert response.json()["detail"] == "OTP already sent. Please verify or use resend OTP."
    
def test_register_organization():

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Company Admin",
            "email": "company@test.com",
            "password": "Password123",
            "confirm_password": "Password123",
            "account_type": "Organization",
            "organization_name": "Test Company"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "OTP sent successfully"

def test_password_mismatch():

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "wrong@test.com",
            "password": "Password123",
            "confirm_password": "WrongPassword",
            "account_type": "Individual"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords do not match"
    
def test_valid_login():

    db = TestingSessionLocal()

    user = User(
        full_name="Login User",
        email="login@test.com",
        password_hash=hash_password("Password123"),
        account_type="Individual",
        is_active=True
    )

    db.add(user)
    db.commit()
    db.close()

    response = client.post(
        "/auth/login",
        json={
            "email": "login@test.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"

    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    
def test_logout():

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"
    
def test_refresh_without_token():

    response = client.post("/auth/refresh-token")

    assert response.status_code == 401
    
def test_verify_invalid_otp():

    response = client.post(
        "/auth/verify-otp",
        json={
            "otp": "000000"
        }
    )

    assert response.status_code in [400, 401, 404]
    
def test_me_with_login():

    db = TestingSessionLocal()

    user = User(
        full_name="Test User",
        email="me@test.com",
        password_hash=hash_password("Password123"),
        account_type="Individual",
        is_active=True
    )

    db.add(user)
    db.commit()
    db.close()

    login_response = client.post(
        "/auth/login",
        json={
            "email": "me@test.com",
            "password": "Password123"
        }
    )

    assert login_response.status_code == 200

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"
    
def test_refresh_token_success():

    db = TestingSessionLocal()

    user = User(
        full_name="Refresh User",
        email="refresh@test.com",
        password_hash=hash_password("Password123"),
        account_type="Individual",
        is_active=True
    )

    db.add(user)
    db.commit()
    db.close()

    login_response = client.post(
        "/auth/login",
        json={
            "email": "refresh@test.com",
            "password": "Password123"
        }
    )

    assert login_response.status_code == 200

    response = client.post("/auth/refresh-token")

    assert response.status_code == 200
    assert response.json()["message"] == "Access token refreshed"
    
def test_invalid_otp_verification():

    response = client.post(
        "/auth/verify-otp",
        json={
            "otp": "999999"
        }
    )

    assert response.status_code in [400, 401, 404]