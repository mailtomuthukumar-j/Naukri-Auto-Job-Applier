# Naukri Auto Job Applier 🤖
### For: Muthu Kumar J

## ⚙️ Setup

### Step 1 — Install packages
```
pip install undetected-chromedriver pyautogui setuptools flask flask-cors selenium webdriver-manager
```

### Step 2 — Enter Naukri password
Open `config/secrets.py` → Replace `YOUR_NAUKRI_PASSWORD_HERE`

### Step 3 — Run
```
python runNaukriBot.py
```

## 📋 Config Files
| File | What to change |
|------|---------------|
| `config/secrets.py` | ⚠️ Naukri password |
| `config/search.py` | Job titles, location |
| `config/personals.py` | Name, phone, city |
| `config/questions.py` | Salary, experience, notice period |

## 📁 Output
- `all excels/all_applied_applications_history.csv` — Applied jobs
- `all excels/all_failed_applications_history.csv` — Failed jobs
