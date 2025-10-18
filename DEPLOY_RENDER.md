# Quick Deploy to Render (Free)

This guide will get your app online in ~10 minutes.

## Step 1: Prepare Your Files

Make sure you have:
- ✅ All project files
- ✅ `credentials.json` from Google Cloud
- ✅ Your `.env` values ready

## Step 2: Push to GitHub (Optional but Recommended)

1. Create a new repository on GitHub
2. Upload all files EXCEPT:
   - `.env` (never commit this!)
   - `credentials.json` (never commit this!)
   
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_URL
git push -u origin main
```

## Step 3: Deploy on Render

### Create Account
1. Go to [render.com](https://render.com)
2. Sign up (can use GitHub account)

### Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repo (or choose "Deploy from Git")
3. If using Git URL, paste your repo URL

### Configure Service

**Basic Settings:**
- Name: `shopping-list-app` (or any name you want)
- Region: Choose closest to you
- Branch: `main`
- Root Directory: Leave blank
- Runtime: `Python 3`

**Build & Deploy:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

**Instance Type:**
- Select: `Free` (this is enough!)

### Add Environment Variables

Click "Advanced" → "Add Environment Variable" for each:

```
GOOGLE_SHEETS_CREDS_FILE=/etc/secrets/credentials.json
SPREADSHEET_NAME=Shopping Items
TWILIO_ACCOUNT_SID=your_actual_sid
TWILIO_AUTH_TOKEN=your_actual_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+1234567890
```

Replace with your actual values!

### Add Secret File (credentials.json)

1. Still in "Advanced" section
2. Click "Add Secret File"
3. Filename: `credentials.json`
4. Contents: Paste your entire credentials.json file content
5. Mount Path: `/etc/secrets/credentials.json`

### Deploy!

1. Click "Create Web Service"
2. Wait 2-3 minutes for deployment
3. Your app URL will be shown at the top (e.g., `https://shopping-list-app.onrender.com`)

## Step 4: Test Your App

1. Open the URL Render provides
2. You should see your shopping list interface
3. Try loading items from your Google Sheet
4. Test sending to WhatsApp

## Troubleshooting Deploy Issues

### Build fails
- Check `requirements.txt` is correct
- Ensure Python version compatibility

### App crashes on start
- Verify all environment variables are set
- Check credentials.json was uploaded correctly
- Look at logs in Render dashboard

### Can't connect to Google Sheets
- Verify credentials.json path is `/etc/secrets/credentials.json`
- Check the service account email has access to your sheet
- Ensure both Google Sheets API and Drive API are enabled

### WhatsApp not working
- Confirm Twilio credentials are correct
- Verify phone number format: `whatsapp:+1234567890`
- Check you joined the Twilio sandbox
- Look for error messages in Render logs

## Free Tier Limitations

Render free tier:
- ✅ Unlimited requests
- ✅ Always online
- ⚠️ May spin down after 15 minutes of inactivity (takes ~30 seconds to wake up)
- ✅ Custom domain support
- ✅ Automatic HTTPS

This is perfect for personal use!

## Keeping Your App Awake (Optional)

If you want instant response times, you can:
1. Upgrade to paid tier ($7/month) - instant, never sleeps
2. Use a free uptime monitoring service to ping your app every 10 minutes

## Updating Your App

When you want to update:
1. Push changes to GitHub
2. Render automatically redeploys (or click "Manual Deploy" in dashboard)

## Security Tips

✅ DO:
- Use environment variables for all secrets
- Keep credentials.json as a secret file
- Regularly rotate Twilio tokens

❌ DON'T:
- Commit `.env` to GitHub
- Commit `credentials.json` to GitHub  
- Share your Render URL publicly if you want to keep it private

## Your App is Live! 🎉

Bookmark your Render URL and use it anytime to create shopping lists!

Example URL: `https://your-app-name.onrender.com`
