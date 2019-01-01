#!/usr/bin/python

from ansible.module_utils.basic import *
from ansible.module_utils.sensu_api import *

class SensuNamespace:
  def __init__(self, api, name):
    self.api       = api
    self.name      = name
    self.exist     = False

  def get_data(self):
    status_code, data = self.api.get('namespaces')
    for namespace in data:
      if namespace['name'] == self.name:
        self.exist = True
    
  def create(self):
    self.api.put(
      'namespaces/{}'.format(self.name),
      { 'name': self.name }
    )

  def delete(self):
    self.api.delete(
      'namespaces/{}'.format(self.name)
    )
    
def main():
  fields = {
    'name':         { 'type': 'str',  'required': True },
    'api_url':      { 'type': 'str',  'default': 'http://127.0.0.1:8080' },
    'api_user':     { 'type': 'str',  'default': 'admin' },
    'api_password': { 'type': 'str',  'default': 'P@ssw0rd!' },
    'state':        { 'type': 'str',  'default': 'present', 'choices': ['present', 'absent'] }
  }
  module = AnsibleModule(argument_spec=fields)
  changed = True

  api = SensuApi(
    module.params['api_url'],
    module.params['api_user'],
    module.params['api_password']
  )
  api.auth()

  namespace = SensuNamespace(
    api,
    module.params['name']
  )
  namespace.get_data()

  if module.params['state'] == 'present':
    if not namespace.exist: 
      namespace.create()
    else:
      changed = False
  else:
    if namespace.exist:
      namespace.delete()
    else:
      changed = False

  module.exit_json(changed=changed)

if __name__ == '__main__':
  main()
