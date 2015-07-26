#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#
# services.py
#
# Copyright (C) 2012 Lorenzo Carbonell
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
#
#
#

import requests
import json
import os
from urllib.parse import urlencode
import random
import time
from logindialog import LoginDialog
import mimetypes
import io


KEY = '2eoegx5n62z1qyh'
SECRET = '9gsfezp3hc1xl44'
class DropboxService(object):
	def __init__(self,client_id,client_secret,token_file):
		self.session = requests.session()
		self.request_token_url = 'https://api.dropbox.com/1/oauth/request_token'
		self.authorize_url = 'https://www.dropbox.com/1/oauth/authorize'
		self.access_token_url = 'https://api.dropbox.com/1/oauth/access_token'
		self.key = '2eoegx5n62z1qyh'
		self.secret = '9gsfezp3hc1xl44'
		self.client_id = client_id
		self.client_secret = client_secret
		self.token_file = token_file
		self.access_token = None
		self.refresh_token = None
		if os.path.exists(token_file):
			f = open(token_file,'r')
			text = f.read()
			f.close()
			try:			
				data = json.loads(text)
				self.oauth_token = data['oauth_token']
				self.oauth_token_secret = data['oauth_token_secret']
			except Exception as e:
				print('Error')
				print(e)

	def get_request_token(self):
		params = {}
		params['oauth_consumer_key'] = KEY
		params['oauth_timestamp'] = int(time.time())
		params['oauth_nonce'] = ''.join([str(random.randint(0, 9)) for i in range(8)])
		params['oauth_version'] = '1.0'
		params['oauth_signature_method'] = 'PLAINTEXT'
		params['oauth_signature'] = '%s&'%SECRET
		response = self.session.request('POST',self.request_token_url,params=params)
		if response.status_code == 200:
			oauth_token_secret, oauth_token = response.text.split('&')
			oauth_token_secret = oauth_token_secret.split('=')[1]
			self.ts = oauth_token_secret
			oauth_token = oauth_token.split('=')[1]
			return oauth_token, oauth_token_secret
		return None

	def get_authorize_url(self,oauth_token,oauth_token_secret):
		params = {}
		params['oauth_token'] = oauth_token
		params['oauth_callback'] = 'http://localhost'
		return 'https://www.dropbox.com/1/oauth/authorize?%s'%(urlencode(params))

	def get_access_token(self,oauth_token,secret):
		params = {}
		params['oauth_consumer_key'] = KEY
		params['oauth_token'] = oauth_token
		params['oauth_timestamp'] = int(time.time())
		params['oauth_nonce'] = ''.join([str(random.randint(0, 9)) for i in range(8)])
		params['oauth_version'] = '1.0'
		params['oauth_signature_method'] = 'PLAINTEXT'
		params['oauth_signature'] = '%s&%s'%(SECRET,secret)
		response = self.session.request('POST',self.access_token_url,params=params)
		print(response,response.status_code,response.text)
		if response.status_code == 200:
			oauth_token_secret, oauth_token,uid = response.text.split('&')
			oauth_token_secret = oauth_token_secret.split('=')[1]
			oauth_token = oauth_token.split('=')[1]
			uid = uid.split('=')[1]
			self.oauth_token = oauth_token
			self.oauth_token_secret = oauth_token_secret
			f = open(self.token_file,'w')
			f.write(json.dumps({'oauth_token':oauth_token,'oauth_token_secret':oauth_token_secret}))
			f.close()
			
			return uid, oauth_token, oauth_token_secret
		return None		
		
	def get_account_info(self):
		ans = self.__do_request('GET','https://api.dropbox.com/1/account/info')
		if ans.status_code == 200:
			print(ans.text)

	def get_file(self,afile):
		url = 'https://api-content.dropbox.com/1/files/sandbox/%s'%(afile)
		ans = self.__do_request('GET',url)
		if ans.status_code == 200:
			print(ans.text)

	def put_file(self,afile):
		name = afile.split('/')[-1]
		print(name)
		url = 'https://api-content.dropbox.com/1/files_put/sandbox/%s'%(name)
		print(url)
		addparams = {}
		addparams['overwrite'] = True
		afilee = open(afile,'rb')
		data = afilee.read()
		afilee.close()
		addheaders={'Content-type':'multipart/related; boundary="END_OF_PART"','Content-length':str(len(data)),'MIME-version':'1.0'}
		ans = self.__do_request('POST',url, addheaders = addheaders,addparams=addparams, data=data)
		if ans is not None:
			return ans.text
		
	def __do_request(self,method,url,addheaders=None,data=None,addparams=None,first=True,files=None):
		params = {}
		params['oauth_consumer_key'] = KEY
		params['oauth_token'] = self.oauth_token
		params['oauth_timestamp'] = int(time.time())
		params['oauth_nonce'] = ''.join([str(random.randint(0, 9)) for i in range(8)])
		params['oauth_version'] = '1.0'
		params['oauth_signature_method'] = 'PLAINTEXT'
		params['oauth_signature'] = '%s&%s'%(SECRET,self.oauth_token_secret)
		headers = None
		if headers is not None:
			headers.update(addheaders)
		else:
			headers = addheaders
		if addparams is not None:
			params.update(addparams)
		if data:
			response = self.session.request(method,url,data=data,headers=headers,params=params,files = files)
		else:
			response = self.session.request(method,url,headers=headers,params=params,files=files)
		print(response,response.status_code)
		if response.status_code == 200 or response.status_code == 201:
			return response
		elif (response.status_code == 401 or response.status_code == 403) and first:
			'''
			ans = self.do_refresh_authorization()
			if ans:
				return self.__do_request(method,url,addheaders,data,params,first=False)
			'''
		return None

UBUNTU_CONSUMER_KEY = 'ubuntuone'		
UBUNTU_CONSUMER_SECRET = 'hammertime'

class UbuntuOneService(object):
	def __init__(self, token_file):
		self.session = requests.session()
		self.request_token_url = 'https://one.ubuntu.com/oauth/request/'
		self.authorize_url = 'https://one.ubuntu.com/oauth/authorize/'
		self.access_token_url = 'https://one.ubuntu.com/oauth/access/'
		self.token_file = token_file
		self.access_token = None
		self.refresh_token = None
		if os.path.exists(token_file):
			f = open(token_file,'r')
			text = f.read()
			f.close()
			try:			
				data = json.loads(text)
				self.oauth_token = data['oauth_token']
				self.oauth_token_secret = data['oauth_token_secret']
			except Exception as e:
				print('Error')
				print(e)

	def get_request_token(self):
		params = {}
		params['oauth_consumer_key'] = UBUNTU_CONSUMER_KEY
		params['oauth_timestamp'] = int(time.time())
		params['oauth_nonce'] = ''.join([str(random.randint(0, 9)) for i in range(8)])
		params['oauth_version'] = '1.0'
		params['oauth_signature_method'] = 'PLAINTEXT'
		params['oauth_signature'] = 'hammertime%26'
		response = self.session.request('POST',self.request_token_url,params=params)
		print(response)
		if response.status_code == 200:
			oauth_token_secret, oauth_token = response.text.split('&')
			oauth_token_secret = oauth_token_secret.split('=')[1]
			self.ts = oauth_token_secret
			oauth_token = oauth_token.split('=')[1]
			return oauth_token, oauth_token_secret
		return None

	def get_authorize_url(self,oauth_token,oauth_token_secret):
		params = {}
		params['oauth_token'] = oauth_token
		params['oauth_callback'] = 'http://localhost'
		return 'https://www.dropbox.com/1/oauth/authorize?%s'%(urlencode(params))

	def get_access_token(self,oauth_token,secret):
		params = {}
		params['Oauth realm'] = ''
		params['oauth_consumer_key'] = UBUNTU_CONSUMER_KEY
		params['oauth_token'] = oauth_token
		params['oauth_timestamp'] = int(time.time())
		params['oauth_nonce'] = ''.join([str(random.randint(0, 9)) for i in range(8)])
		params['oauth_version'] = '1.0'
		params['oauth_signature_method'] = 'PLAINTEXT'
		params['oauth_signature'] = '%s&%s'%(UBUNTU_CONSUMER_SECRET,secret)
		params['oauth_callback'] = 'http://localhost:8801/index.cfm/general/getAccessToken'
		response = self.session.request('POST',self.access_token_url,params=params)
		print(response,response.status_code,response.text)
		if response.status_code == 200:
			oauth_token_secret, oauth_token,uid = response.text.split('&')
			oauth_token_secret = oauth_token_secret.split('=')[1]
			oauth_token = oauth_token.split('=')[1]
			uid = uid.split('=')[1]
			self.oauth_token = oauth_token
			self.oauth_token_secret = oauth_token_secret
			f = open(self.token_file,'w')
			f.write(json.dumps({'oauth_token':oauth_token,'oauth_token_secret':oauth_token_secret}))
			f.close()
			
			return uid, oauth_token, oauth_token_secret
		return None		
		
	def get_account_info(self):
		ans = self.__do_request('GET','https://api.dropbox.com/1/account/info')
		if ans.status_code == 200:
			print(ans.text)

	def get_file(self,afile):
		url = 'https://api-content.dropbox.com/1/files/dropbox/%s'%(afile)
		ans = self.__do_request('GET',url)
		if ans.status_code == 200:
			print(ans.text)
		
	def __do_request(self,method,url,addheaders=None,data=None,params=None,first=True,files=None):
		params = {}
		params['oauth_consumer_key'] = UBUNTU_CONSUMER_KEY
		params['oauth_token'] = self.oauth_token
		params['oauth_timestamp'] = int(time.time())
		params['oauth_nonce'] = ''.join([str(random.randint(0, 9)) for i in range(8)])
		params['oauth_version'] = '1.0'
		params['oauth_signature_method'] = 'PLAINTEXT'
		params['oauth_signature'] = '%s&%s'%(UBUNTU_CONSUMER_SECRET,self.oauth_token_secret)
		headers = None
		if addheaders:
			headers.update(addheaders)
		if data:
			if params:
				response = self.session.request(method,url,data=data,headers=headers,params=params,files=files)
			else:
				response = self.session.request(method,url,data=data,headers=headers,files=files)
		else:
			if params:
				response = self.session.request(method,url,headers=headers,params=params,files=files)
			else:		
				response = self.session.request(method,url,headers=headers,files=files)
		print(response,response.status_code)
		if response.status_code == 200 or response.status_code == 201:
			return response
		elif (response.status_code == 401 or response.status_code == 403) and first:
			'''
			ans = self.do_refresh_authorization()
			if ans:
				return self.__do_request(method,url,addheaders,data,params,first=False)
			'''
		return None

class GoogleService(object):
	def __init__(self,auth_url,token_url,redirect_uri,scope,client_id,client_secret,token_file):
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
			f = open(token_file,'r')
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
		oauth_params = {'redirect_uri': self.redirect_uri, 'client_id': self.client_id, 'scope': self.scope, 'response_type':'code'}
		authorize_url = "%s?%s" % (self.auth_url, urlencode(oauth_params))
		print('Authorization url: %s'%authorize_url)
		return authorize_url

	def get_authorization(self,temporary_token):
		data = {'redirect_uri': self.redirect_uri, 'client_id': self.client_id, 'client_secret': self.client_secret, 'code': temporary_token,'grant_type':'authorization_code','scope':self.scope}
		response = self.session.request('POST',self.token_url,data=data)
		if response.status_code == 200:
			ans = json.loads(response.text)
			self.access_token = ans['access_token']
			self.refresh_token = ans['refresh_token']
			f = open(self.token_file,'w')
			f.write(json.dumps({'access_token':self.access_token,'refresh_token':self.refresh_token}))
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
		data = {'client_id': self.client_id, 'client_secret': self.client_secret,'refresh_token': self.refresh_token,'grant_type':'refresh_token'}
		response = self.session.request('POST',self.token_url,data=data)
		if response.status_code == 200:
			ans = json.loads(response.text)
			self.access_token = ans['access_token']
			f = open(self.token_file,'w')
			f.write(json.dumps({'access_token':self.access_token,'refresh_token':self.refresh_token}))
			f.close()
			print('Refresh Authorization')
			return self.access_token
		return None
		
	def do_request(self,method,url,addheaders,data=None,params=None,first=True):
		headers ={'Authorization':'OAuth %s'%self.access_token}
		if addheaders:
			headers.update(addheaders)
		print(headers)
		if data:
			if params:
				response = self.session.request(method,url,data=data,headers=headers,params=params)		
			else:
				response = self.session.request(method,url,data=data,headers=headers)		
		else:
			if params:
				response = self.session.request(method,url,headers=headers,params=params)		
			else:
				response = self.session.request(method,url,headers=headers)
		print(response)
		if response.status_code == 200:
			return response
		elif response.status_code == 403 and first:
			ans = self.do_refresh_authorization()
			print(ans)
			if ans:
				return self.do_request(method,url,addheaders,first=False)
		return None
if __name__ == '__main__':
	us = UbuntuOneService('tokenus')
	session = requests.session()
	ans = session.request('GET','https://login.ubuntu.com/')
	print(ans)
	print(ans.text)
	#oauth_token,oauth_token_secret = us.get_request_token()
	
	
	#ds = DropboxService('','','token')
	'''
	oauth_token,oauth_token_secret = ds.get_request_token()
	authorize_url = ds.get_authorize_url(oauth_token,oauth_token_secret)
	ld = LoginDialog(1024,600,authorize_url,'http://localhost/?uid=','not_approved=true')
	ld.run()
	ans = ld.code
	ld.destroy()
	if ans is not None:
		print(ans)
		uid,oauth_token = ans.split('&')
		uid = uid.split('=')[1]
		oauth_token = oauth_token.split('=')[1]
		print(uid,oauth_token)
		ans = ds.get_access_token(oauth_token,oauth_token_secret)
		print(ans)
		print(ds.get_account_info())
	'''
	'''
	print(ds.get_account_info())
	print(ds.get_file('data'))
	print(ds.put_file('/home/atareao/Escritorio/data'))
	'''
	exit(0)
	
