"""Octoproxy - Service for Sidelaunching on GitHub Events"""
__version__ = '0.1.0'
__author__ = 'M. de Verteuil <mverteuil@github.com>'
__all__ = ['app', 'events', ]

from collections import namedtuple
import functools
import hashlib
import hmac
import os

from flask import Flask
from flask import request


# Configuration
# ==================================================================================================
SECRET = os.environ.get('OCTOPROXY_SECRET')
WEBHOOK_PATH = os.environ.get('OCTOPROXY_PATH', '/octoproxy/webhook/')

# Headers
# ==================================================================================================
EVENT_HEADER = 'X-GitHub-Event'
SIGNATURE_HEADER = 'X-Hub-Signature'


Event = namedtuple('Event', 'event_type repository callback')
RequestSignature = namedtuple('RequestDigest', 'algorithm digest')


def compare_digest(a, b):
    """
    Return a == b.

    If python > 2.7.7, uses hmac.compare_digest, otherwise uses `==` comparison.
    """
    if hasattr(hmac, 'compare_digest'):
        return hmac.compare_digest(a, b)
    else:
        return a == b


def with_hmac_verification(app_route):
    """ Decorates app routes with HMAC verification against the configuration secret. """
    @functools.wraps(app_route)
    def wrapper():
        if SECRET is not None:
            header_bytes = bytes(request.headers[SIGNATURE_HEADER])
            signature = RequestSignature(*header_bytes.split('='))
            verification = hmac.new(SECRET, request.data, getattr(hashlib, signature.algorithm))
            assert compare_digest(signature.digest, verification.hexdigest())
        return app_route()
    return wrapper


class EventRouter(object):
    event_handlers = []

    def trigger_event_handlers(self, event_type, event_data):
        match = True
        for event_handler in self.event_handlers:
            event_repository = event_data['repository']['full_name']
            # Skip if not the right type
            if event_handler.event_type != event_type:
                continue
            # Skip if not the right repository
            if event_handler.repository != '*' and event_handler.repository != event_repository:
                continue
            event_handler.callback(event_type, event_data)

    def register_event(self, event_type, repository='*'):
        def wrap(callback):
            self.event_handlers.append(Event(event_type, repository, callback))
            return callback
        return wrap


app = Flask(__name__)
events = EventRouter()


@app.route(WEBHOOK_PATH, methods=['POST'])
@with_hmac_verification
def request_proxy():
    events.trigger_event_handlers(request.headers[EVENT_HEADER], request.json)
    return request.data
