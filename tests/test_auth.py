import pytest
from fastapi import HTTPException
from tests.conftest import TestingSessionLocal
from models.user import User
from services.password_service import hash_password, validate_password

def test_health_check(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }
    
def test_login_invalid_credentials(client):

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
    
def test_forgot_password(client):

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
    
def test_me_without_login(client):

    response = client.get("/auth/me")

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Not authenticated"
    }
    
def test_register_individual(client):

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "john@gmail.com",
            "password": "Password@123",
            "confirm_password": "Password@123",
            "account_type": "Individual"
        }
    )
    
    print(response.json())

    assert response.status_code == 200

    assert response.json() == {
        "message": "OTP sent successfully"
    }
    
def test_duplicate_email(client):

    data = {
        "full_name": "Test User",
        "email": "duplicate@gmail.com",
        "password": "Password@123",
        "confirm_password": "Password@123",
        "account_type": "Individual"
    }

    client.post("/auth/register", json=data)

    response = client.post("/auth/register", json=data)

    assert response.status_code == 400

    assert response.json()["detail"] == "OTP already sent. Please verify or use resend OTP."
    
def test_register_organization(client):

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Admin",
            "email": "admin@mycompany.com",
            "password": "Password@123",
            "confirm_password": "Password@123",
            "account_type": "Organization",
            "organization_name": "My Company"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "OTP sent successfully"

def test_password_mismatch(client):

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@gmail.com",
            "password": "Password@123",
            "confirm_password": "Password@456",
            "account_type": "Individual"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords do not match"
    
def test_valid_login(client):

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
    
def test_logout(client):

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"
    
def test_refresh_without_token(client):

    response = client.post("/auth/refresh-token")

    assert response.status_code == 401
    
def test_verify_invalid_otp(client):

    response = client.post(
        "/auth/verify-otp",
        json={
            "otp": "000000"
        }
    )

    assert response.status_code in [400, 401, 404]
    
def test_me_with_login(client):

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
    
def test_refresh_token_success(client):

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
    assert response.json()["message"] == "Tokens refreshed successfully"
    
def test_invalid_otp_verification(client):

    response = client.post(
        "/auth/verify-otp",
        json={
            "otp": "999999"
        }
    )

    assert response.status_code in [400, 401, 404]
    
def test_individual_with_business_email(client):

    response = client.post(
        "/auth/register",
        json={
            "full_name": "John Doe",
            "email": "admin@company.com",
            "password": "Password@123",
            "confirm_password": "Password@123",
            "account_type": "Individual"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Individual accounts must use a personal email address"
    )
    
def test_organization_with_personal_email(client):

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Admin User",
            "email": "admin@gmail.com",
            "password": "Password@123",
            "confirm_password": "Password@123",
            "account_type": "Organization",
            "organization_name": "ABC Company"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Organization accounts must use an official business email"
    )
    
def test_organization_without_name(client):

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Admin User",
            "email": "admin@company.com",
            "password": "Password@123",
            "confirm_password": "Password@123",
            "account_type": "Organization"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Organization name is required"
    )
    
def test_register_with_weak_password(client):

    response = client.post(
        "/auth/register",
        json={
            "full_name": "John Doe",
            "email": "john@gmail.com",
            "password": "password",
            "confirm_password": "password",
            "account_type": "Individual"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Password must contain at least one uppercase letter"
    )
    
def test_weak_password():

    with pytest.raises(HTTPException) as exc:
        validate_password("password")

    assert exc.value.status_code == 400
    assert "uppercase" in exc.value.detail
# def test_reset_password_with_weak_password(client):

#     # Use a valid email and verified OTP setup

#     response = client.post(
#         "/auth/reset-password",
#         json={
#             "email": "john@gmail.com",
#             "password": "password",
#             "confirm_password": "password"
#         }
#     )

#     assert response.status_code == 400