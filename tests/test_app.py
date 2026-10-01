from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.db import OperationalError


def test_health(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_readiness(client):
    assert client.get("/ready/").status_code == 200


def test_readiness_hides_database_error(client):
    with patch("apps.core.views.connection.cursor", side_effect=OperationalError("private-host")):
        response = client.get("/ready/")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert b"private-host" not in response.content


@pytest.mark.django_db
def test_custom_user(client):
    user = get_user_model().objects.create_user(username="alice", password="strong-test-password")
    assert user.check_password("strong-test-password")
    assert client.login(username="alice", password="strong-test-password")
    assert client.get("/admin/").status_code == 302
