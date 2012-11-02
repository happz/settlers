ROOT_DIR="/data/settlers/osadnici/"

# No need to change variables below this line...
DOC_DIR="$ROOT_DIR/doc/"
CONF_DIR="$ROOT_DIR/conf/"
LIB_DIR="$ROOT_DIR/lib/"

PACKAGES="events games handlers lib tournaments templates ../static/script/ ../static/css/"

EPYDOC_OPTIONS="--config $CONF_DIR/makedoc.conf -c static/css/epydoc.css"
PYLINT_OPTIONS="--rcfile=$CONF_DIR/pylintrc"

CLOC_OPTIONS="--read-lang-def=$CONF_DIR/cloc.langs --exclude-dir=$DOC_DIR,$LIB_DIR, --skip-uniqueness"
