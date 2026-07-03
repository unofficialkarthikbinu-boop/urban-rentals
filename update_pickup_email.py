import re

file_path = r'd:\UrbanRentals\UrbanRentalsProject\VendorApp\views.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find the schedule_pickup function
pattern = r'(def schedule_pickup\(request, return_id\):[\s\S]*?messages\.success\(request, f\'Pickup scheduled successfully for.*?\).*?return redirect\(\'vendor_return_requests\'\))'

def replacement(match):
    original = match.group(0)
    # We want to insert the email logic right before messages.success
    
    email_logic = """
            # Send email to customer
            try:
                from datetime import datetime
                try:
                    pickup_date_obj = datetime.strptime(pickup_date, '%Y-%m-%d').date()
                    formatted_date = pickup_date_obj.strftime('%B %d, %Y')
                except ValueError:
                    formatted_date = pickup_date
                
                customer_email = return_req.customer.email
                customer_name = return_req.customer.name
                product_name = return_req.order_item.product.product_name
                
                subject = f"Return Pickup Scheduled - {product_name}"
                body = f\"\"\"Hello {customer_name},

Your return request for '{product_name}' has been processed.

Our pickup team is scheduled to visit your location on: {formatted_date}

Please ensure the item is ready for inspection and handover.

Thank you for choosing Urban Rentals.
\"\"\"
                send_email_notification(subject, body, customer_email)
            except Exception as mail_error:
                print(f"Error sending mail: {mail_error}")

            messages.success(request, f'Pickup scheduled successfully for {pickup_date} and notification sent.')"""
    
    # Replace the part from "return_req.save()" to the end of the success message block
    # But wait, original captures a large block.
    # It might be simpler to write a targeted replacement
    return original

# Let's try a different approach, finding the specific block to replace
start_marker = "            return_req.save()"
end_marker = "messages.success(request, f'Pickup scheduled successfully for"

new_block = """            return_req.save()

            # Send email to customer
            try:
                from datetime import datetime
                try:
                    pickup_date_obj = datetime.strptime(pickup_date, '%Y-%m-%d').date()
                    formatted_date = pickup_date_obj.strftime('%B %d, %Y')
                except ValueError:
                    formatted_date = pickup_date

                customer_email = return_req.customer.email
                customer_name = return_req.customer.name
                product_name = return_req.order_item.product.product_name

                subject = f"Return Pickup Scheduled - {product_name}"
                body = f\"\"\"Hello {customer_name},

Your return request for '{product_name}' has been processed.

Our pickup team is scheduled to visit your location on: {formatted_date}

Please ensure the item is ready for inspection and handover.

Thank you for choosing Urban Rentals.
\"\"\"
                send_email_notification(subject, body, customer_email)
            except Exception as mail_error:
                print(f"Error sending mail: {mail_error}")

            messages.success(request, f'Pickup scheduled successfully for {pickup_date} and notification sent.')"""

# Finding the exact block
if start_marker in content:
    # We replace the line 'return_req.save()' and the following messages.success line with our new block
    # But we need to be careful about what comes between them
    
    # Let's use regex to find the block
    regex = r"return_req\.save\(\)\s+messages\.success\(request, f'Pickup scheduled successfully for \{pickup_date\}'\)"
    
    updated_content = re.sub(regex, new_block, content)
    
    if updated_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("Updated schedule_pickup with email notification.")
    else:
        print("Could not find the specific block to replace.")
        # Debug: print snippets around the marker
        idx = content.find(start_marker)
        if idx != -1:
            print(f"Content around marker: {content[idx:idx+200]}")
else:
    print("Could not find return_req.save()")
