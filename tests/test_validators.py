"""Unit тести функції validate_product (routes/api.py).

Функція чиста: приймає словник, повертає список помилок.
Без бази даних, без Flask-запитів, тому тести швидкі й ізольовані.
"""
import pytest

from routes.api import validate_product


def test_valid_product_has_no_errors():
    # Arrange
    data = {'name': 'Чай', 'price': 50}

    # Act
    errors = validate_product(data)

    # Assert
    assert errors == []


def test_all_fields_valid():
    data = {'name': 'Кава', 'price': 80.5, 'stock': 3,
            'delivery': 100, 'sale_price': 70}

    assert validate_product(data) == []


def test_empty_dict_gives_name_and_price_errors():
    errors = validate_product({})

    assert len(errors) == 2
    assert any(e.startswith('name') for e in errors)
    assert any(e.startswith('price') for e in errors)


def test_negative_price_is_error():
    errors = validate_product({'name': 'Чай', 'price': -1})

    assert len(errors) == 1
    assert errors[0].startswith('price')


def test_partial_allows_missing_fields():
    # PATCH: поля необов'язкові, порожній словник валідний
    assert validate_product({}, partial=True) == []


def test_partial_still_checks_present_fields():
    errors = validate_product({'price': -5}, partial=True)

    assert len(errors) == 1
    assert errors[0].startswith('price')


# ---------- параметризовані тести: граничні випадки ----------

@pytest.mark.parametrize('name', ['', ' ', '   ', '\t\n', None, 123, [], True])
def test_invalid_names(name):
    errors = validate_product({'name': name, 'price': 10})

    assert len(errors) == 1
    assert errors[0].startswith('name')


@pytest.mark.parametrize('price', [-0.01, -1, -1000, '10', None, True, False, [], {}])
def test_invalid_prices(price):
    errors = validate_product({'name': 'Чай', 'price': price})

    assert len(errors) == 1
    assert errors[0].startswith('price')


@pytest.mark.parametrize('price', [0, 0.0, 0.01, 9.99, 1000, 10**12])
def test_valid_prices_including_boundaries(price):
    # 0 і дуже велике число: граничні значення
    assert validate_product({'name': 'Кава', 'price': price}) == []


@pytest.mark.parametrize('stock', [-1, 1.5, '5', True, False])
def test_invalid_stock(stock):
    errors = validate_product({'name': 'Чай', 'price': 10, 'stock': stock})

    assert len(errors) == 1
    assert errors[0].startswith('stock')


@pytest.mark.parametrize('stock', [0, 1, 10**6])
def test_valid_stock(stock):
    assert validate_product({'name': 'Чай', 'price': 10, 'stock': stock}) == []


@pytest.mark.parametrize('field', ['delivery', 'sale_price'])
@pytest.mark.parametrize('value', [-1, '100', True])
def test_invalid_optional_numbers(field, value):
    errors = validate_product({'name': 'Чай', 'price': 10, field: value})

    assert len(errors) == 1
    assert errors[0].startswith(field)


@pytest.mark.parametrize('field', ['delivery', 'sale_price'])
def test_optional_numbers_may_be_none_or_zero(field):
    assert validate_product({'name': 'Чай', 'price': 10, field: None}) == []
    assert validate_product({'name': 'Чай', 'price': 10, field: 0}) == []