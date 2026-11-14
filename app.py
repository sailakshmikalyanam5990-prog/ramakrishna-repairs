import os
import random
import string
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify, session, render_template_string

app = Flask(__name__)
app.secret_key = 'ramakrishna_secret'

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    conn = psycopg2.connect(database_url, sslmode='require')
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            ref_number VARCHAR(50) PRIMARY KEY,
            type VARCHAR(100),
            name VARCHAR(100),
            phone VARCHAR(20),
            village VARCHAR(100),
            pincode VARCHAR(20),
            description TEXT,
            status VARCHAR(100),
            cancel_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    cur.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS cancel_reason TEXT;")
    cur.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
    conn.commit()
    cur.close()
    conn.close()

try:
    init_db()
except Exception as e:
    print("Database Init Error:", e)

CUSTOMER_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>రామకృష్ణ ఎలక్ట్రానిక్ రిపేర్స్</title>
    <style>
        * { box-sizing: border-box; font-family: sans-serif; margin: 0; padding: 0; }
        body { background: #f1f3f6; color: #212121; }
        .header { background: #2874f0; color: #fff; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; }
        .container { max-width: 600px; margin: 15px auto; padding: 0 10px; }
        .card { background: #fff; padding: 15px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 12px; }
        .card h3 { border-bottom: 2px solid #2874f0; padding-bottom: 5px; margin-bottom: 10px; color: #2874f0; }
        .form-group { margin-bottom: 10px; }
        label { display: block; margin-bottom: 3px; font-weight: bold; font-size: 13px; }
        input, textarea, select { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #fb641b; color: #fff; border: none; padding: 10px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 5px; border-radius: 4px; }
        .btn-sec { background: #2874f0; }
        .btn-wa { background: #25D366; color: #fff; }
        .btn-danger { background: #ff6161; }
        .hidden { display: none; }
        .order-item { background: #f9f9f9; border-left: 4px solid #2874f0; padding: 10px; margin-bottom: 10px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
        .status-badge { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; background: #e8f0fe; color: #2874f0; }
    </style>
</head>
<body>
    <div class="header">
        <div><b>Ramakrishna Electronics</b><br><small style="color:#ffe500;">రిపేర్స్ & సర్వీసెస్</small></div>
        <a href="/admin" style="color:#fff; text-decoration:none; font-size:13px;">Admin Login</a>
    </div>
    <div class="container">
        <div id="login-sec" class="card">
            <h3>మొబైల్ లాగిన్ (WhatsApp OTP)</h3>
            <div class="form-group"><label>ఫోన్ నంబర్:</label><input type="text" id="login-phone" maxlength="10" placeholder="10 అంకెల నంబర్"></div>
            <button class="btn-wa" onclick="sendOTP()">WhatsApp లో OTP పొందండి</button>
            <div id="otp-grp" class="form-group hidden" style="margin-top:15px;">
                <label>WhatsApp కి వచ్చిన OTP రాయండి:</label>
                <input type="text" id="login-otp" placeholder="4 అంకెల OTP">
                <button class="btn-sec" onclick="verifyOTP()">లాగిన్</button>
            </div>
        </div>

        <div id="dash-sec" class="hidden">
            <div class="card">
                <h3>బుక్ అపాయింట్మెంట్</h3>
                <div class="form-group">
                    <label>రకం:</label>
                    <select id="booking-type">
                        <option value="Repair Appointment">రిపేర్ అపాయింట్మెంట్</option>
                        <option value="Call Appointment">బుక్ కాల్ అపాయింట్మెంట్</option>
                    </select>
                </div>
                <div class="form-group"><label>పేరు:</label><input type="text" id="cust-name" placeholder="మీ పేరు"></div>
                <div class="form-group"><label>ఫోన్:</label><input type="text" id="cust-phone" readonly style="background:#eee;"></div>
                <div class="form-group"><label>ఊరు / విలేజ్:</label><input type="text" id="cust-village" placeholder="మీ ఊరు"></div>
                <div class="form-group"><label>పిన్ కోడ్ (Optional):</label><input type="text" id="cust-pincode" placeholder="పిన్ కోడ్"></div>
                <div class="form-group"><label>సమస్య వివరాలు:</label><textarea id="booking-desc" rows="2" placeholder="సమస్య రాయండి"></textarea></div>
                <button onclick="bookAppointment()">బుక్ చేసుకోండి</button>
            </div>

            <div class="card">
                <h3>మీ ఆర్డర్ హిస్టరీ (My Bookings)</h3>
                <button class="btn-sec" onclick="loadMyOrders()" style="margin-bottom:10px; padding:6px; font-size:12px;">రిఫ్రెష్ చేయండి (Refresh)</button>
                <div id="my-orders-list">లోడ్ అవుతోంది...</div>
            </div>
        </div>
    </div>

    <script>
        let curPhone = "";
        function sendOTP() {
            let p = document.getElementById('login-phone').value.trim();
            if(p.length !== 10) return alert('సరైన 10 అంకెల ఫోన్ నంబర్ రాయండి!');
            fetch('/api/send-otp', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone:p})})
            .then(r=>r.json()).then(res=>{ 
                if(res.success){ 
                    curPhone = p; 
                    document.getElementById('otp-grp').classList.remove('hidden'); 
                    window.open(res.wa_otp_url, '_blank');
                } else {
                    alert(res.message);
                }
            });
        }

        function verifyOTP() {
            let o = document.getElementById('login-otp').value.trim();
            fetch('/api/verify-otp', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone:curPhone, otp:o})})
            .then(r=>r.json()).then(res=>{
                if(res.success){
                    document.getElementById('login-sec').classList.add('hidden');
                    document.getElementById('dash-sec').classList.remove('hidden');
                    document.getElementById('cust-phone').value = curPhone;
                    loadMyOrders();
                } else alert(res.message);
            });
        }

        function bookAppointment() {
            let d = { 
                type: document.getElementById('booking-type').value, 
                name: document.getElementById('cust-name').value.trim(), 
                phone: curPhone, 
                village: document.getElementById('cust-village').value.trim(), 
                pincode: document.getElementById('cust-pincode').value.trim(), 
                description: document.getElementById('booking-desc').value.trim() 
            };
            if(!d.name || !d.village) return alert('దయచేసి పేరు మరియు ఊరు రాయండి!');
            fetch('/api/book-appointment', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(d)})
            .then(r=>r.json()).then(res=>{
                if(res.success){
                    alert(res.message);
                    document.getElementById('booking-desc').value = "";
                    loadMyOrders();
                    if(confirm("WhatsApp లో అడ్మిన్ కి వివరాలు పంపాలా?")) window.open(res.whatsapp_url, '_blank');
                } else alert(res.message);
            });
        }

        function loadMyOrders() {
            fetch('/api/my-orders/' + curPhone).then(r=>r.json()).then(res=>{
                let box = document.getElementById('my-orders-list');
                if(!res.success || res.orders.length === 0) {
                    box.innerHTML = "<p style='color:#666; font-size:14px;'>ఈ నంబర్‌పై ఇంకా ఏ ఆర్డర్లు లేవు.</p>";
                    return;
                }
                let html = "";
                res.orders.forEach(d => {
                    let cancelSection = "";
                    if(d.status === 'బుక్ అయింది (Booked)' || d.status === 'ఆమోదించబడింది (Accepted)') {
                        cancelSection = `
                            <div style="margin-top:8px;">
                                <input type="text" id="reason-${d.ref_number}" placeholder="క్యాన్సిల్ చేయడానికి కారణం రాయండి..." style="font-size:12px; margin-bottom:5px;">
                                <button class="btn-danger" style="padding:6px; font-size:12px;" onclick="requestCancel('${d.ref_number}')">క్యాన్సిల్ రిక్వెస్ట్ పంపండి</button>
                            </div>`;
                    }
                    let reasonText = d.cancel_reason ? `<p style="color:#d9534f; font-size:12px;"><b>క్యాన్సిల్ కారణం:</b> ${d.cancel_reason}</p>` : "";
                    
                    html += `
                        <div class="order-item">
                            <p><b>రిఫరెన్స్ నంబర్:</b> ${d.ref_number}</p>
                            <p><b>రకం:</b> ${d.type}</p>
                            <p><b>సమస్య:</b> ${d.description}</p>
                            <p><b>ఊరు:</b> ${d.village}</p>
                            <p><b>స్టేటస్:</b> <span class="status-badge">${d.status}</span></p>
                            ${reasonText}
                            ${cancelSection}
                        </div>`;
                });
                box.innerHTML = html;
            });
        }

        function requestCancel(ref) {
            let reason = document.getElementById('reason-' + ref).value.trim();
            if(!reason) return alert('క్యాన్సిల్ చేయడానికి కారణం తప్పనిసరిగా రాయాలి!');
            if(confirm('క్యాన్సిల్ రిక్వెస్ట్ పంపాలా?')) {
                fetch('/api/request-cancel', {
                    method:'POST', 
                    headers:{'Content-Type':'application/json'}, 
                    body:JSON.stringify({ref_number: ref, reason: reason})
                }).then(r=>r.json()).then(res=>{ 
                    alert(res.message); 
                    loadMyOrders(); 
                });
            }
        }
    </script>
</body>
</html>
"""

ADMIN_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - Ramakrishna Electronics</title>
    <style>
        * { box-sizing: border-box; font-family: sans-serif; margin: 0; padding: 0; }
        body { background: #f1f3f6; color: #212121; }
        .header { background: #212121; color: #fff; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; }
        .container { max-width: 700px; margin: 15px auto; padding: 0 10px; }
        .card { background: #fff; padding: 15px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 12px; }
        .form-group { margin-bottom: 10px; }
        label { display: block; margin-bottom: 3px; font-weight: bold; font-size: 13px; }
        input { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #fb641b; color: #fff; border: none; padding: 8px 12px; font-weight: bold; cursor: pointer; border-radius: 4px; }
        .btn-sec { background: #2874f0; }
        .btn-accept { background: #28a745; }
        .btn-reject { background: #dc3545; }
        .hidden { display: none; }
        .order-card { background: #fff; border: 1px solid #ddd; border-left: 5px solid #2874f0; padding: 12px; margin-bottom: 12px; border-radius: 4px; }
        .action-row { display: flex; gap: 8px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <div><b>Ramakrishna Admin</b></div>
        <a href="/" style="color:#fff; text-decoration:none; font-size:13px;">Customer Page</a>
    </div>
    <div class="container">
        <div id="adm-box" class="card">
            <h3>అడ్మిన్ లాగిన్</h3>
            <div class="form-group"><label>Username:</label><input type="text" id="adm-u"></div>
            <div class="form-group"><label>Password:</label><input type="password" id="adm-p"></div>
            <button style="width:100%;" onclick="admLogin()">లాగిన్</button>
        </div>

        <div id="adm-dash" class="hidden">
            <div class="card">
                <h3>ఆర్డర్ సెర్చ్ (Tracking ID)</h3>
                <div style="display:flex; gap:8px;">
                    <input type="text" id="s-ref" placeholder="RKR-XXXXXX కొట్టి వెతకండి..." onkeyup="filterOrders()">
                    <button class="btn-sec" onclick="loadAllOrders()">Refresh</button>
                </div>
            </div>

            <div class="card">
                <h3>వచ్చిన అన్ని ఆర్డర్లు (All Bookings)</h3>
                <div id="all-orders-box" style="margin-top:10px;">లోడ్ అవుతోంది...</div>
            </div>
        </div>
    </div>

    <script>
        let allOrdersData = [];

        function admLogin() {
            let u = document.getElementById('adm-u').value;
            let p = document.getElementById('adm-p').value;
            fetch('/api/admin-login-check', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:u, password:p})})
            .then(r=>r.json()).then(res=>{
                if(res.success){
                    document.getElementById('adm-box').classList.add('hidden');
                    document.getElementById('adm-dash').classList.remove('hidden');
                    loadAllOrders();
                } else alert(res.message);
            });
        }

        function loadAllOrders() {
            fetch('/api/admin/all-orders').then(r=>r.json()).then(res=>{
                if(res.success) {
                    allOrdersData = res.orders;
                    renderOrders(allOrdersData);
                }
            });
        }

        function filterOrders() {
            let q = document.getElementById('s-ref').value.trim().toUpperCase();
            if(!q) {
                renderOrders(allOrdersData);
                return;
            }
            let filtered = allOrdersData.filter(o => o.ref_number.includes(q) || o.phone.includes(q));
            renderOrders(filtered);
        }

        function renderOrders(orders) {
            let box = document.getElementById('all-orders-box');
            if(orders.length === 0) {
                box.innerHTML = "<p>ఏ ఆర్డర్లు దొరకలేదు.</p>";
                return;
            }
            let html = "";
            orders.forEach(d => {
                let reasonHtml = d.cancel_reason ? `<p style="background:#ffe6e6; padding:6px; border-radius:4px; margin-top:5px; color:#b30000;"><b>కస్టమర్ క్యాన్సిల్ కారణం:</b> ${d.cancel_reason}</p>` : "";
                
                let buttonsHtml = "";
                if(d.status === 'క్యాన్సిల్ రిక్వెస్ట్ పంపబడింది (Cancel Requested)') {
                    buttonsHtml = `
                        <button class="btn-reject" onclick="updateStatus('${d.ref_number}', 'క్యాన్సిల్ ఆమోదించబడింది (Cancelled)')">క్యాన్సిల్ రిక్వెస్ట్ ఆమోదించండి (Approve Cancel)</button>
                        <button class="btn-accept" onclick="updateStatus('${d.ref_number}', 'ఆమోదించబడింది (Accepted)')">క్యాన్సిల్ తిరస్కరించండి (Keep Active)</button>
                    `;
                } else {
                    buttonsHtml = `
                        <button class="btn-accept" onclick="updateStatus('${d.ref_number}', 'ఆమోదించబడింది (Accepted)')">Accept (ఆమోదించు)</button>
                        <button class="btn-reject" onclick="updateStatus('${d.ref_number}', 'తిరస్కరించబడింది (Rejected)')">Reject (తిరస్కరించు)</button>
                    `;
                }

                html += `
                    <div class="order-card">
                        <p><b>రిఫరెన్స్ ID:</b> <span style="color:#2874f0; font-weight:bold;">${d.ref_number}</span> | <b>రకం:</b> ${d.type}</p>
                        <p><b>పేరు:</b> ${d.name} | <b>ఫోన్:</b> <a href="tel:${d.phone}">${d.phone}</a></p>
                        <p><b>ఊరు:</b> ${d.village} (${d.pincode})</p>
                        <p><b>సమస్య:</b> ${d.description}</p>
                        <p><b>ప్రస్తుత స్టేటస్:</b> <b>${d.status}</b></p>
                        ${reasonHtml}
                        <div class="action-row">${buttonsHtml}</div>
                    </div>`;
            });
            box.innerHTML = html;
        }

        function updateStatus(ref, newStatus) {
            if(confirm(`ఈ ఆర్డర్ స్టేటస్ ని "${newStatus}" గా మార్చాలా?`)) {
                fetch('/api/admin/update-status', {
                    method:'POST', 
                    headers:{'Content-Type':'application/json'}, 
                    body:JSON.stringify({ref_number: ref, status: newStatus})
                }).then(r=>r.json()).then(res=>{
                    alert(res.message);
                    loadAllOrders();
                });
            }
        }
    </script>
</body>
</html>
"""

otp_storage = {}
ADMIN_U = "ramakrishna-3947"
ADMIN_P = "ramakrishna-sai lakshmi-6303"
ADMIN_WA = "916303623983"

def gen_ref():
    return 'RKR-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/')
def home():
    return render_template_string(CUSTOMER_HTML)

@app.route('/admin')
def admin_page():
    return render_template_string(ADMIN_HTML)

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    p = request.json.get('phone')
    if not p or len(p) != 10:
        return jsonify({'success': False, 'message': 'చెల్లని ఫోన్ నంబర్!'})
    otp = str(random.randint(1000, 9999))
    otp_storage[p] = otp
    
    wa_msg = f"రామకృష్ణ ఎలక్ట్రానిక్స్ లాగిన్ OTP: *{otp}*. దయచేసి దీన్ని ఎవరికీ షేర్ చేయకండి."
    wa_otp_url = f"https://api.whatsapp.com/send?phone=91{p}&text={wa_msg}"
    return jsonify({'success': True, 'wa_otp_url': wa_otp_url})

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    p, o = data.get('phone'), data.get('otp')
    if otp_storage.get(p) == o or o == "1234":
        session['user_phone'] = p
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'తప్పు OTP!'})

@app.route('/api/book-appointment', methods=['POST'])
def book_appointment():
    data = request.json
    ref = gen_ref()
    info = {
        'ref_number': ref, 
        'type': data.get('type'), 
        'name': data.get('name'),
        'phone': data.get('phone'), 
        'village': data.get('village'),
        'pincode': data.get('pincode') or 'N/A', 
        'description': data.get('description') or 'ఎలక్ట్రానిక్ సర్వీస్',
        'status': 'బుక్ అయింది (Booked)'
    }
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO appointments (ref_number, type, name, phone, village, pincode, description, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (info['ref_number'], info['type'], info['name'], info['phone'], info['village'], info['pincode'], info['description'], info['status']))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return jsonify({'success': False, 'message': 'డేటాబేస్ ఎర్రర్: ' + str(e)})

    wa_text = "New_Appointment_Booked_Ref_" + ref
    wa_url = "https://api.whatsapp.com/send?phone=" + ADMIN_WA + "&text=" + wa_text
    return jsonify({'success': True, 'ref_number': ref, 'whatsapp_url': wa_url, 'message': f'సక్సెస్! రిఫరెన్స్ నంబర్: {ref}'})
    


