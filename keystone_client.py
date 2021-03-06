# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Digital Catapult

# This file belongs to the orion context broker plugin
# of the Business API Ecosystem.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Author: Angelo Capossele

from __future__ import unicode_literals

import requests


class KeystoneClient:

    _access_token = None
    _server = None
    _domain = None

    def __init__(self, user, password, domain, protocol, host, port=5000):
        self._domain = domain
        self._server = protocol + '://' + host + ':' + unicode(port)
        self._access_token = self._login(user, password)

    def _login(self, user, password):
        url = self._server + '/v3/auth/tokens'

        login_resp = requests.post(url, json={
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "domain": {
                                "name": self._domain
                            },
                            "name": user,
                            "password": password
                        }
                    }
                }
            }
        })

        login_resp.raise_for_status()
        return login_resp.headers.get('X-Subject-Token', '')

    def _make_get_request(self, url):
        resp = requests.get(url, headers={
            'X-Auth-Token': self._access_token
        })

        resp.raise_for_status()
        return resp.json()

    # def get_project_by_name(self, project_name):
    #     return self._make_get_request(self._server + '/v3/projects?name=' + project_name)

    def get_application_by_id(self, application_id):
        return self._make_get_request(self._server + '/v3/OS-OAUTH2/consumers/' + application_id)
    
    def get_azf_domain_by_app_id(self, application_id):
        resp = self._make_get_request(self._server + '/v3/OS-OAUTH2/consumers/' + application_id)
        return resp['consumer']['ac_domain']

    def get_domain_by_id(self, domain_id):
        return self._make_get_request(self._server + '/v3/domains/' + domain_id)

    def get_domain_id(self, domain_name):
        resp = self._make_get_request(self._server + '/v3/domains?name=' + domain_name)
        for domain_id in resp['domains']:
            return domain_id['id']
    # def get_role_by_name(self, role_name):
    #     return self._make_get_request(self._server + '/v3/roles?name=' + role_name)

    def get_role_by_name(self, role_name):
        return self._make_get_request(self._server + '/v3/roles?name=' + role_name)

    #http://idm.docker:5000/v3/OS-ROLES/roles?application_id=47ca01dd15b446b5a5f9f08ad495f52a&name=Consumer
    def get_role_id_by_name(self, application_id, role_name):
        resp = self._make_get_request(self._server + '/v3/OS-ROLES/roles?application_id=' + application_id + '&name=' + role_name)
        for role in resp['roles']:
            if role['name'] == role_name:
                return role['id']
        return False
    

    # def get_user_by_name(self, username):
    #     return self._make_get_request(self._server + '/v3/users?name=' + username)

    def get_user_by_username(self, username):
        return self._make_get_request(self._server + '/v3/users?username=' + username)
    
    def get_user_by_name(self, name):
        return self._make_get_request(self._server + '/v3/users?name=' + name)

    def get_token_info(self, token):
        return self._make_get_request(self._server + '/v3/access-tokens/' + token)

    def check_role(self, application_id, user_id, role_id):
        #get roles for user on application
        resp = self._make_get_request(self._server + '/v3/OS-ROLES/users/role_assignments?user_id=' + user_id + '&application_id=' + application_id)
        for role in resp['role_assignments']:
            if role['role_id'] == role_id:
                return True
        return False 

    def create_permission(self, permission):
        resp = requests.post(self._server + '/v3/OS-ROLES/permissions',
                            json = permission,
                            headers={'X-Auth-Token': self._access_token})
        resp.raise_for_status()
        return resp

    def create_role(self, role):
        resp = requests.post(self._server + '/v3/OS-ROLES/roles',
                            json = role,
                            headers={'X-Auth-Token': self._access_token})
        resp.raise_for_status()
        return resp

    def grant_permission_to_role(self, permission_id, role_id):
        resp = requests.put(self._server + '/v3/OS-ROLES/roles/' + role_id + '/permissions/' + permission_id, headers={
            'X-Auth-Token': self._access_token
        })
        resp.raise_for_status()
        return resp

    def grant_role(self, application_id, user_id, role_id):
        resp = requests.put(self._server + '/v3/OS-ROLES/users/' + user_id + '/applications/' + application_id + '/roles/' + role_id, headers={
            'X-Auth-Token': self._access_token
        })
        resp.raise_for_status()
        return resp

    def revoke_role(self, application_id, user_id, role_id):
        resp = requests.delete(self._server + '/v3/OS-ROLES/users/' + user_id + '/applications/' + application_id + '/roles/' + role_id, headers={
            'X-Auth-Token': self._access_token
        })
        resp.raise_for_status()  
        return resp
