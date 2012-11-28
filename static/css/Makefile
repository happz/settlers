STYLES = settlers.css pages/settings.css pages/game.css pages/admin.css pages/maintenance.css pages/monitor.css \
         games/settlers/settlers.css

all: $(STYLES)

clean:
	rm -f $(STYLES)

games/settlers/settlers.css: lib.scss
pages/admin.css: lib.scss
pages/game.css: lib.scss
pages/monitor.css: lib.scss
pages/settings.css: lib.scss
settlers.css: lib.scss

%.css: %.scss
	/usr/lib/python2.7/site-packages/pyScss-1.1.3-py2.7-linux-x86_64.egg/scss/__init__.py -C -o $@ $<
