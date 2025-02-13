import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Siyavula Authentication URL
SIYAVULA_AUTH_URL = "https://www.siyavula.com/api/siyavula/v1/get-token"

def siyavula_get_token(username, password, region="ZA", curriculum="CAPS"):
    """
    Authenticate with Siyavula API and retrieve tokens.
    
    :param username: Siyavula username
    :param password: Siyavula password
    :param region: Default 'ZA'
    :param curriculum: Default 'CAPS'
    :return: JSON response with authentication tokens or error message
    """
    payload = {
        "name": username,
        "password": password,
        "region": region,
        "curriculum": curriculum
    }

    try:
        response = requests.post(SIYAVULA_AUTH_URL, json=payload, timeout=10)
        response_data = response.json()

        if response.status_code == 200:
            return {"status": "success", "tokens": response_data}
        else:
            return {"status": "error", "message": response_data.get("message", "Failed to authenticate")}, response.status_code

    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/siyavula-auth", methods=["POST"])
def siyavula_auth():
    """Flask endpoint for Siyavula authentication."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required"}), 400

    result = siyavula_get_token(username, password)
    return jsonify(result), (result.get("status_code", 200) if isinstance(result, tuple) else 200)

if __name__ == "__main__":
    app.run(debug=True)
