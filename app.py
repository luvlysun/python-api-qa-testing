from flask import Flask, jsonify, request


def create_app():
    app = Flask(__name__)
    orders = []
    processed_keys = {}
   

    @app.post("/orders")
    def create_order():
        payload = request.get_json()
        quantity = payload.get("quantity")
        key = request.headers.get("Idempotency-Key")

        if type(quantity) is not int or quantity < 1:
            return jsonify(error="quantity must be a positive integer"), 400
        if key is not None and key in processed_keys:
            previous_order = processed_keys[key]

            if previous_order["quantity"] != quantity:
                return jsonify(error="Idempotency key reused with different quantity"), 409

            return jsonify(previous_order), 201

        order = {"id":len(orders) +1, "quantity": quantity}
        orders.append(order)

        if key is not None:
            processed_keys[key] = order

        return jsonify(order), 201    

    
    return app