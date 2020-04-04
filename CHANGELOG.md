# CHANGELOG

This project adheres to [Semantic Versioning](http://semver.org/).
Which is based on [Keep A Changelog](http://keepachangelog.com/)

## [Unreleased]

## [1.3.0] - 2020-04-04

### Fixed

- add compatibily with new sensu version
- remove no_log warnings with sensu_go libraries

### Changed

- test: replace kitchen to molecule
- add loop label for sensu_go modules

## [1.2.0] - 2019-06-22

- feat: add support for ansible 2.8
- feat: add labels in checks
- feat: add a debug mode with sensu_no_log variable
- feat: add mutators
- feat: add sensu_agent_redact variable to add new redact keywords
- fix: add new return code for api with the version 5.10
- fix: handler, asset and filter wasn't idempotent
- fix: create roles before users
- doc: add example in readme

## [1.1.0] - 2019-02-17

- feat: add support of centos 7
- feat: add support of ubuntu 16.04
- feat: add support of ubuntu 18.04
- feat: add multiple namespaces for the checks, filters, handlers or assets
- fix: install python-requests for backend
- test: add travis ci

## [1.0.0] - 2019-02-06

- first version
