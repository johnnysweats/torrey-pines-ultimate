from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    
    run_type = data.get('runType', 'now')
    
    # Log the submission
    print("Received submission:", data)
    
    if run_type == 'now':
        # TODO: Execute automation immediately
        message = f"Great! We'll run the waitlist automation now for {data['firstName']} {data['lastName']}."
    else:
        # TODO: Schedule automation for later
        schedule_time = data.get('scheduleDateTime')
        message = f"Perfect! We've scheduled the waitlist automation for {schedule_time} for {data['firstName']} {data['lastName']}."
    
    return jsonify({
        'status': 'success',
        'message': message,
        'data': data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
