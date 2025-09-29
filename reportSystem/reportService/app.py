from flask import Flask, jsonify, request
from clickhouse_driver import Client

app = Flask(__name__)

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

    
@app.route('/api/reports', methods=['GET'])
def get_report_data(): 
    if not clickhouse_client:
        return jsonify({"error": "ClickHouse not connected"}), 500
    
    limit = request.args.get('limit', 100, type=int)
    if limit > 1000:
        limit = 1000
    
    try:
        query = """
        SELECT 
            u.first_name,
            u.last_name,
            t.valueA,
            t.valueB,
            t.valueC,
            t.valueD,
            t.timestamp 
        FROM users u 
        LEFT JOIN telemetry t ON u.user_id = t.user_id
        LIMIT %(limit)s
        """
        data = clickhouse_client.execute(query, {'limit': limit})
        
        columns = ['first_name', 'last_name', 'valueA', 'valueB', 'valueC', 'valueD', 'timestamp']
        
        result = [dict(zip(columns, row)) for row in data]
        
        return jsonify({
            "report": "users_telemetry",
            "data": result,
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
    app.run(host='0.0.0.0', port=5000, debug=True)