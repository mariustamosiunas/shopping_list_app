from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

app = Flask(__name__)

# Configuration
GOOGLE_SHEETS_CREDS_FILE = os.getenv('GOOGLE_SHEETS_CREDS_FILE', 'credentials.json')
SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME', 'Shopping Items')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM')
WHATSAPP_TO = os.getenv('WHATSAPP_TO')

def get_google_sheet():
    """Connect to Google Sheets and return the workbook"""
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDS_FILE, scope)
        client = gspread.authorize(creds)
        workbook = client.open(SPREADSHEET_NAME)
        return workbook
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None

def generate_next_item_id():
    """Generate next sequential item ID like ID1, ID2, ID3, etc."""
    try:
        workbook = get_google_sheet()
        if not workbook:
            return "ID1"
        
        sheet = workbook.worksheet('Items')
        headers = sheet.row_values(1)
        
        if 'Item_ID' not in headers:
            return "ID1"
        
        id_col = headers.index('Item_ID') + 1
        all_ids = sheet.col_values(id_col)[1:]  # Skip header
        
        # Filter out empty values
        all_ids = [id for id in all_ids if id and id.startswith('ID')]
        
        if not all_ids:
            return "ID1"
        
        # Extract numbers and find max
        numbers = []
        for id_str in all_ids:
            try:
                num = int(id_str.replace('ID', ''))
                numbers.append(num)
            except:
                continue
        
        if not numbers:
            return "ID1"
        
        next_num = max(numbers) + 1
        return f"ID{next_num}"
    
    except Exception as e:
        print(f"Error generating ID: {e}")
        return "ID1"

def ensure_history_sheet():
    """Create Shopping_History sheet if it doesn't exist"""
    try:
        workbook = get_google_sheet()
        if not workbook:
            return False
        
        try:
            workbook.worksheet('Shopping_History')
        except:
            # Sheet doesn't exist, create it
            sheet = workbook.add_worksheet(title='Shopping_History', rows=1000, cols=6)
            # Add headers
            sheet.update('A1:F1', [['Timestamp', 'Date', 'Total_Items', 'Unique_Items', 'Items_JSON', 'Items_Display']])
            print("Created Shopping_History sheet")
        
        return True
    except Exception as e:
        print(f"Error ensuring history sheet: {e}")
        return False

def get_all_items():
    """Fetch all items from Items sheet and enrich with category data"""
    workbook = get_google_sheet()
    if not workbook:
        return []
    
    try:
        items_sheet = workbook.worksheet('Items')
        items = items_sheet.get_all_records()
        
        # Filter out empty items (no name)
        items = [item for item in items if item.get('Item', '').strip()]
        
        # Get categories to enrich items with aisle order
        categories_sheet = workbook.worksheet('Categories')
        categories = categories_sheet.get_all_records()
        
        # Create category lookup map
        category_map = {cat['Category']: cat for cat in categories}
        
        # Track if we need to update any IDs
        headers = items_sheet.row_values(1)
        id_col_exists = 'Item_ID' in headers
        
        if id_col_exists:
            id_col = headers.index('Item_ID') + 1
            needs_update = False
            
            # Enrich items with aisle order from categories
            for idx, item in enumerate(items, start=2):
                # Ensure each item has an Item_ID
                if not item.get('Item_ID') or not str(item.get('Item_ID')).strip():
                    # Generate ID for this item
                    item['Item_ID'] = generate_next_item_id()
                    # Update in sheet
                    items_sheet.update_cell(idx, id_col, item['Item_ID'])
                    needs_update = True
                
                # Set default purchase count if not present
                if 'Purchase_Count' not in item or item.get('Purchase_Count') == '':
                    item['Purchase_Count'] = 0
                else:
                    try:
                        item['Purchase_Count'] = int(item['Purchase_Count'])
                    except:
                        item['Purchase_Count'] = 0
                
                # Set default unit type if not present
                if 'Unit_Type' not in item or not item.get('Unit_Type'):
                    item['Unit_Type'] = 'quantity'  # Default to quantity
                else:
                    # Normalize to lowercase
                    unit_type = str(item.get('Unit_Type')).lower().strip()
                    if unit_type in ['weight', 'kg', 'g', 'weighted']:
                        item['Unit_Type'] = 'weight'
                    else:
                        item['Unit_Type'] = 'quantity'
                
                category_name = item.get('Category', '')
                if category_name in category_map:
                    item['Aisle_Order'] = category_map[category_name].get('Aisle_Order', 999)
                elif 'Aisle_Order' not in item:
                    item['Aisle_Order'] = 999
        else:
            # No Item_ID column, just set default values
            for item in items:
                item['Item_ID'] = ''
                
                if 'Purchase_Count' not in item or item.get('Purchase_Count') == '':
                    item['Purchase_Count'] = 0
                else:
                    try:
                        item['Purchase_Count'] = int(item['Purchase_Count'])
                    except:
                        item['Purchase_Count'] = 0
                
                # Set default unit type
                if 'Unit_Type' not in item or not item.get('Unit_Type'):
                    item['Unit_Type'] = 'quantity'
                else:
                    unit_type = str(item.get('Unit_Type')).lower().strip()
                    if unit_type in ['weight', 'kg', 'g', 'weighted']:
                        item['Unit_Type'] = 'weight'
                    else:
                        item['Unit_Type'] = 'quantity'
                
                category_name = item.get('Category', '')
                if category_name in category_map:
                    item['Aisle_Order'] = category_map[category_name].get('Aisle_Order', 999)
                elif 'Aisle_Order' not in item:
                    item['Aisle_Order'] = 999
        
        return items
    except Exception as e:
        print(f"Error fetching items: {e}")
        return []

def get_all_categories():
    """Fetch all categories from Categories sheet"""
    workbook = get_google_sheet()
    if not workbook:
        return []
    
    try:
        sheet = workbook.worksheet('Categories')
        records = sheet.get_all_records()
        return records
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

def add_item_to_sheet(item_name, category, unit_type='quantity'):
    """Add a new item to Items sheet with Item_ID, purchase count, and unit type"""
    try:
        workbook = get_google_sheet()
        if not workbook:
            return False, None
        
        sheet = workbook.worksheet('Items')
        
        # Generate next Item_ID
        item_id = generate_next_item_id()
        
        # Check if sheet has Item_ID and Purchase_Count columns
        headers = sheet.row_values(1)
        
        # Normalize unit_type
        unit_type = 'weight' if unit_type.lower() in ['weight', 'kg', 'g'] else 'quantity'
        
        # Prepare row data based on existing columns
        if 'Item_ID' in headers and 'Purchase_Count' in headers and 'Unit_Type' in headers:
            # Full row with all columns
            sheet.append_row([item_name, category, item_id, 0, unit_type])
        elif 'Item_ID' in headers and 'Purchase_Count' in headers:
            # Has ID and count but not unit type
            sheet.append_row([item_name, category, item_id, 0])
        elif 'Item_ID' in headers:
            # Has Item_ID but not Purchase_Count
            sheet.append_row([item_name, category, item_id])
        else:
            # Legacy format - just Item and Category
            sheet.append_row([item_name, category])
        
        return True, item_id
    except Exception as e:
        print(f"Error adding item to Google Sheets: {e}")
        return False, None

def update_purchase_counts(item_ids_with_quantities):
    """Update purchase count for items that were bought"""
    try:
        workbook = get_google_sheet()
        if not workbook:
            return False
        
        sheet = workbook.worksheet('Items')
        headers = sheet.row_values(1)
        
        # Check if Item_ID and Purchase_Count columns exist
        if 'Item_ID' not in headers or 'Purchase_Count' not in headers:
            print("Item_ID or Purchase_Count column not found")
            return False
        
        id_col = headers.index('Item_ID') + 1
        count_col = headers.index('Purchase_Count') + 1
        
        # Get all data
        all_data = sheet.get_all_values()
        
        # Update counts
        for row_idx, row in enumerate(all_data[1:], start=2):  # Skip header
            item_id = row[id_col - 1] if len(row) > id_col - 1 else ''
            
            if item_id in item_ids_with_quantities:
                current_count = row[count_col - 1] if len(row) > count_col - 1 else '0'
                try:
                    current_count = int(current_count) if current_count else 0
                except:
                    current_count = 0
                
                # Add the quantity purchased
                new_count = current_count + item_ids_with_quantities[item_id]
                sheet.update_cell(row_idx, count_col, new_count)
        
        return True
    except Exception as e:
        print(f"Error updating purchase counts: {e}")
        return False

def save_shopping_history(items_data):
    """Save shopping list to Shopping_History sheet"""
    try:
        ensure_history_sheet()
        workbook = get_google_sheet()
        if not workbook:
            return False
        
        sheet = workbook.worksheet('Shopping_History')
        
        # Prepare data
        timestamp = datetime.now().isoformat()
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        total_items = sum(item.get('quantity', 1) for item in items_data)
        unique_items = len(items_data)
        
        # Create JSON representation (for programmatic access)
        items_json = json.dumps([{
            'item_id': item.get('Item_ID', ''),
            'name': item.get('Item', ''),
            'category': item.get('Category', ''),
            'quantity': item.get('quantity', 1)
        } for item in items_data])
        
        # Create display representation (for human reading)
        items_display = '; '.join([
            f"{item.get('Item', 'Unknown')} ({item.get('quantity', 1)}x)"
            for item in items_data
        ])
        
        # Append to history
        sheet.append_row([timestamp, date, total_items, unique_items, items_json, items_display])
        
        return True
    except Exception as e:
        print(f"Error saving shopping history: {e}")
        return False

def update_last_shopping_list(items_data):
    """Update the most recent shopping list instead of creating a new one"""
    try:
        workbook = get_google_sheet()
        if not workbook:
            return False
        
        sheet = workbook.worksheet('Shopping_History')
        all_records = sheet.get_all_records()
        
        if not all_records:
            return False
        
        # Get the last row number (add 2: 1 for header, 1 for 1-based indexing)
        last_row = len(all_records) + 1
        
        # Check if last list was within 1 hour
        last_record = all_records[-1]
        timestamp_str = last_record.get('Timestamp', '')
        
        if timestamp_str:
            try:
                list_time = datetime.fromisoformat(timestamp_str)
                now = datetime.now()
                time_diff = (now - list_time).total_seconds() / 60
                
                if time_diff >= 60:  # More than 1 hour ago
                    return False
            except:
                return False
        else:
            return False
        
        # Update the last row with new data
        timestamp = datetime.now().isoformat()
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        total_items = sum(item.get('quantity', 1) for item in items_data)
        unique_items = len(items_data)
        
        items_json = json.dumps([{
            'item_id': item.get('Item_ID', ''),
            'name': item.get('Item', ''),
            'category': item.get('Category', ''),
            'quantity': item.get('quantity', 1)
        } for item in items_data])
        
        items_display = '; '.join([
            f"{item.get('Item', 'Unknown')} ({item.get('quantity', 1)}x)"
            for item in items_data
        ])
        
        # Update the row
        sheet.update(f'A{last_row}:F{last_row}', [[timestamp, date, total_items, unique_items, items_json, items_display]])
        
        return True
    except Exception as e:
        print(f"Error updating shopping history: {e}")
        return False

def get_shopping_history(limit=3):
    """Get last N shopping lists from history"""
    try:
        workbook = get_google_sheet()
        if not workbook:
            return []
        
        sheet = workbook.worksheet('Shopping_History')
        all_records = sheet.get_all_records()
        
        # Get last N records (most recent first)
        recent = list(reversed(all_records[-limit:]))
        
        # Parse JSON for each record and check if editable
        for record in recent:
            try:
                record['items'] = json.loads(record.get('Items_JSON', '[]'))
                
                # Check if this list was sent within last hour
                timestamp_str = record.get('Timestamp', '')
                if timestamp_str:
                    try:
                        list_time = datetime.fromisoformat(timestamp_str)
                        now = datetime.now()
                        time_diff = (now - list_time).total_seconds() / 60  # minutes
                        record['is_editable'] = time_diff < 60  # Within 1 hour
                        record['minutes_ago'] = int(time_diff)
                    except:
                        record['is_editable'] = False
                        record['minutes_ago'] = 999
                else:
                    record['is_editable'] = False
                    record['minutes_ago'] = 999
            except:
                record['items'] = []
                record['is_editable'] = False
                record['minutes_ago'] = 999
        
        return recent
    except Exception as e:
        print(f"Error fetching shopping history: {e}")
        return []

def sort_items_by_aisle(items):
    """Sort items by aisle order"""
    return sorted(items, key=lambda x: x.get('Aisle_Order', 999))

def sort_items_by_popularity(items):
    """Sort items by purchase count (most bought first)"""
    return sorted(items, key=lambda x: x.get('Purchase_Count', 0), reverse=True)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/items', methods=['GET'])
def get_items():
    """API endpoint to get all available items"""
    try:
        items = get_all_items()
        # Sort by popularity (most bought first)
        items = sort_items_by_popularity(items)
        return jsonify({'success': True, 'items': items})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """API endpoint to get all categories"""
    try:
        categories = get_all_categories()
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/items', methods=['POST'])
def add_item():
    """API endpoint to add a new item to Google Sheets"""
    try:
        data = request.json
        item_name = data.get('item_name', '').strip()
        category = data.get('category', '').strip()
        unit_type = data.get('unit_type', 'quantity').strip()
        
        if not item_name or not category:
            return jsonify({'success': False, 'error': 'Item name and category are required'}), 400
        
        success, item_id = add_item_to_sheet(item_name, category, unit_type)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Item added successfully!',
                'item': {
                    'Item': item_name,
                    'Category': category,
                    'Item_ID': item_id,
                    'Purchase_Count': 0,
                    'Unit_Type': unit_type
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to add item'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """API endpoint to get shopping history"""
    try:
        limit = int(request.args.get('limit', 3))
        history = get_shopping_history(limit)
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send-whatsapp', methods=['POST'])
def send_whatsapp():
    """API endpoint to send shopping list via WhatsApp"""
    try:
        data = request.json
        selected_items = data.get('items', [])
        is_update = data.get('is_update', False)  # New parameter
        
        if not selected_items:
            return jsonify({'success': False, 'error': 'No items selected'}), 400
        
        sorted_items = sort_items_by_aisle(selected_items)
        
        # Build message with update indicator if updating
        if is_update:
            message = "🛒 *Shopping List (UPDATED)*\n\n"
        else:
            message = "🛒 *Shopping List*\n\n"
        
        current_category = None
        
        for item in sorted_items:
            category = item.get('Category', 'Other')
            if category != current_category:
                message += f"\n📍 *{category}*\n"
                current_category = category
            
            item_name = item.get('Item', 'Unknown')
            quantity = item.get('quantity', 1)
            
            if quantity > 1:
                message += f"  • {item_name} × {quantity}\n"
            else:
                message += f"  • {item_name}\n"
        
        message += "\n✅ Happy shopping!"
        
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, WHATSAPP_TO]):
            return jsonify({'success': False, 'error': 'Twilio credentials not configured'}), 500
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        twilio_message = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=WHATSAPP_TO
        )
        
        # Save or update history based on mode
        if is_update:
            # Try to update existing list
            updated = update_last_shopping_list(selected_items)
            if not updated:
                # If update fails (list too old), save as new
                save_shopping_history(selected_items)
        else:
            # Save as new list
            save_shopping_history(selected_items)
        
        # Update purchase counts
        item_counts = {}
        for item in selected_items:
            item_id = item.get('Item_ID', '')
            quantity = item.get('quantity', 1)
            if item_id:
                item_counts[item_id] = quantity
        
        update_purchase_counts(item_counts)
        
        return jsonify({
            'success': True,
            'message': 'Shopping list sent successfully!' if not is_update else 'Shopping list updated successfully!',
            'message_sid': twilio_message.sid,
            'was_update': is_update
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/preview', methods=['POST'])
def preview_list():
    """API endpoint to preview sorted shopping list"""
    try:
        data = request.json
        selected_items = data.get('items', [])
        
        if not selected_items:
            return jsonify({'success': False, 'error': 'No items selected'}), 400
        
        sorted_items = sort_items_by_aisle(selected_items)
        
        return jsonify({'success': True, 'items': sorted_items})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
