''' simple http app using hotline library '''
from flask import Flask, redirect, request
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
    data = request.get_json()
    try:
        keypress = data['digits']
    except:
        return redirect('/%s' % endpoint)
    else:
        return script.parse_keypress(keypress)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3030)
