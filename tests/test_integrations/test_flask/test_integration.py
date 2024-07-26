from flask import Flask
from injection import Provide, inject

app = Flask(__name__)
app.config.update({"TESTING": True})


@app.route("/some_resource")
@inject
def flask_endpoint(redis=Provide["redis"]):
    value = redis.get(-900)
    return {"detail": value}


def test_flask_endpoint():
    client = app.test_client()
    response = client.get("/some_resource")
    assert response.status_code == 200
    assert response.json == {"detail": -900}
