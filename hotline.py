''' a phone tree system '''
import re
from twilio import twiml

voice = 'alice'
class Hotline(object):
    ''' create a hotline object '''
    script = {}
    endpoints = []
    hangup_message = ''
    error_message = ''

    def __init__(self, script_json):
        self.build_from_json(script_json)

    def build_from_json(self, script_json):
        ''' create a script from a json file '''
        #validate_script_json(script_json)

        # configure
        if 'settings' in script_json:
            self.hangup_message = script_json['settings'].get('hangup-message')
            self.error_message = script_json['settings'].get('error-message')

        # add each scene
        for (key, scene_json) in script_json.items():
            if key == 'settings':
                continue
            self.endpoints.append(key)
            scene = Scene(key,
                          text=scene_json['text'],
                          options=scene_json['options'])
            self.script[key] = scene


    def run(self, endpoint='start', mode='twiml'):
        ''' begin call '''
        return self.script[endpoint].play(mode=mode)


    def parse_keypress(self, scene, keypress):
        ''' interpret phone input '''
        try:
            number = int(keypress) - 1
        except ValueError:
            # not sure how this would happen, but I guess
            # if it's an invalid input, replay this scene
            return self.script[scene].play(error=True)

        try:
            option = self.script[scene].options[number]
        except KeyError:
            # they picked a different number, replay this scene
            return self.script[scene].play(error=True)

        if 'next' in option:
            # route to the selected next scene
            next_scene = option['next']
            return self.script[next_scene].play()
        elif 'dial' in option:
            return self.dial(option['dail'])
        return self.hangup()


    def dial(self, number):
        ''' transfer to an outgoing call '''
        r = twiml.Response()
        r.dial(number)
        return str(r)


    def hangup(self):
        ''' end a call '''
        r = twiml.Response()
        r.say(self.hangup_message, voice=voice)
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

    def play(self, mode='twiml', error=False):
        ''' generate TWiML for the scene '''
        text = self.text
        if mode == 'html':
            r = '<p>' + self.error_message + '</p>' if error else ''
            r += '<p>' + text + '</p> <ul>'
            r += ''.join(format_html_option(o) for o in self.options)
            r += '</ul>'
        else:
            r = twiml.Response()
            if error:
                r.say(self.error_message, voice=voice)
            r.say(text, voice=voice)
            with r.gather(numDigits=1, method='POST') as g:
                g.say(', '.join([o['text'] for o in self.options]), voice=voice)
        return str(r)


def format_html_option(option):
    ''' create links for html version of hotline '''
    if 'next' in option:
        link = '<a href="' + option['next'] + '?mode=html">' + \
                option['text'] + '</a>'
    else:
        link = option['text']
    return '<li>' + link + '</li>'

