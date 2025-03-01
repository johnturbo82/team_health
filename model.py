import sqlite3

def init_db() -> None:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY, question TEXT, category TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY, value INTEGER, user TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS surveys (id INTEGER PRIMARY KEY, uuid TEXT, questions TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()

def insert_entry(value: int, user: str) -> None:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO entries (value, user) VALUES (?, ?)', (value, user,))
    conn.commit()
    conn.close()

def get_entries() -> list[any]:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM entries')
    entries = c.fetchall()
    conn.close()
    return entries

def get_survey_by_uuid(uuid: str) -> dict:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM surveys WHERE uuid = ?', (uuid,))
    survey = c.fetchone()
    conn.close()
    if survey:
        return {'id': survey[0], 'uuid': survey[1], 'questions': survey[2], 'timestamp': survey[3]}
    return None

def get_questions_by_ids(ids: list[str]) -> list[dict]:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    placeholders = ','.join('?' for _ in ids)
    c.execute(f'SELECT * FROM questions WHERE id IN ({placeholders})', ids)
    questions = c.fetchall()
    conn.close()
    return [{'id': q[0], 'question': q[1], 'category': q[2]} for q in questions]