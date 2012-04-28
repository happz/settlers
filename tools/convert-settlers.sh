. /data/osadnici/conf/tools.sh

export PYTHONPATH=$ROOT_DIR/src

python $ROOT_DIR/tools/convert_board_coffee.py > $ROOT_DIR/static/script/games/settlers/settlers-board.coffee
python $ROOT_DIR/tools/convert_board_css.py > $ROOT_DIR/static/css/games/settlers/settlers-board.css
