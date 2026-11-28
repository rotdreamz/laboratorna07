import pytest

from app import app as flask_app
from models import init_db


@pytest.fixture
def app(tmp_path):
    """Flask-застосунок з окремою тимчасовою базою даних.

    tmp_path створює нову порожню директорію для кожного тесту,
    тому робоча база db.sqlite ніколи не змінюється.
    """
    old_database = flask_app.config['DATABASE']
    flask_app.config['TESTING'] = True
    flask_app.config['DATABASE'] = str(tmp_path / 'test.db')
    with flask_app.app_context():
        init_db()
    yield flask_app
    flask_app.config['DATABASE'] = old_database


@pytest.fixture
def client(app):
    """Тестовий клієнт: надсилає запити без запуску справжнього сервера."""
    return app.test_client()


@pytest.fixture
def product(client):
    """Готовий товар у тестовій БД (створений через API)."""
    response = client.post('/api/products', json={
        'name': 'Чай', 'price': 50, 'stock': 10,
    })
    return response.json