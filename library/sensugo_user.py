#!/usr/bin/python

from ansible.module_utils.basic import *
from ansible.module_utils.sensu_api import *

class SensuUser:
  def __init__(self, api, name):
    self.api       = api
    self.name      = name
    self.exist     = False

  def get_data(self):
    try:
      status_code, data = self.api.get('users/{}'.format(self.name))
      if status_code == 200 and not data['disabled']:
        self.exist   = True
        self.options = {
          'groups':  data['groups']
        }
    except:
      pass
    
  def has_changed(self, options):
    for option, value in self.options.items():
      if options[option] != value:
        return True
    
    return False

  def password_has_changed(self, password):
    try:
      self.api.auth(self.name, password)
      self.api.auth()
      return False
    except:
      return True

  def create(self, options):
    options.update({
      'username': self.name,
      'disabled': False
    })

    self.api.put(
      'users/{}'.format(self.name),
      options
    )

  def delete(self):
    self.api.delete(
      'users/{}'.format(self.name)
    )
    
def main():
  fields = {
    'name':         { 'type': 'str',  'required': True },
    'groups':       { 'type': 'list', 'default': [] },
    'password':     { 'type': 'str',  'default': None },
    'api_url':      { 'type': 'str',  'default': 'http://127.0.0.1:8080' },
    'api_user':     { 'type': 'str',  'default': 'admin' },
    'api_password': { 'type': 'str',  'default': 'P@ssw0rd!' },
    'state':        { 'type': 'str',  'default': 'present', 'choices': ['present', 'absent'] }
  }
  module = AnsibleModule(argument_spec=fields)
  changed = True

  options = {
    'groups':   module.params['groups'],
    'password': module.params['password']
  }

  api = SensuApi(
    module.params['api_url'],
    module.params['api_user'],
    module.params['api_password']
  )
  api.auth()

  user = SensuUser(
    api,
    module.params['name']
  )
  user.get_data()

  if module.params['state'] == 'present':
    if not user.exist or user.has_changed(options) or user.password_has_changed(module.params['password']):
      user.create(options)
    else:
      changed = False
  else:
    if user.exist:
      user.delete()
    else:
      changed = False

  module.exit_json(changed=changed)

if __name__ == '__main__':
  main()
