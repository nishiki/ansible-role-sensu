require 'serverspec'

set :backend, :exec

puts
puts '================================'
puts %x(ansible --version)
puts '================================'

%w[
  sensu-go-agent
  sensu-go-cli
  sensu-go-backend
  build-essential
  monitoring-plugins-basic
  python-requests
].each do |package|
  describe package(package) do
    it { should be_installed }
  end
end

%w[
  sensu-agent
  sensu-backend
].each do |service|
  describe service(service) do
    it { should be_enabled }
    it { should be_running }
    it { should be_running.under('systemd') }
  end
end

[3000, 8080, 8081].each do |port|
  describe port(port) do
    it { should be_listening.with('tcp6') }
  end
end

describe command(
  'sensuctl configure -n --password "P@ssw0rd!" ' \
  '--url http://127.0.0.1:8080 --username admin --format tabular'
) do
  its(:exit_status) { should eq 0 }
end

describe command('sensuctl namespace list') do
  its(:exit_status) { should eq 0 }
  its(:stdout) { should match 'production' }
  its(:stdout) { should match 'dev' }
end

describe command('sensuctl user list') do
  its(:exit_status) { should eq 0 }
  its(:stdout) { should match(/johndoe.*\s+devops,users\s+.*true/) }
end

%w[production dev].each do |namespace|
  describe command("sensuctl asset list --namespace  #{namespace}") do
    its(:exit_status) { should eq 0 }
    its(:stdout) { should match(/superasset.*\s+.*test.sh\s+cf83e13/) }
  end

  describe command("sensuctl handler list --namespace #{namespace}") do
    its(:exit_status) { should eq 0 }
    its(:stdout) { should match(/mail.*\s+pipe\s+.*echo test \| mail -s coucou\s+/) }
  end

  describe command("sensuctl check list --namespace #{namespace}") do
    its(:exit_status) { should eq 0 }
    its(:stdout) { should match(/ping.*\s+ping -c 1 127.0.0.1\s+60\s+.*\s+linux\s+/) }
  end

  describe command("sensuctl filter list --namespace #{namespace}") do
    its(:exit_status) { should eq 0 }
    its(:stdout) { should match(/state_changed.*\s+allow\s+event\.check\.occurrences == 1/) }
  end
end

describe command('sensuctl cluster-role list') do
  its(:exit_status) { should eq 0 }
  its(:stdout) { should match(/view.*\s+1/) }
end
