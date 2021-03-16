export HOST=merlin

export PROJECT=bbsengine4
export VERSION=v4

export PROD = $(HOST):/srv/www/vhosts/bbsengine.org/
export STAGE = /srv/staging/bbsengine.org/
export STAGEDOCROOT = $(STAGE)html/

export datestamp = $(shell date +%Y%m%d-%H%M)
export archivename = $(PROJECT)-$(datestamp)-$(USER)
export installfile = install --verbose --mode=0660 --compare

export RSYNC = rsync --chmod=Dg=rwxs,Fgu=rw,Fo=r --verbose \
	--archive --update --backup --recursive \
	--human-readable --rsh=ssh \
	--checksum --times \
	--exclude '*~' \
	--exclude 'templates_c' \
	--exclude '443' \
	--exclude 'tinymce' \
	--delete-after

all:

#apidocs:
#	mkdir -p $(STAGEDOCROOT)$(VERSION)/apidocs/
#	phpdoc \
#	--directory php \
#	--defaultpackagename="$(PROJECT)" \
#	--title="$(PROJECT) $(VERSION) API documentation" \
#	--target="$(STAGEDOCROOT)$(VERSION)/apidocs/"

handbook:
	mkdir -p $(STAGEDOCROOT)$(VERSION)/handbook/
	$(RSYNC) ../handbook/*.txt ../handbook/*.md $(STAGEDOCROOT)$(VERSION)/handbook/

clean:
	-rm *~
	$(MAKE) -C skin clean
	$(MAKE) -C php clean
	$(MAKE) -C smarty clean

prod:	export DOCROOT = $(STAGEDOCROOT)
#prod:	export STAGE = $(STAGE)
prod:
	mkdir -p $(DOCROOT)
	mkdir -p $(STAGE)templates_c/
	mkdir -p $(STAGE)releases/

	$(MAKE) -C php install
	$(MAKE) -C skin install
	$(MAKE) -C smarty install
	$(MAKE) -C js install

	# $(MAKE) -C .. docs
	$(installfile) config-prod.php $(DOCROOT)config.php
	-$(RSYNC) ../handbook/*.txt ../handbook/*.md $(DOCROOT)$(VERSION)/handbook/
	-$(RSYNC) ../*.txt ../*.md $(DOCROOT)$(VERSION)/ # install, readme, changelog, etc
	-$(RSYNC) htpasswd-prod $(DOCROOT).htpasswd
	$(RSYNC) htaccess-prod $(DOCROOT).htaccess
	$(RSYNC) --exclude "releases" --copy-links $(STAGE) $(PROD)

release:
	$(MAKE) -C php release;
	$(MAKE) -C smarty release;
	$(MAKE) -C skin release;
