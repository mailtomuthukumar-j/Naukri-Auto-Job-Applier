# Naukri Auto Job Applier

Automatically apply to jobs on Naukri.com using Selenium bot + Web UI.

---

## Overview

This project has TWO ways to use it:

### Method 1: Web UI (Recommended - Easy)
Run `app.py` -> Open browser at `http://localhost:5000` -> Fill forms in tabs -> Click "Apply for Jobs"

### Method 2: Direct Bot (Advanced)
Edit config files manually -> Run `python runNaukriBot.py`

---

## Complete Project Structure (Top to Bottom)

```
naukri-auto-job-applier/
│
├── app.py                          # MAIN FILE - Flask web server. Run this for Web UI method.
├── runNaukriBot.py                 # BOT ENGINE - Selenium automation. Auto-launched by app.py,
│                                       or run directly for CLI method.
│
├── templates/
│   └── index.html                  # Web UI page (HTML/CSS/JS) - 5 tabs: Login, Profile, 
│                                       Job Search, Launch Bot, History
│
├── config/                         # *** ALL CONFIG FILES - Fill these ***
│   ├── secrets.py                  # Naukri login credentials (email + password) + AI settings
│   ├── personals.py                # Your personal details (name, phone, city, gender, etc.)
│   ├── search.py                   # Job search preferences (job titles, location, filters)
│   ├── questions.py                # Application answers (experience, salary, notice period, 
│   │                                   cover letter, resume path)
│   ├── settings.py                 # Bot behaviour settings (stealth mode, background, logs)
│   └── resume.py                   # Resume configuration (usually not needed to edit)
│
├── modules/                        # Python helper modules
│   ├── open_chrome.py              # Opens Chrome browser with stealth/undetected mode
│   ├── helpers.py                  # Logging, directory creation, utility functions
│   ├── clickers_and_finders.py     # Selenium click, scroll, find, input functions
│   ├── validator.py                # Validates all config file values
│   ├── ai/                         # AI integration for answering application questions
│   │   ├── openaiConnections.py    # OpenAI GPT integration
│   │   ├── geminiConnections.py    # Google Gemini integration
│   │   ├── deepseekConnections.py  # DeepSeek integration
│   │   └── prompts.py             # AI prompt templates
│   ├── resumes/                    # Resume generation/extraction tools
│   │   ├── generator.py            # Generate resume PDFs
│   │   └── extractor.py           # Extract text from existing resumes
│   ├── images/                     # PNG images for LinkedIn button matching (for LinkedIn version)
│   ├── javascript/                 # JS scripts (e.g., unfollow companies)
│   └── __deprecated__/             # Old/backup files (not used)
│
├── all resumes/
│   └── default/
│       └── resume.pdf              # <<< PUT YOUR RESUME PDF HERE >>>
│
├── all excels/                     # AUTO-CREATED - Contains applied/failed job history CSVs
├── logs/                           # AUTO-CREATED - Contains bot log files
│
├── setup/                          # One-click setup scripts
│   ├── setup.sh                    # Linux/Mac setup
│   ├── windows-setup.bat           # Windows CMD setup
│   └── windows-setup.ps1           # Windows PowerShell setup
│
├── .gitignore                      # Files to exclude from git
├── LICENSE                         # GNU AGPL v3 license
├── README.md                       # This file
└── README_NAUKRI.md                # Brief setup notes for Naukri bot
```

---

## Config Files - What Details Go Where

### 1. `config/secrets.py` - Login Credentials
```
username = "your_naukri_email@example.com"     # Your Naukri registered email
password = "your_naukri_password"               # Your Naukri password
use_AI = False                                   # Set True to use AI for answering questions
ai_provider = "openai"                           # openai / deepseek / gemini
llm_api_url = "https://api.openai.com/v1/"       # API endpoint URL
llm_api_key = ""                                 # Your API key (if using AI)
llm_model = "gpt-4o-mini"                       # AI model name
```

### 2. `config/personals.py` - Personal Details
```
first_name = "Muthu Kumar"           # Your first name
middle_name = ""                     # Middle name (optional)
last_name = "J"                      # Your last name
phone_number = "9042160283"          # Your mobile number
current_city = "Sivakasi"            # Your current city
street = ""                          # Street address
state = "Tamil Nadu"                 # Your state
zipcode = "626123"                   # PIN code
country = "India"                    # Country
ethnicity = "Decline"                # Decline / Hispanic/Latino / Asian / etc.
gender = "Male"                      # Male / Female / Other / Decline
disability_status = "No"             # Yes / No / Decline
veteran_status = "No"                # Yes / No / Decline
```

### 3. `config/search.py` - Job Search Settings
```
search_terms = [                     # Job titles to search (one per line in list)
    "Full Stack Developer",
    "React Developer",
    "Frontend Developer",
]
search_location = "India"            # Location to search in
switch_number = 20                   # Max applications per search term
date_posted = "Past week"            # Past 24 hours / Past week / Past month
naukri_experience = "0"              # Experience filter (0 = fresher)
naukri_date_posted = "7"             # Days: 1, 7, 15, or 30
bad_words = [                        # Skip jobs containing these words
    "10+ years", "Senior Developer", "C++"
]
current_experience = 1               # Your total experience in years
```

### 4. `config/questions.py` - Application Answers
```
default_resume_path = "all resumes/default/resume.pdf"   # Path to your resume
years_of_experience = "1"           # Years of experience for application forms
desired_salary = 400000             # Expected salary in INR
current_ctc = 0                     # Current salary in INR
notice_period = 0                   # Notice period in days
cover_letter = ""                   # Default cover letter text
linkedIn = ""                       # LinkedIn profile URL
website = ""                        # Portfolio website URL
recent_employer = "Fresher"         # Current/most recent company
pause_before_submit = True          # Pause to review before submitting
```

### 5. `config/settings.py` - Bot Behaviour
```
stealth_mode = True                 # Bypass anti-bot detection (recommended)
run_in_background = False           # Run without visible browser
safe_mode = False                   # Safe mode for troubleshooting
keep_screen_awake = True            # Prevent screen sleep during automation
file_name = "all excels/all_applied_applications_history.csv"
failed_file_name = "all excels/all_failed_applications_history.csv"
```

---

## How to Run the Complete Project

There are **3 ways** to run this project:

---

### Method 1: Web UI (Easiest - Recommended)

This method gives you a browser interface with tabs to fill your details and start the bot.

#### Step 1: Install Prerequisites
```bash
# Install Python packages
pip install flask flask-cors selenium pyautogui undetected-chromedriver webdriver-manager setuptools
```

> **Windows users**: You can also run `setup/windows-setup.bat` (double-click) or `setup/windows-setup.ps1` (PowerShell) to auto-install everything.
>
> **Linux/Mac users**: Run `bash setup/setup.sh` to auto-install.

#### Step 2: Add Your Resume
Place your resume PDF file at this exact location:
```
all resumes/default/resume.pdf
```
The bot uploads this resume when applying to jobs.

#### Step 3: Start the Web Server
```bash
python app.py
```
You will see output like:
```
* Running on http://127.0.0.1:5000
```

#### Step 4: Open the Web UI
Open your browser and go to:
```
http://localhost:5000
```

#### Step 5: Fill the 5 Tabs

**Tab 1 - Login (🔐):**
| Field | What to enter |
|-------|--------------|
| Naukri Email | Your Naukri.com registered email address |
| Naukri Password | Your Naukri.com account password |

**Tab 2 - Profile (👤):**
| Field | What to enter |
|-------|--------------|
| First Name | Your first name (e.g., Muthu Kumar) |
| Last Name | Your last name (e.g., J) |
| Phone Number | Your 10-digit mobile number |
| Current City | City you currently live in (e.g., Sivakasi) |
| State | Your state (e.g., Tamil Nadu) |
| Zipcode | PIN code (e.g., 626123) |
| Gender | Select from dropdown |
| Country | India (default) |
| Years of Experience | Total work experience in years |
| Current Experience | Current experience level in years |
| Desired Salary | Expected annual salary in INR (e.g., 400000) |
| Notice Period | Notice period in days (0 if none) |
| Recent Employer | Current/last company name (write "Fresher" if none) |
| Portfolio Website | Your personal website URL (optional) |
| LinkedIn Profile URL | Full LinkedIn profile URL (optional) |
| Naukri Headline | Your professional headline (e.g., "Fresher Full Stack Developer") |
| Cover Letter | Brief introduction about yourself |

**Tab 3 - Job Search (🔍):**
| Field | What to enter |
|-------|--------------|
| Job Titles | One job title per line (e.g., Full Stack Developer, React Developer, etc.) |
| Search Location | Location filter (e.g., India, Chennai, Bangalore) |
| Date Posted | Select: Last 1 day / Last 7 days (default) / Last 15 days / Last 30 days |
| Naukri Experience Filter | Select your experience level for Naukri search filter |
| Experience Level | Check relevant boxes: Internship, Entry level, Associate, Mid-Senior |
| Job Type | Check relevant boxes: Full-time, Internship, Contract, Part-time |
| Skip/Bad Words | Comma-separated words - jobs with these words in description will be skipped |

**Tab 4 - Launch (🚀):**
| Setting | Description |
|---------|-------------|
| Pause Before Submit | Bot pauses before each submission so you can review |
| Run in Background | Hide Chrome window (faster but you can't intervene) |
| Stealth Mode | Bypass anti-bot detection (recommended to keep ON) |

Then click **"Apply for Jobs"** button to start.

**Tab 5 - History (📋):**
Shows all previously applied jobs from the CSV history file.

#### Step 6: Watch the Bot Work
- The bot opens Chrome, logs into Naukri.com
- Searches each job title one by one
- Opens job listings, checks descriptions
- Skips jobs with bad words or high experience requirements
- Clicks Apply, fills forms, uploads resume, submits
- Shows live logs in the Web UI
- Saves results to CSV files

---

### Method 2: Direct Bot (Advanced - No Web UI)

Use this if you want to run the bot directly without the Flask web interface.

#### Step 1: Install Packages
```bash
pip install selenium pyautogui undetected-chromedriver webdriver-manager setuptools
```

#### Step 2: Manually Edit ALL Config Files

You must edit these 5 files in the `config/` folder:

**a) `config/secrets.py`** - Your Naukri login:
```python
username = "your_email@example.com"    # ← Change this
password = "your_naukri_password"       # ← Change this
```

**b) `config/personals.py`** - Your personal details:
```python
first_name = "Muthu Kumar"    # ← Change this
last_name = "J"               # ← Change this
phone_number = "9042160283"   # ← Change this
current_city = "Sivakasi"     # ← Change this
state = "Tamil Nadu"          # ← Change this
zipcode = "626123"            # ← Change this
```

**c) `config/search.py`** - Job search terms and filters:
```python
search_terms = [
    "Full Stack Developer",    # ← Add your job titles
    "React Developer",
]
search_location = "India"      # ← Change this
```

**d) `config/questions.py`** - Application form answers:
```python
years_of_experience = "1"       # ← Change this
desired_salary = 400000         # ← Change this
notice_period = 0               # ← Change this
cover_letter = "..."            # ← Change this
```

**e) `config/settings.py`** - Bot behavior (usually keep defaults):
```python
stealth_mode = True            # Recommended to keep True
run_in_background = False      # Set True to hide browser
```

#### Step 3: Add Resume
```
all resumes/default/resume.pdf    # ← Place your PDF here
```

#### Step 4: Run the Bot
```bash
python runNaukriBot.py
```
The bot will:
1. Open Chrome browser
2. Go to Naukri.com and log in
3. Search each job title
4. Apply to jobs automatically
5. Save history to CSV files in `all excels/`
6. Show a summary popup when done

---

### Method 3: Setup Scripts (One-Click Automation)

For quick installation without typing pip commands manually:

**Windows (CMD):**
```
Double-click setup/windows-setup.bat
```
Or run in terminal:
```
setup\windows-setup.bat
```

**Windows (PowerShell):**
```
Right-click setup/windows-setup.ps1 → Run with PowerShell
```
Or run in terminal:
```
powershell -ExecutionPolicy Bypass -File setup\windows-setup.ps1
```

**Linux / Mac:**
```bash
bash setup/setup.sh
```

These scripts automatically:
- Check if Python is installed
- Install all required pip packages
- Create necessary directories
- Print instructions for next steps

---

## Output Files (Auto-Created)

| File | Description |
|------|-------------|
| `all excels/all_applied_applications_history.csv` | Successfully applied jobs |
| `all excels/all_failed_applications_history.csv` | Jobs that failed during apply |
| `logs/log.txt` | All bot activity logs |
| `logs/bot_output.log` | Bot console output (when using Web UI) |

---

## Note: How to Use AI (Claude/ChatGPT) to Fill Config Files

If you want to fill all config files quickly without manually editing each one, follow this method:

### Step 1: Create a ZIP of the project folder

### Step 2: Upload the ZIP to Claude AI or ChatGPT

### Step 3: Use this prompt (copy-paste):

```
I have a Naukri Auto Job Applier project. Here is my personal information:

- Naukri Email: your_email@example.com
- Naukri Password: your_password
- Full Name: Muthu Kumar J
- Phone: 9042160283
- City: Sivakasi
- State: Tamil Nadu
- Country: India
- Years of Experience: 1
- Current CTC: 0 (Fresher)
- Desired Salary: 400000 INR
- Notice Period: 0 days
- Recent Employer: Fresher
- Portfolio Website: https://your-portfolio.com
- LinkedIn: https://linkedin.com/in/yourprofile
- Cover Letter: I am a passionate Full Stack Developer skilled in React, Node.js, and PHP...

Job Search Preferences:
- Job Titles: Full Stack Developer, React Developer, Frontend Developer, Web Developer, Node.js Developer, JavaScript Developer, PHP Developer
- Location: India
- Experience Level: Entry level
- Job Type: Full-time, Internship, Contract

Please fill in ALL config files in the `/config/` folder with these details:
1. config/secrets.py - Put my email and password
2. config/personals.py - Put my personal details
3. config/search.py - Put my job search preferences
4. config/questions.py - Put my experience, salary, cover letter
5. config/settings.py - Leave defaults (stealth_mode = True, run_in_background = False)

IMPORTANT: 
- Keep all Python syntax correct (quotes, commas, etc.)
- Do NOT change any variable names
- Make sure strings are properly quoted
- Set use_AI = False in secrets.py
- Set pause_before_submit = True in questions.py
```

### Step 4: Claude/ChatGPT will return the updated config files with all values filled in

### Step 5: Copy each file content back into the corresponding `config/*.py` file

### Step 6: Place your resume PDF at `all resumes/default/resume.pdf`

### Step 7: Run the project (choose ONE method)
```
# Web UI method (easier):
python app.py
# Then open http://localhost:5000 in browser

# OR Direct Bot method (no browser needed):
python runNaukriBot.py
```

---

## Requirements

- Python 3.8+
- Google Chrome (latest version)
- pip: `flask`, `flask-cors`, `selenium`, `pyautogui`, `undetected-chromedriver`
- Windows / Linux / macOS

## Important Notes

- Never commit real passwords to GitHub
- This tool is for personal use only
- Use responsibly and respect Naukri.com terms of service
- If Chrome driver fails, try `safe_mode = True` in `config/settings.py`
