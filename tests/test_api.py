import pytest
import random
import faker
from falcon import testing
import datetime

from charge.app import create


@pytest.fixture
def client():
    return testing.TestClient(create())


def generate_random_input():
    # create a valid input example with random values
    faker_ = faker.Faker()
    fake_timestamp_start = faker_.date_time()
    input_example = \
        {
            "rate": {
                "energy": random.uniform(0, 10),
                "time": random.uniform(0, 10),
                "transaction": random.uniform(0, 10)
            },
            "cdr": {
                "meterStart": random.randrange(10000, 30000),
                "timestampStart": fake_timestamp_start.isoformat(),
                "meterStop": random.randrange(30000, 60000),
                "timestampStop": (
                        fake_timestamp_start + datetime.timedelta(minutes=random.randrange(1, 60))
                ).isoformat()
            }
        }
    return input_example


def test_rate_success(client):
    req = generate_random_input()
    response = client.simulate_post("/rate", json=req)
    assert response.status_code == 200


def test_rate_validation_error(client):
    # not valid iso time format
    req = dict(generate_random_input())
    req['cdr']['timestampStop'] = "2021-04-05-11:27:00"
    response = client.simulate_post("/rate", json=req)
    assert response.status_code == 400

    # not valid meters type
    req = dict(generate_random_input())
    req['cdr']['meterStart'] = "33"
    response = client.simulate_post("/rate", json=req)
    assert response.status_code == 400

    # not valid numbers type
    req = dict(generate_random_input())
    req['rate']['energy'] = "0.3"
    response = client.simulate_post("/rate", json=req)
    assert response.status_code == 400

    # missing parameter
    req = dict(generate_random_input())
    req['rate'].pop("time")
    response = client.simulate_post("/rate", json=req)
    assert response.status_code == 400
