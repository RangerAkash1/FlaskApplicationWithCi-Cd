import os
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from logger_client import send_log   

app = Flask(__name__)

# Configure MySQL from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'default_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'default_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'default_db')

# Initialize MySQL
mysql = MySQL(app)

def init_db():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message TEXT
        );
        ''')
        mysql.connection.commit()
        cur.close()

@app.before_request
def log_request():
    send_log("info", f"Incoming request: {request.method} {request.path}")

@app.route('/')
def hello():
    send_log("info", "Fetching messages from DB")
    cur = mysql.connection.cursor()
    cur.execute('SELECT message FROM messages')
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    send_log("info", f"New message submitted: {new_message}")
    
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
    mysql.connection.commit()
    cur.close()
    
    return jsonify({'message': new_message})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/api/messages', methods=['GET'])
def get_messages():
    send_log("info", "API call to fetch all messages")
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, message FROM messages')
    rows = cur.fetchall()
    cur.close()
    
    messages = [{"id": r[0], "message": r[1]} for r in rows]
    return jsonify(messages)

@app.route('/delete/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    send_log("warning", f"Deleting message with id={message_id}")
    
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM messages WHERE id = %s', (message_id,))
    mysql.connection.commit()
    cur.close()
    
    return jsonify({"status": "success", "deleted_id": message_id})

@app.route('/health', methods=['GET'])
def health_check():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT 1')
        cur.close()
        send_log("info", "Health check passed")
        return jsonify({"status": "UP"}), 200
    except Exception as e:
        send_log("error", f"Health check failed: {str(e)}")
        return jsonify({"status": "DOWN"}), 500
