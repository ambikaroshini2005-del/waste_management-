# 🌍 AI-Based Smart Waste Management System - Complete Setup

## Project Overview

This is an **AI-Powered Smart Waste Management System** that enables:

### ✅ Core Features Implemented:

1. **🖼️ Waste Image Classification**
   - Upload waste images for AI-based classification
   - Categories: Cardboard, Glass, Metal, Paper, Plastic, Trash
   - Real-time classification with instant results

2. **📍 Location Tracking**
   - GPS coordinate capture
   - Integration with Google Maps
   - Location-based waste management routing

3. **📧 Email Notifications** (NEW!)
   - Detailed waste reports sent to your Gmail
   - Location coordinates included
   - Reward points displayed
   - Organization notifications sent to waste management centers

4. **🎁 Reward System**
   - Earn points for each waste report:
     - Plastic: 20 points
     - Glass/Metal: 15 points
     - Cardboard/Paper: 10 points
     - Mixed Waste: 5 points
   - Track total rewards on dashboard

5. **🔔 Smart Notifications**
   - Automatic notifications to nearby waste management orgs
   - Real-time status updates
   - Multi-channel alert system

6. **📊 Dashboard Analytics**
   - View all waste reports
   - Track waste distribution by category
   - Monitor total rewards earned
   - Real-time statistics

---

## 🚀 Quick Start Guide

### 1. Access the Application

**URL:** http://127.0.0.1:5000/

### 2. Report Waste

1. **Enter Your Details:**
   - Name: Your full name
   - Email: Gmail address (for reports)
   - Location: Click "Get My Location" button
   - Image: Upload waste photo

2. **Submit Report:**
   - Click "Classify Waste & Report"
   - AI classifies the waste
   - Email notification sent automatically
   - Rewards displayed

### 3. View Dashboard

**URL:** http://127.0.0.1:5000/dashboard

- See all reports submitted
- View waste category distribution
- Check total rewards earned
- Monitor collection status

---

## 🔧 Email Configuration

### Required: Setup Gmail Notifications

**File to Edit:** `utils.py` (Lines 16-17)

```python
GMAIL_USER = "your_email@gmail.com"
GMAIL_PASSWORD = "your_16char_password"
```

### Get Your App Password:

1. Go to: https://myaccount.google.com/
2. Click: Security → App passwords
3. Generate password for "Mail" on "Windows Computer"
4. Copy the 16-character password
5. Paste it into `utils.py`

👉 **Detailed instructions:** See `SETUP_GMAIL.md`

---

## 📁 Project Structure

```
waste-classification-main/
├── app.py                      # Flask application (main)
├── utils.py                    # AI & email functions
├── WASTE_MANAGEMENT.ipynb      # Training notebook
├── SETUP_GMAIL.md             # Email setup guide
├── README.md                   # Project documentation
├── static/
│   ├── css/
│   │   └── style.css          # Beautiful UI styles
│   └── uploads/               # Uploaded waste images
└── templates/
    ├── index.html             # Home page (report form)
    ├── result.html            # Results page (with email status)
    └── dashboard.html         # Analytics dashboard
```

---

## 🎯 Features in Detail

### Waste Classification
- **Input:** JPG, PNG, JPEG images
- **Output:** 
  - Waste category (cardboard, glass, metal, paper, plastic, trash)
  - Waste type (Degradable/Non-Degradable/Mixed)
  - Reward points earned
  - Google Maps location

### Email Reports Include:
✅ Waste classification details  
✅ Location coordinates with Maps link  
✅ Reward points breakdown  
✅ Organizations notified count  
✅ Formatted HTML email  
✅ Report timestamp  

### Organization Notifications:
- Sent to nearby waste management centers
- Location with Google Maps link
- Urgent priority marking
- Direct action link

### Dashboard Features:
- Total reports submitted
- Total rewards earned
- Waste category breakdown (chart)
- Recent reports table
- Reporter information
- Collection status

---

## 🔐 System Architecture

### Frontend:
- Beautiful gradient UI
- Drag-and-drop file upload
- GPS location integration
- Responsive design

### Backend:
- Flask web framework
- Python-based processing
- JSON data storage
- SMTP email service

### AI Models:
- Support for TensorFlow models
- Mock predictions (if TensorFlow unavailable)
- Extensible for custom models

### Database:
- JSON file-based storage (`waste_reports.json`)
- Rewards tracking per user
- Report history

---

## 📊 Example Workflow

1. **User Reports Waste:**
   ```
   Name: Arun
   Email: arun@gmail.com
   Location: 13.0827°N, 80.2707°E
   Image: plastic_bottle.jpg
   ```

2. **System Processes:**
   ```
   ✅ Image uploaded
   🤖 AI classifies: PLASTIC
   📊 Type: Non-Degradable
   🎁 Points: +20
   📍 Location identified
   ```

3. **Email Sent to User:**
   ```
   From: your-configured-gmail@gmail.com
   To: arun@gmail.com
   Subject: 🗑️ Waste Report Confirmation - PLASTIC
   
   Includes:
   - Classification details
   - Location on Google Maps
   - Reward points
   - Organization notifications status
   ```

4. **Organizations Notified:**
   ```
   - City Waste Management
   - GreenCycle Solutions
   - EcoClean Services
   
   Email: Alert with location coordinates
   ```

5. **Dashboard Updated:**
   ```
   - Report added to history
   - Rewards incremented
   - Statistics updated
   ```

---

## ⚙️ Technical Specifications

### Supported Image Formats:
- JPG/JPEG
- PNG

### Max File Size:
- Limited by Flask (default: 16MB)

### Processing Speed:
- < 2 seconds per image (demo mode)

### Email Delivery:
- Gmail SMTP (SSL/TLS)
- Instant delivery (usually < 30 seconds)

### Location Accuracy:
- Browser GPS: ±10-50 meters
- Manual input: As provided

---

## 🛠️ Running the Application

### Start the Server:
```powershell
cd "c:\Users\aruld\Downloads\waste-classification-main\waste-classification-main"
python app.py
```

### Stop the Server:
```
Press Ctrl+C in terminal
```

### Access Points:
- **Home:** http://127.0.0.1:5000/
- **Dashboard:** http://127.0.0.1:5000/dashboard
- **API - Reports:** http://127.0.0.1:5000/api/reports
- **API - User Rewards:** http://127.0.0.1:5000/api/user-rewards/username

---

## 📱 Mobile Compatibility

✅ Responsive design works on:
- Desktop computers
- Tablets
- Mobile phones

✅ Location access works on:
- Chrome/Chromium
- Firefox
- Safari
- Edge

---

## 🔄 Data Storage

### Reports Saved In:
`waste_reports.json`

**Sample Entry:**
```json
{
  "user_name": "Arun",
  "user_email": "arun@gmail.com",
  "latitude": "13.0827",
  "longitude": "80.2707",
  "waste_category": "plastic",
  "waste_type": "Non-Degradable",
  "reward_points": 20,
  "organizations_notified": 3,
  "timestamp": "2026-01-31 15:45:30.123456",
  "image_path": "static/uploads/waste_image.jpg",
  "email_status": "success"
}
```

---

## 🚀 Future Enhancements

1. **IoT Integration:**
   - Smart bin sensors
   - Real-time waste levels
   - Automatic collection alerts

2. **Advanced ML Models:**
   - Multi-class waste detection
   - Confidence scoring
   - Custom model training

3. **Mobile App:**
   - Native iOS/Android
   - Offline mode
   - Push notifications

4. **Blockchain:**
   - Reward token system
   - Transparent tracking
   - Reward redemption

5. **Payment Integration:**
   - Reward points marketplace
   - Vendor partnerships
   - Direct payouts

---

## 📞 Support

### Common Issues:

**Q: Emails not sending?**
A: Check Gmail configuration in `utils.py`. See `SETUP_GMAIL.md`

**Q: Location not updating?**
A: Allow browser access to GPS. Refresh page and retry.

**Q: Images not processing?**
A: Check file format (JPG/PNG) and size (< 16MB)

**Q: Dashboard shows no reports?**
A: Submit at least one waste report first.

---

## 📄 License

This project implements a **Smart Waste Management System** as per the project abstract.

**Abstract Summary:**
- ✅ AI-based waste classification (degradable/non-degradable)
- ✅ Real-time waste reporting system
- ✅ Location-based services
- ✅ Automated notifications to waste management orgs
- ✅ Reward-based incentive mechanism
- ✅ Real-time status tracking
- ✅ Community participation model
- ✅ Smart city initiative

---

## 🎉 You're All Set!

1. **Configure Gmail:** Edit `utils.py` with your credentials
2. **Start Server:** `python app.py`
3. **Access App:** http://127.0.0.1:5000/
4. **Report Waste:** Upload images and get instant results
5. **Check Email:** Receive detailed notifications
6. **View Dashboard:** Track all submissions

**Happy Waste Management! 🌍♻️**
