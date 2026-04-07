# united-seat-service

[UDC-1] Add OpenAPI 3.1 spec for seat map API v2 endpoints
[UDC-1] Add request/response schemas and error code definitions
[UDC-6] Implement seat hold endpoint with 5-min Redis TTL
[UDC-7] Add Redis persistence layer for seat hold state
[UDC-10] Add Redis cluster config for dev and staging environments
[UDC-8] Fix: Apply URL decoding before flightId parsing
[UDC-2] Implement GET /v2/flights/{flightId}/seatmap endpoint
[UDC-2] Add pricing tier filtering based on customer auth token
[UDC-4] Add unit tests for SeatMapController — 87% coverage achieved
[UDC-9] Add integration tests for seat hold and release lifecycle
[UDC-3] Add Solace event consumer for seat inventory topic
