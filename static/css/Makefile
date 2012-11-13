STYLES = reset.css settlers.css public.css private.css \
         pages/home.css pages/chat.css pages/new.css pages/settings.css pages/chat.css pages/game.css pages/admin.css pages/maintenance.css pages/monitor.css pages/tournament.css pages/stats.css \
         games/settlers/settlers.css

all: $(STYLES)

clean:
	rm -f $(STYLES)

games/settlers/settlers.css: lib.scss
pages/admin.css: lib.scss
pages/chat.css: lib.scss chat.scss
pages/game.css: lib.scss playable.scss
pages/home.css: lib.scss playable.scss
pages/monitor.css: lib.scss
pages/new.css: lib.scss
pages/settings.css: lib.scss
pages/tournament.css: lib.scss playable.scss
pages/stats.css: lib.scss
chat.css: lib.scss
private.css: lib.scss
public.css: lib.scss
reset.css: lib.scss
settlers.css: lib.scss
playable.css: lib.scss
playable.css: chat.scss

%.css: %.scss
	/usr/lib/python2.7/site-packages/pyScss-1.1.3-py2.7-linux-x86_64.egg/scss/__init__.py -C -o $@ $<
