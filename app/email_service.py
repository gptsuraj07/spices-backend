import os
import logging
from datetime import datetime
import resend

logger = logging.getLogger(__name__)

# Load Resend API Key from Environment
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
ORDER_FROM_EMAIL = os.getenv("ORDER_FROM_EMAIL", "Aridhu Foods <orders@aridhufoods.com>")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "aridhu2026@gmail.com")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

def format_currency(val) -> str:
    try:
        amount = float(val)
        return f"₹{amount:,.2f}"
    except (ValueError, TypeError):
        return f"₹{val}"

def format_date(iso_str) -> str:
    if not iso_str:
        return datetime.utcnow().strftime("%B %d, %Y %I:%M %p UTC")
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y %I:%M %p UTC")
    except Exception:
        return str(iso_str)

def build_items_html_rows(items: list) -> str:
    rows = ""
    for item in items:
        name = item.get("name", "Product")
        qty = item.get("quantity", 1)
        price = format_currency(item.get("price", 0))
        subtotal = format_currency(item.get("subtotal", item.get("price", 0) * qty))
        
        rows += f"""
        <tr>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f0e6df; color: #2A160C; font-weight: 500;">{name}</td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f0e6df; color: #555555; text-align: center;">{qty}</td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f0e6df; color: #555555; text-align: right;">{price}</td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f0e6df; color: #2A160C; font-weight: 600; text-align: right;">{subtotal}</td>
        </tr>
        """
    return rows

def build_customer_email_html(order: dict) -> str:
    order_number = order.get("orderNumber", "N/A")
    created_at = format_date(order.get("createdAt"))
    customer = order.get("customer", {})
    cust_name = customer.get("name", "Valued Customer")
    
    address = order.get("shippingAddress", {})
    addr_line1 = address.get("line1", "")
    addr_line2 = address.get("line2", "")
    city = address.get("city", "")
    state = address.get("state", "")
    pincode = address.get("pincode", "")
    country = address.get("country", "India")
    
    addr_str = f"{addr_line1}"
    if addr_line2:
        addr_str += f", {addr_line2}"
    if city or state or pincode:
        addr_str += f"<br/>{city}, {state} {pincode}"
    if country:
        addr_str += f"<br/>{country}"

    items_rows = build_items_html_rows(order.get("items", []))
    subtotal = format_currency(order.get("subtotal", 0))
    shipping = format_currency(order.get("shipping", 0)) if order.get("shipping", 0) > 0 else "FREE"
    discount = format_currency(order.get("discount", 0)) if order.get("discount", 0) > 0 else None
    total = format_currency(order.get("total", 0))

    payment = order.get("payment", {})
    payment_method = payment.get("method", order.get("paymentMethod", "UPI"))
    payment_status = payment.get("status", order.get("paymentStatus", "PENDING_VERIFICATION"))
    utr_number = payment.get("utrNumber", order.get("utrNumber"))

    discount_row = f"""
    <tr>
        <td colspan="3" style="padding: 8px 16px; text-align: right; color: #315C2B; font-weight: 500;">Discount:</td>
        <td style="padding: 8px 16px; text-align: right; color: #315C2B; font-weight: 600;">-{discount}</td>
    </tr>
    """ if discount else ""

    utr_html = f"<br/><span style='color: #666;'>UTR Reference:</span> <strong>{utr_number}</strong>" if utr_number else ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Order Confirmation - Aridhu Foods</title>
    </head>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #FBF8F5; margin: 0; padding: 20px; color: #2A160C;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 640px; background-color: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #EAE0D5; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <!-- Header -->
            <tr>
                <td style="background-color: #2A160C; padding: 32px 24px; text-align: center;">
                    <h1 style="color: #D97706; font-size: 28px; margin: 0; font-family: Georgia, serif; letter-spacing: 1px;">ARIDHU FOODS</h1>
                    <p style="color: #E2D9D2; font-size: 13px; margin: 6px 0 0; text-transform: uppercase; letter-spacing: 2px;">Authentic South Indian Heritage Spices</p>
                </td>
            </tr>

            <!-- Confirmation Banner -->
            <tr>
                <td style="padding: 32px 32px 16px; text-align: center;">
                    <div style="display: inline-block; background-color: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 50px; padding: 8px 20px; color: #166534; font-weight: 600; font-size: 14px; margin-bottom: 16px;">
                        ✓ Order Placed Successfully
                    </div>
                    <h2 style="margin: 0 0 8px; color: #2A160C; font-size: 22px;">Thank you for your order, {cust_name}!</h2>
                    <p style="color: #666666; font-size: 15px; margin: 0; line-height: 1.5;">We have received your order <strong>#{order_number}</strong> and are preparing it with care.</p>
                </td>
            </tr>

            <!-- Order Summary Info -->
            <tr>
                <td style="padding: 16px 32px;">
                    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #FDFBF7; border-radius: 12px; border: 1px solid #F0E6DF; padding: 16px;">
                        <tr>
                            <td width="50%" style="vertical-align: top; padding: 8px;">
                                <span style="font-size: 12px; color: #888888; text-transform: uppercase; letter-spacing: 0.5px;">Order Number</span>
                                <div style="font-size: 16px; font-weight: 700; color: #2A160C; margin-top: 4px;">#{order_number}</div>
                            </td>
                            <td width="50%" style="vertical-align: top; padding: 8px;">
                                <span style="font-size: 12px; color: #888888; text-transform: uppercase; letter-spacing: 0.5px;">Date & Time</span>
                                <div style="font-size: 14px; font-weight: 600; color: #2A160C; margin-top: 4px;">{created_at}</div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- Order Items Table -->
            <tr>
                <td style="padding: 16px 32px;">
                    <h3 style="font-size: 16px; color: #2A160C; margin: 0 0 12px; font-family: Georgia, serif;">Order Items</h3>
                    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse; border: 1px solid #F0E6DF; border-radius: 8px; overflow: hidden;">
                        <thead>
                            <tr style="background-color: #F8F1EB; color: #2A160C; font-size: 13px; text-transform: uppercase;">
                                <th style="padding: 10px 16px; text-align: left;">Item</th>
                                <th style="padding: 10px 16px; text-align: center;">Qty</th>
                                <th style="padding: 10px 16px; text-align: right;">Price</th>
                                <th style="padding: 10px 16px; text-align: right;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_rows}
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="3" style="padding: 12px 16px 4px; text-align: right; color: #666666;">Subtotal:</td>
                                <td style="padding: 12px 16px 4px; text-align: right; font-weight: 600; color: #2A160C;">{subtotal}</td>
                            </tr>
                            {discount_row}
                            <tr>
                                <td colspan="3" style="padding: 4px 16px; text-align: right; color: #666666;">Delivery Charge:</td>
                                <td style="padding: 4px 16px; text-align: right; font-weight: 600; color: #2A160C;">{shipping}</td>
                            </tr>
                            <tr>
                                <td colspan="3" style="padding: 12px 16px; text-align: right; color: #2A160C; font-weight: 700; font-size: 16px; border-top: 2px solid #2A160C;">Grand Total:</td>
                                <td style="padding: 12px 16px; text-align: right; color: #D97706; font-weight: 700; font-size: 18px; border-top: 2px solid #2A160C;">{total}</td>
                            </tr>
                        </tfoot>
                    </table>
                </td>
            </tr>

            <!-- Shipping & Payment Details -->
            <tr>
                <td style="padding: 16px 32px 32px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td width="50%" style="vertical-align: top; padding-right: 12px;">
                                <div style="background-color: #FDFBF7; border: 1px solid #F0E6DF; border-radius: 12px; padding: 16px; height: 100%;">
                                    <h4 style="margin: 0 0 10px; font-size: 14px; color: #2A160C; text-transform: uppercase; letter-spacing: 0.5px;">📍 Shipping Address</h4>
                                    <div style="font-size: 14px; color: #444444; line-height: 1.6;">
                                        <strong>{cust_name}</strong><br/>
                                        {addr_str}<br/>
                                        📞 {customer.get("phone", "")}
                                    </div>
                                </div>
                            </td>
                            <td width="50%" style="vertical-align: top; padding-left: 12px;">
                                <div style="background-color: #FDFBF7; border: 1px solid #F0E6DF; border-radius: 12px; padding: 16px; height: 100%;">
                                    <h4 style="margin: 0 0 10px; font-size: 14px; color: #2A160C; text-transform: uppercase; letter-spacing: 0.5px;">💳 Payment Details</h4>
                                    <div style="font-size: 14px; color: #444444; line-height: 1.6;">
                                        <span style="color: #666;">Method:</span> <strong>{payment_method}</strong><br/>
                                        <span style="color: #666;">Status:</span> <span style="display: inline-block; background: #FEF3C7; color: #92400E; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;">{payment_status}</span>
                                        {utr_html}
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- Footer -->
            <tr>
                <td style="background-color: #F8F1EB; padding: 24px; text-align: center; border-top: 1px solid #EAE0D5;">
                    <p style="margin: 0 0 8px; color: #2A160C; font-weight: 600; font-size: 14px;">Aridhu Foods — Pure Traditional Taste</p>
                    <p style="margin: 0; color: #888888; font-size: 12px;">If you have any questions, feel free to contact us at support@aridhu.com</p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def build_admin_email_html(order: dict) -> str:
    order_number = order.get("orderNumber", "N/A")
    created_at = format_date(order.get("createdAt"))
    customer = order.get("customer", {})
    cust_name = customer.get("name", "N/A")
    cust_email = customer.get("email", "N/A")
    cust_phone = customer.get("phone", "N/A")

    address = order.get("shippingAddress", {})
    addr_line1 = address.get("line1", "")
    addr_line2 = address.get("line2", "")
    city = address.get("city", "")
    state = address.get("state", "")
    pincode = address.get("pincode", "")
    country = address.get("country", "India")
    
    addr_str = f"{addr_line1}"
    if addr_line2:
        addr_str += f", {addr_line2}"
    if city or state or pincode:
        addr_str += f"<br/>{city}, {state} {pincode}"
    if country:
        addr_str += f"<br/>{country}"

    items_rows = build_items_html_rows(order.get("items", []))
    subtotal = format_currency(order.get("subtotal", 0))
    shipping = format_currency(order.get("shipping", 0)) if order.get("shipping", 0) > 0 else "FREE"
    discount = format_currency(order.get("discount", 0)) if order.get("discount", 0) > 0 else None
    total = format_currency(order.get("total", 0))

    payment = order.get("payment", {})
    payment_method = payment.get("method", order.get("paymentMethod", "UPI"))
    payment_status = payment.get("status", order.get("paymentStatus", "PENDING_VERIFICATION"))
    utr_number = payment.get("utrNumber", order.get("utrNumber"))

    discount_row = f"""
    <tr>
        <td colspan="3" style="padding: 8px 16px; text-align: right; color: #315C2B; font-weight: 500;">Discount:</td>
        <td style="padding: 8px 16px; text-align: right; color: #315C2B; font-weight: 600;">-{discount}</td>
    </tr>
    """ if discount else ""

    utr_html = f"<br/><span style='color: #666;'>UTR Reference:</span> <strong>{utr_number}</strong>" if utr_number else ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>New Order Alert #{order_number} - Aridhu Admin</title>
    </head>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #F3F4F6; margin: 0; padding: 20px; color: #111827;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 640px; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #E5E7EB; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <!-- Admin Header -->
            <tr>
                <td style="background-color: #1E293B; padding: 24px 32px; color: #ffffff;">
                    <div style="background-color: #D97706; color: #ffffff; display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">ADMIN NOTIFICATION</div>
                    <h1 style="font-size: 22px; margin: 0;">⚡ New Order Received: #{order_number}</h1>
                    <p style="margin: 4px 0 0; color: #94A3B8; font-size: 13px;">Placed on {created_at}</p>
                </td>
            </tr>

            <!-- Order Total Highlight -->
            <tr>
                <td style="padding: 24px 32px 12px;">
                    <div style="background-color: #FEF3C7; border: 1px solid #FCD34D; border-radius: 8px; padding: 16px; text-align: center;">
                        <span style="color: #92400E; font-size: 13px; font-weight: 600; text-transform: uppercase;">Total Order Amount</span>
                        <div style="color: #B45309; font-size: 28px; font-weight: 800; margin-top: 2px;">{total}</div>
                    </div>
                </td>
            </tr>

            <!-- Customer Details Block -->
            <tr>
                <td style="padding: 12px 32px;">
                    <h3 style="font-size: 15px; color: #111827; margin: 0 0 10px; border-bottom: 2px solid #E5E7EB; padding-bottom: 6px;">👤 Customer Information</h3>
                    <table width="100%" cellpadding="6" cellspacing="0" style="font-size: 14px; color: #374151;">
                        <tr>
                            <td width="30%" style="color: #6B7280; font-weight: 500;">Name:</td>
                            <td><strong>{cust_name}</strong></td>
                        </tr>
                        <tr>
                            <td style="color: #6B7280; font-weight: 500;">Email:</td>
                            <td><a href="mailto:{cust_email}" style="color: #2563EB;">{cust_email}</a></td>
                        </tr>
                        <tr>
                            <td style="color: #6B7280; font-weight: 500;">Phone:</td>
                            <td><a href="tel:{cust_phone}" style="color: #2563EB;">{cust_phone}</a></td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- Items Purchased -->
            <tr>
                <td style="padding: 16px 32px;">
                    <h3 style="font-size: 15px; color: #111827; margin: 0 0 10px; border-bottom: 2px solid #E5E7EB; padding-bottom: 6px;">🛒 Ordered Products</h3>
                    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse; border: 1px solid #E5E7EB; border-radius: 6px; overflow: hidden; font-size: 14px;">
                        <thead>
                            <tr style="background-color: #F9FAFB; color: #374151; font-size: 12px; text-transform: uppercase;">
                                <th style="padding: 8px 12px; text-align: left;">Product</th>
                                <th style="padding: 8px 12px; text-align: center;">Qty</th>
                                <th style="padding: 8px 12px; text-align: right;">Price</th>
                                <th style="padding: 8px 12px; text-align: right;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_rows}
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="3" style="padding: 8px 12px 2px; text-align: right; color: #6B7280;">Subtotal:</td>
                                <td style="padding: 8px 12px 2px; text-align: right; font-weight: 600; color: #111827;">{subtotal}</td>
                            </tr>
                            {discount_row}
                            <tr>
                                <td colspan="3" style="padding: 2px 12px; text-align: right; color: #6B7280;">Shipping:</td>
                                <td style="padding: 2px 12px; text-align: right; font-weight: 600; color: #111827;">{shipping}</td>
                            </tr>
                            <tr>
                                <td colspan="3" style="padding: 8px 12px; text-align: right; color: #111827; font-weight: 700; border-top: 2px solid #111827;">Grand Total:</td>
                                <td style="padding: 8px 12px; text-align: right; color: #B45309; font-weight: 700; border-top: 2px solid #111827;">{total}</td>
                            </tr>
                        </tfoot>
                    </table>
                </td>
            </tr>

            <!-- Delivery & Payment Information -->
            <tr>
                <td style="padding: 12px 32px 28px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td width="50%" style="vertical-align: top; padding-right: 8px;">
                                <div style="background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 14px;">
                                    <h4 style="margin: 0 0 8px; font-size: 13px; color: #374151; text-transform: uppercase;">📍 Shipping Address</h4>
                                    <div style="font-size: 13px; color: #4B5563; line-height: 1.5;">
                                        <strong>{cust_name}</strong><br/>
                                        {addr_str}
                                    </div>
                                </div>
                            </td>
                            <td width="50%" style="vertical-align: top; padding-left: 8px;">
                                <div style="background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 14px;">
                                    <h4 style="margin: 0 0 8px; font-size: 13px; color: #374151; text-transform: uppercase;">💳 Payment Details</h4>
                                    <div style="font-size: 13px; color: #4B5563; line-height: 1.5;">
                                        Payment Method: <strong>{payment_method}</strong><br/>
                                        Payment Status: <strong>{payment_status}</strong>
                                        {utr_html}
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- Footer -->
            <tr>
                <td style="background-color: #1E293B; color: #94A3B8; padding: 16px; text-align: center; font-size: 12px;">
                    Aridhu Foods Admin Dashboard • Automated Notification System
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def send_order_confirmation_email(order: dict) -> bool:
    """Send customer order confirmation email via Resend SDK."""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY is not set. Skipping customer order email dispatch.")
        return False

    customer_email = order.get("customer", {}).get("email", "").strip()
    if not customer_email:
        logger.warning(f"Order #{order.get('orderNumber')} has no customer email address.")
        return False

    order_number = order.get("orderNumber", "")
    html_content = build_customer_email_html(order)

    try:
        params = {
            "from": ORDER_FROM_EMAIL,
            "to": [customer_email],
            "subject": f"Order Confirmation - #{order_number} | Aridhu Foods",
            "html": html_content,
        }
        logger.info(f"Attempting to send customer confirmation email for order #{order_number} to {customer_email}")
        response = resend.Emails.send(params)
        logger.info(f"Customer confirmation email sent successfully for order #{order_number}. Resend ID: {response.get('id') if isinstance(response, dict) else response}")
        return True
    except Exception as e:
        logger.error(f"Failed to send customer confirmation email for order #{order_number} to {customer_email}: {e}")
        return False

def send_admin_order_notification(order: dict) -> bool:
    """Send admin notification email for a newly placed order via Resend SDK."""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY is not set. Skipping admin order email notification.")
        return False

    if not ADMIN_EMAIL:
        logger.warning("ADMIN_EMAIL is not set. Skipping admin order notification.")
        return False

    order_number = order.get("orderNumber", "")
    cust_name = order.get("customer", {}).get("name", "Customer")
    html_content = build_admin_email_html(order)

    try:
        params = {
            "from": ORDER_FROM_EMAIL,
            "to": [ADMIN_EMAIL],
            "subject": f"⚡ NEW ORDER ALERT: #{order_number} - {cust_name}",
            "html": html_content,
        }
        logger.info(f"Attempting to send admin order notification for order #{order_number} to {ADMIN_EMAIL}")
        response = resend.Emails.send(params)
        logger.info(f"Admin order notification sent successfully for order #{order_number}. Resend ID: {response.get('id') if isinstance(response, dict) else response}")
        return True
    except Exception as e:
        logger.error(f"Failed to send admin order notification for order #{order_number}: {e}")
        return False

def send_order_emails_task(order: dict) -> None:
    """Background task handler for dispatching order emails safely without delaying HTTP response."""
    order_number = order.get("orderNumber", "Unknown")
    logger.info(f"Starting background email dispatch task for order #{order_number}")
    try:
        cust_success = send_order_confirmation_email(order)
        admin_success = send_admin_order_notification(order)
        logger.info(f"Background email task for order #{order_number} completed. Customer email: {cust_success}, Admin email: {admin_success}")
    except Exception as e:
        logger.error(f"Unexpected error in send_order_emails_task for order #{order_number}: {e}", exc_info=True)
