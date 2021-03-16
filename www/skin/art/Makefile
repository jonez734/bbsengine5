all:

clean:
	-rm *~

install:
	mkdir -p $(DOCROOT)skin/art/
	-$(RSYNC) *.png *.gif *.jpg *.otf $(DOCROOT)skin/art/ # -$(installfile) *.png *.gif *.jpg $(DOCROOT)skin/art/
release:
	mkdir -p $(PROJECTBUILDDIR)www/skin/art/
	-$(RSYNC) *.png *.gif *.jpg $(PROJECTBUILDDIR)www/skin/art/ #-$(installfile) *.png *.gif $(PROJECTBUILDDIR)www/skin/art/

