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

# -------------------------------
# GLOBAL CACHE (avoids quota exhaustion)
# -------------------------------
_cache = {"items": None, "categories": None, "history": None, "timestamp": 0}
CACHE_TTL = 60  # seconds


def get_google_sheet():
    """Connect to Google Sheets and return the workbook"""
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDS_FILE, scope)
        client = gspread.authorize(creds)
        workbook = client.open(SPREADSHEET_NAME)
        return workbook
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None


def cached_fetch(key, fetch_func):
    """Generic cache helper to limit Google Sheets API calls"""
    now = time.time()
    if _cache[key] and (now - _cache["timestamp"]) < CACHE_TTL:
        return _cache[key]
    data = fetch_func()
    _cache[key] = data
    _cache["timestamp"] = now
    return data


# -------------------------------
# DATA FETCHING FUNCTIONS
# -------------------------------
def generate_next_item_id():
    """Generate next sequential item ID like ID1, ID2, etc."""
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
        all_ids = [i for i in all_ids if i.startswith('ID')]

        if not all_ids:
            return "ID1"

        nums = []
        for s in all_ids:
            try:
                nums.append(int(s.replace('ID', '')))
            except:
                continue
        next_num = max(nums) + 1 if nums else 1
        return f"ID{next_num}"
    except Exception as e:
        print(f"Error generating ID: {e}")
        return "ID1"


def ensure_history_sheet():
    """Create Shopping_History sheet if missing"""
    try:
        workbook = get_google_sheet()
        if not workbook:
            return False
        try:
            workbook.worksheet('Shopping_History')
        except:
            ws = workbook.add_worksheet(title='Shopping_History', rows=1000, cols=6)
            ws.update('A1:F1', [['Timestamp', 'Date', 'Total_Items', 'Unique_Items', 'Items_JSON', 'Items_Display']])
        return True
    except Exception as e:
        print(f"Error ensuring history sheet: {e}")
        return False


def get_all_items():
    """Fetch all items from Items sheet and enrich with category data"""
    def _fetch_items():
        workbook = get_google_sheet()
        if not workbook:
            return []

        try:
            items_sheet = workbook.worksheet('Items')
            items = items_sheet.get_all_records()
            items = [i for i in items if i.get('Item', '').strip()]

            categories_sheet = workbook.worksheet('Categories')
            categories = categories_sheet.get_all_records()
            cat_map = {c['Category']: c for c in categories}

            for i in items:
                if not i.get('Purchase_Count'):
                    i['Purchase_Count'] = 0
                if not i.get('Unit_Type'):
                    i['Unit_Type'] = 'quantity'
                cat = i.get('Category', '')
                i['Aisle_Order'] = cat_map.get(cat, {}).get('Aisle_Order', 999)
            return items
        except Exception as e:
            print(f"Error fetching items: {e}")
            return []

    return cached_fetch("items", _fetch_items)


def get_all_categories():
    """Fetch all categories"""
    def _fetch_categories():
        workbook = get_google_sheet()
        if not workbook:
            return []
        try:
            return workbook.worksheet('Categories').get_all_records()
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []

    return cached_fetch("categories", _fetch_categories)


def get_shopping_history(limit=3):
    """Get last N shopping lists safely"""
    def _fetch_history():
        workbook = get_google_sheet()
        if not workbook:
            return []
        try:
            sheet = workbook.worksheet('Shopping_History')
            records = sheet.get_all_records()
            if not records:
                return []
            last = records[-limit:] if len(records) >= limit else records
            last.reverse()
            for r in last:
                try:
                    r['items'] = json.loads(r.get('Items_JSON', '[]'))
                except:
                    r['items'] = []
            return last
        except Exception as e:
            print(f"Error fetching shopping history: {e}")
            return []

    return cached_fetch("history", _fetch_history)


# -------------------------------
# HELPERS
# -------------------------------
def sort_items_by_aisle(items):
    return sorted(items, key=lambda x: x.get('Aisle_Order', 999))


def sort_items_by_popularity(items):
    return sorted(items, key=lambda x: x.get('Purchase_Count', 0), reverse=True)


# -------------------------------
# ROUTES
# -------------------------------
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
