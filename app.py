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
            fetch('/api/book-appointment', {method:'POST', headers:{
            
