# 🚀 QUICK START CHECKLIST

Follow these steps to get your shopping list app online!

## ✅ Phase 1: Setup (15 minutes)

### 1. Google Sheets Setup
- [ ] Create a Google Sheet named "Shopping Items"
- [ ] Add columns: `Item`, `Category`, `Aisle_Order`
- [ ] Add your shopping items (see SAMPLE_DATA.md for examples)
- [ ] Go to Google Cloud Console
- [ ] Enable Google Sheets API
- [ ] Enable Google Drive API
- [ ] Create Service Account
- [ ] Download credentials.json
- [ ] Share your Google Sheet with the service account email

### 2. Twilio Setup
- [ ] Sign up for Twilio account (free trial)
- [ ] Join WhatsApp Sandbox
- [ ] Note your Account SID
- [ ] Note your Auth Token
- [ ] Note the Twilio WhatsApp number

### 3. Local Testing (Optional)
- [ ] Install Python 3.8+
- [ ] Run: `pip install -r requirements.txt`
- [ ] Copy .env.example to .env
- [ ] Fill in .env with your credentials
- [ ] Place credentials.json in app directory
- [ ] Run: `python app.py`
- [ ] Test at http://localhost:5000

## ✅ Phase 2: Deploy Online (10 minutes)

### Deploy to Render
- [ ] Sign up at render.com
- [ ] Push code to GitHub (exclude .env and credentials.json!)
- [ ] Create new Web Service on Render
- [ ] Connect your GitHub repo
- [ ] Set Build Command: `pip install -r requirements.txt`
- [ ] Set Start Command: `gunicorn app:app`
- [ ] Add all environment variables from .env
- [ ] Upload credentials.json as Secret File to `/etc/secrets/credentials.json`
- [ ] Click "Create Web Service"
- [ ] Wait 2-3 minutes for deployment

## ✅ Phase 3: Test & Use

- [ ] Open your Render URL
- [ ] Verify items load from Google Sheets
- [ ] Select some items
- [ ] Click "Preview List" to see sorted order
- [ ] Click "Send to WhatsApp"
- [ ] Check your phone for the message!

## 🎉 You're Done!

Bookmark your app URL and use it whenever you need to create a shopping list.

## 📚 Need Help?

- **Setup Issues**: Check README.md
- **Deployment Issues**: Check DEPLOY_RENDER.md
- **Understanding the code**: Check ARCHITECTURE.md
- **Google Sheets format**: Check SAMPLE_DATA.md

## 💡 Quick Tips

1. **Add items**: Just add new rows in your Google Sheet - changes are instant
2. **Change store layout**: Update Aisle_Order numbers in your sheet
3. **Multiple stores**: Create multiple sheets, switch SPREADSHEET_NAME in settings
4. **Share with family**: Just share your Render URL with them

## ⏱️ Time Estimate

- Google Setup: 10 min
- Twilio Setup: 5 min
- Deploy to Render: 5 min
- **Total: ~20 minutes**

## 🔒 Security Reminder

✅ **NEVER** commit these files to public GitHub:
- `.env`
- `credentials.json`

These contain your API keys and should stay secret!

---

**Ready to start? Begin with Phase 1, Step 1! 🛒**
