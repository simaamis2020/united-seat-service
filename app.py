import random
from flask import Flask, render_template_string

app = Flask(__name__)

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
  <span class="flight-info">Flight UA 101 &nbsp;|&nbsp; Chicago → San Francisco</span>
</div>

<div class="legend">
  <div class="legend-item">
    <div class="legend-dot" style="background:#c9a84c;"></div>
    <span>Polaris (Rows 1-5)</span>
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:#3b82f6;"></div>
    <span>Economy Plus (Rows 6-10)</span>
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:#22c55e;"></div>
    <span>Economy (Rows 11-30)</span>
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:#e5e7eb;border:1px solid #ccc;"></div>
    <span>Taken</span>
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:#003087;"></div>
    <span>Selected</span>
  </div>
</div>

<div class="container">
  <!-- Seat map -->
  <div class="seat-map-container">
    <h2>Select Your Seat</h2>

    <!-- Column headers -->
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
        <div class="cabin-label polaris">Polaris Business — Rows 1–5</div>
      {% elif row.number == 6 %}
        <div class="cabin-label economy-plus">Economy Plus — Rows 6–10</div>
      {% elif row.number == 11 %}
        <div class="cabin-label economy">Economy — Rows 11–30</div>
      {% endif %}

      <div class="row">
        <div class="row-number">{{ row.number }}</div>
        {% for seat in row.seats %}
          {% if loop.index == 4 %}
            <div class="aisle"></div>
          {% endif %}
          <button
            class="seat {{ seat.cabin_class }}{% if seat.taken %} taken{% else %} available{% endif %}"
            {% if not seat.taken %}
              onclick="selectSeat(this, {{ row.number }}, '{{ seat.letter }}', '{{ seat.cabin_class }}', '{{ seat.price_label }}', '{{ seat.price_value }}')"
            {% else %}
              disabled
            {% endif %}
          >{{ seat.letter }}</button>
        {% endfor %}
      </div>
    {% endfor %}
  </div>

  <!-- Confirmation panel -->
  <div class="confirmation-panel">
    <h2>Your Selection</h2>
    <div class="no-selection" id="no-selection">
      <div class="icon">💺</div>
      <p>Click a seat on the map to select it</p>
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
          <div class="price-label">Seat upgrade price</div>
          <div class="price" id="detail-price">—</div>
        </div>
        <span class="class-badge" id="detail-badge">—</span>
      </div>
      <button class="confirm-btn" onclick="confirmSeat()">Confirm Seat</button>
    </div>
  </div>
</div>

<script>
  let currentSelected = null;

  function selectSeat(btn, rowNum, letter, cabinClass, priceLabel, priceValue) {
    // Deselect previously selected seat
    if (currentSelected) {
      currentSelected.classList.remove('selected');
      currentSelected.classList.add('available');
    }

    // Select new seat
    btn.classList.remove('available');
    btn.classList.add('selected');
    currentSelected = btn;

    // Update confirmation panel
    document.getElementById('no-selection').style.display = 'none';
    var details = document.getElementById('seat-details');
    details.classList.add('visible');

    document.getElementById('detail-seat').textContent = rowNum + letter;
    document.getElementById('detail-row').textContent = rowNum;
    document.getElementById('detail-class').textContent = priceLabel;
    document.getElementById('detail-price').textContent = priceValue;

    var badge = document.getElementById('detail-badge');
    badge.textContent = priceLabel;
    badge.className = 'class-badge ' + cabinClass;
  }

  function confirmSeat() {
    if (!currentSelected) return;
    var seatText = document.getElementById('detail-seat').textContent;
    alert('Seat ' + seatText + ' confirmed! Thank you for choosing United Airlines.');
  }
</script>

</body>
</html>"""

SEAT_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F']
TOTAL_SEATS = 30 * 6
TAKEN_COUNT = int(TOTAL_SEATS * 0.30)


def get_cabin_info(row_num):
    if row_num <= 5:
        return 'polaris', 'Polaris Business', '$450'
    elif row_num <= 10:
        return 'economy-plus', 'Economy Plus', '$79'
    else:
        return 'economy', 'Economy', 'Included'


def build_seat_map():
    # Randomly pick 30% of seats to be taken
    all_seat_ids = [
        f"{row}{letter}"
        for row in range(1, 31)
        for letter in SEAT_LETTERS
    ]
    taken_ids = set(random.sample(all_seat_ids, TAKEN_COUNT))

    rows = []
    for row_num in range(1, 31):
        cabin_class, price_label, price_value = get_cabin_info(row_num)
        seats = []
        for letter in SEAT_LETTERS:
            seat_id = f"{row_num}{letter}"
            seats.append({
                'id': seat_id,
                'letter': letter,
                'cabin_class': cabin_class,
                'price_label': price_label,
                'price_value': price_value,
                'taken': seat_id in taken_ids,
            })
        rows.append({'number': row_num, 'seats': seats})
    return rows


@app.route('/')
def index():
    rows = build_seat_map()
    return render_template_string(HTML, rows=rows)


if __name__ == '__main__':
    app.run(host='100.53.12.150', port=5000, debug=False)
