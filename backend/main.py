from flask import Flask, json, make_response
from flask_cors import CORS
import gzip

app = Flask(__name__)
cors = CORS(
    app,
    origins=["http://localhost:4200"],
    supports_credentials=True,
)

@app.route('/test')
def hello():
    content = gzip.compress(
        json.dumps(
            {
                "message": "I'm alive"
            }
        ).encode("utf-8"),
        5,
    )

    resp = make_response(content)

    resp.headers["Content-Type"] = "application/json"
    resp.headers["Content-Length"] = len(content)
    resp.headers["Content-Encoding"] = "gzip"

    return resp

if __name__ == '__main__':
    app.run()