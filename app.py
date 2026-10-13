
from flask import Flask, render_template_string, request, redirect, url_for, session
from datetime import datetime
import urllib.parse
import random

app = Flask(__name__)
app.secret_key = 'ramakrishna_secret_key_123'

ADMIN_USERNAME = "Ramakrishna repairs"
ADMIN_PASSWORD = "Ramakrishna repairs@2026"
OWNER_PHONE = "916303623983"

# bookings format: {b_id: {type, name, phone, address, device, issue, time, status}}
bookings = {}
# Temporary OTP storage: {phone: otp}
otp_storage = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="te">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>రామకృష్ణ ఎలక్ట్రానిక్ రిపేర్స్</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); position: relative; }
        
        /* Menu / Top Navigation */
        .topnav { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px; flex-wrap: wrap; gap: 5px; }
        .topnav a { text-decoration: none; color: #0275d8; font-weight: bold; font-size: 14px; padding: 5px 10px; background: #eef5fb; border-radius: 4px; }
        
        h1 { color: #d9534f; text-align: center; font-size: 22px; margin-top: 5px; }
        h2 { color: #0275d8; font-size: 20px; border-bottom: 2px solid #eee; padding-bottom: 5px; text-align: center; }
        
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        
        button { background-color: #5cb85c; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; font-weight: bold; }
        button:hover { background-color: #4cae4c; }
        
        .btn-danger { background-color: #d9534f; color: white; padding: 8px 12px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; text-align: center; font-weight: bold; font-size: 14px; margin-top: 5px; }
        .btn-danger:hover { background-color: #c9302c; }
        
        .btn-primary { background-color: #0275d8; color: white; padding: 8px 12px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; text-align: center; font-weight: bold; font-size: 14px; margin-top: 5px; }
        .btn-primary:hover { background-color: #025aa5; }

        .alert { background: #dff0d8; color: #3c763d; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; }
        .error { background: #f2dede; color: #a94442; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; }
        .otp-box { background: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; font-weight: bold; }
        
        .booking-card { background: #fff; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        
        .status-pending { color: #f0ad4e; font-weight: bold; }
        .status-accepted { color: #5cb85c; font-weight: bold; }
        .status-cancelled { color: #d9534f; font-weight: bold; }

        .footer-link { text-align: center; margin-top: 20px; }
        .footer-link a { color: #0275d8; text-decoration: none; font-weight: bold; }
        
        .whatsapp-btn { background-color: #25d366; color: white; display: block; text-align: center; padding: 12px; border-radius: 5px; text-decoration: none; font-weight: bold; margin-top: 15px; }
        .whatsapp-btn:hover { background-color: #20ba5a; }
    </style>
</head>
<body>
    <div class="container">
        
        <!-- Navigation bar -->
        <div class="topnav">
            <a href="/">🏠 హోమ్ (బుక్ చేయండి)</a>
            <a href="/call-booking">📞 కాల్ బుకింగ్</a>
            <a href="/my-orders">📦 నా ఆర్డర్స్ హిస్టరీ</a>
            {% if session.get('customer_phone') %}
                <a href="/customer-logout" style="background: #f2dede; color: #a94442;">లాగౌట్ ({{ session.get('customer_phone') }})</a>
            {% else %}
                <a href="/customer-login">🔐 లాగిన్</a>
            {% endif %}
        </div>

        {% if role == 'customer' %}
            <h1>రామకృష్ణ ఎలక్ట్రానిక్ రిపేర్స్</h1>
            <p style="text-align: center; color: #666;">Flipkart లాగా మీ నంబర్ తో లాగిన్ అయి రిపేర్ అపాయింట్మెంట్ బుక్ చేసుకోండి.</p>
            
            {% if not session.get('customer_phone') %}
                <div class="error" style="background: #fcf8e3; color: #8a6d3b;">
                    దయచేసి బుక్ చేయడానికి ముందు మీ ఫోన్ నంబర్‌తో లాగిన్ అవ్వండి! <br>
                    <a href="/customer-login" class="btn-primary" style="margin-top: 10px;">నెంబర్ తో లాగిన్ అవ్వండి</a>
                </div>
            {% else %}
                {% if success_id %}
                    <div class="alert">
                        మీ రిపేర్ అపాయింట్మెంట్ విజయవంతంగా బుక్ అయింది!<br>
                        మీ ఆర్డర్ ఐడీ: <strong>{{ success_id }}</strong>
                    </div>
                    <a class="whatsapp-btn" href="https://wa.me/{{ owner_phone }}?text={{ wa_message }}" target="_blank">📲 ఓనర్ వాట్సాప్‌కి వివరాలు పంపండి (Click Here)</a>
                {% endif %}

                <form method="POST" action="/book">
                    <div class="form-group">
                        <label>మీ పేరు:</label>
                        <input type="text" name="name" required placeholder="మీ పూర్తి పేరు రాయండి">
                    </div>
                    <div class="form-group">
                        <label>ఫోన్ నంబర్ (లాగిన్ నంబర్):</label>
                        <input type="text" name="phone" value="{{ session.get('customer_phone') }}" readonly style="background: #eef5fb;">
                    </div>
                    <div class="form-group">
                        <label>చిరునామా (Address):</label>
                        <textarea name="address" rows="3" required placeholder="మీ ఊరు / అడ్రస్ రాయండి"></textarea>
                    </div>
                    <div class="form-group">
                        <label>ఏ పరికరం రిపేర్ చేయాలి? (టైప్ చేయండి)</label>
                        <input type="text" name="device" required placeholder="ఉదా: AC, TV, Fridge, Washing Machine మొదలైనవి">
                    </div>
                    <div class="form-group">
                        <label>సమస్య ఏమిటి?</label>
                        <textarea name="issue" rows="2" required placeholder="సమస్య వివరాలు తెలపండి"></textarea>
                    </div>
                    <button type="submit">అపాయింట్మెంట్ ఆర్డర్ చేయండి</button>
                </form>
            {% endif %}
            
            <div class="footer-link">
                <a href="/admin-login">🔒 ఓనర్ (Admin) లాగిన్ కోసం ఇక్కడ నొక్కండి</a>
            </div>

        {% elif role == 'customer_login' %}
            <h2>📱 కస్టమర్ ఫోన్ నంబర్ లాగిన్ (Flipkart Style)</h2>
            
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}

            <form method="POST" action="/customer-login">
                <div class="form-group">
                    <label>మీ 10 అంకెల ఫోన్ నంబర్:</label>
                    <input type="text" name="phone" required placeholder="ఫోన్ నంబర్ ఎంటర్ చేయండి" maxlength="10">
                </div>
                <button type="submit">OTP పంపు (Get OTP)</button>
            </form>

            <div class="footer-link">
                <a href="/">⬅️ హోమ్ పేజీకి వెళ్లండి</a>
            </div>

        {% elif role == 'verify_otp' %}
            <h2>🔐 OTP వెరిఫికేషన్</h2>
            
            {% if otp_sent %}
                <div class="otp-box">
                    మీ సిమ్యులేటెడ్ OTP: {{ otp_sent }} (ఇది కింద ఎంటర్ చేయండి)
                </div>
            {% endif %}

            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}

            <form method="POST" action="/verify-otp">
                <div class="form-group">
                    <label>OTP ఎంటర్ చేయండి:</label>
                    <input type="text" name="entered_otp" required placeholder="4 అంకెల OTP రాయండి" maxlength="4">
                </div>
                <button type="submit">వెరిఫై & లాగిన్ అవ్వండి</button>
            </form>

            <div class="footer-link">
                <a href="/customer-login">⬅️ వెనుకకు వెళ్లండి</a>
            </div>

        {% elif role == 'call_booking' %}
            <h2>📞 ఫోన్ కాల్ బుకింగ్ (Call Request)</h2>
            <p style="text-align: center; color: #666;">మాతో మాట్లాడడానికి మీ వివరాలు ఇవ్వండి, మేమే మీకు కాల్ చేస్తాము.</p>
            
            {% if success_id %}
                <div class="alert">
                    మీ కాల్ రిక్వెస్ట్ విజయవంతంగా నమోదయింది!<br>
                    మీ రిఫరెన్స్ ఐడీ: <strong>{{ success_id }}</strong>
                </div>
                <a class="whatsapp-btn" href="https://wa.me/{{ owner_phone }}?text={{ wa_message }}" target="_blank">📲 ఓనర్ వాట్సాప్‌కి కాల్ రిక్వెస్ట్ పంపండి</a>
            {% endif %}

            <form method="POST" action="/call-booking">
                <div class="form-group">
                    <label>మీ పేరు:</label>
                    <input type="text" name="name" required placeholder="మీ పూర్తి పేరు రాయండి">
                </div>
                <div class="form-group">
                    <label>ఫోన్ నంబర్:</label>
                    <input type="text" name="phone" value="{{ session.get('customer_phone', '') }}" required placeholder="10 అంకెల ఫోన్ నంబర్">
                </div>
                <div class="form-group">
                    <label>మీ ఊరు / అడ్రస్:</label>
                    <textarea name="address" rows="3" required placeholder="మీ ఊరు పేరు రాయండి"></textarea>
                </div>
                <button type="submit">కాల్ రిక్వెస్ట్ పంపండి</button>
            </form>

            <div class="footer-link">
                <a href="/">⬅️ హోమ్ పేజీకి వెళ్లండి</a>
            </div>

        {% elif role == 'my_orders' %}
            <h2>📦 నా ఆర్డర్స్ & అపాయింట్మెంట్స్ హిస్టరీ</h2>
            
            {% if not session.get('customer_phone') %}
                <div class="error" style="background: #fcf8e3; color: #8a6d3b;">
                    మీ ఆర్డర్ హిస్టరీ చూసుకోవడానికి దయచేసి లాగిన్ అవ్వండి! <br>
                    <a href="/customer-login" class="btn-primary" style="margin-top: 10px;">లాగిన్ అవ్వండి</a>
                </div>
            {% else %}
                <p style="text-align: center; color: #666;">లాగిన్ అయిన నంబర్: <strong>{{ session.get('customer_phone') }}</strong></p>
                
                {% if not matched_bookings %}
                    <p style="text-align: center; color: #777; margin-top: 20px;">మీ నంబర్ తో ఎలాంటి బుకింగ్స్ / ఆర్డర్స్ లేవు.</p>
                {% else %}
                    {% for b_id, data in matched_bookings.items() %}
                        <div class="booking-card">
                            <p><strong>ఆర్డర్ ఐడీ:</strong> {{ b_id }}</p>
                            <p><strong>రకం:</strong> {% if data.type == 'call' %}📞 కాల్ బుకింగ్{% else %}🛠️ రిపేర్ అపాయింట్మెంట్ ఆర్డర్{% endif %}</p>
                            <p><strong>పేరు:</strong> {{ data.name }}</p>
                            <p><strong>ఫోన్:</strong> {{ data.phone }}</p>
                            <p><strong>అడ్రస్:</strong> {{ data.address }}</p>
                            {% if data.type == 'repair' %}
                                <p><strong>పరికరం:</strong> {{ data.device }}</p>
                                <p><strong>సమస్య:</strong> {{ data.issue }}</p>
                            {% endif %}
                            <p><strong>సమయం:</strong> {{ data.time }}</p>
                            <p><strong>స్టేటస్:</strong> 
                                {% if data.status == 'Pending' %}
                                    <span class="status-pending">పెండింగ్ (Pending)</span>
                                {% elif data.status == 'Accepted' %}
                                    <span class="status-accepted">యాక్సెప్ట్ చేయబడింది (Accepted)</span>
                                {% elif data.status == 'Cancelled' %}
                                    <span class="status-cancelled">క్యాన్సిల్ చేయబడింది (Cancelled)</span>
                                {% endif %}
                            </p>
                            
                            {% if data.status != 'Cancelled' %}
                                <a href="/cancel-booking/{{ b_id }}" class="btn-danger" onclick="return confirm('మీరు నిజంగా ఈ ఆర్డర్‌ని క్యాన్సిల్ చేయాలనుకుంటున్నారా?');">ఆర్డర్ క్యాన్సిల్ చేయండి</a>
                            {% endif %}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endif %}

        {% elif role == 'login' %}
            <h2>🔐 అడ్మిన్ లాగిన్</h2>
            
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}

            <form method="POST" action="/admin-login">
                <div class="form-group">
                    <label>యూజర్ నేమ్:</label>
                    <input type="text" name="username" required placeholder="యూజర్ నేమ్ రాయండి">
                </div>
                <div class="form-group">
                    <label>పాస్‌వర్డ్:</label>
                    <input type="password" name="password" required placeholder="పాస్‌వర్డ్ రాయండి">
                </div>
                <button type="submit">లాగిన్ అవ్వండి</button>
            </form>

            <div class="footer-link">
                <a href="/">⬅️ హోమ్ పేజీకి వెళ్లండి</a>
            </div>

        {% elif role == 'admin' %}
            <h2>⚙️ ఓనర్ / అడ్మిన్ డాష్‌బోర్డ్</h2>
            <p>కస్టమర్ల బుకింగ్స్ మరియు అపాయింట్మెంట్ ఆర్డర్స్ వివరాలు:</p>
            
            {% if not bookings %}
                <p style="text-align: center; color: #777;">ప్రస్తుతం ఎలాంటి రిక్వెస్ట్లు లేవు.</p>
            {% else %}
                {% for b_id, data in bookings.items() %}
                    <div class="booking-card">
                        <p><strong>ఐడీ:</strong> {{ b_id }}</p>
                        <p><strong>రకం:</strong> {% if data.type == 'call' %}📞 కాల్ బుకింగ్{% else %}🛠️ రిపేర్ అపాయింట్మెంట్{% endif %}</p>
                        <p><strong>పేరు:</strong> {{ data.name }}</p>
                        <p><strong>ఫోన్:</strong> <a href="tel:{{ data.phone }}">{{ data.phone }}</a></p>
                        <p><strong>అడ్రస్:</strong> {{ data.address }}</p>
                        {% if data.type == 'repair' %}
                            <p><strong>పరికరాలు:</strong> {{ data.device }}</p>
                            <p><strong>సమస్య:</strong> {{ data.issue }}</p>
                        {% endif %}
                        <p><strong>సమయం:</strong> {{ data.time }}</p>
                        <p><strong>స్టేటస్:</strong> 
                            {% if data.status == 'Pending' %}
                                <span class="status-pending">పెండింగ్</span>
                            {% elif data.status == 'Accepted' %}
                                <span class="status-accepted">యాక్సెప్ట్ చేయబడింది</span>
                            {% elif data.status == 'Cancelled' %}
                                <span class="status-cancelled">క్యాన్సిల్ చేయబడింది</span>
                            {% endif %}
                        </p>

                        {% if data.status == 'Pending' %}
                            <a href="/admin-action/{{ b_id }}/accept" class="btn-primary">✅ యాక్సెప్ట్ చేయి</a>
                            <a href="/admin-action/{{ b_id }}/reject" class="btn-danger">❌ రిజెక్ట్ చేయి</a>
                        {% endif %}
                    </div>
                {% endfor %}
            {% endif %}
            
            <div class="footer-link" style="margin-top: 20px;">
                <a href="/logout">🚪 లాగౌట్ అయి హోమ్ పేజీకి వెళ్లండి</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, role='customer', owner_phone=OWNER_PHONE)

@app.route('/customer-login', methods=['GET', 'POST'])
def customer_login():
    error = None
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        if len(phone) == 10 and phone.isdigit():
            # Generate 4-digit OTP (Flipkart style simulation)
            otp = str(random.randint(1000, 9999))
            otp_storage[phone] = otp
            session['temp_phone'] = phone
            return render_template_string(HTML_TEMPLATE, role='verify_otp', otp_sent=otp)
        else:
            error = "దయచేసి సరైన 10 అంకెల ఫోన్ నంబర్ ఎంటర్ చేయండి!"
    return render_template_string(HTML_TEMPLATE, role='customer_login', error=error)

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    entered_otp = request.form.get('entered_otp', '').strip()
    phone = session.get('temp_phone')
    
    if phone and phone in otp_storage and otp_storage[phone] == entered_otp:
        session['customer_phone'] = phone
        session.pop('temp_phone', None)
        return redirect(url_for('home'))
    else:
        error = "తప్పు OTP! దయచేసి మళ్లీ ప్రయత్నించండి."
        otp = otp_storage.get(phone, "1234")
        return render_template_string(HTML_TEMPLATE, role='verify_otp', otp_sent=otp, error=error)

@app.route('/customer-logout')
def customer_logout():
    session.pop('customer_phone', None)
    return redirect(url_for('home'))

@app.route('/book', methods=['POST'])
def book():
    if not session.get('customer_phone'):
        return redirect(url_for('customer_login'))
        
    name = request.form.get('name')
    phone = session.get('customer_phone')
    address = request.form.get('address')
    device = request.form.get('device')
    issue = request.form.get('issue')
    
    b_id = "RER" + datetime.now().strftime("%H%M%S")
    time_str = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    bookings[b_id] = {
        'type': 'repair',
        'name': name,
        'phone': phone,
        'address': address,
        'device': device,
        'issue': issue,
        'time': time_str,
        'status': 'Pending'
    }
    
    raw_msg = f"కొత్త రిపేర్ అపాయింట్మెంట్ ఆర్డర్ వచ్చింది!\n\nఆర్డర్ ఐడీ: {b_id}\nపేరు: {name}\nఫోన్: {phone}\nఅడ్రస్: {address}\nపరికరం: {device}\nసమస్య: {issue}\nసమయం: {time_str}"
    wa_message = urllib.parse.quote(raw_msg)
    
    return render_template_string(HTML_TEMPLATE, role='customer', owner_phone=OWNER_PHONE, success_id=b_id, wa_message=wa_message)

@app.route('/call-booking', methods=['GET', 'POST'])
def call_booking():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        b_id = "CALL" + datetime.now().strftime("%H%M%S")
        time_str = datetime.now().strftime("%d-%m-%Y %H:%M")
        
        bookings[b_id] = {
            'type': 'call',
            'name': name,
            'phone': phone,
            'address': address,
            'time': time_str,
            'status': 'Pending'
        }
        
        raw_msg = f"కొత్త కాల్ రిక్వెస్ట్ వచ్చింది!\n\nఐడీ: {b_id}\nపేరు: {name}\nఫోన్: {phone}\nఅడ్రస్: {address}\nసమయం: {time_str}"
        wa_message = urllib.parse.quote(raw_msg)
        
        return render_template_string(HTML_TEMPLATE, role='call_booking', o
