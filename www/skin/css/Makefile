all:

clean:
	-rm *~

dev:
	mkdir -p $(STAGEDEVDOCROOT)skin/css/
	-$(installfile) *.css $(STAGEDEVDOCROOT)skin/css/

prod:
	mkdir -p $(STAGEPRODDOCROOT)skin/css/
	-$(installfile) *.css $(STAGEPRODDOCROOT)skin/css/

install:
	mkdir -p $(DOCROOT)skin/css/
	-$(installfile) *.css $(DOCROOT)skin/css/

release:
	mkdir -p $(PROJECTBUILDDIR)www/skin/css/
	-$(installfile) *.css $(PROJECTBUILDDIR)www/skin/css/
