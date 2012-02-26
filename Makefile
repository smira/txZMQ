VIRTUALENV?=virtualenv

all: test check

clean:
	rm -rf env/
	find ./ -name "*.pyc" -exec rm {} \;
	find ./ -name "*.pyo" -exec rm {} \;

env:
	$(VIRTUALENV) --no-site-packages env/
	env/bin/python -c 'import sys; print "_pypy" if sys.subversion[0] == "PyPy" else "_cpython"' > .runtime_cfg
	env/bin/pip install -r requirements`cat .runtime_cfg`.txt -r requirements.txt
	rm -f .runtime_cfg

env-clean: clean env

check: env
	env/bin/pep8 --repeat txzmq
	env/bin/pyflakes txzmq

check-clean: clean check

test: env
	env/bin/trial txzmq

test-clean: clean test

.PHONY: env env-clean check check-clean test test-clean
