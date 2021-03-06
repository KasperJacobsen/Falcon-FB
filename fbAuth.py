#!/usr/bin/python2.7
"""
Generate OAuth token for a FB app using local http server
Most useful for generating and returning and access token

Courtesy of Samir Bajaj
https://github.com/samirbajaj/cs229-project/tree/master/fbDataCollector
"""
import os.path
import json
import urllib2
import urllib
import urlparse
import BaseHTTPServer
import webbrowser
import facebook
import sys

APP_ID = '464116283658633'
APP_SECRET = 'd104c58965556de3725cb4f2326a6722'
ENDPOINT = 'graph.facebook.com'
REDIRECT_URI = 'http://127.0.0.1:8080/'
ACCESS_TOKEN = None
LOCAL_FILE = '.fb_access_token'

# OLD_SCOPE_STR = 'read_stream,user_about_me,friends_about_me,user_likes,friends_likes,user_activities,friends_activities,user_events,friends_events,user_groups,friends_groups,friends_notes,friends_status,friends_games_activity'
SCOPE_STR = 'friends_birthday,friends_likes'
STATUS_TEMPLATE = u"{name}\033[0m: {message}"

def get_url(path, args=None):
    args = args or {}
    if ACCESS_TOKEN:
        args['access_token'] = ACCESS_TOKEN
    if 'access_token' in args or 'client_secret' in args:
        endpoint = "https://"+ENDPOINT
    else:
        endpoint = "http://"+ENDPOINT
    return endpoint+path+'?'+urllib.urlencode(args)

def get(path, args=None):
    return urllib2.urlopen(get_url(path, args=args)).read()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        global ACCESS_TOKEN
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        code = urlparse.parse_qs(urlparse.urlparse(self.path).query).get('code')
        code = code[0] if code else None
        if code is None:
            self.wfile.write("<html><head><title>Error</title></head><body><center><h1>An error occured when logging in to facebook, try again</h1></center></body></html>")
            exit(1)

        response = get('/oauth/access_token', {'client_id':APP_ID,
                                               'redirect_uri':REDIRECT_URI,
                                               'client_secret':APP_SECRET,
                                               'code':code})
        ACCESS_TOKEN = urlparse.parse_qs(response)['access_token'][0]
        open(LOCAL_FILE,'w').write(ACCESS_TOKEN)
        self.wfile.write("<html><head><title>Success!</title></head><body><center><h1>You can close this window now.</h1><h4>We got the token!</h4></center></body></html>")

def print_status(item, color=u'\033[1;35m'):
    print item

def get_token():
    global ACCESS_TOKEN
    if not os.path.exists(LOCAL_FILE):
        print >> sys.stderr, "Logging you in to facebook..."
        webbrowser.open(get_url('/oauth/authorize',
                                {'client_id':APP_ID,
                                 'redirect_uri':REDIRECT_URI,
                                 'scope':SCOPE_STR}))

        httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8080), RequestHandler)
        while ACCESS_TOKEN is None:
            httpd.handle_request()
    else:
        ACCESS_TOKEN = open(LOCAL_FILE).read()

    return ACCESS_TOKEN

if __name__ == '__main__':
    print >> sys.stderr, 'attempting to obtain oauth token'
    ACCESS_TOKEN = get_token()
    print >> sys.stderr, 'generating facebook graph api object'
    facebook_graph = facebook.GraphAPI(ACCESS_TOKEN)
    profile = facebook_graph.get_object("me")
    print profile