STYLES = settlers.css public.css private.css \
         pages/home.css \
         pages/chat.css \
         pages/new.css \
         pages/settings.css \
         pages/chat.css \
         pages/game.css

all: $(STYLES)

%.css: %.scss
	/usr/lib/python2.7/site-packages/pyScss-1.1.3-py2.7-linux-x86_64.egg/scss/__init__.py -o $@ $<
