VIRTUALENV?=virtualenv

all: test check

env:
	rm -rf env/
	$(VIRTUALENV) --no-site-packages env/
	env/bin/pip install -r requirements.txt

check:
	env/bin/pep8 --repeat --ignore=E501 txZMQ
	env/bin/pyflakes txZMQ

test:
	env/bin/trial txZMQ

.PHONY: env check test
