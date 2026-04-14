import random
import threading
from flask import Flask, jsonify, render_template, abort

app = Flask(__name__)

SEAT_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F']
TOTAL_ROWS = 30

POLARIS_ROWS = range(1, 6)       # rows 1-5
ECONOMY_PLUS_ROWS = range(6, 11) # rows 6-10
ECONOMY_ROWS = range(11, 31)     # rows 11-30

POLARIS_PRICE = 450
ECONOMY_PLUS_PRICE = 79
ECONOMY_PRICE = 0

_seats_lock = threading.Lock()


def _get_seat_class(row: int) -> str:
    if row in POLARIS_ROWS:
        return 'polaris'
    if row in ECONOMY_PLUS_ROWS:
        return 'economy-plus'
    return 'economy'


def _get_seat_price(seat_class: str) -> int:
    return {'polaris': POLARIS_PRICE, 'economy-plus': ECONOMY_PLUS_PRICE, 'economy': ECONOMY_PRICE}[seat_class]


def _build_seats() -> dict:
    seats = {}
    all_ids = []
    for row in range(1, TOTAL_ROWS + 1):
        seat_class = _get_seat_class(row)
        price = _get_seat_price(seat_class)
        for letter in SEAT_LETTERS:
            seat_id = f"{row}{letter}"
            seats[seat_id] = {
                'id': seat_id,
                'row': row,
                'letter': letter,
                'seat_class': seat_class,
                'price': price,
                'available': True,
                'selected': False,
            }
            all_ids.append(seat_id)

    # Random 30% occupation on startup
    occupied_count = round(len(all_ids) * 0.30)
    for seat_id in random.sample(all_ids, occupied_count):
        seats[seat_id]['available'] = False

    return seats


# In-memory seat store initialised once at startup
seats: dict = _build_seats()


@app.route('/')
def index():
    with _seats_lock:
        seats_snapshot = {k: dict(v) for k, v in seats.items()}
    return render_template('index.html', seats=seats_snapshot,
                           rows=range(1, TOTAL_ROWS + 1),
                           letters=SEAT_LETTERS)


@app.route('/api/seats')
def api_seats():
    with _seats_lock:
        return jsonify(list(seats.values()))


@app.route('/api/seats/<seat_id>/select', methods=['POST'])
def select_seat(seat_id):
    with _seats_lock:
        seat = seats.get(seat_id)
        if seat is None:
            abort(404)
        if not seat['available']:
            return jsonify({'error': 'Seat is already taken'}), 409
        seat['available'] = False
        seat['selected'] = True
        return jsonify(dict(seat))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
