''' simple http app using hotline library '''
from flask import Flask, request
from hotline import Hotline
import json

app = Flask(__name__)
script = Hotline(json.load(file('script.json')))

@app.route('/', methods=['GET'])
@app.route('/<endpoint>', methods=['GET'])
def call_endpoint(endpoint='start'):
    ''' receive a call or play a scene '''
    mode = request.args.get('mode')
    return script.run(endpoint, mode=mode)


@app.route('/', methods=['POST'])
@app.route('/<endpoint>', methods=['POST'])
def receive_data(endpoint='start'):
    ''' process a keypress during a phone call '''
    digits = request.form.get('Digits', 0)
    return script.parse_keypress(endpoint, digits)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3030)
