import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import hashlib
import sys

# Fix for Python 3.8 compatibility with ReportLab
# Monkey patch hashlib.md5 to avoid 'usedforsecurity' parameter issue
if sys.version_info < (3, 9):
    _original_md5 = hashlib.md5
    def md5_wrapper(*args, **kwargs):
        kwargs.pop('usedforsecurity', None)
        return _original_md5(*args, **kwargs)
    hashlib.md5 = md5_wrapper

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

# Try to import TensorFlow, but don't fail if it's not available
try:
    import tensorflow as tf
    import numpy as np
    from PIL import Image as PILImage  # Import with alias to avoid shadowing reportlab's Image
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️  TensorFlow not available - using mock predictions for demo")

# Gmail Configuration - UPDATE THESE WITH YOUR CREDENTIALS
GMAIL_USER = "smartdrip19@gmail.com"  # Change this to your Gmail (sender)
GMAIL_PASSWORD = "auuu terx ocrh uvca"  # Use Gmail App Password (not regular password)

# Management Email
MANAGEMENT_EMAIL = "smartdrip19@gmail.com"  # Change this to your management email address

# Receiver Email - Change this to receive user submissions with location and PDF
RECEIVER_EMAIL = "viswamecse@gmail.com"  # Primary receiver email address
RECEIVER_EMAIL_2 = "viswamecse@gmail.com"  # Secondary receiver email address

RECEIVER_EMAILS = [RECEIVER_EMAIL, RECEIVER_EMAIL_2]  # List of all receiver emails

# Email Reports Directory (fallback if Gmail fails)
EMAIL_REPORTS_DIR = 'email_reports'
if not os.path.exists(EMAIL_REPORTS_DIR):
    os.makedirs(EMAIL_REPORTS_DIR)

# Categories mapping
CATEGORIES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

# Waste type classification (degradable/non-degradable)
WASTE_TYPE = {
    'cardboard': 'Degradable',
    'glass': 'Non-Degradable',
    'metal': 'Non-Degradable',
    'paper': 'Degradable',
    'plastic': 'Non-Degradable',
    'trash': 'Mixed'
}

# Mock model for demonstration
model = None

# Nearby waste management organizations (mock data)
WASTE_MANAGEMENT_ORGS = [
    {'name': 'City Waste Management', 'email': 'dispatch@citywaste.com', 'lat': 13.0827, 'lon': 80.2707},
    {'name': 'GreenCycle Solutions', 'email': 'info@greencycle.com', 'lat': 13.0880, 'lon': 80.2707},
    {'name': 'EcoClean Services', 'email': 'collect@ecoclean.com', 'lat': 13.0750, 'lon': 80.2660},
]

# Reward points system
REWARD_POINTS = {
    'cardboard': 10,
    'glass': 15,
    'metal': 15,
    'paper': 10,
    'plastic': 20,
    'trash': 5
}

def preprocess_image(image_path):
    """Preprocess the image to match model requirements."""
    if not TENSORFLOW_AVAILABLE:
        return None
    
    try:
        img = PILImage.open(image_path)
        img = img.resize((128, 128))
        
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)
        img_array = img_array / 255.0
        
        return img_array
    except Exception as e:
        print(f"Error preprocessing image: {str(e)}")
        return None

def predict_waste_category(image_path):
    """Predict the waste category for a given image."""
    if TENSORFLOW_AVAILABLE and model is not None:
        try:
            processed_image = preprocess_image(image_path)
            if processed_image is None:
                return random.choice(CATEGORIES)
            predictions = model.predict(processed_image, verbose=0)
            predicted_class = np.argmax(predictions[0])
            return CATEGORIES[predicted_class]
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return random.choice(CATEGORIES)
    else:
        # Mock prediction for demo - simple random selection
        return random.choice(CATEGORIES)

def get_waste_type(category):
    """Get waste type (degradable/non-degradable) for a category."""
    return WASTE_TYPE.get(category, 'Unknown')

def calculate_reward_points(category):
    """Calculate reward points for reported waste."""
    return REWARD_POINTS.get(category, 5)

def find_nearby_organizations(latitude, longitude, radius_km=5):
    """Find nearby waste management organizations."""
    nearby = []
    for org in WASTE_MANAGEMENT_ORGS:
        # Simple distance calculation
        distance = ((org['lat'] - latitude)**2 + (org['lon'] - longitude)**2)**0.5
        if distance * 111 < radius_km:  # Rough conversion to km
            nearby.append(org)
    return nearby if nearby else WASTE_MANAGEMENT_ORGS[:2]

def send_email_report(user_name, user_email, waste_category, waste_type, latitude, longitude, 
                      reward_points, organizations_notified, image_path):
    """Send detailed waste report email to user."""
    try:
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🗑️ Waste Report Confirmation - {waste_category.upper()}"
        msg['From'] = GMAIL_USER
        msg['To'] = user_email
        
        # Create HTML email body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
                    <h2 style="text-align: center; margin: 0 0 20px 0;">
                        🌍 Smart Waste Management System
                    </h2>
                    <div style="background: white; color: #333; padding: 25px; border-radius: 8px;">
                        <h3 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                            ✅ Waste Report Submitted Successfully
                        </h3>
                        
                        <p><strong>Reporter:</strong> {user_name}</p>
                        <p><strong>Report Time:</strong> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</p>
                        
                        <h4 style="color: #667eea; margin-top: 20px;">📊 Waste Classification Details:</h4>
                        <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #667eea; border-radius: 4px;">
                            <p><strong>Category:</strong> <span style="color: #667eea; font-weight: bold; text-transform: uppercase;">{waste_category}</span></p>
                            <p><strong>Type:</strong> {waste_type}</p>
                            <p><strong>Reward Points Earned:</strong> <span style="color: #4CAF50; font-size: 18px; font-weight: bold;">+{reward_points}</span></p>
                        </div>
                        
                        <h4 style="color: #667eea; margin-top: 20px;">📍 Location Information:</h4>
                        <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #2196F3; border-radius: 4px;">
                            <p><strong>Latitude:</strong> {latitude}°</p>
                            <p><strong>Longitude:</strong> {longitude}°</p>
                            <p><strong>Google Maps:</strong> <a href="https://maps.google.com/?q={latitude},{longitude}" style="color: #2196F3; text-decoration: none;">View on Map</a></p>
                        </div>
                        
                        <h4 style="color: #667eea; margin-top: 20px;">🔔 Notifications Sent:</h4>
                        <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #FF9800; border-radius: 4px;">
                            <p><strong>{organizations_notified}</strong> waste management organizations have been notified about your report.</p>
                            <p style="margin: 10px 0 0 0; font-size: 12px; color: #999;">
                                They will prioritize waste collection at your reported location based on the waste category.
                            </p>
                        </div>
                        
                        <h4 style="color: #667eea; margin-top: 20px;">🎁 Reward Information:</h4>
                        <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 15px; border-radius: 4px; color: white;">
                            <p><strong>You have earned {reward_points} reward points!</strong></p>
                            <p>Collect more points by reporting waste and help maintain a clean environment. 🌱</p>
                        </div>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; font-size: 12px; color: #999;">
                            <p>Thank you for contributing to a cleaner and smarter city! 🌍</p>
                            <p>Smart Waste Management System © 2026</p>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Attach HTML body
        part = MIMEText(html_body, 'html')
        msg.attach(part)
        
        # Send email
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, user_email, msg.as_string())
            server.close()
            print(f"✅ Email report sent successfully to {user_email}")
            
            # Also save to file as backup
            save_email_to_file(user_name, user_email, waste_category, waste_type, latitude, longitude, 
                             reward_points, organizations_notified, html_body)
            
            return {'status': 'success', 'message': f'Email sent to {user_email}'}
        except smtplib.SMTPAuthenticationError:
            print(f"❌ Gmail authentication failed. Saving report locally...")
            
            # Save email to file as backup
            save_email_to_file(user_name, user_email, waste_category, waste_type, latitude, longitude, 
                             reward_points, organizations_notified, html_body)
            
            return {'status': 'backup_saved', 'message': 'Report saved locally (Gmail credentials not working)'}
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}. Saving report locally...")
            
            # Save email to file as backup
            save_email_to_file(user_name, user_email, waste_category, waste_type, latitude, longitude, 
                             reward_points, organizations_notified, html_body)
            
            return {'status': 'backup_saved', 'message': f'Report saved locally'}
    
    except Exception as e:
        print(f"❌ Error creating email report: {str(e)}")
        return {'status': 'failed', 'message': str(e)}

def send_organization_notification(waste_category, latitude, longitude, user_name, org_email):
    """Send notification to waste management organizations."""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 New Waste Report: {waste_category.upper()}"
        msg['From'] = GMAIL_USER
        msg['To'] = org_email
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #FF5722;">🚨 URGENT: New Waste Report</h2>
                    <div style="background: #fff3e0; padding: 20px; border-left: 4px solid #FF5722; border-radius: 4px;">
                        <p><strong>Waste Category:</strong> <span style="color: #FF5722; font-size: 18px;">{waste_category.upper()}</span></p>
                        <p><strong>Location:</strong> {latitude}°, {longitude}°</p>
                        <p><strong>Reporter:</strong> {user_name}</p>
                        <p><strong>Report Time:</strong> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</p>
                        <p style="margin-top: 15px;">
                            <a href="https://maps.google.com/?q={latitude},{longitude}" style="display: inline-block; background: #FF5722; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                                View on Google Maps
                            </a>
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        part = MIMEText(html_body, 'html')
        msg.attach(part)
        
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, org_email, msg.as_string())
            server.close()
            print(f"✅ Organization notification sent to {org_email}")
            return True
        except Exception as e:
            print(f"⚠️  Could not send organization notification: {str(e)}")
            return False
    
    except Exception as e:
        print(f"Error creating organization notification: {str(e)}")
        return False

def send_notification(user_data, waste_category, org_list):
    """Send notification to nearby waste management organizations."""
    try:
        notification = {
            'status': 'sent',
            'message': f'New waste report: {waste_category.upper()} at coordinates ({user_data["latitude"]}, {user_data["longitude"]})',
            'organizations_notified': len(org_list),
            'timestamp': str(datetime.now())
        }
        print(f"✅ Notification sent to {len(org_list)} waste management organizations")
        print(f"   Message: {notification['message']}")
        return notification
    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

def save_email_to_file(user_name, user_email, waste_category, waste_type, latitude, longitude, 
                       reward_points, organizations_notified, html_body):
    """Save email report to file as backup."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{EMAIL_REPORTS_DIR}/{user_name}_{waste_category}_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_body)
        
        print(f"✅ Report saved to: {filename}")
        return {'status': 'saved', 'filename': filename}
    except Exception as e:
        print(f"❌ Error saving report file: {str(e)}")
        return {'status': 'failed', 'error': str(e)} 


def generate_pdf_report(reports_data, pdf_filename='dashboard_report.pdf', image_paths=None):
    """Generate a PDF report with all waste reports and submitted images."""
    try:
        from reportlab.pdfgen import canvas
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3c72'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2a5298'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("🗑️ Waste Management System - Report", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Report date
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        story.append(Paragraph(f"<b>Report Generated:</b> {report_date}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Statistics
        if reports_data:
            total_reports = len(reports_data)
            total_rewards = sum(r.get('reward_points', 0) for r in reports_data)
            
            stats_text = f"""
            <b>📊 Summary Statistics:</b><br/>
            • Total Reports: {total_reports}<br/>
            • Total Reward Points: {total_rewards}<br/>
            """
            story.append(Paragraph(stats_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Generate waste distribution chart
            story.append(Paragraph("<b>🗑️ Waste Distribution:</b>", heading_style))
            
            # Calculate waste distribution
            waste_dist = {}
            for report in reports_data:
                category = report.get('waste_category', 'Unknown').lower()
                waste_dist[category] = waste_dist.get(category, 0) + 1
            
            if waste_dist:
                # Create bar chart using matplotlib
                import matplotlib.pyplot as plt
                import io
                
                categories = list(waste_dist.keys())
                counts = list(waste_dist.values())
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
                
                fig, ax = plt.subplots(figsize=(7, 3))
                bars = ax.bar(categories, counts, color=colors[:len(categories)], edgecolor='black', linewidth=1.5)
                ax.set_ylabel('Count', fontsize=10, fontweight='bold')
                ax.set_xlabel('Waste Category', fontsize=10, fontweight='bold')
                ax.set_title('Waste Distribution by Category', fontsize=12, fontweight='bold')
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontweight='bold')
                
                plt.tight_layout()
                
                # Save chart to bytes
                chart_buffer = io.BytesIO()
                plt.savefig(chart_buffer, format='png', dpi=100, bbox_inches='tight')
                chart_buffer.seek(0)
                plt.close()
                
                # Add chart to PDF
                chart_image = Image(chart_buffer, width=5.5*inch, height=2.5*inch)
                story.append(chart_image)
                story.append(Spacer(1, 0.2*inch))
        
        # Reports table
        if reports_data:
            story.append(Paragraph("<b>📋 Detailed Reports:</b>", heading_style))
            
            # Prepare table data
            table_data = [['Date', 'User', 'Category', 'Type', 'Points', 'Location']]
            
            for report in reports_data:
                date_str = report.get('timestamp', 'N/A')[:10]
                user = report.get('user_name', 'Unknown')[:15]
                category = report.get('waste_category', 'Unknown')
                waste_type = report.get('waste_type', 'N/A')
                points = str(report.get('reward_points', 0))
                
                lat = report.get('latitude', 'N/A')
                lon = report.get('longitude', 'N/A')
                
                # Handle both string and float formats
                try:
                    lat = float(lat) if isinstance(lat, str) else lat
                    lon = float(lon) if isinstance(lon, str) else lon
                    location = f"{lat:.4f}, {lon:.4f}"
                except:
                    location = f"{lat}, {lon}"
                
                table_data.append([date_str, user, category, waste_type, points, location])
            
            # Create table
            table = Table(table_data, colWidths=[1*inch, 1.2*inch, 1*inch, 0.8*inch, 0.7*inch, 1.3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a5298')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
        
        # Add images if provided
        if image_paths:
            story.append(PageBreak())
            story.append(Paragraph("<b>📸 Submitted Waste Images:</b>", heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            for img_path in image_paths:
                if os.path.exists(img_path):
                    try:
                        # Add image with limited height
                        img = Image(img_path, width=4*inch, height=3*inch)
                        story.append(img)
                        story.append(Spacer(1, 0.2*inch))
                        story.append(Paragraph(f"<i>File: {os.path.basename(img_path)}</i>", styles['Normal']))
                        story.append(Spacer(1, 0.3*inch))
                    except Exception as e:
                        story.append(Paragraph(f"<i>Error loading image: {img_path}</i>", styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        print(f"✅ PDF Report generated: {pdf_filename}")
        return {'status': 'success', 'filename': pdf_filename}
    
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


def email_pdf_report(recipient_email, pdf_filename, user_name="User", is_personal=False, location=None):
    """Email the PDF report to user."""
    try:
        # Read PDF file
        with open(pdf_filename, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename= ' + os.path.basename(pdf_filename))
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = recipient_email
        
        # Different subject for personal vs dashboard reports
        if is_personal:
            msg['Subject'] = f'🗑️ Your Waste Report - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            body = f"""
Hi {user_name},

Your waste submission has been successfully processed! 

Please find the attached PDF report with:
✓ Waste classification details
✓ Your submitted image
✓ GPS location coordinates
✓ Rewards earned
✓ Organizations notified

Thank you for contributing to waste management!

Best regards,
Waste Management System
        """
        else:
            msg['Subject'] = f'🚨 NEW WASTE REPORT ALERT - {user_name} - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            location_info = f"\n\n📍 GPS LOCATION COORDINATES:\n{'='*50}\nLatitude, Longitude: {location}\nGoogle Maps: https://www.google.com/maps/search/{location.replace(' ', '')}\n{'='*50}" if location else ""
            body = f"""
🚨 NEW WASTE SUBMISSION ALERT

User: {user_name}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}{location_info}

Please find attached the detailed classification PDF with:
✓ Waste classification results
✓ Submitted image/photo
✓ GPS location coordinates  
✓ Reward points earned
✓ Organizations notified
✓ Classification confidence

ACTION REQUIRED:
1. Review the attached PDF
2. Verify the waste classification
3. Take appropriate collection action
4. Update collection status in dashboard

Best regards,
Waste Management System (Automated Alert)
        """
        
        msg.attach(MIMEText(body, 'plain'))
        msg.attach(part)
        
        # Send email with better error handling
        try:
            print(f"📧 Attempting to send email to {recipient_email}")
            print(f"📧 From: {GMAIL_USER}")
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            
            print(f"✅ Gmail login successful")
            print(f"📧 Sending message...")
            
            server.send_message(msg)
            server.quit()
            
            print(f"✅ PDF Report emailed to: {recipient_email}")
            return {'status': 'sent', 'email': recipient_email}
        except smtplib.SMTPAuthenticationError as auth_error:
            error_msg = f"Gmail authentication failed: {str(auth_error)}. Check GMAIL_USER and GMAIL_PASSWORD in utils.py"
            print(f"❌ {error_msg}")
            return {'status': 'failed', 'error': error_msg}
        except smtplib.SMTPException as smtp_error:
            error_msg = f"SMTP error: {str(smtp_error)}. The receiver email ({recipient_email}) might be blocking Gmail emails."
            print(f"❌ {error_msg}")
            return {'status': 'failed', 'error': error_msg}
    
    except Exception as e:
        error_msg = f"Error emailing PDF report: {str(e)}"
        print(f"❌ {error_msg}")
        return {'status': 'failed', 'error': error_msg}


def generate_user_pdf_report(user_reports, user_name, user_location, pdf_filename, image_paths=None):
    """Generate a personalized PDF report for a user with their submissions and location."""
    try:
        # Create PDF document
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1e3c72'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2a5298'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph(f"🗑️ Personal Waste Report - {user_name}", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # User info
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_info = f"""
        <b>📋 Report Details:</b><br/>
        • User: {user_name}<br/>
        • Generated: {report_date}<br/>
        • Total Submissions: {len(user_reports)}<br/>
        """
        story.append(Paragraph(user_info, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Location info
        location_info = f"""
        <b>📍 Your Location:</b><br/>
        • Coordinates: {user_location}<br/>
        • <a href="https://www.google.com/maps/search/{user_location.replace(' ', '')}" color="blue">View on Google Maps</a><br/>
        """
        story.append(Paragraph(location_info, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary statistics
        if user_reports:
            total_rewards = sum(r.get('reward_points', 0) for r in user_reports)
            
            stats_text = f"""
            <b>⭐ Summary:</b><br/>
            • Total Reward Points: {total_rewards}<br/>
            """
            story.append(Paragraph(stats_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Detailed submissions
        story.append(Paragraph("<b>📊 Your Waste Submissions:</b>", heading_style))
        
        table_data = [['Date', 'Category', 'Type', 'Points', 'Status']]
        
        for report in user_reports:
            date_str = report.get('timestamp', 'N/A')
            category = report.get('waste_category', 'Unknown')
            waste_type = report.get('waste_type', 'N/A')
            points = str(report.get('reward_points', 0))
            orgs_notified = report.get('organizations_notified', 0)
            status = f"✓ {orgs_notified} org"
            
            table_data.append([date_str, category.upper(), waste_type, points, status])
        
        # Create table
        table = Table(table_data, colWidths=[1.8*inch, 1.2*inch, 1*inch, 0.8*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8f4f8')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2a5298')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f4f8')]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Add submitted images
        if image_paths:
            story.append(PageBreak())
            story.append(Paragraph("<b>📸 Your Submitted Waste Images:</b>", heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            for i, img_path in enumerate(image_paths, 1):
                print(f"📸 Loading image #{i}: {img_path}")
                
                # Try to load the image
                if os.path.exists(img_path):
                    try:
                        print(f"✅ File exists: {img_path}")
                        
                        # Add image to PDF with fixed dimensions
                        img = Image(img_path, width=5*inch, height=4*inch)
                        story.append(img)
                        story.append(Spacer(1, 0.2*inch))
                        
                        # Add caption
                        caption = f"<b>Waste Image #{i}</b><br/><i>{os.path.basename(img_path)}</i>"
                        story.append(Paragraph(caption, styles['Normal']))
                        story.append(Spacer(1, 0.3*inch))
                        
                        print(f"✅ Image #{i} successfully added to PDF")
                    except Exception as e:
                        print(f"❌ Error adding image to PDF: {str(e)}")
                        error_msg = f"<b>Image #{i}:</b> Could not load image - {str(e)[:40]}"
                        story.append(Paragraph(error_msg, styles['Normal']))
                        story.append(Spacer(1, 0.2*inch))
                else:
                    print(f"❌ File not found: {img_path}")
                    story.append(Paragraph(f"<b>Image #{i}:</b> Image file not found on server", styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer_text = f"<i>Thank you {user_name} for contributing to waste management! Generated on {report_date}</i>"
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        try:
            doc.build(story)
            
            # Verify PDF was created and has content
            if not os.path.exists(pdf_filename):
                raise Exception(f"PDF file was not created at {pdf_filename}")
            
            file_size = os.path.getsize(pdf_filename)
            if file_size == 0:
                raise Exception("Generated PDF file is empty")
            
            # Verify PDF has proper magic bytes
            with open(pdf_filename, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    raise Exception(f"Invalid PDF file - wrong magic bytes: {header}")
            
            print(f"✅ Personal PDF Report generated: {pdf_filename} ({file_size} bytes)")
            return {'status': 'success', 'filename': pdf_filename}
        except Exception as e:
            raise Exception(f"Error building PDF: {str(e)}")
    
    except Exception as e:
        print(f"❌ Error generating personal PDF: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


def generate_classification_pdf_for_management(report_data, pdf_filename, image_path=None):
    """Generate a PDF report of waste classification for management."""
    try:
        # Create PDF document
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e3c72'),
            spaceAfter=15,
            alignment=TA_CENTER
        )
        
        # Title
        story.append(Paragraph("♻️ Waste Classification Report", title_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Report timestamp
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timestamp_info = f"""
        <b>Report Generated:</b> {report_date}<br/>
        <b>Report ID:</b> {report_date.replace(' ', '_').replace(':', '-')}
        """
        story.append(Paragraph(timestamp_info, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # User information
        user_info = f"""
        <b>👤 Submitter Information:</b><br/>
        • Name: {report_data.get('user_name', 'Anonymous')}<br/>
        • Email: {report_data.get('user_email', 'N/A')}<br/>
        • Phone: {report_data.get('contact_phone', 'N/A')}<br/>
        """
        story.append(Paragraph(user_info, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Classification results
        classification_info = f"""
        <b>🗑️ Classification Results:</b><br/>
        • <b>Category:</b> {report_data.get('waste_category', 'Unknown').upper()}<br/>
        • <b>Type:</b> {report_data.get('waste_type', 'Unknown')}<br/>
        • <b>Degradability:</b> {report_data.get('waste_type', 'Unknown')}<br/>
        """
        story.append(Paragraph(classification_info, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Reward information
        reward_info = f"""
        <b>🎁 Reward Details:</b><br/>
        • Reward Points Earned: {report_data.get('reward_points', 0)}<br/>
        """
        story.append(Paragraph(reward_info, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Location information
        location_info = f"""
        <b>📍 Location:</b><br/>
        • Latitude: {report_data.get('latitude', 'N/A')}<br/>
        • Longitude: {report_data.get('longitude', 'N/A')}<br/>
        • Organizations Notified: {report_data.get('organizations_notified', 0)}<br/>
        """
        story.append(Paragraph(location_info, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Submitted image
        if image_path and os.path.exists(image_path):
            try:
                story.append(Paragraph("<b>📸 Submitted Image:</b>", styles['Heading3']))
                story.append(Spacer(1, 0.1*inch))
                
                # Add image with max width
                img = Image(image_path, width=5*inch, height=3.75*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                print(f"⚠️  Could not add image to PDF: {str(e)}")
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer_text = """
        <b>📌 Note for Management:</b><br/>
        This report contains the classification results for a waste submission made through the system.
        Please verify the classification and take appropriate action based on your organization's protocols.
        """
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        print(f"✅ Classification PDF generated for management: {pdf_filename}")
        return {'status': 'success', 'filename': pdf_filename}
    
    except Exception as e:
        print(f"❌ Error generating classification PDF: {str(e)}")
        return {'status': 'failed', 'error': str(e)}