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
import logging
from google.appengine.api import channel
from gaesessions import get_current_session
from google.appengine.api import memcache
from google.appengine.ext import ndb
import datetime

import hashlib
try:
    import simplejson as json
except:
    import json


class CommCreateHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
        
        session = get_current_session()
        if session.has_key('user') == False:
            self.response.write("{\"error\":\"login please\"}")
            return

        d        = datetime.datetime.now()
        unixtime = int(d.strftime('%s'))
        m        = hashlib.md5()
        m.update(str(unixtime))
        
        roomid   = m.hexdigest()[0:11]
        token    = channel.create_channel(roomid, duration_minutes=1440)
        
        myuser   = session['user']
        roominfo = {"token": token, "roomid":roomid, "users":[ myuser ]}
        output   = roominfo
        output["current"] = myuser

        self.response.write(json.dumps(output))
        
        memcache.add(key="room["+ roomid +"]" , value=json.dumps(output), time=86400)
        
class Record(ndb.Model):
    uid   = ndb.StringProperty()
    rid   = ndb.StringProperty()
    score = ndb.IntegerProperty()
    time  = ndb.DateTimeProperty(auto_now_add=True)
        
class CommJoinHandler(webapp2.RequestHandler):
    def get(self):

        self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
        
        session = get_current_session()
        #error check
        if session.has_key('user') == False:
            logging.error("Login Please")
            self.response.write("{\"error\":\"login please\"}")
            return

        roomid   = self.request.get('roomid')
        myuser   = session["user"]
        roominfo = json.loads(memcache.get(key="room["+ roomid +"]"))

        needupdate = True
        for inuser in roominfo["users"]:
            if inuser['id'] == myuser['id']:
                #self.response.write("{\"error\":\"You have in this room.\"}")
                needupdate = False
                break

         
        logging.info(json.dumps(roominfo))
        if needupdate==True:
            roominfo["users"].append(myuser) 
            memcache.set(key="room["+ roomid +"]" , value=json.dumps(roominfo), time=86400)
        
        logging.info(json.dumps(roominfo))
        #push data
        data = {
            "from" : myuser,
            "method": "join"
        }
        
        channel.send_message(roomid, json.dumps(data))
        roominfo["current"] = myuser
        self.response.write(json.dumps(roominfo))

class CommCounterHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
        roomid  = self.request.get('roomid')
        
        session = get_current_session()
            
        if session.has_key("user")==False:
            self.response.write("{\"status\":false }")
            
        # save personal data
        if session.has_key("room["+ roomid +"]"): 
            session["room["+ roomid +"]"] = session["room["+ roomid +"]"] + 1
        else:
            session["room["+ roomid +"]"] = 1
        
        myuser  = session['user']
        
        key = ndb.Key("Record", str(myuser["id"]) + "_" + str(roomid))
        pushupRc = Record(key=key)
        pushupRc.populate(uid=str(myuser["id"]), rid=str(roomid), score=session["room["+ roomid +"]"])
        pushupRc.put()

        logging.info("[K]"+str(key.kind()))
        logging.info("[I]"+str(key.id()))

        #push data
        output = {
            "from": myuser,
            "count": session["room["+ roomid +"]"],
            "method": "incr"
        }

        channel.send_message(roomid, json.dumps(output))

        self.response.write("{\"status\":true }")


class CommBoardHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
        roomid  = self.request.get('roomid')
        
        session = get_current_session()
            
        if session.has_key("user")==False:
            self.response.write("{\"status\":false }")
        
        myuser = session['user']
        qry    = Record.query(Record.uid == myuser['id']).order(-Record.score)
        rcs    = qry.fetch()
        
        output = []
        for rc in rcs:
            output.append({"score": rc.score, "time": int(rc.time.strftime('%s')) })

        self.response.write(json.dumps(output))
        return



app = webapp2.WSGIApplication([
    ('/create', CommCreateHandler),
    ('/join', CommJoinHandler),
    ('/push', CommCounterHandler),
    ('/board', CommBoardHandler)
], debug=True)

