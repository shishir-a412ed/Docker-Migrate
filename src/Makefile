# Installation Directories
PREFIX ?= $(DESTDIR)/usr
SYSCONFDIR ?= $(DESTDIR)/etc/sysconfig
PROFILEDIR ?= $(DESTDIR)/etc/profile.d
PYTHON ?= /usr/bin/python
PYLINT ?= /usr/bin/pylint


all: python-build

test:
	sh ./test.sh

python-build: docker-migrate
	$(PYTHON) setup.py build
	$(PYLINT) -E --additional-builtins=_ *.py docker-migrate dockermigrate

.PHONY: install 
install: all
	$(PYTHON) setup.py install `test -n "$(DESTDIR)" && echo --root $(DESTDIR)`
	mkdir -p $(DESTDIR)/usr/libexec/dockermigrate
	install containers-migrate.sh gotar $(DESTDIR)/usr/libexec/dockermigrate

.PHONY: clean
clean:
	$(PYTHON) setup.py clean --all
	rm -rf dist docker_migrate.egg-info
