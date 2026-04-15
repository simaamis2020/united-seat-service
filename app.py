import random
from flask import Flask, render_template_string

app = Flask(__name__)

TOTAL_ROWS = 30
TAKEN_SEAT_PERCENTAGE = 0.30

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>United Seat Selection</title>
  <link rel="stylesheet" href="/static/style.css" />
</head>
<body>

<div class="header">
  <h1>✈ United Airlines — Seat Selection</h1>
  <span class="flight-info">Flight UA 328 &nbsp;|&nbsp; SFO → ORD &nbsp;|&nbsp; Boeing 737</span>
</div>

<div class="legend">
  <div class="legend-item">
    <div class="legend-dot legend-polaris"></div>Polaris (First)
  </div>
  <div class="legend-item">
    <div class="legend-dot legend-economy-plus"></div>Economy Plus
  </div>
  <div class="legend-item">
    <div class="legend-dot legend-available"></div>Available
  </div>
  <div class="legend-item">
    <div class="legend-dot legend-taken"></div>Taken
  </div>
  <div class="legend-item">
    <div class="legend-dot legend-selected"></div>Selected
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

    {% for row in rows %}
      {% if row.number == 1 %}
      <div class="cabin-label polaris">Polaris First Class</div>
      {% elif row.number == 6 %}
      <div class="cabin-label economy-plus">Economy Plus</div>
      {% elif row.number == 11 %}
      <div class="cabin-label economy">Economy</div>
      {% endif %}

      <div class="row">
        <div class="row-number">{{ row.number }}</div>
        {% for seat in row.seats %}
          {% if loop.index == 4 %}
          <div class="aisle"></div>
          {% endif %}
          <button
            class="seat {{ seat.cabin_class }} {% if seat.taken %}taken{% else %}available{% endif %}"
            {% if seat.taken %}disabled{% endif %}
            data-seat="{{ seat.label }}"
            data-row="{{ row.number }}"
            data-class="{{ seat.cabin_class }}"
            data-price="{{ seat.price }}"
            data-price-label="{{ seat.price_label }}"
            onclick="selectSeat(this)"
          >{{ seat.label[-1] }}</button>
        {% endfor %}
      </div>
    {% endfor %}
  </div>

  <div class="confirmation-panel">
    <h2>Your Selection</h2>
    <div class="no-selection" id="no-selection">
      <div class="icon">💺</div>
      <div>Click a seat on the map to select it</div>
    </div>
    <div class="seat-details" id="seat-details">
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
          <div class="price-label" id="detail-price-label">Seat upgrade</div>
          <div class="price" id="detail-price">—</div>
        </div>
        <span class="class-badge" id="detail-badge">—</span>
      </div>
      <button class="confirm-btn" onclick="confirmSeat()">Confirm Selection</button>
    </div>
  </div>
</div>

<script>
  var currentSeat = null;

  var CLASS_LABELS = {
    'polaris': 'Polaris First',
    'economy-plus': 'Economy Plus',
    'economy': 'Economy'
  };

  function selectSeat(btn) {
    if (btn.classList.contains('taken')) return;

    // Deselect previous
    if (currentSeat) {
      currentSeat.classList.remove('selected');
      currentSeat.classList.add('available');
    }

    // Select new
    btn.classList.remove('available');
    btn.classList.add('selected');
    currentSeat = btn;

    var seatLabel = btn.getAttribute('data-seat');
    var rowNum    = btn.getAttribute('data-row');
    var cabinCls  = btn.getAttribute('data-class');
    var price     = btn.getAttribute('data-price');
    var priceLabel = btn.getAttribute('data-price-label');

    document.getElementById('detail-seat').textContent  = seatLabel;
    document.getElementById('detail-row').textContent   = rowNum;
    document.getElementById('detail-class').textContent = CLASS_LABELS[cabinCls] || cabinCls;
    document.getElementById('detail-price').textContent = price;
    document.getElementById('detail-price-label').textContent = priceLabel;

    var badge = document.getElementById('detail-badge');
    badge.textContent = CLASS_LABELS[cabinCls] || cabinCls;
    badge.className = 'class-badge ' + cabinCls;

    document.getElementById('no-selection').style.display = 'none';
    document.getElementById('seat-details').classList.add('visible');
  }

  function confirmSeat() {
    if (!currentSeat) return;
    var seatLabel = currentSeat.getAttribute('data-seat');
    alert('Seat ' + seatLabel + ' confirmed! Thank you for choosing United Airlines.');
  }
</script>
</body>
</html>
"""


def build_seat_data():
    seats_per_row = ['A', 'B', 'C', 'D', 'E', 'F']
    total_seats = TOTAL_ROWS * len(seats_per_row)
    taken_count = round(total_seats * TAKEN_SEAT_PERCENTAGE)

    # Randomly decide which seats are taken
    all_positions = [(r, s) for r in range(1, TOTAL_ROWS + 1) for s in seats_per_row]
    taken_set = set(random.sample(all_positions, taken_count))

    rows = []
    for row_num in range(1, TOTAL_ROWS + 1):
        if 1 <= row_num <= 5:
            cabin_class = 'polaris'
            price = '$450'
            price_label = 'Polaris upgrade'
        elif 6 <= row_num <= 10:
            cabin_class = 'economy-plus'
            price = '$79'
            price_label = 'Economy Plus upgrade'
        else:
            cabin_class = 'economy'
            price = 'Included'
            price_label = 'No additional charge'

        seats = []
        for col in seats_per_row:
            label = f"{row_num}{col}"
            taken = (row_num, col) in taken_set
            seats.append({
                'label': label,
                'taken': taken,
                'cabin_class': cabin_class,
                'price': price,
                'price_label': price_label,
            })
        rows.append({'number': row_num, 'seats': seats})
    return rows


@app.route('/')
def index():
    rows = build_seat_data()
    return render_template_string(HTML, rows=rows)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
