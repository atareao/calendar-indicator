#! /usr/bin/python
# -*- coding: utf-8 -*-
#
#
# googlereaderapi.py
# 
# A python wrapper for the Google Reader
#
# Copyright (C) 2011 Lorenzo Carbonell
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

__author__ = 'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'
__date__ ='$27/10/2012'
__copyright__ = 'Copyright (c) 2012 Lorenzo Carbonell'
__license__ = 'GPLV3'
__url__ = 'http://www.atareao.es'

from services import UbuntuOneService
from logindialog import LoginDialog

AUTH_URL = 'https://login.ubuntu.com/'
TOKEN_URL = 'https://one.ubuntu.com/oauth/request/'
USER_AUTHORIZATION_URL = 'https://one.ubuntu.com/oauth/authorize/'
AUTH_URL = USER_AUTHORIZATION_URL
ACCESS_TOKEN_URL = 'https://one.ubuntu.com/oauth/access/'
CLIENT_ID = 'ubuntuone'
CLIENT_SECRET = 'hammertime'

class UbuntuOne(UbuntuOneService):			
	def __init__(self,token_file):
		UbuntuOneService.__init__(self,auth_url=AUTH_URL,token_url=TOKEN_URL,redirect_uri='',scope='',client_id=CLIENT_ID,client_secret=CLIENT_SECRET,token_file='token')
	
	def arq(self,method,url,addheaders,data=None,params=None,first=True):
		headers ={'Authorization':'OAuth'}
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
	def __do_request(self,method,url,addheaders=None,data=None,params=None,first=True,files=None):
		headers ={'Authorization':'OAuth %s'%self.access_token,'GData-Version':'2'}
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
			ans = self.do_refresh_authorization()
			if ans:
				return self.__do_request(method,url,addheaders,data,params,first=False)
		return None
		
if __name__=='__main__' :
	import random
	import time
	nonce = random.randint(1000000, 10000000)
	timestamp = time.time()
	print(time.time())
	print(nonce)
	
	uo = UbuntuOne('token')
	authorize_url = uo.get_authorize_url()
	print(authorize_url)
	ld = LoginDialog(authorize_url)
	ld.run()
	#pi.get_authorization(ld.code)
	ld.destroy()	
	
	
	
	uo.arq('POST','https://one.ubuntu.com/oauth/request/',None,data="realm='', oauth_version='1.0', oauth_nonce='%s', oauth_timestamp='%s', oauth_consumer_key='ubuntuone', oauth_signature_method='PLAINTEXT', oauth_signature='hammertime'"%(nonce,timestamp))
	exit(0)
