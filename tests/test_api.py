"""Integration тести REST API /api/products.

Запит проходить увесь шлях: маршрут, валідація, SQLite (тимчасова БД), відповідь.
"""
import pytest

from models import add_client, add_product, create_order


# ---------- GET ----------

def test_get_products_empty(client):
    response = client.get('/api/products')

    assert response.status_code == 200
    assert response.json == []


def test_get_products_returns_created(client, product):
    response = client.get('/api/products')

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['name'] == 'Чай'


def test_get_product_by_id(client, product):
    response = client.get(f"/api/products/{product['id']}")

    assert response.status_code == 200
    assert response.json['price'] == 50
    assert response.json['stock'] == 10


def test_get_unknown_product_returns_404(client):
    response = client.get('/api/products/999')

    assert response.status_code == 404
    assert response.json['error'] == 'Товар не знайдено'


@pytest.mark.parametrize('url', ['/api/unknown', '/api/products/abc', '/api/products/1/extra'])
def test_unknown_api_url_returns_json_404(client, url):
    response = client.get(url)

    assert response.status_code == 404
    assert response.json['error'] == 'Ресурс не знайдено'


def test_method_not_allowed_returns_405(client):
    response = client.put('/api/products', json={'name': 'X', 'price': 1})

    assert response.status_code == 405
    assert 'error' in response.json


# ---------- POST ----------

def test_create_product(client):
    # Arrange
    payload = {'name': 'Чай', 'price': 50}

    # Act
    response = client.post('/api/products', json=payload)

    # Assert
    assert response.status_code == 201
    assert response.json['name'] == 'Чай'
    assert response.json['price'] == 50
    assert 'id' in response.json


def test_create_product_applies_defaults_and_strips_name(client):
    response = client.post('/api/products', json={'name': '  Чай  ', 'price': 50})

    assert response.status_code == 201
    assert response.json['name'] == 'Чай'
    assert response.json['stock'] == 0
    assert response.json['delivery'] == 0
    assert response.json['sale_color'] == 'red'


def test_create_then_get(client):
    created = client.post('/api/products', json={'name': 'Кава', 'price': 80}).json

    response = client.get(f"/api/products/{created['id']}")

    assert response.status_code == 200
    assert response.json == created


def test_create_with_boundary_price_zero(client):
    response = client.post('/api/products', json={'name': 'Безкоштовно', 'price': 0})

    assert response.status_code == 201
    assert response.json['price'] == 0


@pytest.mark.parametrize('payload', [
    {},                                  # порожній об'єкт
    {'name': ''},                        # немає price, порожнє name
    {'name': 'Чай'},                     # немає price
    {'price': 50},                       # немає name
    {'name': '   ', 'price': 50},        # name з пробілів
    {'name': 'Чай', 'price': -1},        # від'ємна ціна
    {'name': 'Чай', 'price': '50'},      # ціна рядком
    {'name': 'Чай', 'price': 50, 'stock': -3},
    {'name': 'Чай', 'price': 50, 'stock': 1.5},
])
def test_create_invalid_returns_400(client, payload):
    response = client.post('/api/products', json=payload)

    assert response.status_code == 400
    assert response.json['error'] == 'Помилка валідації'
    assert len(response.json['details']) >= 1


def test_invalid_create_does_not_save_anything(client):
    client.post('/api/products', json={'name': 'Чай', 'price': -1})

    assert client.get('/api/products').json == []


def test_create_with_non_json_body_returns_400(client):
    response = client.post('/api/products', data='це не json', content_type='text/plain')

    assert response.status_code == 400
    assert 'error' in response.json


def test_create_with_json_array_returns_400(client):
    response = client.post('/api/products', json=[{'name': 'Чай', 'price': 1}])

    assert response.status_code == 400


# ---------- PUT ----------

def test_put_replaces_product(client, product):
    new_data = {'name': 'Зелений чай', 'price': 70, 'stock': 5}

    response = client.put(f"/api/products/{product['id']}", json=new_data)

    assert response.status_code == 200
    assert response.json['name'] == 'Зелений чай'
    assert response.json['price'] == 70
    assert response.json['stock'] == 5


def test_put_unknown_returns_404(client):
    response = client.put('/api/products/999', json={'name': 'X', 'price': 1})

    assert response.status_code == 404


def test_put_invalid_returns_400(client, product):
    response = client.put(f"/api/products/{product['id']}", json={'name': ''})

    assert response.status_code == 400


# ---------- PATCH ----------

def test_patch_changes_only_given_fields(client, product):
    response = client.patch(f"/api/products/{product['id']}", json={'price': 99})

    assert response.status_code == 200
    assert response.json['price'] == 99
    assert response.json['name'] == 'Чай'      # не змінилось
    assert response.json['stock'] == 10        # не змінилось


@pytest.mark.parametrize('payload', [{}, {'foo': 'bar'}])
def test_patch_without_known_fields_returns_400(client, product, payload):
    response = client.patch(f"/api/products/{product['id']}", json=payload)

    assert response.status_code == 400


def test_patch_invalid_price_returns_400(client, product):
    response = client.patch(f"/api/products/{product['id']}", json={'price': -10})

    assert response.status_code == 400


def test_patch_unknown_returns_404(client):
    response = client.patch('/api/products/999', json={'price': 10})

    assert response.status_code == 404


# ---------- DELETE ----------

def test_delete_product(client, product):
    response = client.delete(f"/api/products/{product['id']}")

    assert response.status_code == 204
    assert response.data == b''
    assert client.get(f"/api/products/{product['id']}").status_code == 404


def test_delete_unknown_returns_404(client):
    response = client.delete('/api/products/999')

    assert response.status_code == 404


def test_delete_product_used_in_order_returns_409(app, client):
    # Arrange: товар, який уже є в замовленні (ON DELETE RESTRICT)
    with app.app_context():
        client_id = add_client('Іван', 'ivan@example.com', None)
        product_id = add_product('Чай', None, 50, 10)
        create_order(client_id, {product_id: 2})

    # Act
    response = client.delete(f'/api/products/{product_id}')

    # Assert
    assert response.status_code == 409
    assert client.get(f'/api/products/{product_id}').status_code == 200


# ---------- ізоляція ----------

def test_each_test_gets_clean_database(client):
    # Якщо б тести ділили базу, тут були б товари з попередніх тестів
    assert client.get('/api/products').json == []