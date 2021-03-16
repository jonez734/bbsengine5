all:

clean:
	-rm *~

install:
	mkdir -p $(DOCROOT)skin/tmpl/
	$(RSYNC) *.tmpl $(DOCROOT)skin/tmpl/ # $(installfile) *.tmpl $(DOCROOT)skin/tmpl/

release:
	mkdir -p $(PROJECTBUILDDIR)www/skin/tmpl/
	-$(installfile) *.tmpl $(PROJECTBUILDDIR)www/skin/tmpl/
