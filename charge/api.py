import json

import falcon
from falcon.media.validators import jsonschema

from charge.rate_processor import get_iso_regex_pattern, process_rate


class Rate(object):
    rate_request_schema = {
        "type": "object",
        "properties": {
            "rate": {
                "type": "object",
                "properties": {
                    "energy": {"type": "number"},
                    "time": {"type": "number"},
                    "transaction": {"type": "number"}
                },
                "required": ["energy", "time", "transaction"]
            },
            "cdr": {
                "type": "object",
                "properties": {
                    "meterStart": {"type": "integer"},
                    "timestampStart": {
                        "type": "string",
                        "pattern": get_iso_regex_pattern()
                    },
                    "meterStop": {"type": "integer"},
                    "timestampStop": {
                        "type": "string",
                        "pattern": get_iso_regex_pattern()
                    }
                },
                "required": ["meterStart", "timestampStart", "meterStop", "timestampStop"]
            },
        },
        "required": ["rate", "cdr"]
    }

    @jsonschema.validate(req_schema=rate_request_schema)
    def on_post(self, req, resp):
        """
        :param req: a json contains rate and cdr objects,
            and should be pass ``rate_request_schema`` format.
            Example:
                .. code:: python
                        {
                            "rate": {
                                "energy": 0.3, # -- float --
                                "time": 2, # -- float --
                                "transaction": 1 # -- float --
                            },
                            "cdr": {
                                "meterStart": 1204307, # -- Integer --
                                "timestampStart": "2021-04-05T10:04:00Z", # -- timestamp(ISO 8601) string --
                                "meterStop": 1215230, # -- Integer --
                                "timestampStop": "2021-04-05T11:27:00+00:00" # -- timestamp(ISO 8601) string --
                            }
                        }
        :param resp: a json contains components and overall prices
            Example:
                .. code:: python
                        {
                            "components": {
                                "energy": 3.277, # -- float with maximum 3 decimal places --
                                "time": 2.767, # -- float with maximum 3 decimal places --
                                "transaction": 1 # -- float with maximum 3 decimal places --
                            },
                            "overall": 7.04 # -- float with maximum 3 decimal places --
                        }
        """
        data = req.media
        resp.text = json.dumps(process_rate(data['rate'], data['cdr']))
        resp.status = falcon.HTTP_OK
        resp.content_type = falcon.MEDIA_JSON
