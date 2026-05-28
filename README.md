# 🎯 Naukri Auto Job Applier

Automatically apply to Naukri.com jobs using a simple web UI — no need to edit any config files manually.

---

## 🚀 Quick Start

### 1. Install Requirements

```bash
pip install flask flask-cors selenium pyautogui undetected-chromedriver
```

### 2. Add Your Resume

Place your resume PDF at:
```
all resumes/default/resume.pdf
```

### 3. Run the App

```bash
python app.py
```

### 4. Open the Web UI

```
http://localhost:5000
```

Fill in your details across the tabs and click **🎯 Apply for Jobs**.

---

## 📁 Project Structure

```
├── app.py                  ← Flask server (run this)
├── runNaukriBot.py         ← Bot engine (auto-launched by app.py)
├── templates/
│   └── index.html          ← Web UI
├── config/
│   ├── secrets.py          ← Naukri credentials (auto-filled by UI)
│   ├── personals.py        ← Personal info (auto-filled by UI)
│   ├── search.py           ← Job search settings (auto-filled by UI)
│   └── questions.py        ← Application answers (auto-filled by UI)
├── all resumes/
│   └── default/
│       └── resume.pdf      ← ⚠️ Add your resume here
├── all excels/             ← Applied jobs history (auto-created)
└── logs/                   ← Bot logs (auto-created)
```

---

## 🖥️ Web UI Tabs

| Tab | What to fill |
|-----|-------------|
| 🔐 Login | Naukri email & password |
| 👤 Profile | Name, phone, city, salary, headline, cover letter |
| 🔍 Job Search | Job titles, experience filter, date range, bad words |
| 🚀 Launch Bot | Settings + start button + live logs |
| 📋 History | View all applied jobs |

---

## ⚠️ Important Notes

- Credentials are **never stored permanently** — only written locally when you click the button
- This tool is for **personal use only**
- Make sure **Google Chrome** is installed before running

---

## 🛠️ Requirements

- Python 3.8+
- Google Chrome (latest)
- pip packages: `flask`, `flask-cors`, `selenium`, `pyautogui`, `undetected-chromedriver`
