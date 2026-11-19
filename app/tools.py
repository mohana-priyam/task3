
class MockCRMClient:
    def get_customer(self, customer_id):
        customers = {
            "C101": {
                "customer_id": "C101",
                "name": "Arun Kumar",
                "email": "arun@example.com",
                "status": "Active"
            },
            "C102": {
                "customer_id": "C102",
                "name": "Priya Sharma",
                "email": "priya@example.com",
                "status": "Inactive"
            }
        }
        return customers.get(customer_id)


class MockOrderClient:
    def get_order(self, order_id):
        orders = {
            "O101": {
                "order_id": "O101",
                "customer_id": "C101",
                "product": "Laptop",
                "amount": 55000,
                "status": "Shipped"
            },
            "O102": {
                "order_id": "O102",
                "customer_id": "C102",
                "product": "Mobile",
                "amount": 20000,
                "status": "Delivered"
            }
        }
        return orders.get(order_id)


class CRMTool:
    def __init__(self, client=None):
        self.client = client or MockCRMClient()

    def get_customer(self, customer_id):
        if not customer_id:
            raise ValueError("Customer ID is required.")

        result = self.client.get_customer(customer_id)

        if result is None:
            return {"success": False, "message": "Customer not found."}

        return {"success": True, "data": result}


class OrderTool:
    def __init__(self, client=None):
        self.client = client or MockOrderClient()

    def get_order(self, order_id):
        if not order_id:
            raise ValueError("Order ID is required.")

        result = self.client.get_order(order_id)

        if result is None:
            return {"success": False, "message": "Order not found."}

        return {"success": True, "data": result}