# conftest.py
import pytest
from app import app, db


# Used for tests that need full isolation (registration tests)
@pytest.fixture(scope='function')
def isolated_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        db.drop_all()


# Used for tests that can share state (login tests)
# @pytest.fixture(scope='module')
# def shared_client():
#     app.config['TESTING'] = True
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
#     app.config['WTF_CSRF_ENABLED'] = False

#     with app.app_context():
#         db.create_all()
#         with app.test_client() as client:
#             yield client
#         db.drop_all()