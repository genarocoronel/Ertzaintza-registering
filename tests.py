import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_server import app
client = TestClient(app, backend='trio')
from httpx import AsyncClient
from caller import get_test_PV_item, get_test_RH_item
class TestCallFastAPI:
    def test_read_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

    def test_post_root(self):
        response = client.post("/post")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

    def test_submit_PV(self):
        item = get_test_PV_item()
        response = client.post("/PV", content=item.json())
        assert response.status_code == 200
        #assert response.json() == {"Hello": "World"}

    def test_submit_RH(self):
        item = get_test_RH_item()

        response = client.post("/RH", content=item.json())
        assert response.status_code == 200
        #assert response.json() == {"Hello": "World"}
    def test_submit_PVe(self):
        item = get_test_PV_item()

        response = client.post("/PVe", content=item.json())
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}