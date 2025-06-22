# app_b/tests/test_main.py
import pytest
import json
from collections import Counter
from fastapi.testclient import TestClient

from src.main import app, get_session
from src.models import Purchase

client = TestClient(app)

# נתוני בסיס לדמה
BASE_PURCHASES = [
    ("user1", '["milk","bread"]'),
    ("user2", '["eggs"]'),
    ("user1", '["milk"]'),
    ("user3", '["bread"]'),
]

class DummyResult:
    def __init__(self, value):
        self._value = value

    def scalar_one(self):
        return self._value

    def scalars(self):
        return self

    def all(self):
        return self._value

class DummySession:
    def __init__(self, purchases):
        self.purchases = purchases

    async def execute(self, stmt):
        text = str(stmt).lower()
        # unique_customers
        if "count(distinct" in text:
            unique = len({u for u, _ in self.purchases})
            return DummyResult(unique)
        # loyal_customers
        if "having" in text:
            cnt = Counter(u for u, _ in self.purchases)
            loyal = [u for u, c in cnt.items() if c >= 3]
            return DummyResult([(u,) for u in loyal])
        # top_products: כל שאילתה שמכילה את 'items_list'
        if "items_list" in text:
            lists = [items_json for _, items_json in self.purchases]
            return DummyResult(lists)
        return DummyResult([])

    async def close(self):
        pass

@pytest.fixture(autouse=True)
def override_get_session():
    """
    בולעים כל קריאה ל־get_session ומחזירים DummySession עם BASE_PURCHASES.
    """
    app.dependency_overrides[get_session] = lambda: DummySession(list(BASE_PURCHASES))
    yield
    app.dependency_overrides.clear()

def test_unique_customers():
    resp = client.get("/stats/unique_customers")
    assert resp.status_code == 200
    assert resp.json() == {"unique_customers": 3}

def test_loyal_customers():
    # מאריכים כדי ש־user2 יהיה עם 3 הזמנות
    extended = BASE_PURCHASES + [
        ("user2", '["eggs"]'),
        ("user2", '["bread"]'),
    ]
    app.dependency_overrides[get_session] = lambda: DummySession(extended)

    resp = client.get("/stats/loyal_customers")
    assert resp.status_code == 200
    assert resp.json() == {"loyal_customers": ["user2"]}

def test_top_products():
    resp = client.get("/stats/top_products")
    assert resp.status_code == 200
    top = set(resp.json().get("top_products", []))
    # milk=2, bread=2, eggs=1 => top הם milk ו-bread
    assert top == {"milk", "bread"}
