SCSS = sass --stop-on-error --trace --style expanded --sourcemap=none

all:

.scss.css:
	$(SCSS) $< $@

install: 
	$(SCSS) --update --watch .:$(STAGEDOCROOT)skin/css/

clean:
	-rm *~ *.css *.css.map

.SUFFIXES: .scss .css
