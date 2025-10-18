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
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM')  # Format: whatsapp:+14155238886
WHATSAPP_TO = os.getenv('WHATSAPP_TO')  # Format: whatsapp:+1234567890

def get_google_sheet():
    """Connect to Google Sheets and return the worksheet"""
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SPREADSHEET_NAME).sheet1
        return sheet
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None

def get_all_items():
    """Fetch all items from Google Sheets"""
    sheet = get_google_sheet()
    if not sheet:
        return []
    
    # Get all records (assuming first row is header)
    records = sheet.get_all_records()
    return records

def add_item_to_sheet(item_name, category, aisle_order=999):
    """Add a new item to Google Sheets"""
    try:
        sheet = get_google_sheet()
        if not sheet:
            return False
        
        # Append new row with item data
        sheet.append_row([item_name, category, aisle_order])
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

@app.route('/api/items', methods=['POST'])
def add_item():
    """API endpoint to add a new item to Google Sheets"""
    try:
        data = request.json
        item_name = data.get('item_name', '').strip()
        category = data.get('category', '').strip()
        aisle_order = data.get('aisle_order', 999)
        
        if not item_name or not category:
            return jsonify({'success': False, 'error': 'Item name and category are required'}), 400
        
        success = add_item_to_sheet(item_name, category, aisle_order)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Item added successfully!',
                'item': {
                    'Item': item_name,
                    'Category': category,
                    'Aisle_Order': aisle_order
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
        
        # Sort items by aisle order
        sorted_items = sort_items_by_aisle(selected_items)
        
        # Format message
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
        
        # Send via Twilio
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
        
        # Sort items by aisle order
        sorted_items = sort_items_by_aisle(selected_items)
        
        return jsonify({'success': True, 'items': sorted_items})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
