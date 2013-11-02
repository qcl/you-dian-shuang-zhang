# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.api import urlfetch
from gaesessions import get_current_session
try:
    import simplejson as json
except:
    import json


FacebookOauth = { 
    "appId":"542121675865178", 
    "secret":"8425163cf581ee8161f9487c490e7094",
    #"redir": "http://yhackertw92.appspot.com/callback"
    "redir": "http://localhost:8080/callback"
}

class LoginHandler(webapp2.RequestHandler):
    def get(self):

        tourl = self.request.get('to')
        if tourl is '':
            tourl = '/'
        get_current_session()['tourl'] = tourl
        
         
        fblogin = ("https://www.facebook.com/dialog/oauth?client_id="+FacebookOauth["appId"] + "&"+
        "redirect_uri=" + FacebookOauth["redir"] +
        "&scope=publish_stream,email")

        self.redirect(fblogin)
        


class CallbackHandler(webapp2.RequestHandler): 
    def get(self):
        self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
        session = get_current_session()
        #self.response.write(session['fromurl'])
        code = self.request.get('code')
        
        fboauth = ("https://graph.facebook.com/oauth/access_token?client_id="+FacebookOauth["appId"]+ "&"+
                   "redirect_uri=" + FacebookOauth["redir"] +
                   "&client_secret=" + FacebookOauth["secret"] +"&"+
                   "code="+code)
        result = urlfetch.fetch(fboauth)
        token = result.content
        session['token'] = token 
        userObj = urlfetch.fetch("https://graph.facebook.com/me?fields=id,name&"+token)
        userObj = userObj.content
        userObj = json.loads(userObj)
        session['user'] =  {"id": str(unicode(userObj['id'])), "name": userObj["name"].encode('utf-8') }

        
        self.redirect(session['tourl'])

class UserHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
        if session.has_key('user'):
            self.response.write(json.dumps(session['user']))
        else:
            self.response.write("{\"error\":\"login please\"}")


class TestChinese(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
        self.response.write(("<html><body>嗨肉腳幹"+"</body></html>"))


app = webapp2.WSGIApplication([
    ('/login', LoginHandler),
    ('/callback', CallbackHandler),
    ('/user', UserHandler),
    ('/test', TestChinese)
], debug=True)
