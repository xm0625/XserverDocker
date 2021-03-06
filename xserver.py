# coding=utf-8

# fix zh write bug
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
# fix zh write bug #

# server.py
# from wsgiref module import:
from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
import requests
import json

password = "123456"

class CommonException(Exception):
    code = "0"
    message = "system busy"
    """docstring for CommonException"""
    def __init__(self, code, message="system busy"):
        super(CommonException, self).__init__()
        if code:
            self.code = code
        if message:
            self.message = message

def parse_and_fetch(request):
    if "method" not in request.keys():
        raise CommonException("-1","method not exist")
    if "url" not in request.keys():
        raise CommonException("-1","url not exist")
    if "password" not in request.keys():
        raise CommonException("-1","password not exist")
    if request["password"] != password:
        raise CommonException("-1","password not correct")
    url = request["url"]
    print 'request["method"]:'+request["method"]
    if request["method"] == "GET":
        session = requests.Session()
        response = session.get(url)
        content=response.text
        print "http get res:"+content
        return content
    if request["method"] == "POST":
        if "postDataString" not in request.keys():
            raise CommonException("-1","postDataString not exist")
        postDataString = request["postDataString"]
        session = requests.Session()
        response = session.post(url, postDataString)
        content = response.text
        print "http post res:"+content
        return content
    raise CommonException("-1","method not valid")

def app(environ, start_response):

    request_method = environ["REQUEST_METHOD"] #GET
    path_info = environ["PATH_INFO"]  # /hi/name/index.action
    query_string = environ["QUERY_STRING"]
    remote_address = environ["REMOTE_ADDR"]
    print "request_method:"+request_method
    print "path_info:"+path_info
    print "remote_address:"+remote_address

    if request_method == "GET" :
        request = parse_qs(query_string)
    else:
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
        request_body = environ['wsgi.input'].read(request_body_size)
        request = parse_qs(request_body)
    for (d,x) in request.items():
        if isinstance(x, list) and len(x) == 1:
            request[d] = x[0]
    for (d,x) in request.items():
        print "key:"+d+",value:"+str(x)


    if path_info == "/" :
        response_string = ""
        response_code = "200 OK"
        response_header = [('Content-type', 'text/html')]
        try:
            fetch_result = parse_and_fetch(request)
            response_data = {"code":"1","message":"success","result":fetch_result}
            response_string = json.dumps(response_data)
        except CommonException as ce:
            response_string ='{"code":"'+ce.code+'","message":"'+ce.message+'"}'
        except ValueError:
            response_string ='{"code":"0","message":"system busy"}'
    else:
        response_string = "404 NOT FOUND"
        response_code = "404 NOT FOUND"
        response_header = [('Content-type', 'text/html')]

    start_response(response_code,response_header)
    return [response_string]


httpd = make_server('', 8000, app)
print "Serving HTTP on port 8000..."
httpd.serve_forever()
