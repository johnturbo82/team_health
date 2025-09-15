from flask import Flask, render_template, redirect, request, send_file, url_for, make_response, session
from . import model
import uuid
import datetime
import yaml
import os

# Ermittle den Pfad zur config.yaml dynamisch
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
config_path = os.path.join(project_root, "config.yaml")

app = Flask(__name__, template_folder='../templates', static_folder='../static')
with open(config_path, "r") as file:
    config = yaml.safe_load(file)
app.secret_key = config["secret_key"]

model.init_db()

USERNAME = config["username"]
PASSWORD = config["password"]

def login_required(f):
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for("login"))
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return "Invalid credentials", 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user = ""
    if not request.cookies.get("user"):
        resp = make_response(redirect(url_for("index")))
        expires_date = datetime.datetime.now() + datetime.timedelta(days=365)
        user = str(uuid.uuid4())
        resp.set_cookie("user", user, expires=expires_date)
        return resp
    else:
        user = request.cookies.get("user")
        
    average_per_category = model.get_average_per_category()
    selfcare = 0
    if "Selbsteinschätzung" in average_per_category:
        selfcare = average_per_category["Selbsteinschätzung"]
        average_per_category.pop("Selbsteinschätzung")
        
    surveys = model.get_all_surveys()
    participant_counts = model.get_participant_count()
    return render_template(
        "index.html", 
        average_per_category=average_per_category, 
        selfcare=selfcare, 
        surveys=surveys, 
        participant_counts=participant_counts, 
        user=user,
        user_name=model.get_user_by_uuid(user),
        logged_in=session.get("logged_in")
    )

@app.route("/survey", methods=["GET"])
def survey():
    user = ""
    if not request.cookies.get("user"):
        resp = make_response(redirect(request.url.replace("localhost:8000", "teamhealth.schoettner.dev")))
        expires_date = datetime.datetime.now() + datetime.timedelta(days=365)
        user = str(uuid.uuid4())
        resp.set_cookie("user", user, expires=expires_date)
        return resp
    else:
        user = request.cookies.get("user")

    survey_uuid = request.args.get("uuid")
    if survey_uuid:
        survey = model.get_survey_by_uuid(survey_uuid)
        if survey:
            question_ids = survey["questions"].split(",")
            questions = model.get_questions_by_ids(question_ids)
            return render_template(
                "survey.html", 
                closed=survey["closed"],
                questions=questions, 
                survey_name=survey["name"], 
                survey_uuid=survey_uuid, 
                user=user, 
                user_name=model.get_user_by_uuid(user),
                logged_in=session.get("logged_in")
            )
    return "Survey not found", 404

@app.route("/submit_survey", methods=["POST"])
def submit_survey():
    user = request.cookies.get("user")
    if not user:
        return redirect(url_for("index"))
    
    survey_uuid = request.form.get("survey_uuid")
    survey = model.get_survey_by_uuid(survey_uuid)
    if not survey:
        return "Survey not found", 404
    
    question_ids = survey["questions"].split(",")
    for question_id in question_ids:
        answer = request.form.get(f"question_{question_id}")
        if answer:
            model.insert_answer(question_id, survey_uuid, answer, user)
    
    return redirect(url_for("success"))

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/create_survey", methods=["POST"])
@login_required
def create_survey():
    survey_name = request.form.get("survey_name")
    questions = model.get_random_questions(6)
    question_ids = ",".join(str(q["id"]) for q in questions)
    survey_uuid = str(uuid.uuid4())
    model.insert_survey(survey_uuid, survey_name, question_ids)
    return redirect(url_for("index"))

@app.route("/results", methods=["GET"])
@login_required
def results():
    user = request.cookies.get("user")
    if not user:
        return redirect(url_for("index"))
    
    survey_uuid = request.args.get("uuid")
    public = request.args.get("public")
    if survey_uuid:
        survey = model.get_survey_by_uuid(survey_uuid)
        if survey:
            question_ids = survey["questions"].split(",")
            return render_template(
                "results.html",
                closed=survey["closed"],
                request=request,
                survey_name=survey["name"], 
                questions=model.get_questions_by_ids(question_ids), 
                answers=model.get_answers_by_survey_uuid(survey_uuid), 
                weighted_answers=model.get_weighted_answers_by_survey_uuid(survey_uuid), 
                average_answers=model.get_average_answers_by_survey_uuid(survey_uuid),
                overall_averages=model.get_overall_question_averages(),
                last_averages=model.get_last_averages(survey_uuid, question_ids),
                survey_uuid=survey_uuid,
                score=model.get_score_by_survey(survey_uuid),
                score_count=model.get_score_count_by_survey(survey_uuid),
                public=public if public else False,
                user=user,
                user_name=model.get_user_by_uuid(user),
                users=model.get_uuid_user_matching(),
                logged_in=session.get("logged_in")
            )
    return "Survey not found", 404

@app.route("/delete_survey", methods=["POST"])
@login_required
def delete_survey():
    survey_uuid = request.form.get("uuid")
    if survey_uuid:
        model.delete_survey(survey_uuid)
    return redirect(url_for("index"))

@app.route("/close_survey", methods=["POST"])
def close_survey():
    survey_uuid = request.form.get("uuid")
    if survey_uuid:
        model.update_survey_closed_status(survey_uuid, True)
    return redirect(url_for("index"))

@app.route("/admin")
@login_required
def admin():
    user = request.cookies.get("user")
    if not user:
        return redirect(url_for("index"))
    return render_template("admin.html", user=user, user_name=model.get_user_by_uuid(user), logged_in=session.get("logged_in"))

@app.route("/download_db")
@login_required
def download_db():
    return send_file(model.DATABASE_FILE, as_attachment=True)

@app.route("/upload_db", methods=["GET", "POST"])
@login_required
def upload_db():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part", 400
        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400
        if file:
            file.save(model.DATABASE_FILE)
            return redirect(url_for("admin"))
    return redirect(url_for("admin"))

@app.route("/set_name", methods=["POST"])
@login_required
def set_name():
    user_name = request.form.get("user_name")
    user_uuid = request.cookies.get("user")
    print(f"Setting name for user {user_uuid} to {user_name}")
    if user_name and user_uuid:
        model.update_user_name(user_uuid, user_name)
    return redirect(url_for("admin"))

@app.route("/set_user_id", methods=["POST"])
@login_required
def set_user_id():
    user_id = request.form.get("user")
    resp = make_response(redirect(url_for("admin")))
    expires_date = datetime.datetime.now() + datetime.timedelta(days=365)
    resp.set_cookie("user", user_id, expires=expires_date)
    return resp

@app.route("/rate_survey", methods=["GET"])
def rate_survey():
    survey_uuid = request.args.get("uuid")
    if survey_uuid:
        survey = model.get_survey_by_uuid(survey_uuid)
        if survey:
            return render_template("rate_survey.html", survey=survey)
    return "Survey not found", 404


@app.route("/submit_score", methods=["POST"])
def submit_score():
    survey_uuid = request.form.get("survey_uuid")
    user_uuid = request.cookies.get("user")
    score = int(request.form.get("score"))

    if not (1 <= score <= 10):
        return "Score muss zwischen 1 und 10 liegen.", 400

    if survey_uuid and user_uuid:
        model.insert_or_update_score(survey_uuid, user_uuid, score)
        return redirect(url_for("index"))
    return "Fehlende Daten.", 400

if __name__ == "__main__":
    model.init_db()
    app.run(debug=True)