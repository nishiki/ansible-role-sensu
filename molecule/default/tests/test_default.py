import re
import testinfra.utils.ansible_runner

def test_packages(host):
  for package_name in ['sensu-go-agent', 'sensu-go-cli', 'sensu-go-backend']:
    package = host.package(package_name)
    assert package.is_installed

def test_services(host):
  for service_name in ['sensu-backend', 'sensu-agent']:
    service = host.service(service_name)
    assert service.is_running
    assert service.is_enabled

def test_sockets(host):
  for port in [3000, 8080, 8081]:
    socket = host.socket('tcp://0.0.0.0:%d' % (port))
    assert socket.is_listening

def test_configure_sensuctl(host):
  cmd = host.run('sensuctl configure -n --password "P@ssw0rd!" --url http://127.0.0.1:8080 --username admin --format tabular')
  assert cmd.succeeded

def test_sensu_namespace(host):
  cmd = host.run('sensuctl namespace list')
  assert cmd.succeeded
  assert 'production' in cmd.stdout
  assert 'dev' in cmd.stdout

def test_sensu_user(host):
  cmd = host.run('sensuctl user list')
  assert cmd.succeeded
  assert re.search('johndoe.*\\s+devops,users\\s+.*true', cmd.stdout)

def test_sensu_entity(host):
  cmd = host.run('sensuctl entity info debian10 --format json')
  assert cmd.succeeded
  assert '"supersecret": "REDACTED"' in cmd.stdout

def test_sensu_check(host):
  for namespace in ['production', 'dev']:
    cmd = host.run('sensuctl asset list --namespace  %s' % namespace)
    assert cmd.succeeded
    assert re.search('superasset.*\\s+.*test.sh\\s+cf83e13', cmd.stdout)

    cmd = host.run('sensuctl mutator list --namespace  %s' % namespace)
    assert cmd.succeeded
    assert re.search('transform.*\\s+.*/path/value_to_csv', cmd.stdout)

    cmd = host.run('sensuctl handler list --namespace  %s' % namespace)
    assert cmd.succeeded
    assert re.search('mail.*\\s+pipe\\s+.*echo test | mail -s coucou\\s+', cmd.stdout)

    cmd = host.run('sensuctl check list --namespace  %s' % namespace)
    assert cmd.succeeded
    assert re.search('ping.*\\s+ping -c 1 127.0.0.1\\s+60\\s+.*\\s+linux\\s+', cmd.stdout)

    cmd = host.run('sensuctl filter list --namespace  %s' % namespace)
    assert cmd.succeeded
    assert re.search('state_changed.*\\s+allow\\s+\\(event.check.occurrences == 1\\)', cmd.stdout)
