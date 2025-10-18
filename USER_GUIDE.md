# 📖 USER GUIDE

Step-by-step guide to using your Shopping List App.

## 🏁 Getting Started

### First Time Setup

After deployment, your app is accessible at your unique URL:
```
https://your-app-name.onrender.com
```

Bookmark this URL on your phone for quick access!

## 📱 Using the App

### Step 1: Open the App

```
┌─────────────────────────────────────┐
│  🛒 Shopping List Builder          │
│  Select items and send to WhatsApp │
├─────────────────────────────────────┤
│  🔍 Search items...                │
├─────────────────────────────────────┤
│  No items selected                  │
├─────────────────────────────────────┤
│  Loading items from Google Sheets..│
└─────────────────────────────────────┘
```

The app will automatically load your items from Google Sheets.

### Step 2: Browse Items

Once loaded, you'll see all your items organized:

```
┌─────────────────────────────────────┐
│  ☐ Milk                            │
│     [Dairy]                        │
├─────────────────────────────────────┤
│  ☐ Bread                           │
│     [Bakery]                       │
├─────────────────────────────────────┤
│  ☐ Apples                          │
│     [Produce]                      │
└─────────────────────────────────────┘
```

Each item shows:
- Item name (bold)
- Category badge (colored)

### Step 3: Search (Optional)

Type in the search box to filter items:

```
┌─────────────────────────────────────┐
│  🔍 dairy                          │  ← Type here
├─────────────────────────────────────┤
│  ☐ Milk                            │  ← Matching items
│     [Dairy]                        │     shown
├─────────────────────────────────────┤
│  ☐ Cheese                          │
│     [Dairy]                        │
└─────────────────────────────────────┘
```

Search works for:
- Item names (e.g., "milk")
- Categories (e.g., "dairy")

### Step 4: Select Items

Click on any item (or checkbox) to select it:

```
Before click:                After click:
┌─────────────────┐        ┌─────────────────┐
│  ☐ Milk        │        │  ☑ Milk        │ ← Blue background
│     [Dairy]    │        │     [Dairy]    │    Blue left border
└─────────────────┘        └─────────────────┘
```

**Selection counter updates:**
```
3 items selected
```

You can click again to deselect.

### Step 5: Preview Your List

Click the "👁️ Preview List" button:

```
┌─────────────────────────────────────┐
│  Shopping List Preview        ✕    │
├─────────────────────────────────────┤
│  🛒 Shopping List                  │
│                                     │
│  📍 Dairy                          │
│    • Milk                          │
│    • Cheese                        │
│                                     │
│  📍 Bakery                         │
│    • Bread                         │
│                                     │
│  📍 Produce                        │
│    • Apples                        │
│                                     │
│  ✅ Happy shopping!                │
└─────────────────────────────────────┘
```

Notice:
- Items are grouped by category
- Categories appear in aisle order
- Easy to read format

**Close preview** by clicking:
- The ✕ button
- Outside the preview box

### Step 6: Send to WhatsApp

When ready, click "📱 Send to WhatsApp":

```
┌─────────────────────────────────────┐
│  Send this shopping list            │
│  to WhatsApp?                       │
│                                     │
│         [Cancel]  [OK]              │
└─────────────────────────────────────┘
```

Click OK to send.

**Success message:**
```
✅ Shopping list sent to WhatsApp successfully!
```

**On your phone:**
```
WhatsApp notification from Twilio:

🛒 Shopping List

📍 Dairy
  • Milk
  • Cheese

📍 Bakery
  • Bread

📍 Produce
  • Apples

✅ Happy shopping!
```

### Step 7: Shop!

Follow the list on your phone:
1. Start at the first category (Dairy)
2. Work your way down the list
3. Each category is in the order you encounter them in the store
4. No backtracking needed!

## 🎯 Tips & Tricks

### Quick Selection
- Click anywhere on the item box (not just the checkbox)
- Selected items have blue highlighting

### Efficient Search
- Type partial words: "chee" finds "Cheese"
- Search by category: "dairy" shows all dairy items
- Clear search to see all items again

### Mobile Use
- App is fully mobile-responsive
- Works great on phones and tablets
- Save to home screen for app-like experience

### Reusing Lists
After sending:
- Your selections are cleared
- Start fresh for next shopping trip
- Or select same items again

## 🔄 Common Workflows

### Weekly Grocery Shopping

1. Open app on Monday
2. Select weekly staples
3. Preview to verify
4. Send to WhatsApp
5. Shop on Saturday using the list

### Quick Top-Up Shopping

1. Open app when you notice you're low on something
2. Search for specific items
3. Select just those items
4. Send immediately
5. Quick trip to store

### Party Preparation

1. Think through party needs
2. Search categories: "snacks", "drinks"
3. Select party items
4. Preview to ensure nothing missed
5. Send and shop

## 📊 Understanding Your Google Sheet

Your Google Sheet controls everything:

### Column: Item
```
The name that appears in the app
Example: "Milk", "Whole Wheat Bread", "Granny Smith Apples"
```

### Column: Category  
```
Groups items together
Example: "Dairy", "Bakery", "Produce"
```

### Column: Aisle_Order
```
Number determining order in your store
Lower number = encountered first
Example: 1, 2, 3, 4, 5...

Your store layout:
1 - Produce (first thing you see)
2 - Bakery
3 - Dairy
4 - Meat
5 - Frozen (at the back)
```

## ✏️ Managing Your Items

### Adding New Items

In Google Sheets:
1. Click row below last item
2. Type Item name
3. Type Category
4. Type Aisle_Order number
5. Refresh app (changes are instant!)

### Editing Items

In Google Sheets:
1. Find the item
2. Click the cell to edit
3. Make your change
4. Changes appear in app immediately

### Deleting Items

In Google Sheets:
1. Right-click the row number
2. Select "Delete row"
3. Item disappears from app

### Reorganizing Categories

Change Aisle_Order numbers:
1. Identify which category should come first
2. Give it the lowest number
3. Continue in order through your store
4. Items will sort automatically in app

## 🛒 Shopping Tips

### Efficient Route
Follow the list from top to bottom - it matches your store layout!

### Check Twice
Use the Preview feature before sending to avoid forgetting items.

### Share with Others
Send your Render app URL to family members so they can add to the list.

### Multiple Lists
Keep different sheets for:
- "Weekly Groceries" (regular items)
- "Special Occasions" (party items)
- "Costco Run" (bulk shopping)

Switch by changing SPREADSHEET_NAME in environment variables.

## ⚙️ App Behavior

### Loading Time
- First load: 1-3 seconds
- After wake-up (free tier): ~30 seconds
- Subsequent loads: Instant

### Updates
- Google Sheet changes: Instant
- App code changes: Requires redeployment

### Limits
- Items: Unlimited (Google Sheets supports 5 million cells)
- Selections: Unlimited
- Messages: ~3000 on free Twilio trial

## 🎨 Visual Features

### Color Coding
- Selected items: Blue highlight
- Categories: Purple badges
- Buttons: Gray (Preview) / Green (WhatsApp)

### Responsive Design
- Desktop: Wide layout, large text
- Tablet: Optimized for touch
- Phone: Full-screen, easy selection

### Animations
- Items slide when hovering
- Smooth transitions on selection
- Loading spinner when sending

## 📞 Buttons Explained

### 👁️ Preview List
- Shows you what will be sent
- Items sorted by aisle
- No WhatsApp message sent yet
- Safe to click anytime

### 📱 Send to WhatsApp
- Sends the actual message
- Confirmation required
- Clears selections after sending
- Uses one Twilio credit (~$0.005)

Both buttons are disabled when no items are selected.

## ✅ Best Practices

1. **Update your sheet regularly** - Add items as you run out
2. **Use consistent categories** - Makes sorting more effective
3. **Number aisles accurately** - Walk through your store once
4. **Test the preview** - Before sending
5. **Keep your phone handy** - For receiving WhatsApp messages

---

**Happy Shopping! 🛒**

*Remember: The app is always accessible at your Render URL. Bookmark it for easy access!*
