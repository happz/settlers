SCRIPTS = hlib.js settlers.js \
          pages/game.js \
          pages/issues.js pages/home.js pages/login.js pages/chat.js pages/settings.js pages/admin.js pages/monitor.js pages/loginas.js pages/registration.js pages/password_recovery.js pages/new.js pages/maintenance.js pages/stats.js pages/tournament.js \
          games/settlers/settlers.js games/settlers/settlers-board.js

all: $(SCRIPTS)

%.js: %.coffee
	/data/settlers/osadnici/tools/coffee-compile.py $< > $@
#	/data/osadnici/tools/coffee-compile.py $< | slimit > $@
