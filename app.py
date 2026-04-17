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
    <h1>✈ United Airlines</h1>
    <span class="flight-info">Flight UA 123 &nbsp;|&nbsp; ORD → LAX &nbsp;|&nbsp; Boeing 737</span>
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
      <span>Economy (Available)</span>
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

      {% for row in seats %}
        {% set row_num = row[0].row %}
        {% if row_num == 1 %}
          <div class="cabin-label polaris">Polaris Business — Rows 1–5</div>
        {% elif row_num == 6 %}
          <div class="cabin-label economy-plus">Economy Plus — Rows 6–10</div>
        {% elif row_num == 11 %}
          <div class="cabin-label economy">Economy — Rows 11–30</div>
        {% endif %}

        <div class="row">
          <div class="row-number">{{ row_num }}</div>
          {% for seat in row %}
            <button
              class="seat {{ seat.cls }} {{ seat.status }}"
              data-seat="{{ seat.id }}"
              data-row="{{ seat.row }}"
              data-col="{{ seat.col }}"
              data-class="{{ seat.cls }}"
              data-class-label="{{ seat.cls_label }}"
              data-price="{{ seat.price }}"
              data-price-label="{{ seat.price_label }}"
              {% if seat.status == 'taken' %}disabled{% endif %}
            >{{ seat.col }}</button>
            {% if loop.index == 3 %}<div class="aisle"></div>{% endif %}
          {% endfor %}
        </div>
      {% endfor %}
    </div>

    <!-- Confirmation Panel -->
    <div class="confirmation-panel">
      <h2>Seat Details</h2>
      <div class="no-selection" id="no-selection">
        <div class="icon">🪑</div>
        <div>Click a seat to see details</div>
      </div>
      <div class="seat-details" id="seat-details">
        <div class="detail-row">
          <span class="label">Seat</span>
          <span class="value" id="detail-seat"></span>
        </div>
        <div class="detail-row">
          <span class="label">Row</span>
          <span class="value" id="detail-row"></span>
        </div>
        <div class="detail-row">
          <span class="label">Class</span>
          <span class="value" id="detail-class"></span>
        </div>
        <div class="price-row">
          <div>
            <div class="price-label">Price</div>
            <div class="price" id="detail-price"></div>
          </div>
        </div>
        <button class="confirm-btn" onclick="confirmSeat()">Confirm Selection</button>
      </div>
    </div>
  </div>

  <script>
    let currentSeat = null;

    document.querySelectorAll('.seat:not([disabled])').forEach(function(btn) {
      btn.addEventListener('click', function() {
        if (currentSeat) {
          currentSeat.classList.remove('selected');
          currentSeat.classList.add('available');
        }
        currentSeat = btn;
        btn.classList.remove('available');
        btn.classList.add('selected');

        document.getElementById('no-selection').style.display = 'none';
        var details = document.getElementById('seat-details');
        details.classList.add('visible');

        document.getElementById('detail-seat').textContent = btn.dataset.row + btn.dataset.col;
        document.getElementById('detail-row').textContent = btn.dataset.row;

        var cls = btn.dataset.cls || btn.dataset['class'];
        var clsLabel = btn.dataset.classLabel;
        var classEl = document.getElementById('detail-class');
        classEl.innerHTML = '<span class="class-badge ' + cls + '">' + clsLabel + '</span>';

        var price = btn.dataset.price;
        document.getElementById('detail-price').textContent = price;
      });
    });

    function confirmSeat() {
      if (!currentSeat) return;
      var seat = currentSeat.dataset.row + currentSeat.dataset.col;
      alert('Seat ' + seat + ' confirmed! Thank you for choosing United Airlines.');
    }
  </script>
</body>
</html>"""


def build_seat_map():
    random.seed()
    seats_per_class = {
        'polaris': list(range(1, 6)),
        'economy-plus': list(range(6, 11)),
        'economy': list(range(11, 31)),
    }
    class_labels = {
        'polaris': 'Polaris Business',
        'economy-plus': 'Economy Plus',
        'economy': 'Economy',
    }
    prices = {
        'polaris': '$450',
        'economy-plus': '$79',
        'economy': 'Included',
    }
    cols = ['A', 'B', 'C', 'D', 'E', 'F']

    # Build full seat list and randomly mark ~30% as taken
    all_seats = []
    for cls, rows in seats_per_class.items():
        for row_num in rows:
            for col in cols:
                all_seats.append((row_num, col, cls))

    total = len(all_seats)
    taken_count = round(total * 0.30)
    taken_set = set(random.sample(range(total), taken_count))

    seat_map = []
    idx = 0
    for cls, rows in seats_per_class.items():
        for row_num in rows:
            row = []
            for col in cols:
                status = 'taken' if idx in taken_set else 'available'
                row.append({
                    'id': f'{row_num}{col}',
                    'row': row_num,
                    'col': col,
                    'cls': cls,
                    'cls_label': class_labels[cls],
                    'status': status,
                    'price': prices[cls],
                    'price_label': 'per person',
                })
                idx += 1
            seat_map.append(row)

    return seat_map


@app.route('/')
def index():
    seats = build_seat_map()
    return render_template_string(HTML, seats=seats)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
