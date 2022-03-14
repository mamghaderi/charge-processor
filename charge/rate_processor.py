import datetime

from dateutil import parser
from falcon.errors import HTTPBadRequest


def get_iso_regex_pattern():
    """
        Acceptable iso 8601 format datetime strings:
          2021-04-05T11:27:00.444+00:00
          2021-04-05T11:27:00.444
          2021-04-05T11:27:00.444Z
          2021-04-05T11:27:00Z
          2021-04-05T11:27:00
        :return: a regex to check valid inputs for timestamp iso 8601
    """
    return r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-" \
           r"(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):" \
           r"([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"


def measure_energy(start_energy: int, stop_energy: int, rate: float):
    if stop_energy < start_energy:
        raise HTTPBadRequest(title="Invalid inputs",
                             description="Stop energy value should be greater than start energy value")
    return round((stop_energy - start_energy) * rate / 1000, 3)


def measure_time(start_time: datetime.datetime, stop_time: datetime.datetime, rate: float):
    if stop_time < start_time:
        raise HTTPBadRequest(title="Invalid inputs",
                             description="Stop time value should be greater than start time value")
    delta_time = stop_time - start_time
    return round(delta_time.total_seconds() / 3600 * rate, 3)


def measure_transaction(number: int, rate: float):
    if number == 0:
        raise HTTPBadRequest(title="Invalid inputs",
                             description="The minimum value for transaction is 1")
    return round(rate * number, 3)


def process_rate(rate: dict, cdr: dict):
    # calculate energy
    energy = measure_energy(cdr['meterStart'], cdr['meterStop'], rate['energy'])

    # calculate time
    stop_time = parser.isoparse(cdr['timestampStop'])
    start_time = parser.isoparse(cdr['timestampStart'])
    time = measure_time(start_time, stop_time, rate['time'])

    # calculate transaction
    transaction = measure_transaction(1, rate['transaction'])

    return {
        "components": {'energy': energy, 'time': time, 'transaction': transaction},
        "overall": round(energy + time + transaction, 2)
    }
