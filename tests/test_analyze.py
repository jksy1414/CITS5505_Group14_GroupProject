import io
from models import User


# Analyze page -> Results
def test_set_visibility_not_logged_in(isolated_client):
    with isolated_client.session_transaction() as sess:
        sess['labels'] = [0, 1]
        sess['values'] = {'col1': [1, 2]}
        sess['columns'] = ['col1']
    response = isolated_client.post('/set_visibility_2', data={'visibility': 'friends'}, follow_redirects=True)
    assert b"You must be logged in to set visibility share graphs." in response.data

def test_explore_route(isolated_client):
    response = isolated_client.get('/explore')
    assert response.status_code == 302  # Expect redirect if not logged in


## File upload -- not working (all failing)

# No file uploaded
# def test_analyze_no_file(isolated_client):
#     data = {
#         'step': 'upload'
#         # No file provided
#     }
#     response = isolated_client.post('/analyze_full', data=data, follow_redirects=True)
#     assert b"No file uploaded!" in response.data

# # Incorrect file type
# def test_analyze_wrong_file_type(isolated_client):
#     data = {
#         'fitnessFile': (io.BytesIO(b"not a csv"), 'test.txt'),
#         'step': 'upload'
#     }
#     response = isolated_client.post('/analyze_full', data=data, content_type='multipart/form-data', follow_redirects=True)
#     assert b"Error reading CSV" in response.data

# ## Column selection

# # No columns selected
# def test_select_columns_no_selection(isolated_client):
#     # Step 1: Upload a CSV file
#     csv_content = b"col1,col2\n1,2\n3,4"
#     data = {
#         'fitnessFile': (io.BytesIO(csv_content), 'test.csv'),
#         'step': 'upload'
#     }
#     isolated_client.post('/analyze_full', data=data, content_type='multipart/form-data', follow_redirects=True)

#     # Step 2: Try to proceed without selecting columns
#     data = {
#         'step': 'columns'
#         # No 'columns' key, simulating no selection
#     }
#     response = isolated_client.post('/analyze_full', data=data, follow_redirects=True)
#     assert b"Please select at least one column." in response.data
