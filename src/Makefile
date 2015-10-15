# Installation Directories
PYTHON ?= /usr/bin/python
DESTDIR ?= /usr/lib/docker-migrate

.PHONY: install 
install:
	$(PYTHON) setup.py install
	mkdir -p $(DESTDIR)
	cp containers-migrate.sh gotar $(DESTDIR)

.PHONY: clean
clean:
	$(PYTHON) setup.py clean --all
	rm -rf dist docker_migrate.egg-info
