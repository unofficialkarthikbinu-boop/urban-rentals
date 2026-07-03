import smtplib
from email.message import EmailMessage

def send_email_notification(subject, body, to_email):
    """
    Helper function to send email notifications.
    """
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = "urbanrentalsofficial@gmail.com"
        msg['To'] = to_email
        
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login("urbanrentalsofficial@gmail.com", "kilw hwzc jdkz xlmp")
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def decrement_product_stock(order_item, quantity=None):
    """
    Decrement product stock after successful payment.
    Mark product as out of stock if stock reaches 0.
    
    Args:
        order_item: tbl_order_item instance
        quantity: Quantity to decrement (defaults to order_item.quantity)
    
    Returns:
        tuple: (success: bool, message: str, product: tbl_product or None)
    """
    try:
        from VendorApp.models import tbl_product
        
        if not order_item or not order_item.product:
            return False, "Order item or product not found", None
        
        product = order_item.product
        qty_to_decrement = quantity if quantity is not None else order_item.quantity
        
        # Check if sufficient stock exists
        if product.stock_quantity < qty_to_decrement:
            return False, f"Insufficient stock. Available: {product.stock_quantity}, Required: {qty_to_decrement}", product
        
        # Decrement stock
        product.stock_quantity -= qty_to_decrement
        
        # Mark as out of stock if stock reaches 0
        if product.stock_quantity <= 0:
            product.stock_quantity = 0
            product.is_available = False
            message = f"Product '{product.product_name}' stock decremented by {qty_to_decrement}. Product is now OUT OF STOCK."
        else:
            message = f"Product '{product.product_name}' stock decremented by {qty_to_decrement}. Remaining stock: {product.stock_quantity}"
        
        product.save()
        print(f"[STOCK] {message}")
        return True, message, product
        
    except Exception as e:
        error_msg = f"Error decrementing stock: {str(e)}"
        print(f"[STOCK ERROR] {error_msg}")
        return False, error_msg, None


def restore_product_stock(order_item, quantity=None):
    """
    Restore product stock after return is completed.
    Mark product as available if it was out of stock.
    
    Args:
        order_item: tbl_order_item instance
        quantity: Quantity to restore (defaults to order_item.quantity)
    
    Returns:
        tuple: (success: bool, message: str, product: tbl_product or None)
    """
    try:
        from VendorApp.models import tbl_product
        
        if not order_item or not order_item.product:
            return False, "Order item or product not found", None
        
        product = order_item.product
        qty_to_restore = quantity if quantity is not None else order_item.quantity
        
        # Restore stock
        product.stock_quantity += qty_to_restore
        
        # Mark as available if it was out of stock
        if not product.is_available:
            product.is_available = True
            message = f"Product '{product.product_name}' stock restored by {qty_to_restore}. Product is now AVAILABLE. New stock: {product.stock_quantity}"
        else:
            message = f"Product '{product.product_name}' stock restored by {qty_to_restore}. New stock: {product.stock_quantity}"
        
        product.save()
        print(f"[STOCK] {message}")
        return True, message, product
        
    except Exception as e:
        error_msg = f"Error restoring stock: {str(e)}"
        print(f"[STOCK ERROR] {error_msg}")
        return False, error_msg, None
