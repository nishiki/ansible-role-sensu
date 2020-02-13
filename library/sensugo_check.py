#!/usr/bin/python

from ansible.module_utils.basic import *
from ansible.module_utils.sensu_api import *

class SensuCheck:
  def __init__(self, api, name, namespace, labels):
    self.api       = api
    self.name      = name
    self.namespace = namespace
    self.labels    = labels
    self.exist     = False

  def get_data(self):
    status_code, data = self.api.get('namespaces/{}/checks/{}'.format(self.namespace, self.name))
    if status_code == 200:
      self.exist   = True
      return data

    return {}

  def labels_has_changed(self, new_labels, old_labels):
    if not old_labels and not new_labels:
      return False

    if len(new_labels) != len(old_labels):
      return True

    for old_label, old_value in old_labels.items():
      if old_label in new_labels and new_labels[old_label] == old_value:
        continue
      return True

    return False

  def has_changed(self, options):
    data = self.get_data()
    if self.labels_has_changed(self.labels, data['metadata'].get('labels')):
      return True

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
        'namespace': self.namespace,
        'labels': self.labels
      }
    })

    self.api.put(
      'namespaces/{}/checks/{}'.format(self.namespace, self.name),
      options
    )

  def delete(self):
    self.api.delete(
      'namespaces/{}/checks/{}'.format(self.namespace, self.name)
    )
 
    
def main():
  fields = {
    'name':          { 'type': 'str',  'required': True },
    'namespaces':    { 'type': 'list', 'default': ['default'] },
    'labels':        { 'type': 'dict', 'default': {} },
    'command':       { 'type': 'str',  'required': True },
    'handlers':      { 'type': 'list', 'default': [] },
    'subscriptions': { 'type': 'list', 'required': True },
    'interval':      { 'type': 'int',  'default': 60 },
    'options':       { 'type': 'dict', 'default': {} },
    'api_url':       { 'type': 'str',  'default': 'http://127.0.0.1:8080' },
    'api_user':      { 'type': 'str',  'default': 'admin' },
    'api_password':  { 'type': 'str',  'default': 'P@ssw0rd!' },
    'state':         { 'type': 'str',  'default': 'present', 'choices': ['present', 'absent'] }
  }
  module = AnsibleModule(argument_spec=fields)
  changed = False

  options = {
    'command':       module.params['command'],
    'handlers':      module.params['handlers'],
    'subscriptions': module.params['subscriptions'],
    'interval':      module.params['interval'],
    'publish':       True
  }
  options.update(module.params['options'])
  if 'cron' in options:
    options.pop('interval')

  api = SensuApi(
    module.params['api_url'],
    module.params['api_user'],
    module.params['api_password']
  )
  api.auth()

  for namespace in module.params['namespaces']:
    check = SensuCheck(
      api,
      module.params['name'],
      namespace,
      module.params['labels']
    )
    check.get_data()

    if module.params['state'] == 'present':
      if not check.exist or check.has_changed(options):
        check.create(options)
        changed = True
    elif check.exist:
        check.delete()
        changed = True

  module.exit_json(changed=changed)

if __name__ == '__main__':
  main()
