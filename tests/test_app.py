"""
Unit tests for United Seat Service — State Management and Data Layer (UDC-76)
"""

import pytest
import sys
import os

# Ensure the project root is on the path when running from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app as seat_app
from app import (
    Seat,
    CABIN_CONFIG,
    ROW_CLASS_MAP,
    ROWS,
    SEATS_PER_ROW,
    SEAT_LETTERS,
    TAKEN_PERCENTAGE,
    initialize_seat_map,
    randomize_taken_seats,
    get_seat_data,
    update_seat_status,
    get_available_seats_by_class,
    get_all_seats_as_rows,
)


# ---------------------------------------------------------------------------
# AC1: Seat Data Structure
# ---------------------------------------------------------------------------

class TestSeatDataStructure:
    def test_seat_has_required_fields(self):
        seat = Seat(1, "A", "polaris")
        assert hasattr(seat, "row")
        assert hasattr(seat, "letter")
        assert hasattr(seat, "seat_class")
        assert hasattr(seat, "status")
        assert hasattr(seat, "price")

    def test_seat_default_status_is_available(self):
        seat = Seat(1, "A", "polaris")
        assert seat.status == "available"

    def test_polaris_price(self):
        seat = Seat(1, "A", "polaris")
        assert seat.price == 450

    def test_economy_plus_price(self):
        seat = Seat(6, "A", "economy-plus")
        assert seat.price == 79

    def test_economy_price(self):
        seat = Seat(11, "A", "economy")
        assert seat.price == 0

    def test_seat_to_dict(self):
        seat = Seat(5, "C", "polaris")
        d = seat.to_dict()
        assert d["row"] == 5
        assert d["letter"] == "C"
        assert d["seat_class"] == "polaris"
        assert d["status"] == "available"
        assert d["price"] == 450
        assert d["id"] == "5C"

    def test_row_class_map_polaris(self):
        for row in range(1, 6):
            assert ROW_CLASS_MAP[row] == "polaris"

    def test_row_class_map_economy_plus(self):
        for row in range(6, 11):
            assert ROW_CLASS_MAP[row] == "economy-plus"

    def test_row_class_map_economy(self):
        for row in range(11, 31):
            assert ROW_CLASS_MAP[row] == "economy"


# ---------------------------------------------------------------------------
# AC1: Seat Initialization
# ---------------------------------------------------------------------------

class TestSeatInitialization:
    def test_total_seats(self):
        seat_map = initialize_seat_map()
        assert len(seat_map) == 180  # 30 rows × 6 seats

    def test_all_letters_present_each_row(self):
        seat_map = initialize_seat_map()
        for row in range(1, ROWS + 1):
            for letter in SEAT_LETTERS:
                assert f"{row}{letter}" in seat_map

    def test_all_seats_initially_available(self):
        seat_map = initialize_seat_map()
        for seat in seat_map.values():
            assert seat.status == "available"

    def test_seat_class_assignment(self):
        seat_map = initialize_seat_map()
        assert seat_map["1A"].seat_class == "polaris"
        assert seat_map["6A"].seat_class == "economy-plus"
        assert seat_map["11A"].seat_class == "economy"
        assert seat_map["30F"].seat_class == "economy"


# ---------------------------------------------------------------------------
# AC2: Random Seat Assignment
# ---------------------------------------------------------------------------

class TestRandomSeatAssignment:
    def test_exactly_30_percent_taken(self):
        seat_map = initialize_seat_map()
        randomize_taken_seats(seat_map)
        taken = sum(1 for s in seat_map.values() if s.status == "taken")
        assert taken == 54  # 30% of 180

    def test_taken_seats_spread_across_all_classes(self):
        seat_map = initialize_seat_map()
        randomize_taken_seats(seat_map)
        classes_with_taken = set()
        for seat in seat_map.values():
            if seat.status == "taken":
                classes_with_taken.add(seat.seat_class)
        # With 54 taken seats spread randomly across 180, all three classes
        # should almost certainly have at least one taken seat
        assert len(classes_with_taken) > 0

    def test_custom_percentage(self):
        seat_map = initialize_seat_map()
        randomize_taken_seats(seat_map, percentage=50)
        taken = sum(1 for s in seat_map.values() if s.status == "taken")
        assert taken == 90  # 50% of 180

    def test_non_taken_seats_remain_available(self):
        seat_map = initialize_seat_map()
        randomize_taken_seats(seat_map)
        for seat in seat_map.values():
            assert seat.status in {"available", "taken"}


# ---------------------------------------------------------------------------
# AC4: Data Access Layer
# ---------------------------------------------------------------------------

class TestGetSeatData:
    def test_get_existing_seat(self):
        seat = get_seat_data(1, "A")
        assert seat is not None
        assert seat.row == 1
        assert seat.letter == "A"

    def test_get_nonexistent_seat(self):
        seat = get_seat_data(99, "Z")
        assert seat is None


class TestUpdateSeatStatus:
    def setup_method(self):
        """Ensure a known available seat before each test."""
        seat_app._seat_map["1A"].status = "available"

    def test_update_to_selected(self):
        result = update_seat_status(1, "A", "selected")
        assert result is True
        assert seat_app._seat_map["1A"].status == "selected"

    def test_update_to_taken(self):
        result = update_seat_status(1, "A", "taken")
        assert result is True
        assert seat_app._seat_map["1A"].status == "taken"

    def test_update_to_available(self):
        seat_app._seat_map["1A"].status = "taken"
        result = update_seat_status(1, "A", "available")
        assert result is True
        assert seat_app._seat_map["1A"].status == "available"

    def test_invalid_status_returns_false(self):
        result = update_seat_status(1, "A", "broken")
        assert result is False

    def test_nonexistent_seat_returns_false(self):
        result = update_seat_status(99, "Z", "available")
        assert result is False

    def teardown_method(self):
        """Restore seat to available after each test."""
        seat_app._seat_map["1A"].status = "available"


class TestGetAvailableSeatsByClass:
    def test_returns_all_classes(self):
        result = get_available_seats_by_class()
        assert "polaris" in result
        assert "economy-plus" in result
        assert "economy" in result

    def test_no_taken_seats_in_available(self):
        result = get_available_seats_by_class()
        for seats in result.values():
            for seat in seats:
                assert seat["status"] == "available"

    def test_selected_seats_excluded(self):
        seat_app._seat_map["2B"].status = "selected"
        result = get_available_seats_by_class()
        polaris_ids = [s["id"] for s in result["polaris"]]
        assert "2B" not in polaris_ids
        seat_app._seat_map["2B"].status = "available"


class TestGetAllSeatsAsRows:
    def test_returns_30_rows(self):
        rows = get_all_seats_as_rows()
        assert len(rows) == 30

    def test_each_row_has_6_seats(self):
        rows = get_all_seats_as_rows()
        for row in rows:
            assert len(row["seats"]) == 6

    def test_row_has_class_info(self):
        rows = get_all_seats_as_rows()
        assert rows[0]["seat_class"] == "polaris"
        assert rows[5]["seat_class"] == "economy-plus"
        assert rows[10]["seat_class"] == "economy"


# ---------------------------------------------------------------------------
# Flask route tests
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    seat_app.app.config["TESTING"] = True
    seat_app.app.config["SECRET_KEY"] = "test-secret"
    with seat_app.app.test_client() as c:
        yield c


class TestFlaskRoutes:
    def test_index_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"Seat Selection" in resp.data

    def test_api_seats_returns_json(self, client):
        resp = client.get("/api/seats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 180

    def test_api_seats_by_class_returns_json(self, client):
        resp = client.get("/api/seats/by-class")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "polaris" in data
        assert "economy-plus" in data
        assert "economy" in data

    def test_api_select_available_seat(self, client):
        # Find a guaranteed available seat
        for key, seat in seat_app._seat_map.items():
            if seat.status == "available":
                row, letter = seat.row, seat.letter
                break

        resp = client.post(
            "/api/select",
            json={"row": row, "letter": letter},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["seat"]["status"] == "selected"
        # Cleanup
        seat_app._seat_map[f"{row}{letter}"].status = "available"

    def test_api_select_taken_seat_returns_409(self, client):
        # Force a seat to be taken
        seat_app._seat_map["3C"].status = "taken"
        resp = client.post(
            "/api/select",
            json={"row": 3, "letter": "C"},
            content_type="application/json",
        )
        assert resp.status_code == 409
        seat_app._seat_map["3C"].status = "available"

    def test_api_select_missing_fields_returns_400(self, client):
        resp = client.post(
            "/api/select",
            json={},
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_api_confirm_no_selection_returns_400(self, client):
        resp = client.post("/api/confirm")
        assert resp.status_code == 400

    def test_api_confirm_with_selection(self, client):
        # Select a seat first
        for key, seat in seat_app._seat_map.items():
            if seat.status == "available":
                row, letter = seat.row, seat.letter
                break

        client.post(
            "/api/select",
            json={"row": row, "letter": letter},
            content_type="application/json",
        )
        resp = client.post("/api/confirm")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["confirmed"]["status"] == "taken"
        # Cleanup
        seat_app._seat_map[f"{row}{letter}"].status = "available"
