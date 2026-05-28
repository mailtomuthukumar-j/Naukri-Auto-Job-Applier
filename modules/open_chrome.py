'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion

version:    26.01.20.5.08
'''

import os
import shutil
import pathlib

from modules.helpers import get_default_temp_profile, make_directories
from config.settings import run_in_background, stealth_mode, disable_extensions, safe_mode, file_name, failed_file_name, logs_folder_path, generated_resume_path
from config.questions import default_resume_path
if stealth_mode:
    import undetected_chromedriver as uc
else: 
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log, print_lg
from selenium.common.exceptions import SessionNotCreatedException


def cleanup_temp_profile():
    profile_dir = get_default_temp_profile()
    if profile_dir:
        profile_dir = profile_dir.replace("--user-data-dir=", "")
        try:
            if os.path.exists(profile_dir):
                devtools_file = os.path.join(profile_dir, "DevToolsActivePort")
                if os.path.exists(devtools_file):
                    os.remove(devtools_file)
                    print_lg("Cleaned up stale DevToolsActivePort file from temp profile.")
                singleton_file = os.path.join(profile_dir, "SingletonLock")
                if os.path.exists(singleton_file):
                    os.remove(singleton_file)
        except Exception as e:
            print_lg("Failed to clean up temp profile:", e)


def createChromeSession(isRetry: bool = False):
    make_directories([file_name,failed_file_name,logs_folder_path+"/screenshots",default_resume_path,generated_resume_path+"/temp"])
    cleanup_temp_profile()
    options = uc.ChromeOptions() if stealth_mode else Options()
    if run_in_background:   options.add_argument("--headless")
    if disable_extensions:  options.add_argument("--disable-extensions")

    print_lg("IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM! Or it's highly likely that application will just open browser and not do anything!")
    profile_dir = find_default_profile_directory()
    if isRetry:
        print_lg("Will login with a guest profile, browsing history will not be saved in the browser!")
    elif profile_dir and not safe_mode:
        options.add_argument(f"--user-data-dir={profile_dir}")
    else:
        print_lg("Logging in with a guest profile, Web history will not be saved!")
        options.add_argument(get_default_temp_profile())
    if stealth_mode:
        print_lg("Downloading Chrome Driver... This may take some time. Undetected mode requires download every run!")
        driver = uc.Chrome(options=options)
    else:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)
    return options, driver, actions, wait

try:
    options, driver, actions, wait = None, None, None, None
    options, driver, actions, wait = createChromeSession()
except SessionNotCreatedException as e:
    critical_error_log("Failed to create Chrome Session, retrying with guest profile", e)
    try:
        options, driver, actions, wait = createChromeSession(True)
    except SessionNotCreatedException as e2:
        critical_error_log("Retry with guest profile also failed", e2)
        msg = 'Seems like Chrome session could not be created. Try closing all Chrome processes and try again!\n\nIf issue persists, try Safe Mode. Set safe_mode = True in config.py\n\nPlease check GitHub discussions/support for solutions https://github.com/GodsScion/Auto_job_applier_linkedIn\n                                   OR \nReach out in discord ( https://discord.gg/fFp7uUzWCY )'
        print_lg(msg)
        from pyautogui import alert
        alert(msg, "Error creating Chrome session")
        exit()
except Exception as e:
    msg = 'Seems like Google Chrome is out dated. Update browser and try again! \n\n\nIf issue persists, try Safe Mode. Set, safe_mode = True in config.py \n\nPlease check GitHub discussions/support for solutions https://github.com/GodsScion/Auto_job_applier_linkedIn \n                                   OR \nReach out in discord ( https://discord.gg/fFp7uUzWCY )'
    if isinstance(e,TimeoutError): msg = "Couldn't download Chrome-driver. Set stealth_mode = False in config!"
    print_lg(msg)
    critical_error_log("In Opening Chrome", e)
    from pyautogui import alert
    alert(msg, "Error in opening chrome")
    if driver:
        try: driver.quit()
        except: pass
    exit()
