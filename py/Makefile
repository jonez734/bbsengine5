all:

clean:
	-rm *~

version:
	./updateversion.sh

build: version
	./setup.py build

install: version build
	sudo ./setup.py install
