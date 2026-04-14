import random
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

SEATS = ['A', 'B', 'C', 'D', 'E', 'F']
TOTAL_ROWS = 30


def get_seat_class(row):
    if row <= 5:
        return 'polaris'
    if row <= 10:
        return 'economy-plus'
    return 'economy'


def get_seat_price(row):
    seat_class = get_seat_class(row)
    if seat_class == 'polaris':
        return 450
    if seat_class == 'economy-plus':
        return 79
    return 0


def generate_seat_data():
    seats = {}
    for row in range(1, TOTAL_ROWS + 1):
        for seat in SEATS:
            seat_id = f"{row}{seat}"
            seats[seat_id] = {
                'row': row,
                'seat': seat,
                'seat_class': get_seat_class(row),
                'price': get_seat_price(row),
                'taken': random.random() < 0.30,
            }
    return seats


def build_seat_map_html(seat_data):
    html_parts = []
    prev_cabin = None

    cabin_labels = {
        'polaris': 'Polaris Business',
        'economy-plus': 'Economy Plus',
        'economy': 'Economy',
    }

    for row in range(1, TOTAL_ROWS + 1):
        cabin = get_seat_class(row)
        if cabin != prev_cabin:
            label = cabin_labels[cabin]
            html_parts.append(
                f'<div class="cabin-label {cabin}">{label}</div>'
            )
            prev_cabin = cabin

        html_parts.append('<div class="row">')
        html_parts.append(f'<div class="row-number">{row}</div>')

        for idx, seat in enumerate(SEATS):
            seat_id = f"{row}{seat}"
            info = seat_data[seat_id]
            state_class = 'taken' if info['taken'] else 'available'
            disabled = 'disabled' if info['taken'] else ''
            onclick = '' if info['taken'] else f'onclick="selectSeat(\'{seat_id}\')"'
            aria_label = f"Row {row} Seat {seat}, {cabin_labels[cabin]}, {'taken' if info['taken'] else 'available'}"
            html_parts.append(
                f'<button id="seat-{seat_id}" '
                f'class="seat {cabin} {state_class}" '
                f'{onclick} {disabled} '
                f'aria-label="{aria_label}">'
                f'{seat}</button>'
            )
            if idx == 2:
                html_parts.append('<div class="aisle"></div>')

        html_parts.append('</div>')

    return '\n'.join(html_parts)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>United Airlines — Seat Selection</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>

  <div class="header">
    <h1>&#9992; United Airlines — Seat Selection</h1>
    <div class="flight-info">Flight UA 123 &nbsp;·&nbsp; SFO &#8594; ORD</div>
  </div>

  <div class="legend">
    <div class="legend-item">
      <div class="legend-dot legend-polaris"></div>
      <span>Polaris Business</span>
    </div>
    <div class="legend-item">
      <div class="legend-dot legend-economy-plus"></div>
      <span>Economy Plus</span>
    </div>
    <div class="legend-item">
      <div class="legend-dot legend-available"></div>
      <span>Available</span>
    </div>
    <div class="legend-item">
      <div class="legend-dot legend-taken"></div>
      <span>Taken</span>
    </div>
    <div class="legend-item">
      <div class="legend-dot legend-selected"></div>
      <span>Selected</span>
    </div>
  </div>

  <div class="container">

    <div class="seat-map-container">
      <h2>Select Your Seat</h2>

      <div class="seat-headers">
        <div class="row-number-header"></div>
        <div class="seat-header">A</div>
        <div class="seat-header">B</div>
        <div class="seat-header">C</div>
        <div class="aisle"></div>
        <div class="seat-header">D</div>
        <div class="seat-header">E</div>
        <div class="seat-header">F</div>
      </div>

      {{ seat_map | safe }}
    </div>

    <div class="confirmation-panel" role="complementary" aria-label="Seat selection details">
      <h2>Your Selection</h2>

      <div class="no-selection" id="no-selection" aria-live="polite">
        <div class="icon">&#128186;</div>
        <p>Click an available seat to select it</p>
      </div>

      <div class="seat-details" id="seat-details" aria-live="polite">
        <div class="detail-row">
          <span class="label">Seat</span>
          <span class="value" id="detail-seat">—</span>
        </div>
        <div class="detail-row">
          <span class="label">Row</span>
          <span class="value" id="detail-row">—</span>
        </div>
        <div class="detail-row">
          <span class="label">Class</span>
          <span class="value" id="detail-class">—</span>
        </div>
        <div class="price-row">
          <div>
            <div class="price-label">Price</div>
            <div class="price" id="detail-price">—</div>
          </div>
        </div>
        <button class="confirm-btn" onclick="confirmSeat()">Confirm Seat</button>
      </div>
    </div>

  </div>

  <script>
    const seatData = {{ seat_data | tojson }};
    const classLabels = {
      'polaris': 'Polaris Business',
      'economy-plus': 'Economy Plus',
      'economy': 'Economy'
    };

    let selectedSeatId = null;

    function selectSeat(seatId) {
      const info = seatData[seatId];
      if (!info || info.taken) return;

      const noSel = document.getElementById('no-selection');
      const detailsEl = document.getElementById('seat-details');

      if (selectedSeatId === seatId) {
        const el = document.getElementById('seat-' + seatId);
        el.classList.remove('selected');
        el.classList.add('available');
        selectedSeatId = null;
        noSel.classList.remove('hidden');
        detailsEl.classList.remove('visible');
        return;
      }

      if (selectedSeatId) {
        const prevEl = document.getElementById('seat-' + selectedSeatId);
        if (prevEl) {
          prevEl.classList.remove('selected');
          prevEl.classList.add('available');
        }
      }

      selectedSeatId = seatId;
      const el = document.getElementById('seat-' + seatId);
      el.classList.remove('available');
      el.classList.add('selected');

      noSel.classList.add('hidden');
      detailsEl.classList.add('visible');

      document.getElementById('detail-seat').textContent = info.row + info.seat;
      document.getElementById('detail-row').textContent = info.row;
      document.getElementById('detail-class').innerHTML =
        '<span class="class-badge ' + info.seat_class + '">' +
        classLabels[info.seat_class] + '</span>';
      document.getElementById('detail-price').textContent =
        info.price > 0 ? '$' + info.price : 'Included';
    }

    function confirmSeat() {
      if (!selectedSeatId) return;
      const info = seatData[selectedSeatId];
      const priceText = info.price > 0 ? ' — $' + info.price : ' — Included';
      alert('Seat ' + info.row + info.seat + ' confirmed!' + priceText);
    }
  </script>

</body>
</html>
"""


@app.route('/')
def index():
    seat_data = generate_seat_data()
    seat_map_html = build_seat_map_html(seat_data)
    return render_template_string(
        HTML_TEMPLATE,
        seat_map=seat_map_html,
        seat_data=seat_data,
    )


@app.route('/api/seats')
def api_seats():
    return jsonify(generate_seat_data())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
