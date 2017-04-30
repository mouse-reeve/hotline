# Hotline

Generate a twilio phone tree from a json file.

## How to run it

Set up your dev environment
``` bash
$ virtualenv venv
$ source venv/bin activate
$ pip install -r requirements.txt
```

Create a script
``` bash
$ cp script-sample.json script.json
$ vim script.json
```

Run the script (script validation will print)
``` bash
$ python app.py
```

The app will run at `localhost:3030/start` by default.
