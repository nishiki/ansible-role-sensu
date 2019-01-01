#!/usr/bin/python

from ansible.module_utils.basic import *
from ansible.module_utils.sensu_api import *

class SensuHandler:
  def __init__(self, api, name, namespace):
    self.api       = api
    self.name      = name
    self.namespace = namespace
    self.exist     = False

  def get_data(self):
    status_code, data = self.api.get('namespaces/{}/handlers/{}'.format(self.namespace, self.name))
    if status_code == 200:
      self.exist   = True
      self.options = data
      self.options.pop('metadata')
    
  def has_changed(self, options):
    for option, value in self.options.iteritems():
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
      'namespaces/{}/handlers/{}'.format(self.namespace, self.name),
      options
    )

  def delete(self):
    self.api.delete(
      'namespaces/{}/handlers/{}'.format(self.namespace, self.name)
    )
 
    
def main():
  fields = {
    'name':         { 'type': 'str',  'required': True },
    'namespace':    { 'type': 'str',  'default': 'default' },
    'type':         { 'type': 'str',  'default': 'pipe', 'choices': ['pipe', 'tcp', 'udp', 'set'] },
    'command':      { 'type': 'str',  'required': True },
    'filters':      { 'type': 'list', 'default': [] },
    'options':      { 'type': 'dict', 'default': {} },
    'api_url':      { 'type': 'str',  'default': 'http://127.0.0.1:8080' },
    'api_user':     { 'type': 'str',  'default': 'admin' },
    'api_password': { 'type': 'str',  'default': 'P@ssw0rd!' },
    'state':        { 'type': 'str',  'default': 'present', 'choices': ['present', 'absent'] }
  }
  module = AnsibleModule(argument_spec=fields)
  changed = False

  options = {
    'type':    module.params['type'],
    'command': module.params['command'],
    'filters': module.params['filters']
  }
  options.update(module.params['options'])

  api = SensuApi(
    module.params['api_url'],
    module.params['api_user'],
    module.params['api_password']
  )
  api.auth()

  handler = SensuHandler(
    api,
    module.params['name'],
    module.params['namespace']
  )
  handler.get_data()

  if module.params['state'] == 'present':
    if not handler.exist or handler.has_changed(options):
      handler.create(options)
      changed = True
  elif handler.exist:
      handler.delete()
      changed = True

  module.exit_json(changed=changed)

if __name__ == '__main__':
  main()
