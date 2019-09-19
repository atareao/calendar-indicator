#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Calendar-Indicator
#
# Copyright (C) 2011-2019 Lorenzo Carbonell Cerezo
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests
import json
import os
from urllib.parse import urlencode
import random
import time
from logindialog import LoginDialog
import mimetypes
import io


class GoogleService(object):
    def __init__(self, auth_url, token_url, redirect_uri, scope, client_id,
                 client_secret, token_file):
        self.session = requests.session()
        self.auth_url = auth_url
        self.token_url = token_url
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_file = token_file
        self.access_token = None
        self.refresh_token = None
        if os.path.exists(token_file):
            f = open(token_file, 'r')
            text = f.read()
            f.close()
            try:
                data = json.loads(text)
                self.access_token = data['access_token']
                self.refresh_token = data['refresh_token']
            except Exception as e:
                print('Error')
                print(e)

    def get_authorize_url(self):
        oauth_params = {'redirect_uri': self.redirect_uri,
                        'client_id': self.client_id,
                        'scope': self.scope,
                        'response_type': 'code'}
        authorize_url = "%s?%s" % (self.auth_url, urlencode(oauth_params))
        print('Authorization url: %s' % authorize_url)
        return authorize_url

    def get_authorization(self, temporary_token):
        data = {'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': temporary_token,
                'grant_type': 'authorization_code',
                'scope': self.scope}
        response = self.session.request('POST', self.token_url, data=data)
        if response.status_code == 200:
            ans = json.loads(response.text)
            self.access_token = ans['access_token']
            self.refresh_token = ans['refresh_token']
            f = open(self.token_file, 'w')
            f.write(json.dumps({'access_token': self.access_token,
                                'refresh_token': self.refresh_token}))
            f.close()
            print('Authorizate')
            return self.access_token, self.refresh_token
        return None

    def do_revoke_authorization(self):
        self.access_token = None
        self.refresh_token = None
        if os.path.exists(self.token_file):
            os.remove(self.token_file)

    def do_refresh_authorization(self):
        data = {'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'}
        response = self.session.request('POST', self.token_url, data=data)
        if response.status_code == 200:
            ans = json.loads(response.text)
            self.access_token = ans['access_token']
            f = open(self.token_file, 'w')
            f.write(json.dumps({'access_token': self.access_token,
                                'refresh_token': self.refresh_token}))
            f.close()
            print('Refresh Authorization')
            return self.access_token
        return None

    def do_request(self, method, url, addheaders, data=None, params=None,
                   first=True):
        headers = {'Authorization': 'OAuth %s' % self.access_token}
        if addheaders:
            headers.update(addheaders)
        print(headers)
        if data:
            if params:
                response = self.session.request(method, url, data=data,
                                                headers=headers,
                                                params=params)
            else:
                response = self.session.request(method, url, data=data,
                                                headers=headers)
        else:
            if params:
                response = self.session.request(method, url,
                                                headers=headers,
                                                params=params)
            else:
                response = self.session.request(method, url, headers=headers)
        print(response)
        if response.status_code == 200:
            return response
        elif response.status_code == 403 and first:
            ans = self.do_refresh_authorization()
            print(ans)
            if ans:
                return self.do_request(method, url, addheaders, first=False)
        return None
