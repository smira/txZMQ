VIRTUALENV?=virtualenv

all: test check

clean:
	rm -rf env/
	find ./ -name "*.pyc" -exec rm {} \;
	find ./ -name "*.pyo" -exec rm {} \;

env:
	$(VIRTUALENV) --no-site-packages env/
	env/bin/pip install -r requirements.txt
	rm -f .runtime_cfg

env-clean: clean env

check: env
	env/bin/pep8 --repeat txzmq
	env/bin/pyflakes txzmq

check-clean: clean check

test: env
	env/bin/trial txzmq

test-clean: clean test

docs:
	. env/bin/activate && (cd docs; make html)

.PHONY: env env-clean check check-clean test test-clean docs
