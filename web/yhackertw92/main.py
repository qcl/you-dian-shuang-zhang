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
import jinja2
import os
from gaesessions import get_current_session

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if session.has_key('user')==False:
            template = JINJA_ENVIRONMENT.get_template('index.html')
            innerHTML = template.render()
        else:
            template = JINJA_ENVIRONMENT.get_template('user.html')
            myuser = session["user"]
            template_values = myuser
            template_values["name"] =myuser["name"].decode("utf-8")
            innerHTML = template.render(template_values)
        self.response.write(innerHTML)
        '''
        self.response.write('<div>Hello world!</div>')
        session = get_current_session()
        if session.has_key('user')==False:
            self.response.write('<div><a href="./login">Facebook Login</div>')
        '''

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
