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

    def run(self, endpoint='start', mode='twiml'):
        ''' begin call '''
        return self.script[endpoint].play(mode)


    def parse_keypress(self, scene, keypress):
        ''' interpret phone input '''
        try:
            number = int(keypress) - 1
        except ValueError:
            # if it's an invalid input, replay this scene
            return self.script[scene].play()

        try:
            option = self.options[number]
        except KeyError:
            # they picked a different number, replay this scene
            return self.script[scene].play()

        if 'next' in option:
            # route to the selected next scene
            next_scene = option['next']
            return self.script[next_scene].play()
        elif 'dial' in option:
            return dial(option['dail'])
        return hangup()


def dial(number):
    ''' transfer to an outgoing call '''
    r = twiml.Response()
    r.dial(number)
    return str(r)

def hangup():
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

    def play(self, mode):
        ''' generate TWiML for the scene '''
        text = self.text
        if mode == 'html':
            r = '<p>' + text + '</p> <ul>'
            r += ''.join(format_html_option(o) for o in self.options)
            r += '</ul>'
        else:
            r = twiml.Response()
            r.say(text)
            with r.gather(numDigits=1, method='POST') as g:
                g.say(', '.join([o['text'] for o in self.options]))
        return str(r)


def format_html_option(option):
    ''' create links for html version of hotline '''
    if 'next' in option:
        link = '<a href="' + option['next'] + '?mode=html">' + \
                option['text'] + '</a>'
    else:
        link = option['text']
    return '<li>' + link + '</li>'
