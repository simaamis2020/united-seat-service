import random
from flask import Flask, render_template

app = Flask(__name__)

PRICES = {
    'polaris': '$450',
    'economy-plus': '$79',
    'economy': 'Included',
}

CLASS_NAMES = {
    'polaris': 'Polaris Business',
    'economy-plus': 'Economy Plus',
    'economy': 'Economy',
}


def get_seat_class(row):
    if row <= 5:
        return 'polaris'
    if row <= 10:
        return 'economy-plus'
    return 'economy'


@app.route('/')
def index():
    seat_data = {}
    for row in range(1, 31):
        seat_class = get_seat_class(row)
        seat_data[row] = {
            letter: {'class': seat_class, 'taken': random.random() < 0.30}
            for letter in ['A', 'B', 'C', 'D', 'E', 'F']
        }
    return render_template(
        'index.html',
        seat_data=seat_data,
        prices=PRICES,
        class_names=CLASS_NAMES,
    )


if __name__ == '__main__':
    app.run(port=5000)
