# BUG-001: Duplicate Order Created on Request Retry

**Status:** Fixed and verified  
**Severity:** High (in an order-processing system where duplicates have business consequences)  
**Endpoint:** `POST /orders`  
**Environment:** Python, Flask, pytest

## Description

The API created a new order when a client repeated an identical order creation request using the same idempotency key.

The simulated requirement was that identical retries should return the original order rather than create duplicates.

## Steps to Reproduce

1. Send `POST /orders` with body `{"quantity": 2}` and header `Idempotency-Key: order-123`.
2. Repeat the request using the same body and idempotency key.
3. Compare the order IDs returned by both requests.

## Expected Result

Both requests return the same order ID, and only one order is created.

## Actual Result Before Fix

- First request returned order ID `1`.
- Second request returned order ID `2`.
- Automated regression test failed with `AssertionError: assert 2 == 1`.

## Root Cause

The application did not read or store the idempotency key. Consequently, it could not associate repeated requests with previously created orders.

## Resolution

Implemented in-memory idempotency-key tracking and added a comparison of incoming quantities against previously processed requests.

Identical retries return the original order. Reusing a key with a different quantity returns HTTP `409 Conflict`.

## Verification

Four automated pytest tests passed:

- Valid order creation
- Invalid quantity rejection
- Identical request retry
- Conflicting quantity rejection

## Remaining Limitations

The implementation stores information in process memory and does not protect against concurrent duplicate requests or server restarts.

Persistent storage and atomic request handling would be necessary for a production-grade solution.