import os
import time
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

DB_HOST = os.getenv("DATABASE_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "app_db")
DB_USER = os.getenv("POSTGRES_USER", "app_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "secret123")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.route("/")
def index():
    return jsonify({"message": "Flask application is running"})

@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route("/data")
def data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS test_data (id SERIAL PRIMARY KEY, value VARCHAR(100));")
        cur.execute("INSERT INTO test_data (value) VALUES ('sample_data');")
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM test_data;")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({"status": "success", "records_count": count}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
