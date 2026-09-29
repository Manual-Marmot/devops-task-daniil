import os
import time
import psycopg2
from flask import Flask, jsonify

app = Flask(name)

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
    return jsonify({
        "message": "DevOps Test Application is running!",
        "status": "ok",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "db_version": db_version
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }), 500

@app.route("/data")
def data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_data (
                id SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute(
            "INSERT INTO test_data (message) VALUES (%s) RETURNING id, created_at;",
            (f"Test message at {time.strftime('%Y-%m-%d %H:%M:%S')}",)
        )
        new_id, created_at = cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM test_data;")
        total_records = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({
            "status": "success",
            "new_record": {
                "id": new_id,
                "message": f"Test message at {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "created_at": created_at.isoformat()
            },
            "total_records": total_records
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if name == "main":
    app.run(host="0.0.0.0", port=5000)
