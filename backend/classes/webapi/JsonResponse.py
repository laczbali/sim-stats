from flask import make_response
import jsonpickle
import gzip

class JsonResponse:

    def make_response(message):
        content = gzip.compress(
            jsonpickle.encode(message, unpicklable=False).encode('utf-8')
        )

        resp = make_response(content)

        resp.headers["Content-Type"] = "application/json"
        resp.headers["Content-Length"] = len(content)
        resp.headers["Content-Encoding"] = "gzip"

        return resp