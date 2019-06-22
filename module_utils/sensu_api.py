#!/usr/bin/python
import requests

class SensuApi:
  def __init__(self, url, user, password):
    self.url      = url
    self.user     = user
    self.password = password
    self.headers  = {}

  def auth(self, user = None, password = None):
    user = user or self.user
    password = password or self.password
    r = requests.get(
      '{}/auth'.format(self.url),
      auth=requests.auth.HTTPBasicAuth(user, password)
    )

    if r.status_code == 401:
      raise Exception('Authentification has failed')

    self.headers = { 'Authorization': r.json()['access_token'] }

  def get(self, path):
    r = requests.get(
      '{}/api/core/v2/{}'.format(self.url, path),
      headers=self.headers
    )

    if r.status_code == 500:
      raise Exception('Server return 500 error: {}'.format(r.text))
    elif r.status_code == 401:
      raise Exception('Authentification has failed')
      
    return r.status_code, r.json()

  def post(self, path, data):
    r = requests.post(
      '{}/api/core/v2/{}'.format(self.url, path),
      headers=self.headers,
      json=data
    )
    
    if r.status_code == 500:
      raise Exception('Server return 500 error: {}'.format(r.text))
    elif r.status_code == 401:
      raise Exception('Authentification has failed')
    elif r.status_code != 200:
      raise Exception('Server return an unknown error: {}'.format(r.text))

  def put(self, path, data):
    r = requests.put(
      '{}/api/core/v2/{}'.format(self.url, path),
      headers=self.headers,
      json=data
    )
    
    if r.status_code == 500:
      raise Exception('Server return 500 error: {}'.format(r.text))
    elif r.status_code == 401:
      raise Exception('Authentification has failed')
    elif r.status_code not in [200, 201, 204]:
      raise Exception('Server return an unknown error: {}'.format(r.text))

  def delete(self, path):
    r = requests.delete(
      '{}/api/core/v2/{}'.format(self.url, path),
      headers=self.headers
    )
    
    if r.status_code == 500:
      raise Exception('Server return 500 error: {}'.format(r.text))
    elif r.status_code == 401:
      raise Exception('Authentification has failed')
    elif r.status_code != 204:
      raise Exception('Server return an unknown error: {}'.format(r.text))
