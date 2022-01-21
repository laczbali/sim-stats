from flask import Flask, json, make_response, request
from flask_cors import CORS
import gzip
from udp.udp_handler import UdpHandler


app = Flask(__name__)
cors = CORS(
    app,
    origins=["http://127.0.0.1", "http://localhost:4200"],
    supports_credentials=True,
)


@app.route("/test")
def hello():

    udp = UdpHandler()

    content = gzip.compress(
        json.dumps(
            {"message": f"Hello {request.remote_addr}", "udp_data": str(udp.get_data())}
        ).encode("utf-8"),
        5,
    )

    resp = make_response(content)

    resp.headers["Content-Type"] = "application/json"
    resp.headers["Content-Length"] = len(content)
    resp.headers["Content-Encoding"] = "gzip"

    return resp


if __name__ == "__main__":
    udp_handler = UdpHandler()
    udp_handler.udp_test()

    app.run()
