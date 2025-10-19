from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    
    # For now, just print the data and return success
    print("Received submission:", data)
    
    return jsonify({
        'status': 'success',
        'message': 'Your waitlist request has been received!',
        'data': data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
