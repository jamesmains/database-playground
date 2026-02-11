from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
import docker
import os

app = Flask(__name__)

DB_PARAMS = {
    "host":"db",
    "database":"university_db",
    "user":"admin",
    "password":"password123"
}

client = docker.from_env()

@app.route('/')
def index(data=None):
    return render_template('index.html',data=data)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/view/<table_name>')
def view_table(table_name):
    # Map friendly tables
    allowed_tables = {
        "students": "students",
        "courses": "courses",
        "enrollments": "enrollments"
    }

    if table_name not in allowed_tables:
        return "Table not found", 404
    
    db_table = allowed_tables[table_name]
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Get the data
    cur.execute(f"SELECT * FROM {db_table} ORDER BY id ASC")
    rows = cur.fetchall()

    # Get column names
    columns = rows[0].keys() if rows else []

    cur.close()
    conn.close()

    return render_template('table_view.html',
                            title=table_name.capitalize(),
                            table_name = table_name,
                            columns = columns,
                            rows = rows
                           )

@app.route('/bad-example')
def bad_example():
    return render_template('bad-example.html')

@app.route('/reset-database', methods=['POST'])
def reset_database():
    init_file = open("init.sql")
    data_file = open("dummy-data.sql")
    reset_command = init_file.read()
    fill_command = data_file.read()
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(reset_command)
    conn.commit()
    cur.execute(fill_command)
    conn.commit()
    init_file.close()
    data_file.close()
    return jsonify({"status": "Database Stopped"})

@app.route('/database-running', methods=['GET'])
def database_running():
    try:
        # Use the label search we discussed earlier
        containers = client.containers.list(all=True, filters={"label": "com.docker.compose.service=db"})
        
        if not containers:
            return jsonify({"status": "Not Found"})

        db_container = containers[0]
        
        # Docker status can be: 'running', 'exited', 'paused', 'restarting'
        if db_container.status == 'running':
            return jsonify({"status": "Running", "color": "green"})
        else:
            return jsonify({"status": "Stopped", "color": "red"})
            
    except Exception as e:
        return jsonify({"status": "Error", "error": str(e)})
    
@app.route('/api/<table_name>', methods=['POST'])
@app.route('/api/<table_name>/<int:entry_id>', methods=['PUT', 'DELETE'])
def handle_api(table_name, entry_id=None):
    # Security: Only allow specific tables
    valid_tables = ['students', 'courses', 'enrollments']
    if table_name not in valid_tables:
        return jsonify({"error": "Invalid table"}), 400

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        if request.method == 'DELETE':
            cur.execute(f"DELETE FROM {table_name} WHERE id = %s", (entry_id,))
            
        elif request.method == 'POST':
            data = request.json
            columns = data.keys()
            values = [data[col] for col in columns]
            # Build dynamic SQL: INSERT INTO table (col1, col2) VALUES (%s, %s)
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(values))})"
            cur.execute(query, values)
            
        elif request.method == 'PUT':
            data = request.json
            # Remove 'id' from data if it exists so we don't try to update the PK
            data.pop('id', None)
            columns = data.keys()
            values = [data[col] for col in columns]
            # Build dynamic SQL: UPDATE table SET col1=%s, col2=%s WHERE id=%s
            set_clause = ", ".join([f"{col}=%s" for col in columns])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
            cur.execute(query, values + [entry_id])

        conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()
@app.route('/run-sql', methods=['POST'])
def run_sql():
    query = request.json.get('query')

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query)

        if query.strip().upper().startswith("SELECT"):
            results = cur.fetchall()
        else:
            conn.commit()
            results = "Success!"
        
        cur.close()
        conn.close()
        return jsonify({"data": results})
    except Exception as e:
        return jsonify({"error":str(e)}), 400

@app.route('/db-control', methods=['POST'])
def control_db():
    action = request.json.get('action')
    containers = client.containers.list(all=True, filters={"label": "com.docker.compose.service=db"})
    if not containers:
        return jsonify({"error": "Database container not found"}), 404            
    target_db = containers[0]

    try:
        if action == 'stop':
            target_db.stop()
            return jsonify({"status": "Database Stopped"})
        elif action == 'start':
            target_db.start()
            return jsonify({"status": "Database Started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/db-stats', methods=['GET'])
def get_stats():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify({"table_count":count})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)