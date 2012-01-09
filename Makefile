VIRTUALENV?=virtualenv

all: test check

env:
	rm -rf env/
	$(VIRTUALENV) --no-site-packages env/
	env/bin/python -c 'import sys; print "_pypy" if sys.subversion[0] == "PyPy" else "_cpython"' > .runtime_cfg
	env/bin/pip install -r requirements`cat .runtime_cfg`.txt -r requirements.txt
	rm -f .runtime_cfg

check:
	env/bin/pep8 --repeat --ignore=E501 txzmq
	env/bin/pyflakes txzmq

test:
	env/bin/trial txzmq

.PHONY: env check test
