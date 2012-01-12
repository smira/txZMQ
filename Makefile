VIRTUALENV?=virtualenv

all: test check

clean:
	find ./ -name "*.pyc" -exec rm {} \;
	find ./ -name "*.pyo" -exec rm {} \;
	find ./ -name "*.swp" -exec rm {} \;
	find ./ -name "*.swo" -exec rm {} \;

clean-env: clean
	rm -rf env/

env:
	$(VIRTUALENV) env/
	env/bin/python -c 'import sys; print "_pypy" if sys.subversion[0] == "PyPy" else "_cpython"' > .runtime_cfg
	env/bin/pip install -r requirements`cat .runtime_cfg`.txt -r requirements.txt
	rm -f .runtime_cfg

env-clean: clean-env env

check: env
	env/bin/pep8 --repeat --ignore=E501 txzmq
	env/bin/pep8 --repeat --ignore=E501 examples
	env/bin/pyflakes txzmq
	env/bin/pyflakes examples

check-clean: clean check

test: MOD?="txzmq"
test: env
	env/bin/trial $(MOD)

test-clean: clean test

.PHONY: env env-clean check check-clean test test-clean
