from flask import Flask, render_template, request, redirect, url_for, make_response
import model
import uuid
import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    user = ""
    if not request.cookies.get('user'):
        resp = make_response(redirect(url_for('index')))
        expires_date = datetime.datetime.now() + datetime.timedelta(days=365)
        user = str(uuid.uuid4())
        resp.set_cookie('user', user, expires=expires_date)
        return resp
    else:
        user = request.cookies.get('user')
        
    surveys = model.get_all_surveys()
    participant_counts = model.get_participant_count()
    return render_template('index.html', surveys=surveys, participant_counts=participant_counts, user=user)

@app.route('/survey', methods=['GET'])
def survey():
    user = request.cookies.get('user')
    if not user:
        return redirect(url_for('index'))

    survey_uuid = request.args.get('uuid')
    if survey_uuid:
        survey = model.get_survey_by_uuid(survey_uuid)
        if survey:
            question_ids = survey['questions'].split(',')
            questions = model.get_questions_by_ids(question_ids)
            return render_template('survey.html', questions=questions, survey_uuid=survey_uuid, user=user)
    return "Survey not found", 404

@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    user = request.cookies.get('user')
    if not user:
        return redirect(url_for('index'))
    
    survey_uuid = request.form.get('survey_uuid')
    survey = model.get_survey_by_uuid(survey_uuid)
    if not survey:
        return "Survey not found", 404
    
    question_ids = survey['questions'].split(',')
    for question_id in question_ids:
        answer = request.form.get(f'question_{question_id}')
        if answer:
            model.insert_answer(question_id, survey_uuid, answer, user)
    
    return redirect(url_for('index'))

@app.route('/create_survey', methods=['POST'])
def create_survey():
    questions = model.get_random_questions(6)
    question_ids = ','.join(str(q['id']) for q in questions)
    survey_uuid = str(uuid.uuid4())
    model.insert_survey(survey_uuid, question_ids)
    return redirect(url_for('index'))

@app.route('/results', methods=['GET'])
def results():
    user = request.cookies.get('user')
    if not user:
        return redirect(url_for('index'))
    
    survey_uuid = request.args.get('uuid')
    if survey_uuid:
        survey = model.get_survey_by_uuid(survey_uuid)
        if survey:
            question_ids = survey['questions'].split(',')
            questions = model.get_questions_by_ids(question_ids)
            answers = model.get_answers_by_survey_uuid(survey_uuid)
            weighted_answers = model.get_weighted_answers_by_survey_uuid(survey_uuid)
            average_answers = model.get_aggregated_answers_by_survey_uuid(survey_uuid)
            return render_template('results.html', questions=questions, answers=answers, weighted_answers=weighted_answers, average_answers=average_answers, survey_uuid=survey_uuid, user=user)
    return "Survey not found", 404

@app.route('/delete_survey', methods=['POST'])
def delete_survey():
    survey_uuid = request.form.get('uuid')
    if survey_uuid:
        model.delete_survey(survey_uuid)
    return redirect(url_for('index'))

if __name__ == '__main__':
    model.init_db()
    app.run(debug=True)