'''
Naukri Auto Job Applier Bot
For: Muthu Kumar J

What this bot does:
1. Opens naukri.com
2. Logs in with your credentials
3. Searches jobs based on your search_terms
4. Clicks "Apply" on each job
5. Fills form automatically
6. Saves history to CSV
'''

import os
import csv
import re
import time
import pyautogui

csv.field_size_limit(1000000)

from random import choice, shuffle, randint
from datetime import datetime
from urllib.parse import quote_plus

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    NoSuchElementException, ElementClickInterceptedException,
    NoSuchWindowException, ElementNotInteractableException, WebDriverException
)

from config.personals import *
from config.questions import *
from config.search import *
from config.secrets import use_AI, username, password, ai_provider
from config.settings import *
from modules.open_chrome import *
from modules.helpers import *
from modules.clickers_and_finders import *

pyautogui.FAILSAFE = False

# ─── Global State ─────────────────────────────────────────────────────────────
if run_in_background:
    pause_at_failed_question = False
    pause_before_submit = False
    run_non_stop = False

first_name  = first_name.strip()
middle_name = middle_name.strip()
last_name   = last_name.strip()
full_name   = (first_name + " " + middle_name + " " + last_name).strip() if middle_name else (first_name + " " + last_name).strip()

easy_applied_count = 0
failed_count       = 0
skip_count         = 0
naukri_tab         = None

re_experience = re.compile(r'[(]?\s*(\d+)\s*[)]?\s*[-to]*\s*\d*[+]*\s*year[s]?', re.IGNORECASE)

desired_salary_str     = str(desired_salary)
current_ctc_str        = str(current_ctc)
notice_period_str      = str(notice_period)
notice_period_months   = str(notice_period // 30)


# ─── Login ────────────────────────────────────────────────────────────────────
def is_logged_in_NK() -> bool:
    '''Check if logged into Naukri'''
    try:
        url = driver.current_url
        if 'naukri.com' not in url:
            return False
        # If login page → not logged in
        if 'login' in url or 'mnjuser' not in url and driver.find_elements(By.CSS_SELECTOR, '.login-layer, #login_Layer'):
            return False
        # Check for user avatar / profile menu
        if driver.find_elements(By.CSS_SELECTOR, '.nI-gNb-drawer__icon, .user-name, [class*="avatar"]'):
            return True
        return False
    except:
        return False


def login_NK() -> None:
    '''Login to Naukri.com'''
    driver.get("https://www.naukri.com/nlogin/login")
    sleep(2)

    if username == "username@example.com" or password == "YOUR_NAUKRI_PASSWORD_HERE":
        pyautogui.alert(
            "Please enter your Naukri email and password in config/secrets.py\nOr login manually in the browser.",
            "Login Required", "Okay"
        )
        manual_login_retry(is_logged_in_NK, 3)
        return

    try:
        # Enter email
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Enter your active Email ID / Username"]'))
        )
        email_field.clear()
        email_field.send_keys(username)
        sleep(0.5)

        # Enter password
        pwd_field = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Enter your password"]')
        pwd_field.clear()
        pwd_field.send_keys(password)
        sleep(0.5)

        # Click login
        login_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], .loginButton')
        login_btn.click()
        sleep(3)

        if is_logged_in_NK():
            print_lg("✅ Naukri login successful!")
        else:
            print_lg("Auto-login may have failed. Please login manually.")
            manual_login_retry(is_logged_in_NK, 3)

    except Exception as e:
        print_lg("Naukri auto-login failed:", e)
        pyautogui.alert(
            "Auto-login failed. Please login manually in the browser.\nClick OK once logged in.",
            "Manual Login", "Okay"
        )
        manual_login_retry(is_logged_in_NK, 3)


# ─── Search ───────────────────────────────────────────────────────────────────
def build_naukri_search_url(search_term: str, location: str) -> str:
    '''Build Naukri search URL'''
    # Naukri URL format: /jobs-listings/keyword-location
    keyword_slug = search_term.lower().replace(" ", "-")
    location_slug = location.lower().replace(" ", "-") if location and location != "India" else ""

    if location_slug and location_slug != "india":
        url = f"https://www.naukri.com/{keyword_slug}-jobs-in-{location_slug}"
    else:
        url = f"https://www.naukri.com/{keyword_slug}-jobs"

    # Add freshness filter (last 7 days = &jobAge=7)
    url += "?jobAge=7&experience=0&ctcFilter=0"
    return url


def get_applied_job_ids() -> set:
    '''Load already applied job IDs'''
    job_ids = set()
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row: job_ids.add(row[0])
    except FileNotFoundError:
        print_lg("No history file yet — starting fresh.")
    return job_ids


# ─── Job Listings ─────────────────────────────────────────────────────────────
def get_job_listings_naukri() -> list:
    '''Get all job cards on current page'''
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                '.srp-jobtuple-wrapper, article.jobTuple, .job-tuple'))
        )
        listings = driver.find_elements(By.CSS_SELECTOR, '.srp-jobtuple-wrapper')
        if not listings:
            listings = driver.find_elements(By.CSS_SELECTOR, 'article.jobTuple')
        if not listings:
            listings = driver.find_elements(By.CSS_SELECTOR, '.job-tuple')
        print_lg(f"Found {len(listings)} job listings")
        return listings
    except Exception as e:
        print_lg("No job listings found:", e)
        return []


def get_job_details_naukri(job: WebElement) -> tuple:
    '''Extract job info from card'''
    job_id    = "unknown"
    title     = "Unknown"
    company   = "Unknown"
    location  = "Unknown"
    job_link  = ""

    try:
        scroll_to_view(driver, job, True)

        # Job ID from data attribute
        try:
            job_id = job.get_attribute('data-job-id') or job.get_attribute('id') or f"nk_{randint(10000,99999)}"
        except:
            job_id = f"nk_{randint(10000,99999)}"

        # Title
        try:
            title_el = job.find_element(By.CSS_SELECTOR, 'a.title, .job-title a, h2.title a, a[title]')
            title = title_el.text or title_el.get_attribute('title') or "Unknown"
            job_link = title_el.get_attribute('href') or ""
        except: pass

        # Company
        try:
            company = job.find_element(By.CSS_SELECTOR, '.comp-name, .company-name, a.comp-name').text
        except: pass

        # Location
        try:
            location = job.find_element(By.CSS_SELECTOR, '.locWdth, .job-location, .location').text
        except: pass

    except Exception as e:
        print_lg("Error extracting job details:", e)

    return job_id, title, company, location, job_link


def get_job_description_naukri() -> tuple:
    '''Get job description from detail page'''
    description         = "Unknown"
    experience_required = "Unknown"
    skip       = False
    skip_reason = None
    skip_msg    = None

    try:
        desc_el = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                '.job-desc, #job_description, .dang-inner-html, [class*="job-desc"]'))
        )
        description = desc_el.text
        desc_lower  = description.lower()

        for word in bad_words:
            if word.lower() in desc_lower:
                skip_msg    = f'Bad word "{word}" found. Skipping!'
                skip_reason = f"Bad word: {word}"
                skip = True
                break

        if not skip:
            matches = re.findall(re_experience, description)
            if matches:
                experience_required = max([int(m) for m in matches if int(m) <= 12], default=0)
                if current_experience > -1 and experience_required > current_experience + 2:
                    skip_msg    = f"Experience required {experience_required} > current {current_experience}. Skipping!"
                    skip_reason = "Too much experience required"
                    skip = True

    except Exception as e:
        print_lg("Failed to get job description:", e)

    return description, experience_required, skip, skip_reason, skip_msg


# ─── Apply Flow ───────────────────────────────────────────────────────────────
def find_apply_button_naukri() -> WebElement | None:
    '''Find Apply / Apply Now button on Naukri job page'''
    selectors = [
        '//button[contains(text(),"Apply")]',
        '//a[contains(text(),"Apply")]',
        '//*[@id="apply-button"]',
        '//button[@class[contains(.,"apply")]]',
        '//*[contains(@class,"apply-button")]',
        '//button[contains(text(),"apply")]',
        '//*[@data-ga-track[contains(.,"Apply")]]',
    ]
    for xpath in selectors:
        try:
            btn = driver.find_element(By.XPATH, xpath)
            if btn and btn.is_displayed():
                return btn
        except: pass
    return None


def fill_naukri_form() -> None:
    '''Fill application form fields on Naukri'''
    try:
        sleep(1)

        # Text inputs
        inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="number"], input[type="tel"]')
        for inp in inputs:
            try:
                if not inp.is_displayed(): continue
                val = inp.get_attribute('value') or ''
                if val and not overwrite_previous_answers: continue

                placeholder = (inp.get_attribute('placeholder') or '').lower()
                label_text  = ''
                try:
                    inp_id   = inp.get_attribute('id')
                    label_el = driver.find_element(By.CSS_SELECTOR, f'label[for="{inp_id}"]')
                    label_text = label_el.text.lower()
                except: pass

                combined = placeholder + ' ' + label_text
                answer = ''

                if 'name' in combined:
                    if 'first' in combined: answer = first_name
                    elif 'last' in combined: answer = last_name
                    else: answer = full_name
                elif 'phone' in combined or 'mobile' in combined: answer = phone_number
                elif 'experience' in combined or 'year' in combined: answer = years_of_experience
                elif 'city' in combined or 'location' in combined: answer = current_city
                elif 'salary' in combined or 'ctc' in combined: answer = desired_salary_str
                elif 'notice' in combined:
                    answer = notice_period_months if 'month' in combined else notice_period_str
                elif 'linkedin' in combined: answer = linkedIn
                elif 'portfolio' in combined or 'website' in combined: answer = website

                if answer:
                    inp.clear()
                    inp.send_keys(str(answer))
                    sleep(0.3)
            except: pass

        # Textareas (cover letter etc.)
        textareas = driver.find_elements(By.CSS_SELECTOR, 'textarea')
        for ta in textareas:
            try:
                if not ta.is_displayed(): continue
                val = ta.get_attribute('value') or ta.text or ''
                if val and not overwrite_previous_answers: continue
                ta.clear()
                ta.send_keys(cover_letter)
                sleep(0.3)
            except: pass

        # File upload (resume)
        try:
            file_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
            for fi in file_inputs:
                resume_abs = os.path.abspath(default_resume_path)
                if os.path.exists(resume_abs):
                    fi.send_keys(resume_abs)
                    sleep(2)
                    print_lg("Resume uploaded!")
                    break
        except Exception as e:
            print_lg("Resume upload failed:", e)

    except Exception as e:
        print_lg("Form fill error:", e)


def apply_to_job_naukri(job_id: str, title: str, company: str,
                         job_link: str, location: str,
                         description: str, experience_required) -> bool:
    '''Open job page and apply. Returns True if applied.'''
    global failed_count, easy_applied_count

    try:
        # Open job in new tab
        driver.execute_script("window.open(arguments[0]);", job_link)
        sleep(2)
        driver.switch_to.window(driver.window_handles[-1])
        sleep(2)

        # Get description from job page
        desc, exp_req, should_skip, skip_reason, skip_msg = get_job_description_naukri()
        if should_skip:
            print_lg(f'Skipping "{title}" — {skip_reason}')
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return False

        # Find Apply button
        apply_btn = find_apply_button_naukri()
        if not apply_btn:
            print_lg(f'No Apply button for "{title}"')
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return False

        scroll_to_view(driver, apply_btn)
        apply_btn.click()
        sleep(2)
        print_lg(f'Clicked Apply for "{title} | {company}"')

        # Multi-step form handling
        max_steps = 8
        step = 0
        applied = False

        while step < max_steps:
            step += 1
            sleep(1.5)
            fill_naukri_form()

            # Pause before submit
            if pause_before_submit:
                try:
                    submit_btn = driver.find_element(By.XPATH,
                        '//button[contains(text(),"Submit") or contains(text(),"Apply") and not(contains(text(),"Applied"))]')
                    decision = pyautogui.confirm(
                        f'Ready to submit:\n{title} | {company}\n\nVerify your info. DO NOT click Submit yourself.',
                        "Confirm Submit",
                        ["Submit Application", "Discard", "Disable Pause"]
                    )
                    if decision == "Discard":
                        try: actions.send_keys(Keys.ESCAPE).perform()
                        except: pass
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        return False
                    if decision == "Disable Pause":
                        global pause_before_submit
                        pause_before_submit = False
                except: pass

            # Try Submit button
            for xpath in [
                '//button[normalize-space()="Submit"]',
                '//button[contains(text(),"Submit Application")]',
                '//button[contains(text(),"Apply Now")]',
                '//input[@type="submit"]',
            ]:
                try:
                    btn = driver.find_element(By.XPATH, xpath)
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        sleep(2)

                        # Confirm success
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH,
                                    '//*[contains(text(),"successfully") or contains(text(),"Applied") or contains(text(),"Thank you")]'))
                            )
                        except: pass

                        applied = True
                        print_lg(f'✅ Applied to "{title} | {company}"!')
                        break
                except: pass

            if applied:
                break

            # Try Next / Continue
            continued = False
            for btn_text in ["Next", "Continue", "Proceed"]:
                try:
                    btn = driver.find_element(By.XPATH, f'//button[contains(text(),"{btn_text}")]')
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        sleep(1.5)
                        continued = True
                        break
                except: pass

            if not continued and not applied:
                # Check if already applied confirmation appeared
                try:
                    driver.find_element(By.XPATH,
                        '//*[contains(text(),"already applied") or contains(text(),"Application submitted")]')
                    applied = True
                    break
                except: pass
                print_lg(f"Could not proceed at step {step}")
                break

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        if applied:
            save_applied_job(job_id, title, company, location, description, experience_required, job_link)
            easy_applied_count += 1
            return True
        else:
            failed_count += 1
            save_failed_job(job_id, title, company, job_link, "Could not complete apply flow")
            return False

    except (NoSuchWindowException, WebDriverException) as e:
        raise e
    except Exception as e:
        print_lg(f"Apply error for {job_id}:", e)
        failed_count += 1
        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except: pass
        return False


# ─── Save History ─────────────────────────────────────────────────────────────
def save_applied_job(job_id, title, company, location, description, exp_req, job_link) -> None:
    try:
        with open(file_name, mode='a', newline='', encoding='utf-8') as f:
            fieldnames = ['Job ID','Title','Company','Location','About Job',
                          'Experience Required','Date Applied','Job Link']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0: writer.writeheader()
            writer.writerow({
                'Job ID': str(job_id)[:500],
                'Title': str(title)[:500],
                'Company': str(company)[:500],
                'Location': str(location)[:300],
                'About Job': str(description)[:2000],
                'Experience Required': str(exp_req)[:100],
                'Date Applied': str(datetime.now()),
                'Job Link': str(job_link)[:500],
            })
    except Exception as e:
        print_lg("Failed to save applied job:", e)


def save_failed_job(job_id, title, company, job_link, reason) -> None:
    try:
        with open(failed_file_name, mode='a', newline='', encoding='utf-8') as f:
            fieldnames = ['Job ID','Title','Company','Job Link','Reason','Date']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0: writer.writeheader()
            writer.writerow({
                'Job ID': str(job_id)[:500],
                'Title': str(title)[:500],
                'Company': str(company)[:500],
                'Job Link': str(job_link)[:500],
                'Reason': str(reason)[:1000],
                'Date': str(datetime.now()),
            })
    except Exception as e:
        print_lg("Failed to save failed job:", e)


# ─── Pagination ───────────────────────────────────────────────────────────────
def go_to_next_page_naukri() -> bool:
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR,
            'a[class*="next"], .pagination-next, a[title="Next"]')
        scroll_to_view(driver, next_btn)
        next_btn.click()
        sleep(3)
        return True
    except:
        try:
            # Try clicking by page number
            current = driver.find_element(By.CSS_SELECTOR, '.active.selected, [class*="activePage"]').text
            next_page = str(int(current) + 1)
            btn = driver.find_element(By.XPATH, f'//a[normalize-space()="{next_page}"]')
            btn.click()
            sleep(3)
            return True
        except:
            print_lg("No next page.")
            return False


# ─── Main Loop ────────────────────────────────────────────────────────────────
def apply_to_jobs_naukri(search_terms_list: list) -> None:
    global skip_count, failed_count, easy_applied_count

    applied_jobs = get_applied_job_ids()
    blacklisted  = set()

    if randomize_search_order:
        shuffle(search_terms_list)

    for search_term in search_terms_list:
        print_lg(f'\n{"="*80}\nSearching: "{search_term}"\n{"="*80}')

        url = build_naukri_search_url(search_term, search_location)
        driver.get(url)
        sleep(3)

        if pause_after_filters:
            decision = pyautogui.confirm(
                f'Naukri search loaded for: "{search_term}"\nReview results and click Continue.',
                "Review Results",
                ["Continue", "Skip this search"]
            )
            if decision == "Skip this search":
                continue

        current_count = 0
        page = 1

        while current_count < switch_number:
            print_lg(f"\n--- Page {page} ---")
            listings = get_job_listings_naukri()

            if not listings:
                print_lg("No listings on this page.")
                break

            for job in listings:
                if keep_screen_awake:
                    try: pyautogui.press('shiftright')
                    except: pass

                if current_count >= switch_number:
                    break

                print_lg("\n-@-")

                try:
                    job_id, title, company, location, job_link = get_job_details_naukri(job)

                    if not job_link:
                        print_lg("No job link found, skipping.")
                        continue

                    if job_id in applied_jobs:
                        print_lg(f'Already applied to "{title}". Skipping.')
                        continue

                    # Check blacklisted company
                    if company in blacklisted:
                        print_lg(f'Blacklisted company "{company}". Skipping.')
                        skip_count += 1
                        continue
                    for bad in about_company_bad_words:
                        if bad.lower() in company.lower():
                            blacklisted.add(company)
                            skip_count += 1
                            break
                    if company in blacklisted:
                        continue

                    print_lg(f'Trying: "{title}" at "{company}"')

                    success = apply_to_job_naukri(
                        job_id, title, company, job_link,
                        location, "Pending", "Unknown"
                    )

                    if success:
                        applied_jobs.add(job_id)
                        current_count += 1
                        print_lg(f'Total this search: {current_count}')

                except (NoSuchWindowException, WebDriverException) as e:
                    print_lg("Browser closed!", e)
                    raise e
                except Exception as e:
                    print_lg(f"Error: {e}")
                    try: actions.send_keys(Keys.ESCAPE).perform()
                    except: pass

            if current_count < switch_number:
                if not go_to_next_page_naukri():
                    break
                page += 1
            else:
                break

        print_lg(f'Done: "{search_term}" — Applied {current_count}')


# ─── Entry Point ──────────────────────────────────────────────────────────────
def main() -> None:
    global naukri_tab

    pyautogui.alert(
        "Naukri Auto Job Applier\nFor: Muthu Kumar J\n\nMake sure:\n1. Password set in config/secrets.py\n2. resume.pdf in 'all resumes/default/'\n3. Chrome installed\n\nClick OK to start!",
        "Naukri Bot", "OK"
    )

    total_runs = 1
    try:
        # Create directories
        for path in [file_name, failed_file_name, logs_folder_path + "/screenshots",
                     default_resume_path, "all resumes/temp"]:
            try:
                folder = os.path.dirname(path)
                if folder: os.makedirs(folder, exist_ok=True)
            except: pass

        if not os.path.exists(default_resume_path):
            pyautogui.alert(
                f'Resume not found at:\n{default_resume_path}\nBot will continue without uploading resume.',
                "Resume Missing", "OK"
            )

        # Open Naukri
        driver.get("https://www.naukri.com")
        sleep(2)

        if not is_logged_in_NK():
            login_NK()
        else:
            print_lg("Already logged into Naukri!")

        naukri_tab = driver.current_window_handle
        apply_to_jobs_naukri(search_terms)

        while run_non_stop:
            apply_to_jobs_naukri(search_terms)

    except (NoSuchWindowException, WebDriverException) as e:
        print_lg("Browser closed. Exiting.", e)
    except Exception as e:
        print_lg("Critical error:", e)
        pyautogui.alert(str(e), "Error")
    finally:
        summary = (
            f"Jobs Applied  : {easy_applied_count}\n"
            f"Jobs Failed   : {failed_count}\n"
            f"Jobs Skipped  : {skip_count}\n"
        )
        print_lg("\n\n" + summary)
        pyautogui.alert(
            f"Naukri Bot Finished!\n\n{summary}\nHistory saved to:\n{file_name}",
            "Done!", "Close"
        )
        try:
            if driver: driver.quit()
        except: pass


if __name__ == "__main__":
    main()
