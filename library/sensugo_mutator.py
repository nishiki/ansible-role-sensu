#!/usr/bin/python

from ansible.module_utils.basic import *
from ansible.module_utils.sensu_api import *

class SensuMutator:
  def __init__(self, api, name, namespace):
    self.api       = api
    self.name      = name
    self.namespace = namespace
    self.exist     = False

  def get_data(self):
    status_code, data = self.api.get('namespaces/{}/mutators/{}'.format(self.namespace, self.name))
    if status_code == 200:
      self.exist   = True
      self.options = data
      self.options.pop('metadata')
    
  def has_changed(self, options):
    for option, value in self.options.items():
      if not option in options:
        if value:
          return True
      elif options[option] != value:
        return True
    
    return False

  def create(self, options):
    options.update({
      'metadata': {
        'name': self.name,
        'namespace': self.namespace
      }
    })

    self.api.put(
      'namespaces/{}/mutators/{}'.format(self.namespace, self.name),
      options
    )

  def delete(self):
    self.api.delete(
      'namespaces/{}/mutators/{}'.format(self.namespace, self.name)
    )
 
    
def main():
  fields = {
    'name':          { 'type': 'str',  'required': True },
    'namespaces':    { 'type': 'list', 'default': ['default'] },
    'command':       { 'type': 'str',  'required': True },
    'options':       { 'type': 'dict', 'default': {} },
    'api_url':       { 'type': 'str',  'default': 'http://127.0.0.1:8080' },
    'api_user':      { 'type': 'str',  'default': 'admin' },
    'api_password':  { 'type': 'str',  'default': 'P@ssw0rd!', 'no_log': True },
    'state':         { 'type': 'str',  'default': 'present', 'choices': ['present', 'absent'] }
  }
  module = AnsibleModule(argument_spec=fields)
  changed = False

  options = {
    'command': module.params['command'],
  }
  options.update(module.params['options'])

  api = SensuApi(
    module.params['api_url'],
    module.params['api_user'],
    module.params['api_password']
  )
  api.auth()

  for namespace in module.params['namespaces']:
    mutator = SensuMutator(
      api,
      module.params['name'],
      namespace
    )
    mutator.get_data()

    if module.params['state'] == 'present':
      if not mutator.exist or mutator.has_changed(options):
        mutator.create(options)
        changed = True
    elif mutator.exist:
        mutator.delete()
        changed = True

  module.exit_json(changed=changed)

if __name__ == '__main__':
  main()
