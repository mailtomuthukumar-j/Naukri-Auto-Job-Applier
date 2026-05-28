from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import csv
import subprocess
import sys
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

PATH = 'all excels/'

def write_secrets(data):
    content = f'''username = "{data.get('username', '')}"
password = "{data.get('password', '')}"
use_AI = False
ai_provider = "openai"
llm_api_url = "https://api.openai.com/v1/"
llm_api_key = ""
llm_model = "gpt-4o-mini"
llm_spec = "openai"
stream_output = False
'''
    with open('config/secrets.py', 'w') as f:
        f.write(content)

def write_personals(data):
    content = f'''first_name = "{data.get('first_name', '')}"
middle_name = "{data.get('middle_name', '')}"
last_name = "{data.get('last_name', '')}"
phone_number = "{data.get('phone_number', '')}"
current_city = "{data.get('current_city', '')}"
street = "{data.get('street', '')}"
state = "{data.get('state', '')}"
zipcode = "{data.get('zipcode', '')}"
country = "{data.get('country', 'India')}"
ethnicity = "Decline"
gender = "{data.get('gender', 'Male')}"
disability_status = "No"
veteran_status = "No"
'''
    with open('config/personals.py', 'w') as f:
        f.write(content)

def write_search(data):
    raw_terms = data.get('search_terms', '')
    terms = [t.strip() for t in raw_terms.split('\n') if t.strip()]
    terms_str = ',\n    '.join([f'"{t}"' for t in terms])

    raw_bad = data.get('bad_words', '')
    bad = [t.strip() for t in raw_bad.split(',') if t.strip()]
    bad_str = ', '.join([f'"{b}"' for b in bad])

    exp_levels = data.get('experience_level', ['Entry level'])
    exp_str = ', '.join([f'"{e}"' for e in exp_levels])

    job_types = data.get('job_type', ['Full-time'])
    jtype_str = ', '.join([f'"{j}"' for j in job_types])

    content = f'''search_terms = [
    {terms_str}
]
search_location = "{data.get('search_location', 'India')}"
switch_number = 20
randomize_search_order = False
sort_by = ""
date_posted = "{data.get('date_posted', 'Past week')}"
salary = ""
easy_apply_only = True
experience_level = [{exp_str}]
job_type = [{jtype_str}]
on_site = ["Remote", "Hybrid", "On-site"]
companies = []
location = []
industry = []
job_function = []
job_titles = []
benefits = []
commitments = []
under_10_applicants = False
in_your_network = False
fair_chance_employer = False
pause_after_filters = True
naukri_experience = "{data.get('naukri_experience', '0')}"
naukri_date_posted = "{data.get('naukri_date_posted', '7')}"
about_company_bad_words = ["Crossover"]
about_company_good_words = []
bad_words = [{bad_str}]
security_clearance = False
did_masters = {str(data.get('did_masters', False))}
current_experience = {int(data.get('current_experience', 1))}
'''
    with open('config/search.py', 'w') as f:
        f.write(content)

def write_questions(data):
    content = f'''default_resume_path = "all resumes/default/resume.pdf"
years_of_experience = "{data.get('years_of_experience', '1')}"
require_visa = "No"
website = "{data.get('website', '')}"
linkedIn = "{data.get('linkedIn', '')}"
us_citizenship = "Non-citizen seeking work authorization"
linkedin_headline = "{data.get('linkedin_headline', '')}"
linkedin_summary = "{data.get('linkedin_summary', '')}"
cover_letter = "{data.get('cover_letter', '')}"
recent_employer = "{data.get('recent_employer', 'Fresher')}"
confidence_level = "8"
desired_salary = {int(data.get('desired_salary', 400000))}
current_ctc = {int(data.get('current_ctc', 0))}
notice_period = {int(data.get('notice_period', 0))}
pause_before_submit = {str(data.get('pause_before_submit', True))}
pause_at_failed_question = True
overwrite_previous_answers = False
'''
    with open('config/questions.py', 'w') as f:
        f.write(content)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/save-config', methods=['POST'])
def save_config():
    try:
        data = request.get_json()
        write_secrets(data)
        write_personals(data)
        write_search(data)
        write_questions(data)
        return jsonify({"status": "ok", "message": "Config saved successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/start-bot', methods=['POST'])
def start_bot():
    try:
        data = request.get_json()
        write_secrets(data)
        write_personals(data)
        write_search(data)
        write_questions(data)
        os.makedirs('logs', exist_ok=True)
        proc = subprocess.Popen(
            [sys.executable, 'runNaukriBot.py'],
            stdout=open('logs/bot_output.log', 'a'),
            stderr=subprocess.STDOUT,
            cwd=os.getcwd()
        )
        return jsonify({"status": "ok", "message": f"Bot started! PID: {proc.pid}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/bot-logs', methods=['GET'])
def bot_logs():
    try:
        log_path = 'logs/bot_output.log'
        if not os.path.exists(log_path):
            return jsonify({"logs": "No logs yet..."})
        with open(log_path, 'r') as f:
            lines = f.readlines()
            last_50 = ''.join(lines[-50:])
        return jsonify({"logs": last_50})
    except Exception as e:
        return jsonify({"logs": str(e)})

@app.route('/applied-jobs', methods=['GET'])
def get_applied_jobs():
    try:
        jobs = []
        with open(PATH + 'all_applied_applications_history.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                jobs.append({
                    'Job_ID': row.get('Job ID',''), 'Title': row.get('Title',''),
                    'Company': row.get('Company',''), 'HR_Name': row.get('HR Name',''),
                    'HR_Link': row.get('HR Link',''), 'Job_Link': row.get('Job Link',''),
                    'External_Job_link': row.get('External Job link',''),
                    'Date_Applied': row.get('Date Applied','')
                })
        return jsonify(jobs)
    except FileNotFoundError:
        return jsonify({"error": "No applications history found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
