"""
Regression tests for frontend security headers exposed on port 3000.
"""
import pytest

from frontend.app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


@pytest.mark.parametrize('path', ['/', '/robots.txt'])
def test_security_headers_are_applied_to_all_frontend_responses(client, path):
    response = client.get(path)
    csp = response.headers.get('Content-Security-Policy')

    assert csp is not None
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'self'" in csp
    assert "'unsafe-inline'" not in csp
    assert response.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'


def test_robots_txt_is_served_with_security_headers(client):
    response = client.get('/robots.txt')

    assert response.status_code == 200
    assert response.mimetype == 'text/plain'
    assert response.headers.get('Content-Security-Policy') is not None
    assert response.headers.get('X-Frame-Options') == 'SAMEORIGIN'
