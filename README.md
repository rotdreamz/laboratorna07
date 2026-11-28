# Лабораторна робота 07. Написання unit та integration тестів

ПІБ: Конашук Владислав Сергійович
Група: ІПЗ-21
Склад команди: 1 особа (В.Конашук)
Тема проєкту: Інтернет магазин: Лимон
Репозиторій: https://github.com/rotdreamz/laboratorna07

## 1. Особистий внесок

Роботу виконано індивідуально на основі проєкту лабораторної роботи 6 (копія проєкту, новий репозиторій). **Лабораторну виконано за допомогою ШІ-асистента Claude**: він проаналізував код проєкту, запропонував структуру тестів і підготував код файлів `tests/conftest.py`, `tests/test_validators.py`, `tests/test_api.py`, `pytest.ini` та заготовку `TESTING.md`, а також підказав кроки роботи з Git і GitHub. Увесь код я вставляв у проєкт, запускав (`pytest -v`), перевіряв результат і робив скріншоти самостійно. Результат роботи я розумію і можу пояснити.

Що зроблено:

- створено новий репозиторій і перенесено до нього код лабораторної 6 (без `venv` і старого `.git`);
- встановлено `pytest` і `pytest-cov`, додано `pytest.ini`;
- написано unit тести для функції `validate_product` (`tests/test_validators.py`);
- написано integration тести для API `/api/products` (`tests/test_api.py`);
- налаштовано fixture з окремою тимчасовою базою даних (`tests/conftest.py`), тому тести не змінюють робочу `db.sqlite`;
- перевірено позитивні та негативні сценарії (коди 200, 201, 204, 400, 404, 405, 409), граничні випадки та використано `@pytest.mark.parametrize`;
- виміряно покриття коду тестами (`pytest-cov`);
- описано тестові сценарії у `TESTING.md`.

Історія комітів: https://github.com/rotdreamz/laboratorna07/commits/main

## 2. Запуск

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Запуск застосунку:

```
python app.py
```

Запуск тестів:

```
pytest -v
```

Покриття коду:

```
pytest --cov=routes --cov=models --cov-report=term-missing
```

## 3. Тестування

Результат: 81 тест, усі проходять. Покриття `routes/api.py`: 93%, загальне покриття `routes` і `models`: 63%.

Структура:

```
tests/
├── conftest.py         # fixtures: app, client, product (тимчасова БД)
├── test_validators.py  # unit тести
└── test_api.py         # integration тести
pytest.ini
TESTING.md
```

Опис кожного тесту, скріншоти результатів запуску й покриття та висновки дивіться в [TESTING.md](TESTING.md).