from flask import Flask, render_template, request, jsonify
import database
from datetime import datetime
from automation import run_waitlist_automation
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import pytz

app = Flask(__name__)

# Initialize database on startup
database.init_db()

# Initialize scheduler
scheduler = BackgroundScheduler(timezone=pytz.timezone('America/Los_Angeles'))
scheduler.start()

def execute_scheduled_job(job_id, data):
    """Execute a scheduled job"""
    print(f"Executing scheduled job {job_id} at {datetime.now()}")
    
    # Update status to running
    import sqlite3
    conn = sqlite3.connect(database.DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE jobs SET status = ? WHERE id = ?', ('running', job_id))
    conn.commit()
    conn.close()
    
    # Run the automation
    run_automation_async(job_id, data)

def schedule_existing_jobs():
    """On startup, reschedule any pending jobs"""
    pending_jobs = database.get_pending_jobs()
    pacific_tz = pytz.timezone('America/Los_Angeles')
    
    for job in pending_jobs:
        if job['schedule_datetime']:
            try:
                # Parse the datetime string
                from datetime import datetime as dt
                schedule_time = dt.fromisoformat(job['schedule_datetime'].replace('Z', '+00:00'))
                
                # Make sure it's timezone-aware
                if schedule_time.tzinfo is None:
                    schedule_time = pacific_tz.localize(schedule_time)
                
                # Only schedule if in the future
                now = dt.now(pacific_tz)
                if schedule_time > now:
                    job_data = {
                        'firstName': job['first_name'],
                        'lastName': job['last_name'],
                        'email': job['email'],
                        'phone': job['phone'],
                        'course': job['course'],
                        'players': job['players']
                    }
                    
                    scheduler.add_job(
                        execute_scheduled_job,
                        trigger=DateTrigger(run_date=schedule_time),
                        args=[job['id'], job_data],
                        id=f"job_{job['id']}",
                        replace_existing=True
                    )
                    print(f"Rescheduled job {job['id']} for {schedule_time}")
                else:
                    # Mark as missed if time has passed
                    database.mark_job_completed(job['id'], "Missed - time has passed")
                    print(f"Job {job['id']} missed - scheduled for {schedule_time}, now is {now}")
            except Exception as e:
                print(f"Error rescheduling job {job['id']}: {e}")

# Schedule existing jobs on startup
schedule_existing_jobs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({'status': 'healthy', 'service': 'Torrey Pines Ultimate'})

def run_automation_async(job_id, data):
    """Run automation in background thread"""
    try:
        result = run_waitlist_automation(
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            phone=data['phone'],
            course=data['course'],
            players=data['players'],
            headless=True  # Run headless in production
        )
        
        # Update job in database with result
        if result['status'] == 'success':
            database.mark_job_completed(job_id, result['message'])
        else:
            database.mark_job_completed(job_id, f"Error: {result['message']}")
            
    except Exception as e:
        database.mark_job_completed(job_id, f"Error: {str(e)}")

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    
    run_type = data.get('runType', 'now')
    
    # Save job to database
    job_id = database.add_job(data)
    
    # Log the submission
    print(f"Received submission (Job ID: {job_id}):", data)
    
    if run_type == 'now':
        # Execute automation immediately in background thread
        thread = threading.Thread(target=run_automation_async, args=(job_id, data))
        thread.daemon = True
        thread.start()
        
        message = f"Great! Running the waitlist automation now for {data['firstName']} {data['lastName']}. Check the Scheduled Jobs tab to see the status."
    else:
        # Schedule job for later
        schedule_time_str = data.get('scheduleDateTime')
        
        try:
            from datetime import datetime as dt
            pacific_tz = pytz.timezone('America/Los_Angeles')
            
            # Parse the datetime string (comes from HTML datetime-local input)
            schedule_time = dt.fromisoformat(schedule_time_str)
            
            # Make timezone-aware if it isn't already
            if schedule_time.tzinfo is None:
                schedule_time = pacific_tz.localize(schedule_time)
            
            # Add to scheduler
            scheduler.add_job(
                execute_scheduled_job,
                trigger=DateTrigger(run_date=schedule_time),
                args=[job_id, data],
                id=f"job_{job_id}",
                replace_existing=True
            )
            
            formatted_time = schedule_time.strftime('%B %d, %Y at %I:%M %p PST')
            message = f"Perfect! We've scheduled the waitlist automation for {formatted_time} for {data['firstName']} {data['lastName']}."
            print(f"Scheduled job {job_id} for {schedule_time}")
        except Exception as e:
            message = f"Job created but scheduling failed: {str(e)}. Please contact support."
            print(f"Error scheduling job {job_id}: {e}")
    
    return jsonify({
        'status': 'success',
        'message': message,
        'job_id': job_id,
        'data': data
    })

@app.route('/jobs')
def jobs():
    """Render the jobs management page"""
    return render_template('jobs.html')

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs"""
    all_jobs = database.get_all_jobs()
    return jsonify({
        'status': 'success',
        'jobs': all_jobs
    })

@app.route('/api/jobs/pending', methods=['GET'])
def get_pending_jobs():
    """Get pending jobs"""
    pending = database.get_pending_jobs()
    return jsonify({
        'status': 'success',
        'jobs': pending
    })

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get a specific job"""
    job = database.get_job(job_id)
    if job:
        return jsonify({
            'status': 'success',
            'job': job
        })
    return jsonify({
        'status': 'error',
        'message': 'Job not found'
    }), 404

@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """Update a job"""
    data = request.get_json()
    database.update_job(job_id, data)
    return jsonify({
        'status': 'success',
        'message': 'Job updated successfully'
    })

@app.route('/api/jobs/<int:job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Cancel a job"""
    # Remove from scheduler if it exists
    try:
        scheduler.remove_job(f"job_{job_id}")
        print(f"Removed job {job_id} from scheduler")
    except:
        pass  # Job not in scheduler, that's fine
    
    database.cancel_job(job_id)
    return jsonify({
        'status': 'success',
        'message': 'Job cancelled successfully'
    })

@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a specific job"""
    try:
        import sqlite3
        conn = sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        
        # Delete the job
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Job not found'
            }), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Booking deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/time', methods=['GET'])
def get_time():
    """Get current server time in Pacific timezone"""
    pacific_time = database.get_pacific_time()
    return jsonify({
        'status': 'success',
        'time': pacific_time.isoformat(),
        'timezone': 'America/Los_Angeles',
        'formatted': pacific_time.strftime('%B %d, %Y at %I:%M %p PST')
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
