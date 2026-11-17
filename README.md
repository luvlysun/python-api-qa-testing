# API QA Sample

A Python QA portfolio project using **pytest** to test a Flask REST API.

The project demonstrates successful order creation, input validation, bug reproduction, root-cause investigation, and regression testing.

## Run the Tests

From the project folder, run these commands in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install flask pytest
.\.venv\Scripts\python.exe -m pytest -v
```

**Verified result: 4 tests passed.**

## Automated Test Coverage

| Test | Expected Behavior |
|---|---|
| Valid order with quantity 2 | HTTP 201, order created |
| Invalid order with quantity 0 | HTTP 400, request rejected |
| Retry with the same idempotency key | Original order ID returned |
| Same idempotency key with different quantity | HTTP 409 Conflict |

The tests use Flask's built-in test client.

## Bug Report: Duplicate Order Created on Retry

**Endpoint:** `POST /orders`

**Issue:** Retrying an order creation request with the same idempotency key created a duplicate order.

### Steps to Reproduce

1. Send `POST /orders` with JSON body `{"quantity": 2}` and header `Idempotency-Key: order-123`.
2. Send the identical request again with the same header.
3. Compare the returned order IDs.

### Expected Behavior

The second request returns the original order ID. Only one order is created.

### Actual Behavior Before the Fix

Both requests returned HTTP 201. The first response contained order ID `1`, while the second contained order ID `2`.

The original regression test failed with:

```text
AssertionError: assert 2 == 1
```

### Impact

If the server creates an order but the client times out before receiving the response, a retry could create a duplicate order.

### Root Cause

The original application did not read, store, or check the `Idempotency-Key` header. It therefore had no way to associate a retried request with an existing order.

### Resolution

Implemented an in-memory dictionary to associate idempotency keys with previously created orders.

The API now:

- Creates a new order for a new request.
- Returns the original order for a retry using the same key and quantity.
- Returns HTTP 409 Conflict when the same key is reused with a different quantity.

### Verification

All four automated pytest tests passed after the fix.

## Limitations

This is an educational QA demonstration, not a production-ready order-processing service.

Orders and idempotency records are stored in memory and reset when a new application instance is created. Persistent storage, customer authentication, and concurrency protection are not implemented.