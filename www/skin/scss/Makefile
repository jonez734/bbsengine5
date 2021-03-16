SCSS = sass --sourcemap=none --stop-on-error --trace --style expanded

all:

.scss.css:
	$(SCSS) $< $@

install: 
	$(SCSS) --update --watch .:$(DOCROOT)skin/css/


clean:
	-rm *~ *.css *.css.map

release:
	mkdir -p $(PROJECTBUILDDIR)skin/scss/
	$(RSYNC) Makefile *.scss $(PROJECTBUILDDIR)skin/scss/ # -$(installfile) Makefile *.scss $(PROJECTBUILDDIR)skin/scss/

.SUFFIXES: .scss .css
