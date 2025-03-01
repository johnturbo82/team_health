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
    
    if request.method == 'POST':        
        value = request.form['value']
        model.insert_entry(value, user)
        
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('submitted', 'true')
        return resp
    
    entries = model.get_entries()
    return render_template('index.html', entries=entries, submitted=request.cookies.get('submitted'), user=user)

@app.route('/survey', methods=['GET'])
def survey():
    survey_uuid = request.args.get('uuid')
    if survey_uuid:
        survey = model.get_survey_by_uuid(survey_uuid)
        if survey:
            question_ids = survey['questions'].split(',')
            questions = model.get_questions_by_ids(question_ids)
            return render_template('survey.html', questions=questions)
    return "Survey not found", 404

if __name__ == '__main__':
    model.init_db()
    app.run(debug=True)