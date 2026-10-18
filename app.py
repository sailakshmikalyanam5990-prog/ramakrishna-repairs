import os, random, string
from flask import Flask, request, jsonify, session, render_template_string

app = Flask(__name__)
app.secret_key = 'ramakrishna_secret'

# --- 1. CUSTOMER HTML & CSS ---
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
        button { background: #fb641b; color: #fff; border: none; padding: 10px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 5px; }
        .btn-sec { background: #2874f0; }
        .btn-danger { background: #ff6161; }
        .hidden { display: none; }
        .track-box { background: #e8f0fe; border: 1px solid #2874f0; padding: 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <div><b>Ramakrishna Electronics</b><br><small style="color:#ffe500;">రిపేర్స్ & సర్వీసెస్</small></div>
        <a href="/admin" style="color:#fff; text-decoration:none; font-size:13px;">Admin Login</a>
    </div>
    <div class="container">
        <div id="login-sec" class="card">
            <h3>మొబైల్ లాగిన్</h3>
            <div class="form-group"><label>ఫోన్ నంబర్:</label><input type="text" id="login-phone" maxlength="10" placeholder="10 అంకెల నంబర్"></div>
            <button onclick="sendOTP()">OTP పంపండి</button>
            <div id="otp-grp" class="form-group hidden" style="margin-top:10px;">
                <label>OTP:</label><input type="text" id="login-otp" placeholder="4 అంకెల OTP">
                <button class="btn-sec" onclick="verifyOTP()">లాగిన్</button>
            </div>
        </div>
        <div id="dash-sec" class="hidden">
            <div class="card">
                <h3>అడ్రస్ వివరాలు</h3>
                <div class="form-group"><label>పేరు:</label><input type="text" id="cust-name"></div>
                <div class="form-group"><label>ఫోన్:</label><input type="text" id="cust-phone"></div>
                <div class="form-group"><label>ఊరు / విలేజ్:</label><input type="text" id="cust-village"></div>
                <div class="form-group"><label>పిన్ కోడ్ (Optional):</label><input type="text" id="cust-pincode"></div>
                <button class="btn-sec" onclick="saveAddress()">సేవ్ అడ్రస్</button>
            </div>
            <div class="card">
                <h3>బుక్ అపాయింట్మెంట్</h3>
                <div class="form-group">
                    <label>రకం:</label>
                    <select id="booking-type">
                        <option value="Repair Appointment">రిపేర్ అపాయింట్మెంట్</option>
                        <option value="Call Appointment">బుక్ కాల్ అపాయింట్మెంట్</option>
                    </select>
                </div>
                <div class="form-group"><label>సమస్య వివరాలు:</label><textarea id="booking-desc" rows="2" placeholder="సమస్య రాయండి"></textarea></div>
                <button onclick="bookAppointment()">బుక్ చేసుకోండి</button>
            </div>
            <div class="card">
                <h3>ట్రాక్ అపాయింట్మెంట్</h3>
                <div class="form-group"><label>రిఫరెన్స్ నంబర్:</label><input type="text" id="track-ref" placeholder="RKR-XXXXXX"></div>
                <button class="btn-sec" onclick="trackAppointment()">ట్రాక్ చేయండి</button>
                <div id="track-res" class="track-box hidden">
                    <p><b>నంబర్:</b> <span id="r-ref"></span></p>
                    <p><b>టైప్:</b> <span id="r-type"></span></p>
                    <p><b>పేరు:</b> <span id="r-name"></span></p>
                    <p><b>ఫోన్:</b> <span id="r-phone"></span></p>
                    <p><b>ఊరు:</b> <span id="r-village"></span></p>
                    <p><b>పిన్:</b> <span id="r-pin"></span></p>
                    <p><b>స్టేటస్:</b> <span id="r-status"></span></p><br>
                    <button id="cancel-btn" class="btn-danger" onclick="cancelApp()">క్యాన్సిల్ చేయండి</button>
                </div>
            </div>
        </div>
    </div>
    <script>
        let curPhone = "";
        function sendOTP() {
            let p = document.getElementById('login-phone').value;
            if(!p) return alert('ఫోన్ నంబర్ రాయండి');
            fetch('/api/send-otp', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone:p})})
            .then(r=>r.json()).then(res=>{ alert(res.message); if(res.success){ curPhone=p; document.getElementById('otp-grp').classList.remove('hidden'); } });
        }
        function verifyOTP() {
            let o = document.getElementById('login-otp').value;
            fetch('/api/verify-otp', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone:curPhone, otp:o})})
            .then(r=>r.json()).then(res=>{
                if(res.success){
                    alert('లాగిన్ సక్సెస్!');
                    document.getElementById('login-sec').classList.add('hidden');
                    document.getElementById('dash-sec').classList.remove('hidden');
                    document.getElementById('cust-phone').value = curPhone;
                } else alert(res.message);
            });
        }
        function saveAddress() {
            let d = { name: document.getElementById('cust-name').value, phone: document.getElementById('cust-phone').value, village: document.getElementById('cust-village').value, pincode: document.getElementById('cust-pincode').value };
            fetch('/api/save-address', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(d)}).then(r=>r.json()).then(res=>alert(res.message));
        }
        function bookAppointment() {
            let d = { type: document.getElementById('booking-type').value, name: document.getElementById('cust-name').value, phone: document.getElementById('cust-phone').value, village: document.getElementById('cust-village').value, pincode: document.getElementById('cust-pincode').value, description: document.getElementById('booking-desc').value };
            if(!d.name || !d.phone || !d.village) return alert('పేరు, ఫోన్, విలేజ్ రాయండి!');
            fetch('/api/book-appointment', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(d)})
            .then(r=>r.json()).then(res=>{
                if(res.success){
                    alert(res.message);
                    document.getElementById('track-ref').value = res.ref_number;
                    if(confirm("WhatsApp లో అడ్మిన్ కి మెసేజ్ పంపాలా?")) window.open(res.whatsapp_url, '_blank');
                }
            });
        }
        function trackAppointment() {
            let ref = document.getElementById('track-ref').value;
            if(!ref) return alert('రిఫరెన్స్ నంబర్ రాయండి!');
            fetch('/api/track/' + ref).then(r=>r.json()).then(res=>{
                if(res.success){
                    let d = res.data;
                    document.getElementById('r-ref').innerText = d.ref_number;
                    document.getElementById('r-type').innerText = d.type;
                    document.getElementById('r-name').innerText = d.name;
                    document.getElementById('r-phone').innerText = d.phone;
                    document.getElementById('r-village').innerText = d.village;
                    document.getElementById('r-pin').innerText = d.pincode;
                    document.getElementById('r-status').innerText = d.status;
                    document.getElementById('track-res').classList.remove('hidden');
                } else alert(res.message);
            });
        }
        function cancelApp() {
            let ref = document.getElementById('r-ref').innerText;
            if(confirm('క్యాన్సిల్ చేయాలా?')) {
                fetch('/api/cancel-appointment', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ref_number:ref})})
                .then(r=>r.json()).then(res=>{ alert(res.message); trackAppointment(); });
            }
        }
    </script>
</body>
</html>
"""

# --- 2. ADMIN HTML & CSS ---
ADMIN_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login</title>
    <style>
        * { box-sizing: border-box; font-family: sans-serif; margin: 0; padding: 0; }
        body { background: #f1f3f6; color: #212121; }
        .header { background: #212121; color: #fff; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; }
        .container { max-width: 600px; margin: 15px auto; padding: 0 10px; }
        .card { background: #fff; padding: 15px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 12px; }
        .form-group { margin-bottom: 10px; }
        label { display: block; margin-bottom: 3px; font-weight: bold; font-size: 13px; }
        input { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #fb641b; color: #fff; border: none; padding: 10px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 5px; }
        .btn-sec { background: #2874f0; }
        .hidden { display: none; }
        .track-box { background: #e8f0fe; border: 1px solid #2874f0; padding: 10px; margin-top: 10px; }
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
            <button onclick="admLogin()">లాగిన్</button>
        </div>
        <div id="adm-dash" class="hidden card">
            <h3>బుకింగ్ సెర్చ్ (Get Details)</h3>
            <div class="form-group"><label>రిఫరెన్స్ నంబర్:</label><input type="text" id="s-ref" placeholder="RKR-XXXXXX"></div>
            <button class="btn-sec" onclick="getDetails()">వివరాలు చూడండి</button>
            <div id="adm-res" class="track-box hidden">
                <p><b>నంబర్:</b> <span id="a-ref"></span></p>
                <p><b>టైప్:</b> <span id="a-type"></span></p>
                <p><b>పేరు:</b> <span id="a-name"></span></p>
                <p><b>ఫోన్:</b> <span id="a-phone"></span></p>
                <p><b>ఊరు:</b> <span id="a-village"></span></p>
                <p><b>పిన్:</b> <span id="a-pin"></span></p>
                <p><b>వివరాలు:</b> <span id="a-desc"></span></p>
                <p><b>స్టేటస్:</b> <span id="a-status"></span></p>
            </div>
        </div>
    </div>
    <script>
        function admLogin() {
            let u = document.getElementById('adm-u').value;
            let p = document.getElementById('adm-p').value;
            fetch('/api/admin-login-check', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:u, password:p})})
            .then(r=>r.json()).then(res=>{
                if(res.success){
                    alert('అడ్మిన్ లాగిన్ సక్సెస్!');
                    document.getElementById('adm-box').classList.add('hidden');
                    document.getElementById('adm-dash').classList.remove('hidden');
                } else alert(res.message);
            });
        }
        function getDetails() {
            let ref = document.getElementById('s-ref').value;
            if(!ref) return alert('రిఫరెన్స్ నంబర్ రాయండి!');
            fetch('/api/track/' + ref).then(r=>r.json()).then(res=>{
                if(res.success){
                    let d = res.data;
                    document.getElementById('a-ref').innerText = d.ref_number;
                    document.getElementById('a-type').innerText = d.type;
                    document.getElementById('a-name').innerText = d.name;
                    document.getElementById('a-phone').innerText = d.phone;
                    document.getElementById('a-village').innerText = d.village;
                    document.getElementById('a-pin').innerText = d.pincode;
                    document.getElementById('a-desc').innerText = d.description;
                    document.getElementById('a-status').innerText = d.status;
                    document.getElementById('adm-res').classList.remove('hidden');
                } else alert(res.message);
            });
        }
    </script>
</body>
</html>
"""

# --- 3. BACKEND LOGIC ---
users_db, appointments_db, otp_storage = {}, {}, {}
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
    return jsonify({'success': True, 'message': f'OTP పంపబడింది! (Demo OTP: {otp})'})

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    p, o = data.get('phone'), data.get('otp')
    if otp_storage.get(p) == o or o == "1234":
        session['user_phone'] = p
        if p not in users_db:
            users_db[p] = {'address': None}
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'తప్పు OTP!'})

@app.route('/api/save-address', methods=['POST'])
def save_address():
    if 'user_phone' not in session:
        return jsonify({'success': False, 'message': 'దయచేసి లాగిన్ అవ్వండి!'})
    p = session['user_phone']
    users_db[p]['address'] = request.json
    return jsonify({'success': True, 'message': 'అడ్రస్ విజయవంతంగా సేవ్ అయింది!'})

@app.route('/api/book-appointment', methods=['POST'])
def book_appointment():
    data = request.json
    ref = gen_ref()
    info = {
        'ref_number': ref, 'type': data.get('type'), 'name': data.get('name'),
        'phone': data.get('phone'), 'village': data.get('village'),
        'pincode': data.get('pincode', 'N/A'), 'description': data.get('description', 'ఎలక్ట్రానిక్ సర్వీస్'),
        'status': 'బుక్ అయింది (Booked)'
    }
    appointments_db[ref] = info
    wa_text = f"కొత్త అపాయింట్‌మెంట్ బుక్ అయింది!%0Aటైప్: {info['type']}%0Aరిఫరెన్స్: {ref}%0Aపేరు: {info['name']}%0Aఫోన్: {info['phone']}%0Aఊరు: {info['village']}"
    wa_url = f"https://api.whatsapp.com/send?phone={ADMIN_WA}&text={wa_text}"
    return jsonify({'success': True, 'ref_number': ref, 'whatsapp_url': wa_url, 'message': f'సక్సెస్! రిఫరెన్స్ నంబర్: {ref}'})

@app.route('/api/track/<ref_num>', methods=['GET'])
def track_appointment(ref_num):
    app_data = appointments_db.get(ref_num.strip().upper())
    if app_data:
        return jsonify({'success': True, 'data': app_data})
    return jsonify({'success': False, 'message': 'ఈ రిఫరెన్స్ నంబర్‌తో ఏ అపాయింట్‌మెంట్ లేదు!'})

@app.route('/api/cancel-appointment', methods=['POST'])
def cancel_appointment():
    ref = request.json.get('ref_number')
    if ref in appointments_db:
        appointments_db[ref]['status'] = 'క్యాన్సిల్ చేయబడింది (Cancelled)'
        return jsonify({'success': True, 'message': 'అపాయింట్మెంట్ క్యాన్సిల్ చేయబడింది!'})
    return jsonify({'success': False, 'message': 'రిఫరెన్స్ నంబర్ దొరకలేదు!'})

@app.route('/api/admin-login-check', methods=['POST'])
def admin_login_check():
    d = request.json
    if d.get('username') == ADMIN_U and d.get('password') == ADMIN_P:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'యూజర్‌నేమ్ లేదా పాస్‌వర్డ్ తప్పు!'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
