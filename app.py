import random
from flask import Flask, render_template_string

app = Flask(__name__)

ROWS = 30
SEATS = ['A', 'B', 'C', 'D', 'E', 'F']

def get_seat_class(row):
    if row <= 5:
        return 'polaris'
    elif row <= 10:
        return 'economy-plus'
    return 'economy'

def get_seat_class_label(row):
    if row <= 5:
        return 'Polaris'
    elif row <= 10:
        return 'Economy Plus'
    return 'Economy'

def get_seat_price(row):
    if row <= 5:
        return '$450'
    elif row <= 10:
        return '$79'
    return 'Included'

def generate_seat_map():
    all_seats = [(r, s) for r in range(1, ROWS + 1) for s in SEATS]
    taken_count = int(len(all_seats) * 0.30)
    taken_set = set(random.sample([f"{r}-{s}" for r, s in all_seats], taken_count))

    rows = []
    for row in range(1, ROWS + 1):
        seat_class = get_seat_class(row)
        seats = []
        for seat in SEATS:
            seat_id = f"{row}-{seat}"
            is_taken = seat_id in taken_set
            seats.append({
                'id': seat_id,
                'label': seat,
                'row': row,
                'seat_class': seat_class,
                'class_label': get_seat_class_label(row),
                'price': get_seat_price(row),
                'taken': is_taken,
            })
        rows.append({'number': row, 'seats': seats, 'seat_class': seat_class})
    return rows

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>United Seat Selection</title>
  <link rel="stylesheet" href="/static/style.css" />
</head>
<body>

  <header class="header">
    <h1>✈ United Seat Selection</h1>
    <span class="flight-info">Flight UA 123 &nbsp;|&nbsp; Chicago → San Francisco</span>
  </header>

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
        {% for s in ['A', 'B', 'C', '', 'D', 'E', 'F'] %}
          {% if s == '' %}
            <div class="aisle"></div>
          {% else %}
            <div class="seat-header">{{ s }}</div>
          {% endif %}
        {% endfor %}
      </div>

      {% set ns = namespace(last_class=None) %}
      {% for row in rows %}
        {% if row.seat_class != ns.last_class %}
          {% if row.seat_class == 'polaris' %}
            <div class="cabin-label polaris">Polaris Business</div>
          {% elif row.seat_class == 'economy-plus' %}
            <div class="cabin-label economy-plus">Economy Plus</div>
          {% else %}
            <div class="cabin-label economy">Economy</div>
          {% endif %}
          {% set ns.last_class = row.seat_class %}
        {% endif %}

        <div class="row">
          <div class="row-number">{{ row.number }}</div>
          {% for seat in row.seats %}
            {% if loop.index == 4 %}
              <div class="aisle"></div>
            {% endif %}
            <button
              class="seat {{ seat.seat_class }} {% if seat.taken %}taken{% else %}available{% endif %}"
              id="seat-{{ seat.id }}"
              {% if not seat.taken %}
              onclick="selectSeat('{{ seat.id }}', {{ seat.row }}, '{{ seat.label }}', '{{ seat.class_label }}', '{{ seat.price }}', '{{ seat.seat_class }}')"
              {% endif %}
              {% if seat.taken %}disabled{% endif %}
              aria-label="Row {{ seat.row }} Seat {{ seat.label }}{% if seat.taken %} (taken){% endif %}"
            >{{ seat.label }}</button>
          {% endfor %}
        </div>
      {% endfor %}
    </div>

    <div class="confirmation-panel">
      <h2>Your Selection</h2>

      <div class="no-selection" id="no-selection">
        <div class="icon">🪑</div>
        <div>Click a seat to select it</div>
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
    let selectedSeatId = null;

    function selectSeat(seatId, row, seatLetter, className, price, seatClass) {
      if (selectedSeatId) {
        const prev = document.getElementById('seat-' + selectedSeatId);
        if (prev) {
          prev.classList.remove('selected');
          prev.classList.add('available');
        }
      }

      selectedSeatId = seatId;
      const el = document.getElementById('seat-' + seatId);
      el.classList.remove('available');
      el.classList.add('selected');

      document.getElementById('detail-seat').textContent = row + seatLetter;
      document.getElementById('detail-row').textContent = row;

      const badge = document.getElementById('detail-class');
      badge.textContent = className;
      badge.className = 'class-badge ' + seatClass;

      document.getElementById('detail-price').textContent = price;

      document.getElementById('no-selection').style.display = 'none';
      document.getElementById('seat-details').classList.add('visible');
    }

    function confirmSeat() {
      if (!selectedSeatId) return;
      const seatLabel = document.getElementById('detail-seat').textContent;
      alert('Seat ' + seatLabel + ' confirmed! Thank you for flying United.');
    }
  </script>

</body>
</html>
"""

@app.route('/')
def index():
    rows = generate_seat_map()
    return render_template_string(HTML_TEMPLATE, rows=rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
