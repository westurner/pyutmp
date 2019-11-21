
## Makefile for pyutmp

.PHONY: build

default: build

all: clean uninstall build install-wheel test

build:
	python setup.py build bdist_wheel

install-e:
	pip install -e .
	# Note that this is linux-specific:
	cd pyutmp && rm -rfv *.so && ln -s `find .. -wholename "../build/lib*/*.so"` ./

install-wheel:
	pip install `ls ./dist/pyutmp-*.whl | tail -n1`

uninstall:
	pip uninstall -y pyutmp

test:
	@# The cd to ~ is necessary because there is no .so symlink in pyutmp/
	@# when installing as wheel and pyutmp/ is in the current directory
	cd ~ && python -c 'import pyutmp; assert [x.__dict__ for x in pyutmp.UtmpFile()]'

print:
	cd ~ && python -c 'import pyutmp, pprint; [pprint.pprint(x.__dict__) for x in pyutmp.UtmpFile()]'

clean:
	rm -fv pyutmp_*.so ./pyutmp/*.so
	rm -rfv pyutmp.egg-info/
	rm -rfv build/
	rm -rfv dist/
