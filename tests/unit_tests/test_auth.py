from models import User
from app import app


## Registration test cases

# New user registration success
def test_user_registration(isolated_client): 
    # Register a new user
    response = isolated_client.post('/register', data={
        'username': 'testuser',
        'password': 'TestPass1!',
        'confirm_password': 'TestPass1!',
        'email': 'testuser@email.com',
        'height': 170,
        'weight': 70,
        'dob': '2000-01-01' 
    }, follow_redirects=True)

    assert response.status_code == 200
    # Check flash message
    assert b'Registration successful!' in response.data
    # assert b'alert-success' in response.data

    # Check user exists in database
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'testuser@email.com'

# New user registration failed -> duplicate username
def test_duplicate_user_registration(isolated_client): 
    # First registration should succeed
    response1 = isolated_client.post('/register', data={
        'username': 'testuser',
        'password': 'TestPass1!',
        'confirm_password': 'TestPass1!',
        'email': 'testuser1@email.com',
        'height': 170,
        'weight': 70,
        'dob': '2000-01-01' 
    }, follow_redirects=True)
    assert response1.status_code == 200
    # Second registration with same email or username should fail
    response2 = isolated_client.post('/register', data={
        'username': 'testuser',  # duplicate username
        'password': 'TestPass1!',
        'confirm_password': 'TestPass1!',
        'email': 'testuser2@email.com',  # unique email
        'height': 180,
        'weight': 75,
        'dob': '2002-01-01' 
    }, follow_redirects=True)

    assert response2.status_code == 200
    assert b'Username or email already exists!' in response2.data  
    # assert b'alert-danger' in response2.data

# New user registration failed -> duplicate email
def test_duplicate_email_registration(isolated_client): 
    # First registration should succeed
    response1 = isolated_client.post('/register', data={
        'username': 'testuser1',
        'password': 'TestPass1!',
        'confirm_password': 'TestPass1!',
        'email': 'testuser@email.com',
        'height': 170,
        'weight': 70,
        'dob': '2000-01-01' 
    }, follow_redirects=True)
    assert response1.status_code == 200
    # Second registration with same email or username should fail
    response2 = isolated_client.post('/register', data={
        'username': 'testuser2',  # unique username
        'password': 'TestPass1!',
        'confirm_password': 'TestPass1!',
        'email': 'testuser@email.com',  # duplicate email
        'height': 180,
        'weight': 75,
        'dob': '2002-01-01' 
    }, follow_redirects=True)

    assert response2.status_code == 200
    assert b'Username or email already exists!' in response2.data  
    # assert b'alert-danger' in response2.data



## Login user test cases

# Existing user login success
def test_user_login_success(isolated_client):
    # Register the user first
    isolated_client.post('/register', data={
        'username': 'testuser',
        'password': 'TestPass1!',
        'confirm_password': 'TestPass1!',
        'email': 'testuser@email.com',
        'height': 170,
        'weight': 70,
        'dob': '2000-01-01' 
    }, follow_redirects=True)
    # Then login with correct credentials
    response = isolated_client.post('/login', data={
        'email': 'testuser@email.com',
        'password': 'TestPass1!'
    }, follow_redirects=True)  # Needed to follow redirect to /home and get flash message

    assert response.status_code == 200
    assert b'Login successful!' in response.data  # Depends on flash messages being shown in your templates

# Existing user login failure -> incorrect password
def test_user_login_failure_pass(isolated_client):  
    # Register the user first
    isolated_client.post('/register', data={
        'username': 'testuser',
        'password': 'TestPass1!',
        'confirm_password': 'TestPass1!',
        'email': 'testuser@email.com',
        'height': 170,
        'weight': 70,
        'dob': '2000-01-01' 
    }, follow_redirects=True)

    # Try logging in with wrong email
    response = isolated_client.post('/login', data={
        'email': 'testuser@email.com',
        'password': 'WrongPassword'
    }, follow_redirects=True)  # Follow redirect to /login

    assert response.status_code == 200
    assert b'Invalid email or password.' in response.data

# Existing user login failure -> incorrect email
def test_user_login_failure_email(isolated_client):  
    # Register the user first
    isolated_client.post('/register', data={
        'username': 'testuser',
        'password': 'TestPass1!',
        'confirm_password': 'TestPass1!',
        'email': 'testuser@email.com',
        'height': 170,
        'weight': 70,
        'dob': '2000-01-01' 
    }, follow_redirects=True)

    # Try logging in with wrong email
    response = isolated_client.post('/login', data={
        'email': 'wrongEmail@email.com',
        'password': 'TestPass1'
    }, follow_redirects=True)  # Follow redirect to /login

    assert response.status_code == 200
    assert b'Invalid email or password.' in response.data



