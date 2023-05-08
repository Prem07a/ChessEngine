from flask import Flask
from flask import render_template
from flask import request
import chess
import chess.engine

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('main.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/play')
def root():
    return render_template('chess.html')


# make move API
@app.route('/make_move', methods=['POST'])
def make_move():
    # create chess engine instance
    engine = chess.engine.SimpleEngine.popen_uci('./engine/chess.2')

    # extract FEN string from HTTP POST request body
    fen = request.form.get('fen')

    # extract fixed depth value
    fixed_depth = request.form.get('fixed_depth')

    # extract move time value
    move_time = request.form.get('move_time')

    # init python chess board instance
    board = chess.Board(fen)

    # if move time is available
    if move_time != '0':
        if move_time == 'instant':
            # search for best move instantly
            info = engine.analyse(board, chess.engine.Limit(time=0.1))
        else:
            # search for best move with fixed move time
            info = engine.analyse(board, chess.engine.Limit(time=int(move_time)))

    # if fixed depth is available
    if fixed_depth != '0':
        # search for best move instantly
        info = engine.analyse(board, chess.engine.Limit(depth=int(fixed_depth)))

    # extract best move from PV
    best_move = info['pv'][0]

    # update internal python chess board state
    board.push(best_move)

    # extract FEN from current board state
    fen = board.fen()

    # terminate engine process
    engine.quit()

    return {
        'fen': fen,
        'best_move': str(best_move),
        'score': str(info['score']),
        'depth': info['depth'],
        'pv': ' '.join([str(move) for move in info['pv']]),
        'nodes': info['nodes'],
        'time': info['time']
    }


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
