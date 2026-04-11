from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database connection config
db_config = {
    'user': 'anirudh',
    'password': 'password123',
    'host': 'localhost',
    'database': 'db'
}

# Initialize MySQL database
def init_db():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print("Database error:", err)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        # Save to MySQL database
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (first_name, last_name) VALUES (%s, %s)', (first_name, last_name))
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            return f"Database Error: {err}"

        return redirect(url_for('greet', fname=first_name, lname=last_name))

    return render_template('index.html')

@app.route('/greet')
def greet():
    fname = request.args.get('fname', '')
    lname = request.args.get('lname', '')
    return render_template('greet.html', fname=fname, lname=lname)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
