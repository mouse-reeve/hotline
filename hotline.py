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
    dial_message = ''

    def __init__(self, script_json):
        self.build_from_json(script_json)

    def build_from_json(self, script_json):
        ''' create a script from a json file '''
        validate_script_json(script_json)

        # configure
        if 'settings' in script_json:
            self.hangup_message = script_json['settings'].get('hangup-message')
            self.error_message = script_json['settings'].get('error-message')
            self.dial_message = script_json['settings'].get('dial-message')

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
            if number < 0:
                raise ValueError
        except ValueError:
            return self.script[scene].play(error=self.error_message)

        try:
            option = self.script[scene].options[number]
        except IndexError:
            # they picked a different number, replay this scene
            return self.script[scene].play(error=self.error_message)

        if 'next' in option:
            # route to the selected next scene
            next_scene = option['next']
            return self.script[next_scene].play()
        elif 'dial' in option:
            return self.dial(option['dial'])
        return self.hangup()


    def dial(self, number):
        ''' transfer to an outgoing call '''
        r = twiml.Response()
        r.say(self.dial_message, voice=voice)
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

    # check that every "next" leads somewhere
    scene_ids = script_json.keys()
    scene_ids.remove('settings')

    nexts = []
    hangups = 0
    for scene in script_json.values():
        if 'options' in scene:
            nexts += [n.get('next') for n in scene['options']]
        else:
            hangups += 1

    nexts = list(set(nexts))

    unused_scenes = [s for s in scene_ids if not s in nexts and s]
    if unused_scenes:
        print 'WARNING: These scenes are inaccessible: %s' % unused_scenes

    invalid_nexts = [n for n in nexts if not n in scene_ids and n]
    if invalid_nexts:
        print 'ERROR: These next links are unmatched: %s' % invalid_nexts

    print 'Number of ways to end call: %d' % hangups

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
            r = '<p>' + error + '</p>' if error else ''
            r += '<p>' + text + '</p> <ul>'
            r += ''.join(format_html_option(o) for o in self.options)
            r += '</ul>'
        else:
            r = twiml.Response()

            path = '/' + self.scene_id
            with r.gather(numDigits=1, method='POST', action=path) as g:
                if error:
                    g.say(error, voice=voice)
                g.say(text, voice=voice)
                g.say(', '.join([o['text'] for o in self.options]), voice=voice)
                g.pause()
            r.redirect(path)
        return str(r)


def format_html_option(option):
    ''' create links for html version of hotline '''
    if 'next' in option:
        link = '<a href="' + option['next'] + '?mode=html">' + \
                option['text'] + '</a>'
    else:
        link = option['text']
    return '<li>' + link + '</li>'

