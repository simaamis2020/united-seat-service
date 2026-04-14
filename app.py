"""
United Seat Service — Seat Selection Web UI Demo
UDC-76: State Management and Data Layer
"""

import os
import random
from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "udc-seat-demo-secret-key")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROWS = 30
SEATS_PER_ROW = 6
SEAT_LETTERS = list("ABCDEF")
TAKEN_PERCENTAGE = 30

CABIN_CONFIG = {
    "polaris": {"rows": range(1, 6), "price": 450},
    "economy-plus": {"rows": range(6, 11), "price": 79},
    "economy": {"rows": range(11, 31), "price": 0},
}

# Map each row number -> cabin class name
ROW_CLASS_MAP = {}
for _class_name, _cfg in CABIN_CONFIG.items():
    for _row in _cfg["rows"]:
        ROW_CLASS_MAP[_row] = _class_name


# ---------------------------------------------------------------------------
# Seat data model
# ---------------------------------------------------------------------------

class Seat:
    """Represents a single seat on the aircraft."""

    def __init__(self, row: int, letter: str, seat_class: str):
        self.row = row
        self.letter = letter
        self.seat_class = seat_class
        self.status = "available"  # available | taken | selected
        self.price = self._calculate_price()

    def _calculate_price(self) -> int:
        return CABIN_CONFIG[self.seat_class]["price"]

    def to_dict(self) -> dict:
        return {
            "row": self.row,
            "letter": self.letter,
            "seat_class": self.seat_class,
            "status": self.status,
            "price": self.price,
            "id": f"{self.row}{self.letter}",
        }


# ---------------------------------------------------------------------------
# Seat map — initialised once at application startup
# ---------------------------------------------------------------------------

# Global seat map: { "1A": Seat, "1B": Seat, ... }
_seat_map: dict[str, Seat] = {}


def initialize_seat_map() -> dict[str, Seat]:
    """Generate the full seat layout for the aircraft."""
    seat_map: dict[str, Seat] = {}
    for row in range(1, ROWS + 1):
        seat_class = ROW_CLASS_MAP[row]
        for letter in SEAT_LETTERS:
            key = f"{row}{letter}"
            seat_map[key] = Seat(row, letter, seat_class)
    return seat_map


def randomize_taken_seats(seat_map: dict[str, Seat], percentage: int = TAKEN_PERCENTAGE) -> None:
    """Randomly mark the given percentage of seats as taken."""
    total = len(seat_map)
    taken_count = int(total * percentage / 100)
    keys = list(seat_map.keys())
    random.shuffle(keys)
    for key in keys[:taken_count]:
        seat_map[key].status = "taken"


def _build_seat_map() -> dict[str, Seat]:
    seat_map = initialize_seat_map()
    randomize_taken_seats(seat_map)
    return seat_map


# Initialise the global seat map on module load
_seat_map = _build_seat_map()


# ---------------------------------------------------------------------------
# Data access layer
# ---------------------------------------------------------------------------

def get_seat_data(row: int, letter: str) -> Seat | None:
    """Retrieve a specific seat by row and letter."""
    return _seat_map.get(f"{row}{letter}")


def update_seat_status(row: int, letter: str, status: str) -> bool:
    """
    Change the status of a seat.

    Returns True on success, False if the seat does not exist or the
    requested transition is invalid.
    """
    valid_statuses = {"available", "taken", "selected"}
    if status not in valid_statuses:
        return False
    seat = get_seat_data(row, letter)
    if seat is None:
        return False
    seat.status = status
    return True


def get_available_seats_by_class() -> dict[str, list[dict]]:
    """Return available seats grouped by cabin class."""
    result: dict[str, list[dict]] = {name: [] for name in CABIN_CONFIG}
    for seat in _seat_map.values():
        if seat.status == "available":
            result[seat.seat_class].append(seat.to_dict())
    return result


def get_all_seats_as_rows() -> list[dict]:
    """Return all seats structured as a list of rows for template rendering."""
    rows = []
    for row_num in range(1, ROWS + 1):
        seats = [_seat_map[f"{row_num}{letter}"].to_dict() for letter in SEAT_LETTERS]
        rows.append({"row": row_num, "seats": seats, "seat_class": ROW_CLASS_MAP[row_num]})
    return rows


# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    rows = get_all_seats_as_rows()
    flight_info = {
        "number": os.environ.get("FLIGHT_NUMBER", "UA 1234"),
        "origin": os.environ.get("FLIGHT_ORIGIN", "SFO"),
        "destination": os.environ.get("FLIGHT_DESTINATION", "ORD"),
        "aircraft": os.environ.get("FLIGHT_AIRCRAFT", "Boeing 787"),
    }
    return render_template("index.html", rows=rows, cabin_config=CABIN_CONFIG, flight_info=flight_info)


@app.route("/api/seats")
def api_seats():
    """Return the full seat map as JSON."""
    return jsonify({key: seat.to_dict() for key, seat in _seat_map.items()})


@app.route("/api/seats/by-class")
def api_seats_by_class():
    """Return available seats grouped by cabin class."""
    return jsonify(get_available_seats_by_class())


@app.route("/api/select", methods=["POST"])
def api_select():
    """
    Select or deselect a seat.

    Body: { "row": int, "letter": str }
    """
    data = request.get_json(force=True)
    row = data.get("row")
    letter = data.get("letter", "").upper()

    if not row or not letter:
        return jsonify({"error": "row and letter are required"}), 400

    seat = get_seat_data(row, letter)
    if seat is None:
        return jsonify({"error": "Seat not found"}), 404
    if seat.status == "taken":
        return jsonify({"error": "Seat is already taken"}), 409

    # Release any previously selected seat for this session
    prev_selection = session.get("selected_seat")
    if prev_selection and prev_selection != f"{row}{letter}":
        prev_seat = _seat_map.get(prev_selection)
        if prev_seat and prev_seat.status == "selected":
            prev_seat.status = "available"

    # Toggle selection
    if seat.status == "selected":
        seat.status = "available"
        session.pop("selected_seat", None)
    else:
        seat.status = "selected"
        session["selected_seat"] = f"{row}{letter}"

    return jsonify({"seat": seat.to_dict()})


@app.route("/api/confirm", methods=["POST"])
def api_confirm():
    """Confirm the current seat selection and lock it as 'taken'."""
    selected_key = session.get("selected_seat")
    if not selected_key:
        return jsonify({"error": "No seat selected"}), 400

    seat = _seat_map.get(selected_key)
    if seat is None or seat.status != "selected":
        return jsonify({"error": "Selected seat is no longer available"}), 409

    seat.status = "taken"
    session.pop("selected_seat", None)
    return jsonify({"confirmed": seat.to_dict()})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug)
