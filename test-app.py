''' simple http app using hotline library '''
from flask import Flask, request
from hotline import Hotline
import json

app = Flask(__name__)
script = Hotline(json.load(file('script.json')))

@app.route('/', methods=['GET'])
@app.route('/<endpoint>', methods=['GET'])
def call_endpoint(endpoint='start'):
    return script.run(endpoint)


@app.route('/', methods=['POST'])
@app.route('/<endpoint>', methods=['POST'])
def receive_data(endpoint='start'):
    digits = request.form['Digits']
    return script.parse_keypress(endpoint, digits)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3030)
