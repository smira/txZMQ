VIRTUALENV?=virtualenv
REACTOR?=default

all: test check

clean:
	rm -rf env/
	find ./ -name "*.pyc" -exec rm {} \;
	find ./ -name "*.pyo" -exec rm {} \;

env:
	$(VIRTUALENV) env/
	env/bin/pip install -r requirements-dev.txt

env-clean: clean env

check: env
	env/bin/pycodestyle --repeat txzmq
	env/bin/pyflakes txzmq

check-clean: clean check

test: env
	env/bin/trial --reactor=$(REACTOR) txzmq

test-clean: clean test

docs:
	. env/bin/activate && (cd docs; make html)

.PHONY: env-clean check check-clean test test-clean docs
