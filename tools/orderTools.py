from langchain_core.tools import tool

from data.order import ORDER_DB


@tool
def lookup_order(identifier: str) -> str:
    """
    Look up a FoodLoop order using an order ID, tracking ID,
    or customer email.

    Args:
        identifier: Order ID, tracking ID, or customer email.

    Returns:
        Matching order information.
    """

    identifier = identifier.strip().lower()

    for order_id, order in ORDER_DB.items():

        if (
            order_id.lower() == identifier
            or order["tracking_id"].lower() == identifier
            or order["customer_email"].lower() == identifier
        ):
            return (
                f"Order ID: {order_id}\n"
                f"Customer: {order['customer_name']}\n"
                f"Email: {order['customer_email']}\n"
                f"Item ID: {order['item_id']}\n"
                f"Item: {order['item_name']}\n"
                f"Status: {order['status']}\n"
                f"Price: ${order['price']:.2f}\n"
                f"Order Date: {order['order_date']}\n"
                f"Estimated Delivery: {order['estimated_delivery']}\n"
                f"Tracking ID: {order['tracking_id']}"
            )

    return f"No order found for: {identifier}"