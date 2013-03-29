#!/usr/bin/env python


import time
import sys
import os
import json
from flask import Flask, Request, Response
application = app = Flask('wsgi')

@app.route('/')
def welcome():
    return 'welcome to appfog!'

@app.route('/env')
def env():
    return os.environ.get("VCAP_SERVICES", "{}")

@app.route('/mongo')
def mongotest():
    from pymongo import Connection
    uri = mongodb_uri()
    conn = Connection(uri)
    coll = conn.db['ts']
    coll.insert(dict(now=int(time.time())))
    last_few = [str(x['now']) for x in coll.find(sort=[("_id", -1)], limit=10)]
    body = "\n".join(last_few)
    return Response(body, content_type="text/plain;charset=UTF-8")

@app.route('/token')
def Token():
    rec = {}
    rec['token'] = "MoonXue"
    rec['timestamp'] = request.args.get('timestamp','')
    rec['nonce'] = request.args.get('nonce','')
    echostr = request.args.get('echostr','')
    signature = request.args.get('signature','')
    result = checkRec(rec)
    if result == signature:
        return echostr
    else:
        return 
    
def checkRec(rec):
    from hashlib import sha1
    rec = sortedDictValues(rec)
    s=''
    for v in rec.values():
        s+=v
    return sha1(s).hexdigest()
    
def sortedDictValues(adict):
    items = adict.items()
    items.sort()
    return [value for key, value in items]

def mongodb_uri():
    local = os.environ.get("MONGODB", None)
    if local:
        return local
    services = json.loads(os.environ.get("VCAP_SERVICES", "{}"))
    if services:
        creds = services['mongodb-1.8'][0]['credentials']
        uri = "mongodb://%s:%s@%s:%d/%s" % (
            creds['username'],
            creds['password'],
            creds['hostname'],
            creds['port'],
            creds['db'])
        print >> sys.stderr, uri
        return uri
    else:
        raise Exception, "No services configured"
    

if __name__ == '__main__':
    app.run(debug=True)
