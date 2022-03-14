# Charge Project

A CSMS (charging station management system) such as be.ENERGISED is used to manage charging stations, charging processes
and customers (so-called eDrivers) amongst other things.

One of the most important functionalities of such a CSMS is to calculate a price to a particular charging process so
that the eDriver can be invoiced for the consumed services. Establishing a price for a charging process is usually done
by applying a rate to the CDR (charge detail record) of the corresponding charging process.

This is a microservice developed in python and uses falcon to provide an api that calculate charge prices.

## Project structure

The application code is in the directory `./charge` and the project entrypoint is the `app` object in `./charge/app.py`
.

```bash
.
├── Dockerfile
└── charge
    └── app.py
└── tests
```

## Running locally

To run project locally, create a python environment and install *requirements.txt* as follows:

```bash
python3 -m venv venv2
source venv2/bin/activate
pip install -r requirements.txt 
```

Then simply use *gunicorn* to run project on desire port:

```bash
gunicorn -b 0.0.0.0:8001 charge.app:app
```

You can also run flake8 and tests as follows:

```bash
flake8 .
pytest tests
```

## Running with docker

Make sure to map a local port to container port `80`. To change container expose port, edit Dockerfile

Build and run image with:

```bash
docker build -t charge .
docker run -it -p8001:80 charge
```

You can run tests as follows:

```bash
docker run charge sh -c "pytest tests/"
```

## Test endpoint

Here is an example to call rate endpoint:

```shell
curl --location --request POST 'http://127.0.0.1:8001/rate' \
--header 'Content-Type: application/json' \
--data-raw '{
    "rate": {
        "energy": 0.3,
        "time": 2,
        "transaction": 1
    },
    "cdr": {
        "meterStart": 1204307,
        "timestampStart": "2021-04-05T10:04:00Z",
        "meterStop": 1215230,
        "timestampStop": "2021-04-05T11:27:00+00:00"
    }
}'
```

You should see the results as follows:

```shell
{
    "components": {
        "energy": 3.277,
        "time": 2.767,
        "transaction": 1
    },
    "overall": 7.04
}
```
