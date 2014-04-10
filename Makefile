include Makefile.conf

ROOT_DIR := $(CURDIR)
CONF_DIR := $(ROOT_DIR)/conf/
DOC_DIR := $(ROOT_DIR)/doc/
SCRIPT_DIR := $(ROOT_DIR)/static/script
LIB_DIR := $(ROOT_DIR)/libs
CSS_DIR := $(ROOT_DIR)/static/css

#
# Tools
#
PYLINT_OPTIONS := --rcfile=$(CONF_DIR)/pylintrc $(PYLINT_OPTIONS)
PYLINT_PACKAGES := events games handlers lib tournaments $(PYLINT_PACKAGES)

CLOC_OPTIONS := --read-lang-def=$(CONF_DIR)/cloc.langs --exclude-dir=$(ROOT_DIR)/compiled/ --exclude-ext=js,css --skip-uniqueness $(CLOC_OPTIONS) $(ROOT_DIR)/src $(ROOT_DIR)/static/script/ $(ROOT_DIR)/static/css/

EPYDOC_OPTIONS := --config $(CONF_DIR)/makedoc.conf -c static/css/epydoc.css $(EPYDOC_OPTIONS)
EPYDOC_PACKAGES := $(ROOT_DIR)/src/events $(ROOT_DIR)/src/games $(ROOT_DIR)/src/handlers $(ROOT_DIR)/src/lib $(ROOT_DIR)/src/tournaments $(ROOT_DIR)/src/templates $(ROOT_DIR)/static/script/ $(ROOT_DIR)/static/css/ $(EPYDOC_PACKAGES)

NOSE_OPTIONS := -v -w $(ROOT_DIR)/tests/ --with-id --all-modules $(NOSE_OPTIONS)

.PHONY: clean cloc doc pylint tests test_all

clean:
	@rm -f `find $(ROOT_DIR) -name '*~'`

cloc:
	@echo "----- ----- ----- ----- ----- ----- ----- ----- -----"
	@echo "Cloc status"
	@$(CLOC) $(CLOC_OPTIONS)
	@echo "----- ----- ----- ----- ----- ----- ----- ----- -----"

doc:
	@echo "----- ----- ----- ----- ----- ----- ----- ----- -----"
	@echo "Documentation"
	@rm -rf $(DOC_DIR)
	@$(EPYDOC) -v -o $(DOC_DIR) $(EPYDOC_OPTIONS) $(shell find $(EPYDOC_PACKAGES) -name '*.py')
	@echo "----- ----- ----- ----- ----- ----- ----- ----- -----"

doccheck:
	@echo "----- ----- ----- ----- ----- ----- ----- ----- -----"
	@echo "Documentation check"
	@$(EPYDOC) -v --check hlib
	@echo "----- ----- ----- ----- ----- ----- ----- ----- -----"

pylint:
	@echo "----- ----- ----- ----- ----- ----- ----- ----- -----"
	@echo "Pylint checks"
	@echo
	@PYTHONPATH=$(ROOT_DIR)/src/ $(PYLINT) $(PYLINT_OPTIONS) $(PYLINT_PACKAGES) 2> /dev/null | grep -v 'Locally disabling'
	@echo "----- ----- ----- ----- ----- ----- ----- ----- -----"

coffeelint:
	@echo "----- ----- ----- ----- ----- ----- ----- ----- -----"
	@echo "CoffeeLint checks"
	@echo
	@$(COFFEELINT) -f $(CONF_DIR)/coffeelint.json --nocolor `find $(SCRIPT_DIR) -name '*.coffee'`
	@echo "----- ----- ----- ----- ----- ----- ----- ----- -----"

tests:
	@echo "----- ----- ----- ----- ----- ----- ----- ----- -----"
	@echo "Nose tests"
	@echo
	@$(NOSE) $(NOSE_OPTIONS)
	@echo "----- ----- ----- ----- ----- ----- ----- ----- -----"

test_all: pylint coffeelint tests

checksupdate: pylint coffeelint tests doccheck doc cloc

#
# Scripts and styles have to be updated - translated, compressed...
#
SCRIPTS := $(SCRIPT_DIR)/hlib/hlib.js $(SCRIPT_DIR)/hlib/ajax.js $(SCRIPT_DIR)/hlib/pager.js $(SCRIPT_DIR)/hlib/form.js $(SCRIPT_DIR)/hlib/tabs.js $(SCRIPT_DIR)/hlib/message.js \
           $(SCRIPT_DIR)/settlers.js $(SCRIPT_DIR)/validators.js \
					 $(SCRIPT_DIR)/pages/game.js \
					 $(SCRIPT_DIR)/pages/issues.js $(SCRIPT_DIR)/pages/home.js $(SCRIPT_DIR)/pages/login.js $(SCRIPT_DIR)/pages/chat.js $(SCRIPT_DIR)/pages/settings.js \
					 $(SCRIPT_DIR)/pages/admin.js $(SCRIPT_DIR)/pages/monitor.js $(SCRIPT_DIR)/pages/loginas.js $(SCRIPT_DIR)/pages/registration.js $(SCRIPT_DIR)/pages/password_recovery.js \
					 $(SCRIPT_DIR)/pages/new.js $(SCRIPT_DIR)/pages/maintenance.js $(SCRIPT_DIR)/pages/stats.js $(SCRIPT_DIR)/pages/tournament.js \
					 $(SCRIPT_DIR)/games/settlers/settlers.js $(SCRIPT_DIR)/games/settlers/settlers-board.js \
					 $(SCRIPT_DIR)/realchat/client.js

LIB_SCRIPTS := $(LIB_DIR)/jquery-ui.js \
               $(LIB_DIR)/jquery.form/jquery.form.js $(LIB_DIR)/jquery.timers.js $(LIB_DIR)/jquery.sound.js \
               $(LIB_DIR)/marked/lib/marked.js $(LIB_DIR)/holder/holder.js $(LIB_DIR)/Parsley.js/parsley.js $(LIB_DIR)/stacktrace/stacktrace.js $(LIB_DIR)/strftime.js \
							 $(LIB_DIR)/flot/jquery.flot.js $(LIB_DIR)/flot/jquery.flot.canvas.js $(LIB_DIR)/flot/jquery.flot.js

MINIFIED_SCRIPTS := $(patsubst %.js,%.min.js,$(SCRIPTS)) $(patsubst %.js,%.min.js,$(LIB_SCRIPTS))

scripts_compile: $(SCRIPTS)
scripts_minify: $(MINIFIED_SCRIPTS)
scripts_clean:
	rm -f $(SCRIPTS) $(MINIFIED_SCRIPTS)

scripts: scripts_compile scripts_minify

%.js: %.coffee
	$(COFFEE) -c --bare -m $<

%.min.js: %.js
	cat $< | $(SLIMIT) > $@

STYLES = $(CSS_DIR)/settlers.css $(CSS_DIR)/pages/settings.css $(CSS_DIR)/pages/game.css $(CSS_DIR)/pages/admin.css $(CSS_DIR)/pages/maintenance.css \
         $(CSS_DIR)/pages/monitor.css \
				 $(CSS_DIR)/games/settlers/settlers.css

styles_compile: $(STYLES)
styles: styles_compile
styles_clean:
	rm -f $(STYLES)

$(CSS_DIR)/games/settlers/settlers.css: $(CSS_DIR)/lib.scss
$(CSS_DIR)/pages/admin.css: $(CSS_DIR)/lib.scss
$(CSS_DIR)/pages/game.css: $(CSS_DIR)/lib.scss
$(CSS_DIR)/pages/monitor.css: $(CSS_DIR)/lib.scss
$(CSS_DIR)/pages/settings.css: $(CSS_DIR)/lib.scss
$(CSS_DIR)/settlers.css: $(CSS_DIR)/lib.scss

%.css: %.scss
	$(ENVDIR)/bin/python -mscss -C -I $(CSS_DIR) --output=$@ $<
