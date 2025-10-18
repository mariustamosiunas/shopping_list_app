# 🔧 TROUBLESHOOTING GUIDE

Common issues and how to fix them.

## 🔴 Google Sheets Issues

### "Error connecting to Google Sheets"

**Possible causes:**

1. **credentials.json not found**
   - ✅ Check file is in correct location
   - ✅ For local: same directory as app.py
   - ✅ For Render: uploaded as secret file to `/etc/secrets/credentials.json`

2. **Service account doesn't have access**
   - ✅ Open credentials.json and find "client_email"
   - ✅ Go to your Google Sheet → Share
   - ✅ Add that email as Editor
   - ✅ Make sure you clicked "Send"

3. **APIs not enabled**
   - ✅ Go to Google Cloud Console
   - ✅ Search for "Google Sheets API" → Enable
   - ✅ Search for "Google Drive API" → Enable

### "No items found"

**Check your sheet format:**

```
Correct format:
| Item  | Category | Aisle_Order |
|-------|----------|-------------|
| Milk  | Dairy    | 1          |
| Bread | Bakery   | 2          |

Wrong format:
| item  | category | aisle_order |  ← Wrong! Use exact case
| Items | Cat.     | Order       |  ← Wrong! Wrong names
```

**Column names MUST be exactly:**
- `Item` (capital I)
- `Category` (capital C)  
- `Aisle_Order` (capital A, capital O, underscore)

**Other checks:**
- ✅ First row must be headers
- ✅ Sheet name matches SPREADSHEET_NAME in .env
- ✅ Data starts in row 2

### "Items showing but can't select them"

**Browser issue:**
- ✅ Try refreshing the page (Ctrl+F5 / Cmd+Shift+R)
- ✅ Clear browser cache
- ✅ Try different browser
- ✅ Check browser console for JavaScript errors (F12)

## 📱 WhatsApp/Twilio Issues

### "Twilio credentials not configured"

**Check your .env file (or Render environment variables):**

```
# All of these are required:
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx  ← Must start with AC
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886  ← Must include "whatsapp:"
WHATSAPP_TO=whatsapp:+1234567890            ← Must include "whatsapp:"
```

### "Message not received"

1. **Not joined sandbox**
   - ✅ Go to Twilio Console → Messaging → Try WhatsApp
   - ✅ Send the join code to Twilio's number
   - ✅ Wait for confirmation message

2. **Wrong phone number format**
   ```
   ✅ Correct: whatsapp:+12025551234
   ❌ Wrong:   +1 (202) 555-1234
   ❌ Wrong:   whatsapp:2025551234
   ❌ Wrong:   12025551234
   ```
   - Must include country code
   - No spaces or dashes
   - Must start with "whatsapp:"

3. **Twilio trial limitations**
   - Trial accounts can ONLY send to verified numbers
   - Make sure your number is verified in Twilio Console

4. **Out of credits**
   - Check Twilio Console → Billing
   - Free trial includes $15 (~3000 messages)

### "Error sending message" from Twilio

**Common error codes:**

- **21211**: Invalid phone number format
  - Fix: Use format `whatsapp:+12025551234`

- **21408**: Permission denied
  - Fix: Verify phone number in Twilio Console

- **21610**: Number not opted in
  - Fix: Send join code to Twilio WhatsApp sandbox

## 🌐 Deployment Issues (Render)

### "Build failed"

**Check requirements.txt:**
- ✅ File exists
- ✅ No typos in package names
- ✅ No extra spaces or blank lines

**Build command correct:**
```
pip install -r requirements.txt
```

### "Application failed to start"

**Check start command:**
```
Correct: gunicorn app:app
Wrong:   python app.py  ← Don't use this for Render
```

**Check logs:**
- Go to Render Dashboard → Your Service → Logs
- Look for error messages

**Common issues:**
- Missing environment variable
- credentials.json not uploaded or wrong path
- Port configuration (Render handles this automatically)

### "502 Bad Gateway"

**App crashed - check these:**

1. **Environment variables**
   - ✅ All 5 required variables set
   - ✅ No quotes around values in Render UI
   - ✅ No extra spaces

2. **credentials.json**
   - ✅ Uploaded as Secret File
   - ✅ Path is `/etc/secrets/credentials.json`
   - ✅ GOOGLE_SHEETS_CREDS_FILE points to correct path

3. **Check logs**
   - Python errors will show in logs
   - Look for Import errors or syntax errors

### "App loads but no items appear"

**From deployment perspective:**

1. **Google Sheets API calls failing**
   - Check credentials.json is accessible
   - Verify environment variable GOOGLE_SHEETS_CREDS_FILE=`/etc/secrets/credentials.json`
   - Check Render logs for connection errors

2. **CORS issues** (rare)
   - Not applicable for this app structure

## 💻 Local Development Issues

### "Module not found"

```bash
# Install dependencies
pip install -r requirements.txt

# If using virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### "Port already in use"

```python
# In app.py, change port:
app.run(debug=True, host='0.0.0.0', port=5001)  # Try 5001 or 8000
```

### "Can't find .env file"

- ✅ File must be named exactly `.env` (with the dot)
- ✅ Must be in same directory as app.py
- ✅ Not `.env.txt` or `env` or `.env.example`

## 🔍 Debugging Tips

### Check Render Logs

```
Render Dashboard → Your Service → Logs (tab)
```

Look for:
- ImportError: Missing package
- FileNotFoundError: credentials.json not found
- Authentication errors: Google/Twilio issues
- ValueError: Environment variable issues

### Test Locally First

Always test locally before deploying:

```bash
python app.py
# Open http://localhost:5000
# Try each feature
```

### Enable Debug Mode (Local Only!)

In app.py:
```python
app.run(debug=True)  # Shows detailed errors
```

⚠️ **NEVER** use debug mode in production!

### Test Google Sheets Connection

Create a test script:
```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open('Shopping Items').sheet1
print(sheet.get_all_records())  # Should print your items
```

### Test Twilio Connection

Create a test script:
```python
from twilio.rest import Client

client = Client('YOUR_SID', 'YOUR_TOKEN')
message = client.messages.create(
    body='Test message',
    from_='whatsapp:+14155238886',
    to='whatsapp:+YOUR_NUMBER'
)
print(message.sid)  # Should print message ID
```

## 📞 Getting More Help

### Still stuck?

1. **Check documentation:**
   - [Twilio WhatsApp Docs](https://www.twilio.com/docs/whatsapp)
   - [Google Sheets API Docs](https://developers.google.com/sheets/api)
   - [Render Docs](https://render.com/docs)

2. **Check the logs:**
   - Always start with reading error messages
   - Google the exact error message
   - Check which line number the error occurred

3. **Verify credentials:**
   - Test each API separately
   - Make sure all keys are current and valid

4. **Start fresh:**
   - Delete and recreate the Render service
   - Re-upload credentials.json
   - Re-enter environment variables

## ✅ Verification Checklist

When things don't work, check these in order:

- [ ] credentials.json exists and is valid
- [ ] Google Sheet is shared with service account email
- [ ] Both Google APIs are enabled
- [ ] Sheet has correct column names (Item, Category, Aisle_Order)
- [ ] All 5 environment variables are set
- [ ] Twilio credentials are correct
- [ ] Phone number joined Twilio sandbox
- [ ] Phone number format is correct (whatsapp:+...)
- [ ] Build command is correct
- [ ] Start command is correct
- [ ] No syntax errors in code

---

**Most issues are fixed by double-checking credentials and environment variables!**
