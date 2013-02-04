ROOT_DIR="`(cd \"$(dirname $0)\" && pwd)`/../"

# No need to change variables below this line...
DOC_DIR="$ROOT_DIR/doc/"
CONF_DIR="$ROOT_DIR/conf/"
LIB_DIR="$ROOT_DIR/lib/"

PACKAGES="events games handlers lib tournaments templates ../static/script/ ../static/css/"

PYLINT_OPTIONS="--rcfile=$CONF_DIR/pylintrc"
