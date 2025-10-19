from flask import Flask, render_template, request, jsonify
import database
from datetime import datetime

app = Flask(__name__)

# Initialize database on startup
database.init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    
    run_type = data.get('runType', 'now')
    
    # Save job to database
    job_id = database.add_job(data)
    
    # Log the submission
    print(f"Received submission (Job ID: {job_id}):", data)
    
    if run_type == 'now':
        # TODO: Execute automation immediately
        message = f"Great! We'll run the waitlist automation now for {data['firstName']} {data['lastName']}."
    else:
        # Job is scheduled for later
        schedule_time = data.get('scheduleDateTime')
        message = f"Perfect! We've scheduled the waitlist automation for {schedule_time} for {data['firstName']} {data['lastName']}."
    
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
    database.cancel_job(job_id)
    return jsonify({
        'status': 'success',
        'message': 'Job cancelled successfully'
    })

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
    app.run(host='0.0.0.0', port=8080)
