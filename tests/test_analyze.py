import io
from models import User


## File upload

# No file uploaded
def test_analyze_no_file(isolated_client):
    response = isolated_client.post('/analyze', data={}, follow_redirects=True)
    assert b"Please upload a CSV file." in response.data

# Incorrect file type
def test_analyze_wrong_file_type(isolated_client):
    data = {
        'fitnessFile': (io.BytesIO(b"not a csv"), 'test.txt')
    }
    response = isolated_client.post('/analyze', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert b"Only CSV files are allowed." in response.data


## Column selection

# No columns selected
def test_select_columns_no_selection(isolated_client):
    # Simulate uploading a CSV first
    csv_content = b"col1,col2\n1,2\n3,4"
    data = {
        'fitnessFile': (io.BytesIO(csv_content), 'test.csv')
    }
    isolated_client.post('/analyze', data=data, content_type='multipart/form-data', follow_redirects=True)
    # Now POST to select-columns with no columns selected
    response = isolated_client.post('/select-columns', data={}, follow_redirects=True)
    assert b"Please select at least one column." in response.data

# Duplicate columns selected
def test_analyze_duplicate_columns(isolated_client):
    csv_content = b"col1,col1,col2\n1,2,3\n4,5,6"
    data = {
        'fitnessFile': (io.BytesIO(csv_content), 'test.csv')
    }
    response = isolated_client.post('/analyze', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert b"Duplicate column names detected." in response.data



# Results

# 
def test_results_missing_session(client):
    response = client.get('/results', follow_redirects=True)
    assert b"Missing data for chart rendering." in response.data

def test_set_visibility_public_not_logged_in(client):
    with client.session_transaction() as sess:
        sess['labels'] = [0, 1]
        sess['values'] = {'col1': [1, 2]}
        sess['columns'] = ['col1']
    response = client.post('/set_visibility', data={'visibility': 'public'}, follow_redirects=True)
    assert b"You must be logged in to set visibility to public." in response.data

def test_set_visibility_friends_not_logged_in(client):
    with client.session_transaction() as sess:
        sess['labels'] = [0, 1]
        sess['values'] = {'col1': [1, 2]}
        sess['columns'] = ['col1']
    response = client.post('/set_visibility', data={'visibility': 'friends'}, follow_redirects=True)
    assert b"You must be logged in to set visibility to public." in response.data

def test_set_visibility_missing_data(client):
    response = client.post('/set_visibility', data={'visibility': 'public'}, follow_redirects=True)
    assert b"Missing data for saving the chart." in response.data

def test_explore_route(client):
    response = client.get('/explore')
    assert response.status_code == 200
    assert b"charts" in response.data or b"Fitness Data" in response.data  # Adjust as needed for your template