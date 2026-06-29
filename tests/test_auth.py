from tests.conftest import client

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

    response = client.post(
        "/auth/forgot-password",
        json={
            "email": "cliftondanish3@gmail.com"
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "OTP sent successfully"
    }
    
def test_me_without_login():

    response = client.get("/auth/me")

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Not authenticated"
    }