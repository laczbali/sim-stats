from flask import json, make_response, request
import gzip

class JsonResponse:

    def make_response(message):
        content = gzip.compress(
            json.dumps( message ).encode("utf-8"), 5,
        )

        resp = make_response(content)

        resp.headers["Content-Type"] = "application/json"
        resp.headers["Content-Length"] = len(content)
        resp.headers["Content-Encoding"] = "gzip"

        return resp