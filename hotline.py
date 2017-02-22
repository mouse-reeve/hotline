''' a phone tree system '''
import re
from twilio import twiml

class Hotline(object):
    ''' create a hotline object '''
    script = {}
    endpoints = []

    def __init__(self, script_json):
        self.build_from_json(script_json)

    def build_from_json(self, script_json):
        ''' create a script from a json file '''
        #validate_script_json(script_json)

        # add each scene
        for (key, scene_json) in script_json.items():
            self.endpoints.append(key)
            scene = Scene(key,
                          text=scene_json['text'],
                          options=scene_json['options'])
            self.script[key] = scene

    def run(self, endpoint='start'):
        ''' begin call '''
        return self.script[endpoint].play()


    def parse_keypress(self, scene, keypress):
        ''' interpret phone input '''
        try:
            number = int(keypress) - 1
        except ValueError:
            pass
        try:
            next_scene = self.script[scene].pick(number)
        except KeyError:
            return self.hangup()
        else:
            return self.script[next_scene].play()

    def hangup(self):
        ''' end a call '''
        r = twiml.Response()
        r.hangup()
        return str(r)


def validate_script_json(script_json):
    ''' ensure that a script is properly formatted '''
    keys = script_json.keys()
    options = [k['next'] for k in s['options'] for s in script_json.values()]
    options = list(set(options))
    for key in options:
        if not key in keys:
            raise IndexError()

    return True


class Scene(object):
    ''' one menu item '''

    def __init__(self, scene_id, text=None, options=None):
        self.scene_id = scene_id
        self.text = text
        self.options = options

        # format option numbers
        for (i, option) in enumerate(options):
            option['text'] = re.sub('{}', str(i+1), option['text'])

    def play(self):
        ''' generate TWiML for the scene '''
        text = self.text
        r = twiml.Response()
        r.say(text)
        with r.gather(numDigits=1, method='POST') as g:
            g.say(', '.join([o['text'] for o in self.options]))
        return str(r)

    def pick(self, option_number):
        ''' select a menu option '''
        return self.options[option_number]['next']
