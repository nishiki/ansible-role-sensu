#!/usr/bin/python

from ansible.module_utils.basic import *
from ansible.module_utils.sensu_api import *

class SensuHook:
  def __init__(self, api, name, namespace):
    self.api       = api
    self.name      = name
    self.namespace = namespace
    self.exists    = False

  def get_data(self):
    status_code, data = self.api.get('namespaces/{}/hooks/{}'.format(self.namespace, self.name))
    if status_code == 200:
      self.exists  = True
      return data

    return {}

  def has_changed(self, options):
    data = self.get_data()
    data.pop('metadata')
    for option, value in data.items():
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
      'namespaces/{}/hooks/{}'.format(self.namespace, self.name),
      options
    )

  def delete(self):
    self.api.delete(
      'namespaces/{}/hooks/{}'.format(self.namespace, self.name)
    )

def main():
  fields = {
    'name':         { 'type': 'str',  'required': True },
    'namespaces':   { 'type': 'list', 'default': ['default'] },
    'command':      { 'type': 'str',  'required': True },
    'timeout':      { 'type': 'int',  'default': 10 },
    'api_url':      { 'type': 'str',  'default': 'http://127.0.0.1:8080' },
    'api_user':     { 'type': 'str',  'default': 'admin' },
    'api_password': { 'type': 'str',  'default': 'P@ssw0rd!', 'no_log': True },
    'state':        { 'type': 'str',  'default': 'present', 'choices': ['present', 'absent'] }
  }
  module = AnsibleModule(argument_spec=fields)
  changed = False

  options = {
    'command': module.params['command'],
    'timeout': module.params['timeout']
  }
  api = SensuApi(
    module.params['api_url'],
    module.params['api_user'],
    module.params['api_password']
  )
  api.auth()

  for namespace in module.params['namespaces']:
    hook = SensuHook(
      api,
      module.params['name'],
      namespace
    )
    hook.get_data()

    if module.params['state'] == 'present':
      if not hook.exists or hook.has_changed(options):
        hook.create(options)
        changed = True
    elif hook.exists:
        hook.delete()
        changed = True

  module.exit_json(changed=changed)

if __name__ == '__main__':
  main()
