from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from accounts.models import MyOrganization

from config import WORKER_TOKEN

class TokenAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):

        if not scope['query_string']:
            scope['user'] = AnonymousUser()
            return self.inner(scope)

        query = dict((x.split('=') for x in scope['query_string'].decode().split("&")))
        # User
        if query.get('token'):
            scope['is_worker'] = False
            if query.get('token') == WORKER_TOKEN:
                scope['is_worker'] = True
                scope['user'] = AnonymousUser()
            else:
                try:
                    token = Token.objects.get(key=query.get('token'))
                    scope['user'] = token.user
                except Token.DoesNotExist:
                    scope['user'] = AnonymousUser()
        # Organization
        if query.get('organization'):
            try:
                if scope['is_worker']:
                    scope['organization'] = MyOrganization.objects.get(
                                                slug = query.get('organization'))
                else:
                    scope['organization'] = MyOrganization.objects.get(
                                                slug = query.get('organization'),
                                                myuser=scope['user'])
            except MyOrganization.DoesNotExist:
                print('nie ma')
                scope['organization'] = None
        close_old_connections()
        return self.inner(scope)