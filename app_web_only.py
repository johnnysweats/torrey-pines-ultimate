#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Torrey Pines Waitlist Web Interface (without Selenium for now)
"""

import os
import datetime
import pytz
import time
import threading
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Global variables for job status
job_status = {
    'running': False,
    'message': 'Ready to start',
    'success': False,
    'error': None
}

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
        
        job_status['message'] = 'Automation would start here...'
        job_status['message'] = 'Selenium automation will be added once web interface is working'
        job_status['message'] = 'For now, this simulates the waitlist process'
        
        # Simulate some work
        time.sleep(5)
        
        job_status['message'] = 'Automation completed successfully! (Simulated)'
        job_status['success'] = True
        
    except Exception as e:
        job_status['message'] = f'Error: {e}'
        job_status['error'] = str(e)
    finally:
        job_status['running'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Torrey Pines Waitlist Web Interface is running'})

@app.route('/api')
def api():
    return jsonify({'message': 'Web interface is working! Selenium will be added next.', 'version': '1.0'})

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
