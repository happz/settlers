ROOT_DIR=$(CURDIR)

CONF_DIR := $(ROOT_DIR)/conf/
DOC_DIR := $(ROOT_DIR)/doc/

CLOC_OPTIONS := --read-lang-def=$(CONF_DIR)/cloc.langs --exclude-dir=$(ROOT_DIR)/compiled/ --exclude-ext=js,css --skip-uniqueness $(ROOT_DIR)/src $(ROOT_DIR)/static/script/ $(ROOT_DIR)/static/css/

EPYDOC_OPTIONS := --config $(CONF_DIR)/makedoc.conf -c static/css/epydoc.css
EPYDOC_PACKAGES := $(ROOT_DIR)/src/events $(ROOT_DIR)/src/games $(ROOT_DIR)/src/handlers $(ROOT_DIR)/src/lib $(ROOT_DIR)/src/tournaments $(ROOT_DIR)/src/templates $(ROOT_DIR)/static/script/ $(ROOT_DIR)/static/css/

PYLINT_OPTIONS := --rcfile=$(CONF_DIR)/pylintrc
PYLINT_PACKAGES := events games handlers lib tournaments

NOSE_OPTIONS := -v -w $(ROOT_DIR)/tests/ --with-id --all-modules

.PHONY: clean cloc doc pylint tests test_all

clean:
	@rm -f `find $(ROOT_DIR) -name '*~'`

cloc:
	@cloc $(CLOC_OPTIONS)

doc:
	@rm -rf $(DOC_DIR)
	@epydoc -v -o $(DOC_DIR) $(EPYDOC_OPTIONS) $(shell find $(EPYDOC_PACKAGES) -name '*.py')

pylint:
	@PYTHONPATH=$(ROOT_DIR)/src/ pylint $(PYLINT_OPTIONS) $(PYLINT_PACKAGES) 2> /dev/null | grep -v 'Locally disabling'

tests:
	@nosetests $(NOSE_OPTIONS)

test_all: pylint tests
