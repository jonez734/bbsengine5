all:

clean:
	-rm *~
	$(MAKE) -C css clean
	$(MAKE) -C tmpl clean
	$(MAKE) -C art clean
	$(MAKE) -C scss clean

install:
	mkdir -p $(DOCROOT)skin/tmpl/
	mkdir -p $(DOCROOT)skin/css/
	mkdir -p $(DOCROOT)skin/art/
	$(MAKE) -C scss install
	$(MAKE) -C tmpl install
	$(MAKE) -C art install

release:
	mkdir -p $(PROJECTBUILDDIR)www/skin/
	$(MAKE) -C tmpl release
	$(MAKE) -C scss release
