import random
from flask import Flask, render_template

app = Flask(__name__)

ROWS = 30
SEAT_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F']
TAKEN_PERCENTAGE = 0.30


def get_seat_class(row):
    if row <= 5:
        return 'polaris'
    elif row <= 10:
        return 'economy-plus'
    return 'economy'


def get_seat_price(seat_class):
    if seat_class == 'polaris':
        return '$450'
    elif seat_class == 'economy-plus':
        return '$79'
    return 'Included'


def get_class_label(seat_class):
    if seat_class == 'polaris':
        return 'Polaris'
    elif seat_class == 'economy-plus':
        return 'Economy Plus'
    return 'Economy'


@app.route('/')
def index():
    all_seats = [(row, seat) for row in range(1, ROWS + 1) for seat in SEAT_LETTERS]
    num_taken = int(len(all_seats) * TAKEN_PERCENTAGE)
    taken_set = set(map(tuple, random.sample(all_seats, num_taken)))

    seat_data = {}
    for row in range(1, ROWS + 1):
        seat_data[row] = {}
        seat_class = get_seat_class(row)
        price = get_seat_price(seat_class)
        class_label = get_class_label(seat_class)
        for seat in SEAT_LETTERS:
            seat_data[row][seat] = {
                'id': f'{row}{seat}',
                'taken': (row, seat) in taken_set,
                'seat_class': seat_class,
                'price': price,
                'class_label': class_label,
            }

    return render_template(
        'index.html',
        seat_data=seat_data,
        rows=range(1, ROWS + 1),
        seats=SEAT_LETTERS,
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
