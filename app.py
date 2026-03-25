from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from utils import (preprocess_image, predict_waste_category, get_waste_type,
                   calculate_reward_points, find_nearby_organizations, send_notification,
                   send_email_report, send_organization_notification, generate_pdf_report, email_pdf_report,
                   generate_classification_pdf_for_management, MANAGEMENT_EMAIL, RECEIVER_EMAIL, RECEIVER_EMAIL_2, RECEIVER_EMAILS)

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database file for storing reports
REPORTS_FILE = 'waste_reports.json'

# Database file for storing management collections
COLLECTIONS_FILE = 'waste_collections.json'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_video_file(filename):
    """Check if file is a video."""
    video_extensions = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in video_extensions

def extract_frame_from_video(video_path, output_image_path):
    """Extract the first frame from a video file."""
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            cv2.imwrite(output_image_path, frame)
            print(f"✅ Frame extracted from video: {output_image_path}")
            return True
        else:
            print(f"❌ Could not extract frame from video: {video_path}")
            return False
    except ImportError:
        print("⚠️  OpenCV not available. Cannot process video files.")
        return False
    except Exception as e:
        print(f"❌ Error extracting frame from video: {str(e)}")
        return False

def save_report(report_data):
    """Save waste report to file."""
    reports = []
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, 'r') as f:
            reports = json.load(f)
    
    reports.append(report_data)
    
    with open(REPORTS_FILE, 'w') as f:
        json.dump(reports, f, indent=2)

def get_user_rewards(user_name):
    """Get total rewards for a user."""
    if not os.path.exists(REPORTS_FILE):
        return 0
    
    total_rewards = 0
    with open(REPORTS_FILE, 'r') as f:
        reports = json.load(f)
        for report in reports:
            if report.get('user_name') == user_name:
                total_rewards += report.get('reward_points', 0)
    
    return total_rewards

def save_collection(collection_data):
    """Save waste collection from management to file."""
    collections = []
    if os.path.exists(COLLECTIONS_FILE):
        with open(COLLECTIONS_FILE, 'r') as f:
            collections = json.load(f)
    
    collections.append(collection_data)
    
    with open(COLLECTIONS_FILE, 'w') as f:
        json.dump(collections, f, indent=2)

def get_all_collections():
    """Get all waste collections from management."""
    if not os.path.exists(COLLECTIONS_FILE):
        return []
    
    with open(COLLECTIONS_FILE, 'r') as f:
        collections = json.load(f)
    
    return collections

def mark_waste_as_collected(report_index, management_name):
    """Mark a waste report as collected by management."""
    if not os.path.exists(REPORTS_FILE):
        return False
    
    with open(REPORTS_FILE, 'r') as f:
        reports = json.load(f)
    
    if 0 <= report_index < len(reports):
        reports[report_index]['collected'] = True
        reports[report_index]['collection_date'] = str(datetime.now())
        reports[report_index]['collected_by'] = management_name
        reports[report_index]['status'] = 'collected'
        
        with open(REPORTS_FILE, 'w') as f:
            json.dump(reports, f, indent=2)
        
        print(f"✅ Waste report marked as collected by {management_name}")
        return True
    
    return False

def get_uncollected_waste():
    """Get all uncollected waste reports."""
    if not os.path.exists(REPORTS_FILE):
        return []
    
    with open(REPORTS_FILE, 'r') as f:
        reports = json.load(f)
    
    uncollected = [r for r in reports if not r.get('collected', False)]
    return uncollected

def get_collected_waste():
    """Get all collected waste reports."""
    if not os.path.exists(REPORTS_FILE):
        return []
    
    with open(REPORTS_FILE, 'r') as f:
        reports = json.load(f)
    
    collected = [r for r in reports if r.get('collected', False)]
    return collected

@app.route('/')
def landing():
    """Landing page with user and management portal options."""
    return render_template('landing.html')

@app.route('/home')
def home():
    """User portal - waste reporting page."""
    return render_template('index.html')

@app.route('/management-dashboard')
def management_dashboard():
    """Management portal - view all user submissions."""
    if not os.path.exists(REPORTS_FILE):
        reports = []
        stats = {'total_reports': 0, 'waste_categories': {}, 'collected_count': 0, 'pending_count': 0}
    else:
        with open(REPORTS_FILE, 'r') as f:
            reports = json.load(f)
        
        waste_categories = {}
        collected_count = 0
        pending_count = 0
        
        for report in reports:
            cat = report.get('waste_category', 'unknown')
            waste_categories[cat] = waste_categories.get(cat, 0) + 1
            if report.get('collected', False):
                collected_count += 1
            else:
                pending_count += 1
        
        stats = {
            'total_reports': len(reports),
            'waste_categories': waste_categories,
            'collected_count': collected_count,
            'pending_count': pending_count
        }
    
    # Get collections from management
    collections = get_all_collections()
    
    return render_template('management_dashboard.html', 
                         reports=reports, 
                         stats=stats,
                         collections=collections,
                         total_collections=len(collections))

@app.route('/submission/<int:submission_id>')
def view_submission(submission_id):
    """View detailed submission for both user and management."""
    if not os.path.exists(REPORTS_FILE):
        return "No submissions found", 404
    
    with open(REPORTS_FILE, 'r') as f:
        reports = json.load(f)
    
    if submission_id < 0 or submission_id >= len(reports):
        return "Submission not found", 404
    
    report = reports[submission_id]
    
    return render_template('submission_detail.html',
                         report=report,
                         image_path=report.get('image_path', ''),
                         submission_id=submission_id,
                         category=report.get('waste_category', 'Unknown'),
                         waste_type=report.get('waste_type', 'Unknown'),
                         reward_points=report.get('reward_points', 0),
                         user_name=report.get('user_name', 'Anonymous'),
                         user_email=report.get('user_email', 'N/A'),
                         latitude=report.get('latitude', 'N/A'),
                         longitude=report.get('longitude', 'N/A'),
                         timestamp=report.get('timestamp', 'N/A'),
                         collected=report.get('collected', False),
                         organizations_notified=report.get('organizations_notified', 0))

@app.route('/management')
def management():
    """Show management collection submission page."""
    return render_template('management.html')

@app.route('/waste-pickup')
def waste_pickup():
    """Show waste pickup tracking page for management."""
    uncollected = get_uncollected_waste()
    collected = get_collected_waste()
    
    return render_template('waste_pickup.html', 
                         uncollected=uncollected,
                         collected=collected,
                         uncollected_count=len(uncollected),
                         collected_count=len(collected))

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get user data from form
    user_name = request.form.get('user_name', 'Anonymous')
    user_email = request.form.get('user_email', '')
    latitude = request.form.get('latitude', '0.0')
    longitude = request.form.get('longitude', '0.0')
    
    if file and allowed_file(file.filename):
        # Save the uploaded file
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # If it's a video, extract a frame
        image_for_classification = filename
        if is_video_file(file.filename):
            frame_filename = os.path.join(app.config['UPLOAD_FOLDER'], 
                                        f"frame_{os.path.splitext(file.filename)[0]}.png")
            if extract_frame_from_video(filename, frame_filename):
                image_for_classification = frame_filename
            else:
                return jsonify({'error': 'Could not extract frame from video'}), 400
        
        try:
            # Predict waste category
            category = predict_waste_category(image_for_classification)
            waste_type = get_waste_type(category)
            reward_points = calculate_reward_points(category)
            
            # Find nearby organizations
            nearby_orgs = find_nearby_organizations(float(latitude), float(longitude))
            
            # Send notifications
            notification = send_notification({
                'user_name': user_name,
                'latitude': latitude,
                'longitude': longitude
            }, category, nearby_orgs)
            
            # Create report
            report = {
                'user_name': user_name,
                'user_email': user_email,
                'latitude': latitude,
                'longitude': longitude,
                'waste_category': category,
                'waste_type': waste_type,
                'reward_points': reward_points,
                'organizations_notified': len(nearby_orgs),
                'timestamp': str(datetime.now()),
                'image_filename': os.path.basename(filename),
                'image_path': os.path.abspath(filename),  # Use absolute path for reliability
                'status': 'submitted',
                'collected': False,
                'collection_date': None,
                'collected_by': None,
            }
            
            # Save report to JSON
            save_report(report)
            
            # Generate and send PDF report to user
            email_status = {'status': 'not_sent', 'message': 'No email'}
            if user_email:
                from utils import generate_user_pdf_report, email_pdf_report
                import tempfile
                
                # Generate PDF in temp directory
                temp_dir = tempfile.gettempdir()
                pdf_filename = f"waste_report_{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                pdf_path = os.path.join(temp_dir, pdf_filename)
                
                pdf_result = generate_user_pdf_report(
                    [report], 
                    user_name, 
                    f"{latitude}, {longitude}",
                    pdf_path,
                    [filename] if os.path.exists(filename) else []
                )
                
                if pdf_result['status'] == 'success':
                    # Email the PDF
                    email_result = email_pdf_report(user_email, pdf_path, user_name, is_personal=True)
                    email_status = email_result
                    print(f"📧 ✅ PDF Report emailed to user: {user_email}")
                else:
                    email_status = {'status': 'failed', 'message': pdf_result['error']}
                    print(f"📧 ❌ Error generating PDF for user: {pdf_result['error']}")
            
            # Send notifications to organizations
            for org in nearby_orgs:
                send_organization_notification(category, latitude, longitude, user_name, org['email'])
            
            # Generate and send classification PDF to management
            try:
                import tempfile
                temp_dir = tempfile.gettempdir()
                mgmt_pdf_filename = f"classification_{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                mgmt_pdf_path = os.path.join(temp_dir, mgmt_pdf_filename)
                
                mgmt_pdf_result = generate_classification_pdf_for_management(report, mgmt_pdf_path, filename)
                
                if mgmt_pdf_result['status'] == 'success':
                    # Email the classification PDF to management
                    mgmt_email_result = email_pdf_report(MANAGEMENT_EMAIL, mgmt_pdf_path, user_name, is_personal=False)
                    if mgmt_email_result['status'] == 'sent':
                        print(f"📧 ✅ New Report Alert with PDF sent to management: {MANAGEMENT_EMAIL}")
                    else:
                        print(f"📧 ❌ Failed to email to management: {mgmt_email_result['error']}")
                    
                    # Send to all receiver emails with location data
                    for receiver_email in RECEIVER_EMAILS:
                        if receiver_email and receiver_email.strip():
                            receiver_email_result = email_pdf_report(receiver_email, mgmt_pdf_path, user_name, is_personal=False, location=f"{latitude}, {longitude}")
                            if receiver_email_result['status'] == 'sent':
                                print(f"📧 ✅ Report with location data sent to receiver: {receiver_email}")
                            else:
                                print(f"📧 ❌ Failed to email to receiver {receiver_email}: {receiver_email_result['error']}")
                else:
                    print(f"📧 ❌ Error generating PDF for management: {mgmt_pdf_result['error']}")
            except Exception as e:
                print(f"📧 ❌ Error in management email: {str(e)}")
            
            # Get user total rewards
            total_rewards = get_user_rewards(user_name)
            
            return render_template('result.html', 
                                image_path=filename,
                                category=category,
                                waste_type=waste_type,
                                reward_points=reward_points,
                                total_rewards=total_rewards,
                                latitude=latitude,
                                longitude=longitude,
                                user_name=user_name,
                                user_email=user_email,
                                organizations_notified=len(nearby_orgs),
                                notification=notification['message'],
                                email_status=email_status['status'])
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/submit-collection', methods=['POST'])
def submit_collection():
    """Submit waste collection data from management."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['management_name', 'waste_type', 'quantity', 'location', 'contact_person']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create collection record
        collection = {
            'management_name': data.get('management_name'),
            'contact_person': data.get('contact_person'),
            'contact_phone': data.get('contact_phone', ''),
            'waste_type': data.get('waste_type'),
            'quantity': data.get('quantity'),
            'unit': data.get('unit', 'kg'),
            'location': data.get('location'),
            'latitude': data.get('latitude', '0.0'),
            'longitude': data.get('longitude', '0.0'),
            'notes': data.get('notes', ''),
            'timestamp': str(datetime.now()),
            'status': 'submitted'
        }
        
        # Save collection
        save_collection(collection)
        
        return jsonify({
            'status': 'success',
            'message': f'Waste collection from {data.get("management_name")} submitted successfully!',
            'collection': collection
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/collections', methods=['GET'])
def get_collections():
    """Get all waste collections from management."""
    collections = get_all_collections()
    return jsonify(collections)
def get_reports():
    """Get all waste reports."""
    if not os.path.exists(REPORTS_FILE):
        return jsonify([])
    
    with open(REPORTS_FILE, 'r') as f:
        reports = json.load(f)
    
    return jsonify(reports)

@app.route('/api/mark-collected', methods=['POST'])
def mark_collected():
    """Mark a waste report as collected."""
    try:
        data = request.json
        report_index = data.get('report_index')
        management_name = data.get('management_name', 'Unknown')
        
        if report_index is None:
            return jsonify({'error': 'Missing report_index'}), 400
        
        # Mark waste as collected
        success = mark_waste_as_collected(report_index, management_name)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Waste marked as collected by {management_name}'
            }), 200
        else:
            return jsonify({'error': 'Report not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/uncollected-waste', methods=['GET'])
def get_uncollected():
    """Get all uncollected waste."""
    uncollected = get_uncollected_waste()
    return jsonify(uncollected)

@app.route('/api/collected-waste', methods=['GET'])
def get_collected():
    """Get all collected waste."""
    collected = get_collected_waste()
    return jsonify(collected)

@app.route('/api/user-rewards/<user_name>', methods=['GET'])
def user_rewards(user_name):
    """Get user's total rewards."""
    total_rewards = get_user_rewards(user_name)
    return jsonify({'user_name': user_name, 'total_rewards': total_rewards})

@app.route('/dashboard')
def dashboard():
    """Show dashboard with reports and statistics."""
    if not os.path.exists(REPORTS_FILE):
        reports = []
        stats = {'total_reports': 0, 'total_rewards': 0, 'waste_categories': {}}
    else:
        with open(REPORTS_FILE, 'r') as f:
            reports = json.load(f)
        
        total_rewards = sum(r.get('reward_points', 0) for r in reports)
        waste_categories = {}
        for report in reports:
            cat = report.get('waste_category', 'unknown')
            waste_categories[cat] = waste_categories.get(cat, 0) + 1
        
        stats = {
            'total_reports': len(reports),
            'total_rewards': total_rewards,
            'waste_categories': waste_categories
        }
    
    # Get collections from management
    collections = get_all_collections()
    
    # Calculate collection statistics
    total_quantity = 0
    collection_types = {}
    for collection in collections:
        try:
            total_quantity += float(collection.get('quantity', 0))
        except:
            pass
        ctype = collection.get('waste_type', 'unknown')
        collection_types[ctype] = collection_types.get(ctype, 0) + 1
    
    return render_template('dashboard.html', 
                         reports=reports, 
                         stats=stats,
                         collections=collections,
                         total_collections=len(collections),
                         total_quantity=total_quantity,
                         collection_types=collection_types)


@app.route('/submission/<int:submission_id>/download-pdf')
def download_submission_pdf(submission_id):
    """Download PDF for a specific submission."""
    try:
        if not os.path.exists(REPORTS_FILE):
            return jsonify({'status': 'error', 'message': 'No reports found'}), 404
        
        with open(REPORTS_FILE, 'r') as f:
            reports = json.load(f)
        
        if submission_id < 0 or submission_id >= len(reports):
            return jsonify({'status': 'error', 'message': 'Submission not found'}), 404
        
        report = reports[submission_id]
        user_name = report.get('user_name', 'User').replace(' ', '_')
        user_email = report.get('user_email', '')
        latitude = report.get('latitude', '0')
        longitude = report.get('longitude', '0')
        
        # Get image path if it exists
        image_paths = []
        
        if 'image_path' in report:
            img_path = report['image_path']
            print(f"📸 Checking image_path: {img_path}")
            
            # Handle both absolute and relative paths
            if os.path.isabs(img_path):
                # Absolute path
                if os.path.exists(img_path):
                    image_paths.append(img_path)
                    print(f"✅ Found absolute path: {img_path}")
                else:
                    print(f"❌ Absolute path not found: {img_path}")
            else:
                # Relative path - try multiple variations
                if os.path.exists(img_path):
                    image_paths.append(img_path)
                    print(f"✅ Found relative path: {img_path}")
                else:
                    # Try converting to absolute path
                    abs_path = os.path.abspath(img_path)
                    if os.path.exists(abs_path):
                        image_paths.append(abs_path)
                        print(f"✅ Found as absolute: {abs_path}")
                    else:
                        print(f"❌ Could not find image at: {img_path}")
                        print(f"   Also tried: {abs_path}")
        
        elif 'image_filename' in report:
            # Fallback to searching in uploads folder
            img_path = os.path.join(UPLOAD_FOLDER, report['image_filename'])
            if os.path.exists(img_path):
                image_paths.append(img_path)
                print(f"✅ Found in uploads folder: {img_path}")
            else:
                print(f"❌ Image not found: {img_path}")
        
        # Generate personalized PDF in temp directory
        from utils import generate_user_pdf_report
        import tempfile
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"report_{user_name}_{submission_id}_{timestamp}.pdf"
        
        # Use a more reliable temporary file approach
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, pdf_filename)
        
        print(f"📝 Generating PDF at: {pdf_path}")
        
        result = generate_user_pdf_report([report], user_name, f"{latitude}, {longitude}", pdf_path, image_paths)
        
        if result['status'] != 'success':
            return jsonify({'status': 'error', 'message': result.get('error', 'Failed to generate PDF')}), 500
        
        # Check if file was created successfully
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not created at: {pdf_path}")
            return jsonify({'status': 'error', 'message': 'PDF file was not created'}), 500
        
        file_size = os.path.getsize(pdf_path)
        print(f"✅ PDF created successfully - Size: {file_size} bytes")
        
        if file_size == 0:
            return jsonify({'status': 'error', 'message': 'PDF file is empty'}), 500
        
        # Read file into memory and send as bytes to avoid file locking issues
        try:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_bytes = pdf_file.read()
            
            if len(pdf_bytes) == 0:
                return jsonify({'status': 'error', 'message': 'PDF file is empty'}), 500
            
            # Verify PDF magic bytes
            if not pdf_bytes.startswith(b'%PDF'):
                return jsonify({'status': 'error', 'message': 'Invalid PDF file - corrupted'}), 500
            
            print(f"✅ PDF verified - {len(pdf_bytes)} bytes")
            
            from io import BytesIO
            pdf_io = BytesIO(pdf_bytes)
            
            response = send_file(
                pdf_io,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=pdf_filename
            )
            
            # Add headers to prevent caching issues
            response.headers['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            return response
        except Exception as e:
            print(f"❌ Error reading/sending file: {str(e)}")
            return jsonify({'status': 'error', 'message': f'Error sending PDF: {str(e)}'}), 500
    
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500

@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    """Generate and download/email PDF report."""
    try:
        from utils import MANAGEMENT_EMAIL
        
        data = request.json
        action = data.get('action', 'download')  # 'download' or 'email'
        email_address = data.get('email', '')
        
        # Load all reports
        if not os.path.exists(REPORTS_FILE):
            return jsonify({'status': 'error', 'message': 'No reports found'}), 404
        
        with open(REPORTS_FILE, 'r') as f:
            reports = json.load(f)
        
        # Get all image paths from reports
        image_paths = []
        for report in reports:
            if 'image_filename' in report:
                img_path = os.path.join(UPLOAD_FOLDER, report['image_filename'])
                if os.path.exists(img_path):
                    image_paths.append(img_path)
        
        # Generate PDF
        pdf_filename = f"waste_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        result = generate_pdf_report(reports, pdf_filename, image_paths)
        
        if result['status'] != 'success':
            return jsonify({'status': 'error', 'message': result['error']}), 500
        
        if action == 'email' and email_address:
            # Handle management email specially
            if email_address == MANAGEMENT_EMAIL:
                user_name = "Waste Management"
                is_mgmt = True
            else:
                user_name = reports[0].get('user_name', 'User') if reports else 'User'
                is_mgmt = False
            
            # Email the PDF
            email_result = email_pdf_report(email_address, pdf_filename, user_name, is_personal=is_mgmt)
            
            if email_result['status'] == 'sent':
                return jsonify({'status': 'success', 'message': f'Report emailed to {email_address}'})
            else:
                return jsonify({'status': 'error', 'message': email_result['error']}), 500
        
        else:
            # Download the PDF
            return send_file(pdf_filename, as_attachment=True, 
                           download_name=os.path.basename(pdf_filename))
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/user-report', methods=['POST'])
def user_report():
    """Generate personalized user report with only their submissions."""
    try:
        data = request.json
        user_email = data.get('email', '')
        action = data.get('action', 'email')  # 'email' or 'download'
        
        if not user_email:
            return jsonify({'status': 'error', 'message': 'Email is required'}), 400
        
        # Load all reports and filter by user email
        if not os.path.exists(REPORTS_FILE):
            return jsonify({'status': 'error', 'message': 'No reports found'}), 404
        
        with open(REPORTS_FILE, 'r') as f:
            all_reports = json.load(f)
        
        # Filter reports for this user
        user_reports = [r for r in all_reports if r.get('user_email', '').lower() == user_email.lower()]
        
        if not user_reports:
            return jsonify({'status': 'error', 'message': f'No reports found for {user_email}'}), 404
        
        # Get user's image paths
        image_paths = []
        user_name = user_reports[0].get('user_name', 'User')
        user_location = f"{user_reports[0].get('latitude', 'N/A')}, {user_reports[0].get('longitude', 'N/A')}"
        
        for report in user_reports:
            # Try both image_filename and image_path fields
            if 'image_path' in report:
                img_path = report['image_path']
                if os.path.exists(img_path):
                    image_paths.append(img_path)
            elif 'image_filename' in report:
                img_path = os.path.join(UPLOAD_FOLDER, report['image_filename'])
                if os.path.exists(img_path):
                    image_paths.append(img_path)
        
        # Generate personalized PDF in temp directory
        import tempfile
        temp_dir = tempfile.gettempdir()
        pdf_filename = f"personal_report_{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(temp_dir, pdf_filename)
        
        from utils import generate_user_pdf_report
        result = generate_user_pdf_report(user_reports, user_name, user_location, pdf_path, image_paths)
        
        if result['status'] != 'success':
            return jsonify({'status': 'error', 'message': result['error']}), 500
        
        if action == 'email':
            # Email the personalized PDF
            from utils import email_pdf_report
            email_result = email_pdf_report(user_email, pdf_path, user_name, True)
            
            if email_result['status'] == 'sent':
                return jsonify({'status': 'success', 'message': f'✅ Personal report emailed to {user_email}!'})
            else:
                return jsonify({'status': 'error', 'message': email_result['error']}), 500
        else:
            # Download the PDF - verify it exists and has content
            if not os.path.exists(pdf_path):
                return jsonify({'status': 'error', 'message': 'PDF file not found'}), 500
            
            if os.path.getsize(pdf_path) == 0:
                return jsonify({'status': 'error', 'message': 'PDF file is empty'}), 500
            
            return send_file(pdf_path, as_attachment=True, 
                           download_name=os.path.basename(pdf_path))
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download existing PDF files from the project directory."""
    try:
        # Security check - only allow PDF files
        if not filename.endswith('.pdf'):
            return jsonify({'status': 'error', 'message': 'Only PDF files can be downloaded'}), 403
        
        # Security check - prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({'status': 'error', 'message': 'Invalid filename'}), 403
        
        # Check if file exists in the current directory
        file_path = os.path.abspath(filename)
        project_dir = os.path.abspath('.')
        
        # Ensure file is in the project directory (security)
        if not file_path.startswith(project_dir):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
        # Return the file
        return send_file(file_path, 
                        mimetype='application/pdf',
                        as_attachment=True, 
                        download_name=filename)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/available-reports')
def available_reports():
    """Show page to download existing waste report PDFs."""
    import glob
    from datetime import datetime
    
    # Find all PDF files in the project root
    pdf_files = glob.glob('waste_report_*.pdf')
    
    # Get file info
    reports = []
    for pdf_file in sorted(pdf_files, reverse=True):
        try:
            file_path = os.path.abspath(pdf_file)
            file_size = os.path.getsize(file_path)
            file_mtime = os.path.getmtime(file_path)
            
            # Convert to MB and readable format
            size_mb = round(file_size / (1024 * 1024), 2)
            modified = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M')
            
            reports.append({
                'name': pdf_file,
                'size_mb': size_mb,
                'modified': modified
            })
        except:
            pass
    
    return render_template('download_reports.html', reports=reports)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000) 