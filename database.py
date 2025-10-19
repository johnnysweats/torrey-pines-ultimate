"""
Database module for storing and managing waitlist jobs
"""

import sqlite3
from datetime import datetime
import json
import pytz

# San Diego is in Pacific timezone
PACIFIC_TZ = pytz.timezone('America/Los_Angeles')

def get_pacific_time():
    """Get current time in Pacific timezone"""
    return datetime.now(PACIFIC_TZ)

DB_NAME = 'waitlist_jobs.db'

def init_db():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            course TEXT NOT NULL,
            players TEXT NOT NULL,
            run_type TEXT NOT NULL,
            schedule_datetime TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            executed_at TEXT,
            result TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_job(data):
    """Add a new job to the database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO jobs (
            first_name, last_name, email, phone, course, players,
            run_type, schedule_datetime, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['firstName'],
        data['lastName'],
        data['email'],
        data['phone'],
        data['course'],
        data['players'],
        data['runType'],
        data.get('scheduleDateTime'),
        'pending' if data['runType'] == 'later' else 'running',
        get_pacific_time().isoformat()
    ))
    
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return job_id

def get_all_jobs():
    """Get all jobs from the database"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM jobs ORDER BY created_at DESC
    ''')
    
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jobs

def get_pending_jobs():
    """Get all pending jobs"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM jobs WHERE status = 'pending' ORDER BY schedule_datetime ASC
    ''')
    
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jobs

def get_job(job_id):
    """Get a specific job by ID"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = cursor.fetchone()
    
    conn.close()
    
    return dict(job) if job else None

def update_job(job_id, data):
    """Update a job"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE jobs SET
            first_name = ?,
            last_name = ?,
            email = ?,
            phone = ?,
            course = ?,
            players = ?,
            schedule_datetime = ?
        WHERE id = ?
    ''', (
        data['firstName'],
        data['lastName'],
        data['email'],
        data['phone'],
        data['course'],
        data['players'],
        data.get('scheduleDateTime'),
        job_id
    ))
    
    conn.commit()
    conn.close()

def cancel_job(job_id):
    """Cancel/delete a job"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE jobs SET status = ? WHERE id = ?', ('cancelled', job_id))
    
    conn.commit()
    conn.close()

def mark_job_completed(job_id, result):
    """Mark a job as completed"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE jobs SET
            status = ?,
            executed_at = ?,
            result = ?
        WHERE id = ?
    ''', ('completed', get_pacific_time().isoformat(), result, job_id))
    
    conn.commit()
    conn.close()

