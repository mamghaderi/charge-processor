import datetime
import decimal
import random
import unittest
import faker
import jsonschema
from falcon.errors import HTTPBadRequest

from charge.rate_processor import measure_energy, measure_time, measure_transaction, process_rate
from tests.test_api import generate_random_input


class TestRateUtils(unittest.TestCase):

    def setUp(self) -> None:
        self.rate = random.uniform(0, 12)
        self.component_decimal_place = 3
        self.overall_decimal_places = 2
        self.process_response_schema = {
            "type": "object",
            "properties": {
                "components": {
                    "type": "object",
                    "properties": {
                        "energy": {"type": "number"},
                        "time": {"type": "number"},
                        "transaction": {"type": "number"}
                    },
                    "required": ["energy", "time", "transaction"]
                },
                "overall": {"type": "number"}
            },
            "required": ["components", "overall"]
        }
        self.random_input = generate_random_input()

    def tearDown(self) -> None:
        pass

    def test_measure_energy(self):
        # test logic with valid inputs
        energy = measure_energy(138745, 894579, self.rate)
        output_expectation = round((894579 - 138745) * self.rate / 1000, self.component_decimal_place)
        assert energy == output_expectation

        # test invalid input: stop-energy < start_energy
        with self.assertRaises(HTTPBadRequest):
            measure_energy(999138745, 894579, self.rate)

    def test_measure_time(self):
        # test logic with valid inputs
        faker_ = faker.Faker()
        start_time = faker_.date_time()
        delta_time = datetime.timedelta(minutes=random.randrange(1, 60))
        stop_time = start_time + delta_time
        output_expectation = round(delta_time.seconds / 3600 * self.rate, self.component_decimal_place)
        time = measure_time(start_time, stop_time, self.rate)
        assert time == output_expectation

        # test invalid input: stop-time < start_time
        with self.assertRaises(HTTPBadRequest):
            measure_time(stop_time, start_time, self.rate)

    def test_measure_transaction(self):
        # test logic with valid inputs
        number = random.randrange(1, 10000)
        transaction = measure_transaction(number, self.rate)
        assert transaction == round(self.rate * number, self.component_decimal_place)

        # test invalid input: zero number of transactions
        with self.assertRaises(HTTPBadRequest):
            measure_transaction(0, self.rate)

    def test_process_rate_output_format(self):
        result = process_rate(self.random_input['rate'], self.random_input['cdr'])

        # validate json format
        assert jsonschema.validate(result, self.process_response_schema) is None

        # validate returned value decimal places
        assert decimal.Decimal(result['components']['energy']).as_tuple().exponent \
               <= self.component_decimal_place
        assert decimal.Decimal(result['components']['time']).as_tuple().exponent \
               <= self.component_decimal_place
        assert decimal.Decimal(result['components']['transaction']).as_tuple().exponent \
               <= self.component_decimal_place
        assert decimal.Decimal(result['overall']).as_tuple().exponent <= self.overall_decimal_places
