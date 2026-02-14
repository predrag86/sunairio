from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get("/add")
def add():
    left = request.args.get("left", type=int)
    right = request.args.get("right", type=int)

    if left is None or right is None:
        return jsonify({"error": "Query params 'left' and 'right' must be integers"}), 400

    return jsonify({"sum": left + right}), 200


if __name__ == "__main__":
    # For local dev only. In Docker we run via gunicorn.
    app.run(host="0.0.0.0", port=8080, debug=False)
