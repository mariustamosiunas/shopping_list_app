from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import time

load_dotenv()

app = Flask(__name__)

# Configuration
GOOGLE_SHEETS_CREDS_FILE = os.getenv('GOOGLE_SHEETS_CREDS_FILE', 'credentials.json')
SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME', 'Shopping Items')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM')
WHATSAPP_TO = os.getenv('WHATSAPP_TO')

# Cache configuration
CACHE_TTL = 300  # 5 minutes cache
_cache = {}

def cached_fetch(key, fetch_function, ttl=CACHE_TTL):
    """Generic caching function with TTL"""
    now = time.time()
    
    if key in _cache:
        data, timestamp = _cache[key]
        if now - timestamp < ttl:
            return data
    
    # Cache miss or expired - fetch fresh data
    data = fetch_function()
    _cache[key] = (data, now)
    return data

def invalidate_cache(key=None):
    """Invalidate cache - specific key or all"""
    if key:
        _cache.pop(key, None)
    else:
        _cache.clear()

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

def get_all_items():
    """Fetch all items from Items sheet with caching"""
    def _fetch_items():
        workbook = get_google_sheet()
        if not workbook:
            return []
        
        try:
            items_sheet = workbook.worksheet('Items')
            items = items_sheet.get_all_records()
            
            # Filter out empty items
            items = [item for item in items if item.get('Item', '').strip()]
            
            # Get categories
            categories_sheet = workbook.worksheet('Categories')
            categories = categories_sheet.get_all_records()
            category_map = {cat['Category']: cat for cat in categories}
            
            # Enrich items
            for item in items:
                # Set defaults
                if not item.get('Purchase_Count'):
                    item['Purchase_Count'] = 0
                else:
                    try:
                        item['Purchase_Count'] = int(item['Purchase_Count'])
                    except:
                        item['Purchase_Count'] = 0
                
                # Unit type
                unit_type = str(item.get('Unit_Type', '')).lower().strip()
                if unit_type in ['weight', 'kg', 'g', 'weighted']:
                    item['Unit_Type'] = 'weight'
                else:
                    item['Unit_Type'] = 'quantity'
                
                # Aisle order
                category_name = item.get('Category', '')
                if category_name in category_map:
                    item['Aisle_Order'] = category_map[category_name].get('Aisle_Order', 999)
                else:
                    item['Aisle_Order'] = 999
            
            return items
        except Exception as e:
            print(f"Error fetching items: {e}")
            return []
    
    return cached_fetch("items", _fetch_items)

def get_all_categories():
    """Fetch all categories with caching"""
    def _fetch_categories():
        workbook = get_google_sheet()
        if not workbook:
            return []
        
        try:
            sheet = workbook.worksheet('Categories')
            return sheet.get_all_records()
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []
    
    return cached_fetch("categories", _fetch_categories)

def get_shopping_history(limit=3):
    """Get last N shopping lists with caching"""
    def _fetch_history():
        workbook = get_google_sheet()
        if not workbook:
            return []
        
        try:
            sheet = workbook.worksheet('Shopping_History')
            all_records = sheet.get_all_records()
            
            if not all_records:
                return []
            
            # Get last N records
            recent = all_records[-limit:] if len(all_records) >= limit else all_records
            recent = list(reversed(recent))
            
            # Parse and enrich
            for record in recent:
                try:
                    record['items'] = json.loads(record.get('Items_JSON', '[]'))
                except:
                    record['items'] = []
                
                # Check editability
                timestamp_str = record.get('Timestamp', '')
                if timestamp_str:
                    try:
                        list_time = datetime.fromisoformat(timestamp_str)
                        now = datetime.now()
                        time_diff = (now - list_time).total_seconds() / 60
                        record['is_editable'] = time_diff < 60
                        record['minutes_ago'] = int(time_diff)
                    except:
                        record['is_editable'] = False
                        record['minutes_ago'] = 999
                else:
                    record['is_editable'] = False
                    record['minutes_ago'] = 999
            
            return recent
        except Exception as e:
            print(f"Error fetching shopping history: {e}")
            return []
    
    return cached_fetch("history", _fetch_history, ttl=60)  # Shorter TTL for history

def add_item_to_sheet(item_name, category, unit_type='quantity'):
    """Add new item and invalidate cache"""
    try:
        workbook = get_google_sheet()
        if not workbook:
            return False, None
        
        sheet = workbook.worksheet('Items')
        item_id = generate_next_item_id()
        headers = sheet.row_values(1)
        
        unit_type = 'weight' if unit_type.lower() in ['weight', 'kg', 'g'] else 'quantity'
        
        if 'Item_ID' in headers and 'Purchase_Count' in headers and 'Unit_Type' in headers:
            sheet.append_row([item_name, category, item_id, 0, unit_type])
        elif 'Item_ID' in headers and 'Purchase_Count' in headers:
            sheet.append_row([item_name, category, item_id, 0])
        elif 'Item_ID' in headers:
            sheet.append_row([item_name, category, item_id])
        else:
            sheet.append_row([item_name, category])
        
        # Invalidate caches
        invalidate_cache("items")
        invalidate_cache("categories")
        
        return True, item_id
    except Exception as e:
        print(f"Error adding item: {e}")
        return False, None

def update_purchase_counts(item_counts):
    """Update purchase counts and invalidate cache"""
    try:
        workbook = get_google_sheet()
        if not workbook:
            return False
        
        sheet = workbook.worksheet('Items')
        headers = sheet.row_values(1)
        
        if 'Item_ID' not in headers or 'Purchase_Count' not in headers:
            return False
        
        id_col = headers.index('Item_ID') + 1
        count_col = headers.index('Purchase_Count') + 1
        all_ids = sheet.col_values(id_col)
        
        for item_id, quantity in item_counts.items():
            try:
                if item_id in all_ids:
                    row_idx = all_ids.index(item_id) + 1
                    current_count = sheet.cell(row_idx, count_col).value
                    try:
                        current_count = int(current_count) if current_count else 0
                    except:
                        current_count = 0
                    
                    new_count = current_count + quantity
                    sheet.update_cell(row_idx, count_col, new_count)
            except Exception as e:
                print(f"Error updating count for {item_id}: {e}")
                continue
        
        # Invalidate items cache
        invalidate_cache("items")
        
        return True
    except Exception as e:
        print(f"Error updating purchase counts: {e}")
        return False

def ensure_history_sheet():
    """Ensure Shopping_History sheet exists"""
    try:
        workbook = get_google_sheet()
        if not workbook:
            return False
        
        try:
            workbook.worksheet('Shopping_History')
            return True
        except:
            sheet = workbook.add_worksheet(title='Shopping_History', rows=100, cols=6)
            sheet.append_row(['Timestamp', 'Date', 'Total_Items', 'Unique_Items', 'Items_JSON', 'Items_Display'])
            return True
    except Exception as e:
        print(f"Error ensuring history sheet: {e}")
        return False

def save_shopping_history(items_data):
    """Save shopping list to history and invalidate cache"""
    try:
        ensure_history_sheet()
        workbook = get_google_sheet()
        if not workbook:
            return False
        
        sheet = workbook.worksheet('Shopping_History')
        
        timestamp = datetime.now().isoformat()
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        total_items = sum(item.get('quantity', 1) for item in items_data)
        unique_items = len(items_data)
        
        items_json = json.dumps([{
            'item_id': item.get('Item_ID', ''),
            'name': item.get('Item', ''),
            'category': item.get('Category', ''),
            'quantity': item.get('quantity', 1),
            'unit_type': item.get('Unit_Type', 'quantity')
        } for item in items_data])
        
        items_display = '; '.join([
            f"{item.get('Item', 'Unknown')} ({item.get('quantity', 1)}{'kg' if item.get('Unit_Type') == 'weight' else 'x'})"
            for item in items_data
        ])
        
        sheet.append_row([timestamp, date, total_items, unique_items, items_json, items_display])
        
        # Invalidate history cache
        invalidate_cache("history")
        
        return True
    except Exception as e:
        print(f"Error saving shopping history: {e}")
        return False

def update_last_shopping_list(items_data):
    """Update most recent shopping list and invalidate cache"""
    try:
        workbook = get_google_sheet()
        if not workbook:
            return False
        
        sheet = workbook.worksheet('Shopping_History')
        all_records = sheet.get_all_records()
        
        if not all_records:
            return False
        
        last_row = len(all_records) + 1
        last_record = all_records[-1]
        timestamp_str = last_record.get('Timestamp', '')
        
        if timestamp_str:
            try:
                list_time = datetime.fromisoformat(timestamp_str)
                now = datetime.now()
                time_diff = (now - list_time).total_seconds() / 60
                
                if time_diff >= 60:
                    return False
            except:
                return False
        else:
            return False
        
        timestamp = datetime.now().isoformat()
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        total_items = sum(item.get('quantity', 1) for item in items_data)
        unique_items = len(items_data)
        
        items_json = json.dumps([{
            'item_id': item.get('Item_ID', ''),
            'name': item.get('Item', ''),
            'category': item.get('Category', ''),
            'quantity': item.get('quantity', 1),
            'unit_type': item.get('Unit_Type', 'quantity')
        } for item in items_data])
        
        items_display = '; '.join([
            f"{item.get('Item', 'Unknown')} ({item.get('quantity', 1)}{'kg' if item.get('Unit_Type') == 'weight' else 'x'})"
            for item in items_data
        ])
        
        sheet.update(f'A{last_row}:F{last_row}', [[timestamp, date, total_items, unique_items, items_json, items_display]])
        
        # Invalidate history cache
        invalidate_cache("history")
        
        return True
    except Exception as e:
        print(f"Error updating shopping history: {e}")
        return False

def sort_items_by_aisle(items):
    """Sort items by aisle order"""
    return sorted(items, key=lambda x: x.get('Aisle_Order', 999))

def sort_items_by_popularity(items):
    """Sort items by purchase count"""
    return sorted(items, key=lambda x: x.get('Purchase_Count', 0), reverse=True)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/items', methods=['GET'])
def api_items():
    try:
        items = get_all_items()
        return jsonify({'success': True, 'items': sort_items_by_popularity(items)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/items', methods=['POST'])
def add_item():
    try:
        data = request.json
        item_name = data.get('item_name', '').strip()
        category = data.get('category', '').strip()
        unit_type = data.get('unit_type', 'quantity').strip()
        
        if not item_name or not category:
            return jsonify({'success': False, 'error': 'Item name and category required'}), 400
        
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

@app.route('/api/categories', methods=['GET'])
def api_categories():
    try:
        cats = get_all_categories()
        return jsonify({'success': True, 'categories': cats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def api_history():
    try:
        limit = int(request.args.get('limit', 3))
        hist = get_shopping_history(limit)
        return jsonify({'success': True, 'history': hist})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/preview', methods=['POST'])
def preview():
    try:
        data = request.json
        items = data.get('items', [])
        
        if not items:
            return jsonify({'success': False, 'error': 'No items provided'}), 400
        
        sorted_items = sort_items_by_aisle(items)
        return jsonify({'success': True, 'items': sorted_items})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send-whatsapp', methods=['POST'])
def send_whatsapp():
    try:
        data = request.json
        selected_items = data.get('items', [])
        is_update = data.get('is_update', False)
        
        if not selected_items:
            return jsonify({'success': False, 'error': 'No items selected'}), 400
        
        sorted_items = sort_items_by_aisle(selected_items)
        
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
            unit_type = item.get('Unit_Type', 'quantity')
            
            if unit_type == 'weight':
                message += f"  • {item_name} - {quantity} kg\n"
            elif quantity > 1:
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
        
        # Save or update history and handle purchase counts
        if is_update:
            # Get the previous list to calculate difference
            workbook = get_google_sheet()
            if workbook:
                try:
                    sheet = workbook.worksheet('Shopping_History')
                    all_records = sheet.get_all_records()
                    
                    if all_records:
                        last_record = all_records[-1]
                        old_items_json = last_record.get('Items_JSON', '[]')
                        
                        try:
                            old_items = json.loads(old_items_json)
                            
                            # Calculate NEW items and INCREASED quantities
                            old_item_map = {item['item_id']: item['quantity'] for item in old_items if item.get('item_id')}
                            
                            item_count_diff = {}
                            for item in selected_items:
                                item_id = item.get('Item_ID', '')
                                new_quantity = item.get('quantity', 1)
                                
                                if item_id:
                                    old_quantity = old_item_map.get(item_id, 0)
                                    
                                    if old_quantity == 0:
                                        # New item added to list
                                        item_count_diff[item_id] = new_quantity
                                    elif new_quantity > old_quantity:
                                        # Quantity increased
                                        item_count_diff[item_id] = new_quantity - old_quantity
                            
                            # Update purchase counts only for NEW or INCREASED items
                            if item_count_diff:
                                update_purchase_counts(item_count_diff)
                        except:
                            # JSON parse error - treat as new list
                            pass
                except:
                    pass
            
            # Update history
            updated = update_last_shopping_list(selected_items)
            if not updated:
                # Update failed (list too old) - save as new list
                save_shopping_history(selected_items)
                # Count all items as it's a new shopping trip
                item_counts = {}
                for item in selected_items:
                    item_id = item.get('Item_ID', '')
                    quantity = item.get('quantity', 1)
                    if item_id:
                        item_counts[item_id] = quantity
                update_purchase_counts(item_counts)
        else:
            # New list - save history and update all purchase counts
            save_shopping_history(selected_items)
            item_counts = {}
            for item in selected_items:
                item_id = item.get('Item_ID', '')
                quantity = item.get('quantity', 1)
                if item_id:
                    item_counts[item_id] = quantity
            update_purchase_counts(item_counts)
        
        return jsonify({
            'success': True,
            'message': 'Shopping list updated successfully!' if is_update else 'Shopping list sent successfully!',
            'message_sid': twilio_message.sid,
            'was_update': is_update
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
