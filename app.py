import random
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>United — Seat Selection</title>
  <link rel="stylesheet" href="/static/style.css" />
</head>
<body>

  <div class="header">
    <h1>✈ United Airlines</h1>
    <div class="flight-info">Flight UA 1234 &nbsp;|&nbsp; ORD → SFO &nbsp;|&nbsp; Boeing 737</div>
  </div>

  <div class="legend">
    <div class="legend-item">
      <div class="legend-dot legend-polaris"></div>
      <span>Polaris (rows 1–5)</span>
    </div>
    <div class="legend-item">
      <div class="legend-dot legend-economy-plus"></div>
      <span>Economy Plus (rows 6–10)</span>
    </div>
    <div class="legend-item">
      <div class="legend-dot legend-available"></div>
      <span>Economy Available</span>
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
        {% if row == 1 %}
          <div class="cabin-label polaris">Polaris Business</div>
        {% elif row == 6 %}
          <div class="cabin-label economy-plus">Economy Plus</div>
        {% elif row == 11 %}
          <div class="cabin-label economy">Economy</div>
        {% endif %}

        <div class="row">
          <div class="row-number">{{ row }}</div>
          {% for seat in ['A', 'B', 'C'] %}
            {% set key = row|string + seat %}
            {% set info = seat_data[key] %}
            <button
              class="seat {{ info.seat_class }} {{ 'taken' if info.taken else 'available' }}"
              {% if not info.taken %}
              onclick="selectSeat('{{ key }}', {{ row }}, '{{ seat }}', '{{ info.seat_class }}', {{ info.price }})"
              {% endif %}
              data-seat="{{ key }}"
            >{{ seat }}</button>
          {% endfor %}
          <div class="aisle"></div>
          {% for seat in ['D', 'E', 'F'] %}
            {% set key = row|string + seat %}
            {% set info = seat_data[key] %}
            <button
              class="seat {{ info.seat_class }} {{ 'taken' if info.taken else 'available' }}"
              {% if not info.taken %}
              onclick="selectSeat('{{ key }}', {{ row }}, '{{ seat }}', '{{ info.seat_class }}', {{ info.price }})"
              {% endif %}
              data-seat="{{ key }}"
            >{{ seat }}</button>
          {% endfor %}
        </div>
      {% endfor %}
    </div>

    <!-- Confirmation panel -->
    <div class="confirmation-panel">
      <h2>Selection Details</h2>

      <div class="no-selection" id="no-selection">
        <div class="icon">💺</div>
        <div>Click an available seat to select it</div>
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
            <div class="price-label">Seat price</div>
            <div class="price" id="detail-price">—</div>
          </div>
        </div>
        <button class="confirm-btn" onclick="confirmSelection()">Confirm Seat</button>
      </div>
    </div>
  </div>

  <script>
    let selectedSeatKey = null;

    const CLASS_LABELS = {
      'polaris': 'Polaris',
      'economy-plus': 'Economy Plus',
      'economy': 'Economy'
    };

    function selectSeat(key, row, seat, seatClass, price) {
      // Deselect previously selected seat
      if (selectedSeatKey !== null) {
        var prev = document.querySelector('[data-seat="' + selectedSeatKey + '"]');
        if (prev) {
          prev.classList.remove('selected');
          prev.classList.add('available');
        }
      }

      // Select new seat
      var btn = document.querySelector('[data-seat="' + key + '"]');
      if (btn) {
        btn.classList.remove('available');
        btn.classList.add('selected');
      }
      selectedSeatKey = key;

      // Update confirmation panel
      document.getElementById('no-selection').style.display = 'none';
      document.getElementById('seat-details').className = 'seat-details visible';

      document.getElementById('detail-seat').textContent = row + seat;
      document.getElementById('detail-row').textContent = row;
      document.getElementById('detail-class').innerHTML =
        '<span class="class-badge ' + seatClass + '">' + CLASS_LABELS[seatClass] + '</span>';
      document.getElementById('detail-price').textContent =
        price > 0 ? ('$' + price) : 'Included';
    }

    function confirmSelection() {
      if (selectedSeatKey === null) return;
      var seatText = document.getElementById('detail-seat').textContent;
      alert('Seat ' + seatText + ' confirmed! Thank you for choosing United Airlines.');
    }
  </script>

</body>
</html>
'''


INITIAL_OCCUPANCY_RATE = 0.30


@app.route('/')
def index():
    seats = ['A', 'B', 'C', 'D', 'E', 'F']
    all_keys = [str(r) + s for r in range(1, 31) for s in seats]

    taken_count = int(len(all_keys) * INITIAL_OCCUPANCY_RATE)
    taken_set = set(random.sample(all_keys, taken_count))

    seat_data = {}
    for r in range(1, 31):
        if r <= 5:
            seat_class = 'polaris'
            price = 450
        elif r <= 10:
            seat_class = 'economy-plus'
            price = 79
        else:
            seat_class = 'economy'
            price = 0

        for s in seats:
            key = str(r) + s
            seat_data[key] = {
                'seat_class': seat_class,
                'price': price,
                'taken': key in taken_set,
            }

    return render_template_string(
        HTML_TEMPLATE,
        seat_data=seat_data,
        rows=range(1, 31),
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
