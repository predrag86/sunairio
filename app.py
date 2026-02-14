from flask import Flask, jsonify, request

app = Flask(__name__)

def _parse_int_param(name: str):
    # request.args.getlist handles repeated query params like ?left=1&left=2
    values = request.args.getlist(name)
    if len(values) == 0:
        return None, f"Missing query param '{name}'"
    if len(values) > 1:
        return None, f"Query param '{name}' must appear only once"

    raw = values[0].strip()
    try:
        return int(raw), None
    except ValueError:
        return None, f"Query param '{name}' must be an integer"

@app.get("/add")
def add():
    left, err_left = _parse_int_param("left")
    if err_left:
        return jsonify({"error": err_left}), 400

    right, err_right = _parse_int_param("right")
    if err_right:
        return jsonify({"error": err_right}), 400

    return jsonify({"sum": left + right}), 200


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
