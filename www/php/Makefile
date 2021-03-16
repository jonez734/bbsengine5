all:

clean:
	-rm *~

install:
	$(RSYNC) --copy-links *.php $(DOCROOT) # -$(installfile) *.php $(DOCROOT)

release:
	mkdir -p $(PROJECTBUILDDIR)www/php/
	-$(installfile) *.php $(PROJECTBUILDDIR)www/php/
