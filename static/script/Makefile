SCRIPTS = hlib.js settlers.js \
          pages/home.js pages/login.js pages/page.js pages/chat.js \
          games/settlers/settlers.js games/settlers/settlers-board.js

all: $(SCRIPTS)

%.js: %.coffee
	/data/osadnici/tools/coffee-compile.py $< > $@
#	/data/osadnici/tools/coffee-compile.py $< | slimit > $@
