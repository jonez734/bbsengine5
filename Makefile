export HOST = falcon

export PROJECT = bbsengine5
export datestamp = $(shell date +%Y%m%d-%H%M)
export archivename = $(PROJECT)-$(datestamp)
export PROJECTRELEASEDIR = /srv/repo/$(PROJECT)/
export PROJECTBUILDDIR = /home/jam/projects/$(PROJECT)/releases/$(archivename)/
export installfile = install --mode=0660 --verbose --preserve-timestamps
export RSYNC = rsync --chmod=Dg=rwxs,Fgu=rw,Fo=r --times --verbose \
	--exclude '*~' \
	--archive --update --backup --recursive \
	--human-readable --checksum --rsh=ssh \
	--delete-after 
export PROD = $(HOST):/srv/www/vhosts/bbsengine.org/
export PRODDOCROOT = $(PROD)80/html/
export STAGE = /srv/staging/bbsengine.org/
export STAGEDOCROOT = $(STAGE)80/html/
export VERSION = "v5"
all:

clean:
	-$(MAKE) -C php clean;
	-$(MAKE) -C handbook clean;

release:
	echo "-=- making a new release of $(PROJECT) -=-";
	mkdir -p $(PROJECTBUILDDIR);
	$(MAKE) -C www release;
	$(MAKE) -C handbook release;
	git log > CHANGELOG.txt
	$(installfile) README.txt INSTALL.txt RELEASENOTES.txt CHANGELOG.txt composer.json $(PROJECTBUILDDIR);
	pushd releases;\
	tar jcf $(archivename).tar.bz2 $(archivename)/*;\
	tar zcf $(archivename).tgz $(archivename)/*;\
	zip -r $(archivename).zip $(archivename)/*;\
	mkdir -p $(PROJECTRELEASEDIR);\
	install --mode=0644 $(archivename).tar.bz2 $(archivename).tgz $(archivename).zip $(PROJECTRELEASEDIR);\
	install --mode=0644 $(archivename)/README.txt $(PROJECTRELEASEDIR);\
	install --mode=0644 $(archivename)/CHANGELOG.txt $(PROJECTRELEASEDIR);\
	popd;\
	echo "[DONE]"

apidocs:
	mkdir -p $(STAGEDOCROOT)$(VERSION)/apidocs/
	phpdoc run \
	--target $(STAGEDOCROOT)$(VERSION)/apidocs/ \
	--directory php \
	--extensions php \
	--title "$(PROJECT) apidocs" \
	--defaultpackagename "$(PROJECT)" \
	--sourcecode \
	--progressbar \
	--template responsive

handbook:
	mkdir -p $(STAGEDOCROOT)$(VERSION)/handbook/
	-$(RSYNC) handbook/*.txt handbook/*.md $(STAGEDOCROOT)$(VERSION)/handbook/
	$(RSYNC) $(STAGEDOCROOT)$(VERSION)/handbook/ $(PRODDOCROOT)$(VERSION)/handbook/

push:
	git push -u origin master

.PHONY: handbook release
