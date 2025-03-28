import sqlite3
from contextlib import contextmanager

DATABASE_FILE = 'database.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    try:
        yield conn
    finally:
        conn.close()

def init_db() -> None:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY, question TEXT, low TEXT, high TEXT, category TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS answers (id INTEGER PRIMARY KEY, question_id INTEGER, survey_id TEXT, value INTEGER, user TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        c.execute('CREATE TABLE IF NOT EXISTS surveys (id INTEGER PRIMARY KEY, uuid TEXT, name TEXT, questions TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        conn.commit()

def insert_answer(question_id: int, survey_uuid: str, value: int, user: str) -> None:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM answers WHERE question_id = ? AND survey_id = ? AND user = ?', (question_id, survey_uuid, user))
        existing_entry = c.fetchone()
        if existing_entry:
            c.execute('UPDATE answers SET value = ? WHERE id = ?', (value, existing_entry[0]))
        else:
            c.execute('INSERT INTO answers (question_id, survey_id, value, user) VALUES (?, ?, ?, ?)', (question_id, survey_uuid, value, user))
        
        conn.commit()

def get_answers() -> list[any]:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM answers')
        answers = c.fetchall()
    return answers

def get_all_surveys() -> list[dict]:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM surveys')
        surveys = c.fetchall()
    return [{'id': s[0], 'uuid': s[1], 'name': s[2], 'questions': s[3], 'timestamp': s[4]} for s in surveys]

def get_survey_by_uuid(uuid: str) -> dict:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM surveys WHERE uuid = ?', (uuid,))
        survey = c.fetchone()
    if survey:
        return {'id': survey[0], 'uuid': survey[1], 'name': survey[2], 'questions': survey[3], 'timestamp': survey[4]}
    return None

def get_questions_by_ids(ids: list[str]) -> list[dict]:
    with get_db_connection() as conn:
        c = conn.cursor()
        placeholders = ','.join('?' for _ in ids)
        c.execute(f'SELECT * FROM questions WHERE id IN ({placeholders})', ids)
        questions = c.fetchall()
    return [{'id': q[0], 'question': q[1], 'low': q[2], 'high': q[3], 'category': q[4]} for q in questions]

def get_random_questions(limit: int) -> list[dict]:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM questions ORDER BY RANDOM() LIMIT ?', (limit,))
        questions = c.fetchall()
    return [{'id': q[0], 'question': q[1], 'low': q[2], 'high': q[3], 'category': q[4]} for q in questions]

def insert_survey(uuid: str, name: str, question_ids: str) -> None:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO surveys (uuid, name, questions) VALUES (?, ?, ?)', (uuid, name, question_ids))
        conn.commit()
    
def get_participant_count() -> dict:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT survey_id, COUNT(DISTINCT user) FROM answers GROUP BY survey_id')
        participant_counts = c.fetchall()
    return {row[0]: row[1] for row in participant_counts}

def get_answers_by_survey_uuid(survey_uuid: str) -> dict:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT question_id, value, user FROM answers WHERE survey_id = ?', (survey_uuid,))
        answers = c.fetchall()
    
    answers_dict = {}
    for question_id, value, user in answers:
        if question_id not in answers_dict:
            answers_dict[question_id] = {}
        answers_dict[question_id][user] = value
    
    return answers_dict

def get_average_answers_by_survey_uuid(survey_uuid: str) -> dict:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT question_id, ROUND(AVG(value), 1) FROM answers WHERE survey_id = ? GROUP BY question_id', (survey_uuid,))
        answers = c.fetchall()
    return {a[0]: a[1] for a in answers}

def get_weighted_answers_by_survey_uuid(survey_uuid: str) -> dict:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT question_id, value FROM answers WHERE survey_id = ?', (survey_uuid,))
        answers = c.fetchall()

    weighted_answers = {}
    for question_id, value in answers:
        if question_id not in weighted_answers:
            weighted_answers[question_id] = [0] * 10
        weighted_answers[question_id][value - 1] += 1
    return weighted_answers

def get_overall_question_average() -> dict:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT question_id, ROUND(AVG(value), 1) FROM answers GROUP BY question_id')
        averages = c.fetchall()
    return {a[0]: a[1] for a in averages}

def delete_survey(survey_uuid: str) -> None:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM surveys WHERE uuid = ?', (survey_uuid,))
        c.execute('DELETE FROM answers WHERE survey_id = ?', (survey_uuid,))
        conn.commit()