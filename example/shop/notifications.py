###############
# Qiyas Sadıqov CC
###############


def refunded(order, event):
    return order.status == "refunded" and getattr(order, "tracker_status", None) != "refunded"


def low_stock(product, event):
    return 0 < product.stock < 5 and getattr(product, "tracker_stock", 0) >= 5
