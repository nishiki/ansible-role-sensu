#!/usr/bin/python

from ansible.module_utils.basic import *
from ansible.module_utils.sensu_api import *

class SensuAsset:
  def __init__(self, api, name, namespace):
    self.api       = api
    self.name      = name
    self.namespace = namespace
    self.exist     = False

  def get_data(self):
    status_code, data = self.api.get('namespaces/{}/assets/{}'.format(self.namespace, self.name))
    if status_code == 200:
      self.exist   = True
      self.options = {
        'url':     data['url'],
        'sha512':  data['sha512'],
        'filters': data['filters']
      }
    
  def has_changed(self, options):
    for option, value in self.options.iteritems():
      if options[option] != value:
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
      'namespaces/{}/assets/{}'.format(self.namespace, self.name),
      options
    )
    
def main():
  fields = {
    'name':         { 'type': 'str',  'required': True },
    'namespaces':   { 'type': 'list', 'default': ['default'] },
    'url':          { 'type': 'str',  'required': True },
    'sha512':       { 'type': 'str',  'required': True },
    'filters':      { 'type': 'list', 'default': [] },
    'api_url':      { 'type': 'str',  'default': 'http://127.0.0.1:8080' },
    'api_user':     { 'type': 'str',  'default': 'admin' },
    'api_password': { 'type': 'str',  'default': 'P@ssw0rd!' },
  }
  module = AnsibleModule(argument_spec=fields)
  changed = True

  options = {
    'url':     module.params['url'],
    'sha512':  module.params['sha512'],
    'filters': module.params['filters']
  }

  api = SensuApi(
    module.params['api_url'],
    module.params['api_user'],
    module.params['api_password']
  )
  api.auth()

  for namespace in module.params['namespaces']:
    asset = SensuAsset(
      api,
      module.params['name'],
      namespace
    )
    asset.get_data()

    if not asset.exist or asset.has_changed(options):
      asset.create(options)
    else:
      changed = False

  module.exit_json(changed=changed)

if __name__ == '__main__':
  main()
