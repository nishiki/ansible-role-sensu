#!/usr/bin/python

from ansible.module_utils.basic import *
from ansible.module_utils.sensu_api import *

class SensuClusterRole:
  def __init__(self, api, name):
    self.api   = api
    self.name  = name
    self.exist = False

  def get_data(self):
    status_code, data = self.api.get('clusterroles/{}'.format(self.name))
    if status_code == 200:
      self.exist   = True
      self.options = {
        'rules': data['rules'],
      }
    
  def has_changed(self, options):
    if len(self.options['rules']) != len(options['rules']):
      return True

    for i in range(0, len(self.options['rules'])):
      for rule, value in self.options['rules'][i].items():
        if not rule in options['rules'][i]:
          if value:
            return True
        elif options['rules'][i][rule] != value:
          return True
        
      for rule, value in options['rules'][i].items():
        if not rule in self.options['rules'][i]:
          if value:
            return True
        elif self.options['rules'][i][rule] != value:
          return True

    return False

  def create(self, options):
    options = {
      'metadata': {
        'name': self.name
      },
      'rules': options['rules']
    }

    self.api.put(
      'clusterroles/{}'.format(self.name),
      options
    )

  def delete(self):
    self.api.delete(
      'clusterroles/{}'.format(self.name)
    )
 
    
def main():
  fields = {
    'name':         { 'type': 'str',  'required': True },
    'rules':        { 'type': 'list', 'required': True },
    'api_url':      { 'type': 'str',  'default': 'http://127.0.0.1:8080' },
    'api_user':     { 'type': 'str',  'default': 'admin' },
    'api_password': { 'type': 'str',  'default': 'P@ssw0rd!', 'no_log': True },
    'state':        { 'type': 'str',  'default': 'present', 'choices': ['present', 'absent'] }
  }
  module = AnsibleModule(argument_spec=fields)
  changed = False

  options = {
    'rules': module.params['rules']
  }

  api = SensuApi(
    module.params['api_url'],
    module.params['api_user'],
    module.params['api_password']
  )
  api.auth()

  clusterrole = SensuClusterRole(
    api,
    module.params['name']
  )
  clusterrole.get_data()

  if module.params['state'] == 'present':
    if not clusterrole.exist or clusterrole.has_changed(options):
      clusterrole.create(options)
      changed = True
  elif clusterrole.exist:
      clusterrole.delete()
      changed = True

  module.exit_json(changed=changed)

if __name__ == '__main__':
  main()
