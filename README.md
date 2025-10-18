# Shopping List Web App

A Flask web application that helps you create shopping lists from a Google Sheets database and send them to WhatsApp via Twilio.

## Features

- 📊 **Google Sheets Integration**: Manage your shopping items in Google Sheets
- 🔍 **Search & Filter**: Quickly find items by name or category
- 📱 **WhatsApp Integration**: Send organized shopping lists directly to WhatsApp
- 🗺️ **Smart Sorting**: Items are automatically sorted by aisle order for efficient shopping
- 💻 **Responsive Design**: Works great on desktop and mobile devices

## Prerequisites

1. **Google Cloud Account** (free)
2. **Twilio Account** (free trial available)
3. **Python 3.8+**

## Setup Instructions

### 1. Google Sheets Setup

#### Create Your Spreadsheet
Create a Google Sheet with the following columns (first row as headers):

| Item | Category | Aisle_Order |
|------|----------|-------------|
| Milk | Dairy | 1 |
| Bread | Bakery | 2 |
| Apples | Produce | 3 |
| Chicken | Meat | 4 |
| Pasta | Dry Goods | 5 |

- **Item**: Name of the shopping item
- **Category**: Category/section of the store
- **Aisle_Order**: Number indicating the order you encounter aisles in your store (lower = first)

Name your spreadsheet "Shopping Items" (or customize in `.env` file).

#### Get Google Sheets API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **Google Sheets API**:
   - Search for "Google Sheets API" in the API Library
   - Click "Enable"
4. Enable the **Google Drive API**:
   - Search for "Google Drive API" in the API Library
   - Click "Enable"
5. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Name it (e.g., "shopping-list-app")
   - Click "Create and Continue"
   - Skip optional steps, click "Done"
6. Create a key:
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose JSON format
   - Download the file and save it as `credentials.json` in your app directory
7. Share your Google Sheet:
   - Open your credentials.json file
   - Find the "client_email" field (looks like: `something@something.iam.gserviceaccount.com`)
   - Share your Google Sheet with this email address (give it "Editor" permissions)

### 2. Twilio Setup

#### Create Twilio Account
1. Sign up at [Twilio](https://www.twilio.com/try-twilio)
2. Get a free trial account (includes $15 credit)

#### Enable WhatsApp Sandbox
1. In Twilio Console, go to "Messaging" > "Try it out" > "Send a WhatsApp message"
2. Follow instructions to join the sandbox:
   - Send the code shown (e.g., "join <code>") to the Twilio WhatsApp number
   - You'll receive a confirmation
3. Note down:
   - **Account SID** (from Twilio Console dashboard)
   - **Auth Token** (from Twilio Console dashboard)
   - **WhatsApp From Number** (the Twilio sandbox number, format: `whatsapp:+14155238886`)

### 3. Application Setup

#### Clone/Download the Project
```bash
cd shopping_list_app
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your credentials:
   ```
   GOOGLE_SHEETS_CREDS_FILE=credentials.json
   SPREADSHEET_NAME=Shopping Items
   
   TWILIO_ACCOUNT_SID=your_actual_sid_here
   TWILIO_AUTH_TOKEN=your_actual_token_here
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   WHATSAPP_TO=whatsapp:+1234567890  # Your WhatsApp number
   ```

   **Important**: 
   - Replace `your_actual_sid_here` with your Twilio Account SID
   - Replace `your_actual_token_here` with your Twilio Auth Token
   - Replace `+1234567890` with your actual WhatsApp number (must be registered with Twilio sandbox)

#### Place Your credentials.json
Put the Google Sheets API credentials file in the app directory:
```
shopping_list_app/
  ├── app.py
  ├── credentials.json  ← Place here
  ├── .env
  └── ...
```

### 4. Run Locally

```bash
python app.py
```

Visit: `http://localhost:5000`

## Deploying Online

### Option 1: Render (Recommended - Free Tier Available)

1. Create account at [Render](https://render.com)
2. Click "New +" > "Web Service"
3. Connect your GitHub repo (or upload files)
4. Configuration:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**: Add all variables from your `.env` file
5. Under "Advanced", upload your `credentials.json` as a secret file
6. Click "Create Web Service"

### Option 2: Railway

1. Create account at [Railway](https://railway.app)
2. Click "New Project" > "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables in Settings
5. Upload `credentials.json` in the Files section
6. Deploy!

### Option 3: PythonAnywhere

1. Create account at [PythonAnywhere](https://www.pythonanywhere.com)
2. Upload files via "Files" tab
3. Create a web app (Flask)
4. Configure WSGI file to point to your app
5. Set environment variables in the web app configuration
6. Upload `credentials.json`

## Usage

1. **Open the web app** in your browser
2. **Search** for items using the search box
3. **Select items** by clicking on them (or using checkboxes)
4. **Preview** your list to see it sorted by aisle order
5. **Send to WhatsApp** - the list will be sent to the configured number

## Customization

### Changing Store Layout
Update the `Aisle_Order` column in your Google Sheet. Lower numbers = visited first.

### Adding New Items
Simply add new rows to your Google Sheet with Item, Category, and Aisle_Order.

### Changing Message Format
Edit the message formatting in `app.py`, function `send_whatsapp()`:
```python
message = "🛒 *Shopping List*\n\n"
# Customize this!
```

## Troubleshooting

### "Error connecting to Google Sheets"
- Verify `credentials.json` is in the correct location
- Check that you shared the Google Sheet with the service account email
- Ensure Google Sheets API and Google Drive API are enabled

### "Twilio credentials not configured"
- Check all Twilio variables in `.env` are set correctly
- Verify your phone number joined the Twilio WhatsApp sandbox
- Check Account SID and Auth Token are correct

### "No items found"
- Ensure your Google Sheet has the correct column names: `Item`, `Category`, `Aisle_Order`
- Check that the sheet name matches `SPREADSHEET_NAME` in `.env`
- Verify the first row contains headers

### WhatsApp message not received
- Confirm your phone number joined the Twilio sandbox
- Check you're using the correct WhatsApp number format: `whatsapp:+1234567890`
- Verify you have Twilio credits (free trial includes $15)

## Cost Estimate

- **Google Sheets API**: Free
- **Hosting (Render/Railway)**: Free tier available
- **Twilio WhatsApp**: ~$0.005 per message (free trial includes $15 = ~3000 messages)

## Security Notes

- Never commit `.env` or `credentials.json` to version control
- When deploying, use environment variables for sensitive data
- Regularly rotate your Twilio Auth Token
- Keep your Google service account credentials secure

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review [Twilio WhatsApp Documentation](https://www.twilio.com/docs/whatsapp)
3. Review [Google Sheets API Documentation](https://developers.google.com/sheets/api)

## License

Free to use and modify for personal use.
