from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_PARAMS = {
    "host":"localhost",
    "database":"university_db",
    "user":"admin",
    "password":"password123"
}

@app.route('/')
def index(data=None):
    return render_template('index.html',data=data)

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

if __name__ == '__main__':
    app.run(port=5000,debug=True)