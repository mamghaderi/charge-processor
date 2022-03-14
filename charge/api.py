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
        data = req.media
        resp.text = json.dumps(process_rate(data['rate'], data['cdr']))
        resp.status = falcon.HTTP_OK
        resp.content_type = falcon.MEDIA_JSON
