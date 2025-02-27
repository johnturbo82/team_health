from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY, value TEXT)')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.cookies.get('submitted'):
            return redirect(url_for('index'))
        
        value = request.form['value']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO entries (value) VALUES (?)', (value,))
        conn.commit()
        conn.close()
        
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('submitted', 'true')
        return resp
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM entries')
    entries = c.fetchall()
    conn.close()
    return render_template('index.html', entries=entries, submitted=request.cookies.get('submitted'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)