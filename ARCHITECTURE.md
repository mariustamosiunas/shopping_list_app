# System Architecture

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                      (Web Browser/Phone)                        │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐            │
│  │   Search   │  │   Select   │  │    Send to   │            │
│  │   Items    │  │   Items    │  │   WhatsApp   │            │
│  └────────────┘  └────────────┘  └──────────────┘            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK WEB SERVER                           │
│                     (Python Backend)                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  API Endpoints:                                          │ │
│  │  • GET  /api/items           → Fetch all items          │ │
│  │  • POST /api/preview         → Preview sorted list      │ │
│  │  • POST /api/send-whatsapp   → Send to WhatsApp        │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────┬────────────────────────────┬────────────────────┘
                │                            │
                │                            │
                ▼                            ▼
┌───────────────────────────┐  ┌─────────────────────────────────┐
│    GOOGLE SHEETS API      │  │      TWILIO API                 │
│                           │  │   (WhatsApp Gateway)            │
│  ┌─────────────────────┐ │  │                                 │
│  │ Shopping Items      │ │  │  ┌──────────────────────────┐  │
│  │                     │ │  │  │ WhatsApp Message         │  │
│  │ Item | Cat | Order  │ │  │  │ To: Your Phone          │  │
│  │ Milk | Dai | 1     │ │  │  │ From: Twilio Sandbox    │  │
│  │ Bread| Bak | 2     │ │  │  └──────────────────────────┘  │
│  │ ...  | ... | ...   │ │  │                                 │
│  └─────────────────────┘ │  └─────────────────────────────────┘
│                           │                    │
└───────────────────────────┘                    │
                                                 ▼
                                    ┌─────────────────────────┐
                                    │   YOUR WHATSAPP         │
                                    │                         │
                                    │  🛒 Shopping List       │
                                    │                         │
                                    │  📍 Dairy               │
                                    │    • Milk              │
                                    │    • Cheese            │
                                    │                         │
                                    │  📍 Bakery             │
                                    │    • Bread             │
                                    │                         │
                                    │  ✅ Happy shopping!    │
                                    └─────────────────────────┘
```

## Data Flow

### 1. Loading Items
```
Browser → Flask → Google Sheets API → Your Spreadsheet
                                     ↓
                                   Returns
                                   all items
                                     ↓
        Browser ← Flask ← Formats as JSON
```

### 2. Sending to WhatsApp
```
Browser → User selects items
         ↓
       Flask receives selected items
         ↓
       Sorts by Aisle_Order
         ↓
       Formats message with categories
         ↓
       Twilio API → WhatsApp → Your Phone
```

## Component Details

### Frontend (templates/index.html)
- Pure HTML/CSS/JavaScript
- No framework needed
- Responsive design
- Real-time search/filter
- Visual feedback for selections

### Backend (app.py)
- Flask web framework
- REST API endpoints
- Google Sheets integration via gspread
- WhatsApp messaging via Twilio
- Environment-based configuration

### External Services
1. **Google Sheets**
   - Stores master item list
   - Easy to update
   - No database needed
   - Accessible from anywhere

2. **Twilio WhatsApp API**
   - Reliable message delivery
   - Official WhatsApp integration
   - Usage-based pricing
   - Free sandbox for testing

## Security Architecture

```
┌─────────────────────────────────────┐
│         SENSITIVE DATA              │
├─────────────────────────────────────┤
│ • Google API credentials.json      │  → Secret File (not in code)
│ • Twilio Account SID & Token       │  → Environment Variables
│ • Your WhatsApp number              │  → Environment Variables
└─────────────────────────────────────┘
                  ↓
         Stored securely in:
                  ↓
┌─────────────────────────────────────┐
│    Deployment Platform (Render)     │
├─────────────────────────────────────┤
│ • Environment Variables (encrypted) │
│ • Secret Files (encrypted)          │
│ • Not in Git repository             │
│ • Not visible in logs               │
└─────────────────────────────────────┘
```

## Deployment Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    RENDER.COM                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Container (Linux)                                 │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │  Your Flask App                              │ │ │
│  │  │  + gunicorn (WSGI server)                   │ │ │
│  │  │  + Environment Variables                     │ │ │
│  │  │  + credentials.json (secret file)           │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  Public URL: https://your-app.onrender.com             │
│  HTTPS: ✓  (automatic)                                  │
│  Always On: ✓  (with free tier, may sleep)             │
└──────────────────────────────────────────────────────────┘
                        ↓
              Accessible from anywhere
                        ↓
              ┌──────────────────┐
              │  Your Phone/PC   │
              └──────────────────┘
```

## Scaling Considerations

Current setup handles:
- ✅ 1-10 concurrent users easily
- ✅ Thousands of items in Google Sheet
- ✅ Instant response times
- ✅ 24/7 availability

For higher usage:
- Upgrade to paid Render tier ($7/mo)
- Add Redis for caching
- Add database for user accounts
- Implement rate limiting
