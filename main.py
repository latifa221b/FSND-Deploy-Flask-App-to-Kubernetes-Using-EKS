"""
A simple app to create a JWT token.
"""
#!/usr/local/bin/python3


import os
import logging
import datetime
import functools
import jwt

# pylint: disable=import-error
from flask import Flask, jsonify, request, abort
from aws_cdk import core , aws_ssm as ssm

LOG_LEVEL = os.environ.get('LOG_LEVEL','DEBUG')

def _logger():
    '''
    Setup logger format, level, and handler.

    RETURNS: log object
    '''
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    log = logging.getLogger(__name__)
    log.setLevel(LOG_LEVEL)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    log.addHandler(stream_handler)
    return log


LOG = _logger()
LOG.debug("Starting with log level: %s" % LOG_LEVEL )
APP = Flask(__name__)

class aws:
 def setPara(self):
    self.secret_value = ssm.StringParameter.value_for_secure_string_parameter(self,"JWT_SECRET",
    version=1)
    return self.secret_value

class custom_stack(core.Stack):
   def __init__(self, scope: core.Stack, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
    
app = core.App()
list = custom_stack(app,"udacitystack")
JWT_SECRET = aws.setPara(list)
print(JWT_SECRET)
def require_jwt(function):
    """
    Decorator to check valid jwt is present.
    """
    @functools.wraps(function)
    def decorated_function(*args, **kws):
        if not 'Authorization' in request.headers:
            abort(401)
        data = request.headers['Authorization']
        token = str.replace(str(data), 'Bearer ', '')
        try:
            jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except: # pylint: disable=bare-except
            abort(401)

        return function(*args, **kws)
    return decorated_function


@APP.route('/', methods=['POST', 'GET'])
def health():
    return jsonify("Healthy")


@APP.route('/auth', methods=['POST'])
def auth():
    """
    Create JWT token based on email.
    """
    request_data = request.get_json()
    email = request_data.get('email')
    password = request_data.get('password')
    if not email:
        LOG.error("No email provided")
        return jsonify({"message": "Missing parameter: email"}, 400)
    if not password:
        LOG.error("No password provided")
        return jsonify({"message": "Missing parameter: password"}, 400)
    body = {'email': email, 'password': password}

    user_data = body

    return jsonify(token=_get_jwt(user_data).decode('utf-8'))


@APP.route('/contents', methods=['GET'])
def decode_jwt():
    """
    Check user token and return non-secret data
    """
    if not 'Authorization' in request.headers:
        abort(401)
    data = request.headers['Authorization']
    token = str.replace(str(data), 'Bearer ', '')
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except: # pylint: disable=bare-except
        abort(401)


    response = {'email': data['email'],
                'exp': data['exp'],
                'nbf': data['nbf'],
                'secret': JWT_SECRET }
    return jsonify(**response)


def _get_jwt(user_data):
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=2)
    payload = {'exp': exp_time,
               'nbf': datetime.datetime.utcnow(),
               'email': user_data['email']}
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

if __name__ == '__main__':
    APP.run(host='127.0.0.1', port=8080, debug=True)
