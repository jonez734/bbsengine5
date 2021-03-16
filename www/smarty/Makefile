clean:
	-rm *~
	
install:
	mkdir -p $(STAGE)smarty/
	-$(RSYNC) modifier.*.php function.*.php $(STAGE)smarty/ # $(installfile) modifier.*.php $(STAGE)smarty/
#	-$(RSYNC) --dry-run function.*.php $(STAGE)smarty/ # $(installfile) function.*.php $(STAGE)smarty/

release:
	mkdir -p $(PROJECTBUILDDIR)smarty/
	-$(installfile) *.php Makfile $(PROJECTBUILDDIR)smarty/
