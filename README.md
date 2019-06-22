# Ansible role: Sensu
[![Version](https://img.shields.io/badge/latest_version-1.2.0-green.svg)](https://git.yaegashi.fr/nishiki/ansible-role-sensu/releases)
[![Build Status](https://travis-ci.org/nishiki/ansible-role-sensu.svg?branch=master)](https://travis-ci.org/nishiki/ansible-role-sensu)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://git.yaegashi.fr/nishiki/ansible-role-sensu/src/branch/master/LICENSE)

Install and configure sensu-go backend and agent

## Requirements

* Ansible >= 2.5
* OS
  * Debian Stretch
  * Ubuntu 18.04
  * Ubuntu 16.04
  * Centos 7

## Role variables
### General

* `sensu_repository_system` - system for package repository (default: `ansible_distribution`)
* `sensu_repository_release` - system release for package repository (default: `ansible_distribution_release`)

Notice: for debian9 set `sensu_repository_system` to `ubuntu` and `sensu_repository_release` to `xenial`

### Agent

* `sensu_agent` - enable sensu agent installation (default: `yes`)
* `sensu_agent_user` - the user for backend authentification (default: `agent`)
* `sensu_agent_password` - the password for backend authentification (default: `P@ssw0rd!`)
* `sensu_agent_plugins` - array with the [sensu ruby plugins](https://github.com/sensu-plugins) to intall

```
  - name: sensu-plugins-http
    version: 4.0.0
```

* `sensu_agent_subscriptions` - array with the subscriptions name

```
  - debian
  - mailserver
```

* `sensu_agent_labels` - hash with the labels

```
  region: Europe
  disk_critical: 90
  disk_warning: 75
```

* `sensu_agent_redact` - array with the redact keywords

```
  - supersecret
  - apikey
```

* `sensu_agent_backends` - array with the backends url

```
  - ws://localhost:8081
```

* `sensu_agent_namespace` - the namespace for agent (default: `default`)
* `sensu_agent_config` - hash with the optional configuration ([see sensu configuration](https://docs.sensu.io/sensu-go/latest/reference/agent/))

### Backend

* `sensu_no_log` - you can disable ansible no_log to print the errors with the backend api (default: `true`)
* `sensu_backend` - enable sensu backend installation (default: `no`)
* `sensu_backend_config` - hash with the optional configuration ([see sensu configuration](https://docs.sensu.io/sensu-go/latest/reference/backend/))
* `sensu_assets` - array with the asset definitions

```
  - name: http-binary
    namespace:
      - default
    url: http://host.local
    sha512: XXXX
    filters: []
```

* `sensu_namespaces` - array with the namespace definitions

```
  - name: production
    state: present
```

* `sensu_checks` - array with the check definitions

```
  - name: load
    namespace:
      - default
    labels:
      criticity: high
    command: /usr/bin/load -w 2 -c 5
    handlers:
      - mailer
    subscriptions:
      - linux
    interval: 120
    options:
      ttl: 300
```

* `sensu_mutators` - array with the mutator definitions

```
  - name: convert2csv
    namespace:
      - default
    command: /usr/local/bin/convert_to_csv
    options:
      timeout: 10
```

* `sensu_handlers` - array with the handler definitions

```
  - name: mailer
    namespace:
      - default
    type: pipe
    command: /usr/local/bin/sensu-email-handler -t sensu@host.local
    filters:
      - is_incident
    options:
      timeout: 10
```

* `sensu_filters` - array with the filter definitions

```
  - name: max_occurences
    namespace:
      - default
    action: allow
    expressions:
    runtime_assets: []
    state: present
```

* `sensu_users` - array with the user definitions

```
  - name: john
    groups:
      - dev
    password: secret
    state: present
```

* `sensu_cluster_roles` - array with the cluster role definitions

```
  - name: dev
    rules:
      - verbs:
          - get
          - list
        resources:
          - '*'
    state: present
```

* `sensu_api_url` - url of sensu api (default: `http://127.0.0.1:8080`)
* `sensu_api_user` - user for sensu api (default: `admin`)
* `sensu_api_password` - password for sensu api (default: `P@ssw0rd!`)

## How to use
### Agent

```
- hosts: webserver
  roles:
    - sensu
  vars:
    sensu_agent_subscriptions:
      - debian
      - webserver
    sensu_agent_labels:
      datacenter: paris
      disk_warning: 30
      disk_critical: 50
    sensu_agent_plugins:
      - name: sensu-plugins-disk-checks
        version: 3.1.1
```

### Backend

```
- hosts: monitoring
  roles:
    - sensu
  vars:
    sensu_backend: yes
    sensu_namespaces:
      - name: production
      - name: dev
    sensu_users:
      - name: johndoe
        password: secret1234
        groups:
          - devops
          - users
    sensu_handlers:
      - name: mail
        command: /usr/local/bin/handler-mailer
        namespaces:
          - production
          - dev
    sensu_filters:
      - name: state_changed
        expressions:
          - event.check.occurrences == 1
        namespaces:
          - production
          - dev
    sensu_checks:
      - name: ping
        command: ping -c 1 127.0.0.1
        subscriptions:
          - linux
        namespaces:
          - production
          - dev
    sensu_cluster_roles:
      - name: superview
```

## Development
### Test syntax with yamllint

* install `python` and `python-pip`
* install yamllint `pip install yamllint`
* run `yamllint .`

### Test syntax with ansible-lint

* install `python` and `python-pip`
* install yamllint `pip install ansible-lint`
* run `ansible-lint .`

### Tests with docker

* install [docker](https://docs.docker.com/engine/installation/)
* install ruby
* install bundler `gem install bundler`
* install dependencies `bundle install`
* run the tests `kitchen test`

## License

```
Copyright (c) 2019 Adrien Waksberg

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
