# from functools import wraps

# from flask import make_response, request

# import os


# def basic_auth(func):
#     @wraps(func)
#     def decorated(*args, **kwargs):
#         auth = request.authorization
#         if (
#             auth
#             and auth.username == os.getenv("BASIC_AUTH_USERNAME")
#             and auth.password == os.getenv("BASIC_AUTH_PASSWORD")
#         ):
#             return func(*args, **kwargs)
#         return make_response(
#             "<!doctype html><html lang=en><title>401 Unauthorized</title><h1>Unauthorized</h1><p>The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn&#39;t understand how to supply the credentials required.</p>",
#             401,
#             {"WWW-Authenticate": "Basic realm"},
#         )

#     return decorated

from flask_httpauth import HTTPBasicAuth
import os
from werkzeug.security import generate_password_hash, check_password_hash

basic_auth = HTTPBasicAuth()

auth_user = os.getenv("BASIC_AUTH_USERNAME")
auth_password = generate_password_hash(os.getenv("BASIC_AUTH_PASSWORD"))


@basic_auth.verify_password
def verify_password(username, password):
    if username == auth_user and check_password_hash(auth_password, password):
        return username
