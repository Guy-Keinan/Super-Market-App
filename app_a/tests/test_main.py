import pytest
from fastapi.testclient import TestClient
from src.main import app, get_session
from src.models import Product

client = TestClient(app)

# Dummy products list
DUMMY_PRODUCTS = [
    Product(name="milk", unit_price=1.5),
    Product(name="bread", unit_price=2.0),
    Product(name="eggs", unit_price=3.0),
]


class DummyResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return self

    def all(self):
        return self._items


class DummySession:
    async def execute(self, stmt):
        text = str(stmt).lower()
        if "from product" in text:
            return DummyResult(DUMMY_PRODUCTS)
        return DummyResult([])

    # הכנסנו את המתודות החסרות
    def add(self, obj):
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass

    async def close(self):
        pass


@pytest.fixture(autouse=True)
def override_session():
    """
    בכל בדיקה, לפני יצירת ה–TestClient, נוסיף ל–app.dependency_overrides
    שה–get_session המקורי יוחלף ב–fake_get_session.
    """

    async def fake_get_session():
        yield DummySession()

    app.dependency_overrides[get_session] = fake_get_session
    yield
    app.dependency_overrides.clear()


def test_create_purchase_new_user():
    response = client.post(
        "/purchase", json={"supermarket_id": "SMKT001", "items": ["milk", "bread"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["total_amount"] == pytest.approx(3.5)


def test_create_purchase_unknown_product():
    response = client.post(
        "/purchase", json={"supermarket_id": "SMKT001", "items": ["unknown"]}
    )
    assert response.status_code == 404
    assert "Product 'unknown' not found" in response.json()["detail"]


def test_create_purchase_duplicate_item():
    response = client.post(
        "/purchase", json={"supermarket_id": "SMKT001", "items": ["milk", "milk"]}
    )
    assert response.status_code == 400
    assert "only be purchased once" in response.json()["detail"]
