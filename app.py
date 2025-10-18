from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
import os
from dotenv import load_dotenv

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

def get_all_items():
    """Fetch all items from Items sheet and enrich with category data"""
    workbook = get_google_sheet()
    if not workbook:
        return []
    
    try:
        items_sheet = workbook.worksheet('Items')
        items = items_sheet.get_all_records()
        
        # Get categories to enrich items with aisle order
        categories_sheet = workbook.worksheet('Categories')
        categories = categories_sheet.get_all_records()
        
        # Create category lookup map
        category_map = {cat['Category']: cat for cat in categories}
        
        # Enrich items with aisle order from categories
        for item in items:
            category_name = item.get('Category', '')
            if category_name in category_map:
                # Use aisle order from Categories sheet
                item['Aisle_Order'] = category_map[category_name].get('Aisle_Order', 999)
            elif 'Aisle_Order' not in item:
                # Fallback if no category match and no aisle order in item
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

def add_item_to_sheet(item_name, category):
    """Add a new item to Items sheet (only item name and category)"""
    try:
        workbook = get_google_sheet()
        if not workbook:
            return False
        
        sheet = workbook.worksheet('Items')
        # Only append Item and Category (Aisle_Order comes from Categories sheet)
        sheet.append_row([item_name, category])
        return True
    except Exception as e:
        print(f"Error adding item to Google Sheets: {e}")
        return False

def sort_items_by_aisle(items):
    """Sort items by aisle order"""
    return sorted(items, key=lambda x: x.get('Aisle_Order', 999))

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/items', methods=['GET'])
def get_items():
    """API endpoint to get all available items"""
    try:
        items = get_all_items()
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
        
        if not item_name or not category:
            return jsonify({'success': False, 'error': 'Item name and category are required'}), 400
        
        success = add_item_to_sheet(item_name, category)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Item added successfully!',
                'item': {
                    'Item': item_name,
                    'Category': category
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to add item'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send-whatsapp', methods=['POST'])
def send_whatsapp():
    """API endpoint to send shopping list via WhatsApp"""
    try:
        data = request.json
        selected_items = data.get('items', [])
        
        if not selected_items:
            return jsonify({'success': False, 'error': 'No items selected'}), 400
        
        sorted_items = sort_items_by_aisle(selected_items)
        
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
        
        return jsonify({
            'success': True,
            'message': 'Shopping list sent successfully!',
            'message_sid': twilio_message.sid
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
