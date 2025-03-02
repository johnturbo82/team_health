import sqlite3

def init_db() -> None:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY, question TEXT, low TEXT, high TEXT, category TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS answers (id INTEGER PRIMARY KEY, question_id INTEGER, survey_id TEXT, value INTEGER, user TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS surveys (id INTEGER PRIMARY KEY, uuid TEXT, questions TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()

def insert_answer(question_id: int, survey_uuid: str, value: int, user: str) -> None:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO answers (question_id, survey_id, value, user) VALUES (?, ?, ?, ?)', (question_id, survey_uuid, value, user,))
    conn.commit()
    conn.close()

def get_answers() -> list[any]:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM answers')
    answers = c.fetchall()
    conn.close()
    return answers

def get_all_surveys() -> list[dict]:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM surveys')
    surveys = c.fetchall()
    conn.close()
    return [{'id': s[0], 'uuid': s[1], 'questions': s[2], 'timestamp': s[3]} for s in surveys]

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
    return [{'id': q[0], 'question': q[1], 'low': q[2], 'high': q[3], 'category': q[4]} for q in questions]

def get_random_questions(limit: int) -> list[dict]:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM questions ORDER BY RANDOM() LIMIT ?', (limit,))
    questions = c.fetchall()
    conn.close()
    return [{'id': q[0], 'question': q[1], 'low': q[2], 'high': q[3], 'category': q[4]} for q in questions]

def insert_survey(uuid: str, question_ids: str) -> None:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO surveys (uuid, questions) VALUES (?, ?)', (uuid, question_ids))
    conn.commit()
    conn.close()
    
def get_participant_count() -> dict:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT survey_id, COUNT(DISTINCT user) FROM answers GROUP BY survey_id')
    participant_counts = c.fetchall()
    conn.close()
    return {row[0]: row[1] for row in participant_counts}

def get_answers_by_survey_uuid(survey_uuid: str) -> list[dict]:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT question_id, value, user FROM answers WHERE survey_id = ?', (survey_uuid,))
    answers = c.fetchall()
    conn.close()
    return [{'question_id': a[0], 'value': a[1], 'user': a[2]} for a in answers]

def get_aggregated_answers_by_survey_uuid(survey_uuid: str) -> list[dict]:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT question_id, AVG(value) FROM answers WHERE survey_id = ? GROUP BY question_id', (survey_uuid,))
    answers = c.fetchall()
    conn.close()
    return {a[0]: a[1] for a in answers}

def get_weighted_answers_by_survey_uuid(survey_uuid: str) -> list[dict]:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT question_id, value FROM answers WHERE survey_id = ?', (survey_uuid,))
    answers = c.fetchall()

    # Initialisiere ein Dictionary, um die Häufigkeit der Antworten zu speichern
    weighted_answers = {}
    for question_id, value in answers:
        if question_id not in weighted_answers:
            weighted_answers[question_id] = [0] * 10  # Array mit 10 Einträgen für Antworten von 1 bis 10
        weighted_answers[question_id][value - 1] += 1  # Erhöhe die Häufigkeit der gegebenen Antwort

    return weighted_answers
    