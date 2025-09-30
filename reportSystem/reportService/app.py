from flask import Flask, jsonify, request
from clickhouse_driver import Client
from flask_cors import CORS
import jwt
from functools import wraps

app = Flask(__name__)
CORS(app)

JWKS_URL = "http://keycloak:8080/realms/reports-realm/protocol/openid-connect/certs"
jwks_client = jwt.PyJWKClient(JWKS_URL)


clickhouse_client = None

def init_clickhouse():
    global clickhouse_client
    try:
        clickhouse_client = Client(
            host='clickhouse',
            port=9000,
            user='admin',
            password='admin123',
            database='report'
        )
        print("Connected to ClickHouse successfully")
    except Exception as e:
        print(f"Error connecting to ClickHouse: {e}")


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing Authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            decoded_token = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_exp": False}
            )
            
            request.decoded_token = decoded_token
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401
    
    return decorated_function  
    
@app.route('/api/reports', methods=['GET'])
@jwt_required
def get_report_data(): 
    if "prothetic_user" not in request.decoded_token.get("realm_access", {}).get("roles", []):
        return jsonify({"error": "Нет доступа"}), 403

    if not clickhouse_client:
        return jsonify({"error": "ClickHouse not connected"}), 500

    username = request.decoded_token.get("preferred_username")
    first_name = request.decoded_token.get("given_name")
    last_name = request.decoded_token.get("family_name")
    email = request.decoded_token.get("email")
    
    if not username:
        return jsonify({"error": "Username not found in token"}), 400  
    
    limit = request.args.get('limit', 100, type=int)
    if limit > 1000:
        limit = 1000
    
    try:
        query = """
        SELECT 
            t.valueA,
            t.valueB,
            t.valueC,
            t.valueD,
            t.timestamp 
        FROM users u 
        LEFT JOIN telemetry t ON u.user_id = t.user_id
        WHERE u.username = %(username)s
        LIMIT %(limit)s
        """
        data = clickhouse_client.execute(query, {'username': username,'limit': limit})
        
        columns = ['valueA', 'valueB', 'valueC', 'valueD', 'timestamp']
        
        result = [dict(zip(columns, row)) for row in data]

        return jsonify({
            "report": "users_prothetic_telemetry",
            "user": {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "email": email
            },
            "telemetry_data": result,
            "count": len(data)
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to fetch report data: {str(e)}"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    ch_status = "connected" if clickhouse_client else "disconnected"
    
    return jsonify({
        "status": "healthy",
        "clickhouse": ch_status
    }), 200



init_clickhouse()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)