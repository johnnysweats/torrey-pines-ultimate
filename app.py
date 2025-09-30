#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Torrey Pines Waitlist Web Application
Deployable to Railway for mobile access
"""

import os
import datetime
import pytz
import time
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Global variables for job status
job_status = {
    'running': False,
    'message': 'Ready to start',
    'success': False,
    'error': None
}

def select_react_select_option(driver, input_id, option_text):
    input_elem = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.ID, input_id))
    )
    input_elem.click()
    option_xpath = f"//div[contains(@class, 'option') and text()='{option_text}']"
    option_elem = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.XPATH, option_xpath))
    )
    option_elem.click()

def wait_until_target_time(target_hour, target_minute, timezone_str):
    tz = pytz.timezone(timezone_str)
    now = datetime.datetime.now(tz)
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if now > target:
        target += datetime.timedelta(days=1)
    wait_seconds = (target - now).total_seconds()
    job_status['message'] = f"Waiting until {target.strftime('%Y-%m-%d %H:%M:%S %Z')} ({int(wait_seconds)} seconds)..."
    time.sleep(wait_seconds)

def run_waitlist_automation(user_info, course, players, target_time):
    global job_status
    
    try:
        job_status['running'] = True
        job_status['message'] = 'Starting automation...'
        job_status['success'] = False
        job_status['error'] = None
        
        # Parse target time
        hour, minute = map(int, target_time.split(':'))
        
        # Wait until target time
        wait_until_target_time(hour, minute, "America/Los_Angeles")
        
        job_status['message'] = 'Setting up ChromeDriver...'
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = None
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_script_timeout(30)

            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": 32.8986,
                "longitude": -117.2431,
                "accuracy": 100
            })

            job_status['message'] = 'Navigating to waitlist page...'
            website_url = "https://waitwhile.com/locations/torreypinesgolf/welcome"
            driver.get(website_url)

            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Keep refreshing until "Join waitlist" button is available
            max_attempts = 100
            attempt = 0
            while True:
                try:
                    join_waitlist_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'wwpp-primary-button')]"))
                    )
                    join_waitlist_button.click()
                    job_status['message'] = 'Successfully clicked the Join waitlist button'
                    break
                except Exception:
                    attempt += 1
                    if attempt >= max_attempts:
                        job_status['message'] = 'Max attempts reached. Exiting.'
                        raise
                    now_str = datetime.datetime.now().strftime('%H:%M:%S')
                    job_status['message'] = f'[{now_str}] Join waitlist button not available yet. Refreshing... (Attempt {attempt})'
                    time.sleep(2)
                    driver.refresh()
                    
            # Fill out the form
            job_status['message'] = 'Filling out form...'
            
            first_name_input = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, "form_firstName"))
            )
            first_name_input.clear()
            first_name_input.send_keys(user_info["first_name"])

            last_name_input = driver.find_element(By.ID, "form_lastName")
            last_name_input.clear()
            last_name_input.send_keys(user_info["last_name"])

            email_input = driver.find_element(By.ID, "form_email")
            email_input.clear()
            email_input.send_keys(user_info["email"])

            phone_input = driver.find_element(By.ID, "form_phone")
            phone_input.clear()
            phone_input.send_keys(user_info["phone"])

            job_status['message'] = 'Selecting course and players...'
            
            # Select course and players
            select_react_select_option(driver, "react-select-2-input", course)
            select_react_select_option(driver, "react-select-3-input", players)

            # Click the "Join the line" button
            try:
                join_line_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cy='form-button']"))
                )
                join_line_button.click()
                job_status['message'] = 'Successfully joined the waitlist!'
                job_status['success'] = True
            except Exception as e:
                job_status['message'] = f'Failed to click Join the line button: {e}'
                job_status['error'] = str(e)

            time.sleep(15)

        except Exception as e:
            job_status['message'] = f'Automation failed: {e}'
            job_status['error'] = str(e)
        finally:
            if driver:
                driver.quit()
                
    except Exception as e:
        job_status['message'] = f'Error: {e}'
        job_status['error'] = str(e)
    finally:
        job_status['running'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_automation():
    global job_status
    
    if job_status['running']:
        return jsonify({'error': 'Automation is already running'}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email', 'phone', 'course', 'players', 'target_time']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate course
    courses = {"south": "South", "north": "North", "first avail.": "First Avail."}
    if data['course'].lower() not in courses:
        return jsonify({'error': 'Invalid course. Must be south, north, or first avail.'}), 400
    
    # Validate players
    if data['players'] not in ['1', '2', '3', '4']:
        return jsonify({'error': 'Invalid number of players. Must be 1, 2, 3, or 4.'}), 400
    
    # Validate time format
    try:
        hour, minute = map(int, data['target_time'].split(':'))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError()
    except:
        return jsonify({'error': 'Invalid time format. Use HH:MM in 24-hour format.'}), 400
    
    # Prepare user info
    user_info = {
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'email': data['email'],
        'phone': data['phone']
    }
    
    course = courses[data['course'].lower()]
    players = data['players']
    target_time = data['target_time']
    
    # Start automation in background thread
    thread = threading.Thread(
        target=run_waitlist_automation,
        args=(user_info, course, players, target_time)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Automation started successfully'})

@app.route('/status')
def get_status():
    return jsonify(job_status)

@app.route('/reset')
def reset_status():
    global job_status
    job_status = {
        'running': False,
        'message': 'Ready to start',
        'success': False,
        'error': None
    }
    return jsonify({'message': 'Status reset'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
