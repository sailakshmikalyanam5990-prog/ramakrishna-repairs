from flask import Flask, render_template_string, request, redirect, url_for, session
from datetime import datetime
import urllib.parse

app = Flask(__name__)
app.secret_key = 'ramakrishna_secret_key_123'

ADMIN_USERNAME = "Ramakrishna repairs"
ADMIN_PASSWORD = "Ramakrishna repairs@2026"

bookings = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="te">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>రామకృష్ణ ఎలక్ట్రానిక్ రిపేర్స్</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        h1 { color: #d9534f; text-align: center; font-size: 24px; }
        h2 { color: #0275d8; font-size: 20px; border-bottom: 2px solid #eee; padding-bottom: 5px; text-align: center; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { background-color: #5cb85c; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; font-weight: bold; }
        button:hover { background-color: #4cae4c; }
        .alert { background: #dff0d8; color: #3c763d; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; }
        .error { background: #f2dede; color: #a94442; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; }
        .booking-card { background: #fff; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .footer-link { text-align: center; margin-top: 20px; }
        .footer-link a { color: #0275d8; text-decoration: none; font-weight: bold; }
        .whatsapp-btn { background-color: #25d366; color: white; display: block; text-align: center; padding: 12px; border-radius: 5px; text-decoration: none; font-weight: bold; margin-top: 15px; }
        .whatsapp-btn:hover { background-color: #20ba5a; }
    </style>
</head>
<body>
    <div class="container">
        {% if role == 'customer' %}
            <h1>రామకృష్ణ ఎలక్ట్రానిక్ రిపేర్స్</h1>
            <p style="text-align: center; color: #666;">టీవీ, ఫ్రిజ్, వాషింగ్ మెషీన్ మరియు అన్ని రకాల ఎలక్ట్రానిక్ రిపేర్ల కొరకు సంప్రదించండి.</p>
            
            {% if success_id %}
                <div class="alert">
                    మీ బుకింగ్ విజయవంతంగా నమోదయింది!<br>
                    మీ రిఫరెన్స్ ఐడీ: <strong>{{ success_id }}</strong>
                </div>
                <a class="whatsapp-btn" href="https://wa.me/916303623983?text={{ wa_message }}" target="_blank">📲 ఓనర్ వాట్సాప్‌కి వివరాలు పంపండి (Click Here)</a>
            {% endif %}

            <form method="POST" action="/book">
                <div class="form-group">
                    <label>మీ పేరు:</label>
                    <input type="text" name="name" required placeholder="మీ పూర్తి పేరు రాయండి">
                </div>
                <div class="form-group">
                    <label>ఫోన్ నంబర్:</label>
                    <input type="text" name="phone" required placeholder="10 అంకెల ఫోన్ నంబర్">
                </div>
                <div class="form-group">
                    <label>చిరునామా (Address):</label>
                    <textarea name="address" rows="3" required placeholder="మీ ఊరు / అడ్రస్ రాయండి"></textarea>
                </div>
                <div class="form-group">
                    <label>ఏ పరికరం రిపేర్ చేయాలి?</label>
                    <select name="device">
                        <option value="TV">టీవీ (TV)</option>
                        <option value="Refrigerator">ఫ్రిజ్ (Refrigerator)</option>
                        <option value="Washing Machine">వాషింగ్ మెషీన్ (Washing Machine)</option>
                        <option value="Other">ఇతర ఉపకరణాలు (Other)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>సమస్య ఏమిటి?</label>
                    <textarea name="issue" rows="2" required placeholder="సమస్య వివరాలు తెలపండి"></textarea>
                </div>
                <button type="submit">బుకింగ్ కన్ఫర్మ్ చేయండి</button>
            </form>
            
            <div class="footer-link">
                <a href="/admin-login">🔒 ఓనర్ (Admin) లాగిన్ కోసం ఇక్కడ నొక్కండి</a>
            </div>

        {% elif role == 'login' %}
            <h2>🔐 అడ్మిన్ లాగిన్</h2>
            <p style="text-align: center; color: #666;">ఓనర్ వివరాలు నమోదు చేయండి</p>
            
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
            <p>కస్టమర్లు చేసిన బుకింగ్స్ వివరాలు:</p>
            
            {% if not bookings %}
                <p style="text-align: center; color: #777;">ప్రస్తుతం ఎలాంటి బుకింగ్స్ లేవు.</p>
            {% else %}
                {% for b_id, data in bookings.items() %}
                    <div class="booking-card">
                        <p><strong>ఐడీ:</strong> {{ b_id }}</p>
                        <p><strong>పేరు:</strong> {{ data.name }}</p>
                        <p><strong>ఫోన్:</strong> <a href="tel:{{ data.phone }}">{{ data.phone }}</a></p>
                        <p><strong>అడ్రస్:</strong> {{ data.address }}</p>
                        <p><strong>పరికరాలు:</strong> {{ data.device }}</p>
                        <p><strong>సమస్య:</strong> {{ data.issue }}</p>
                        <p><strong>సమయం:</strong> {{ data.time }}</p>
                    </div>
                {% endfor %}
            {% endif %}
            
            <div class="footer-link">
                <a href="/logout">🚪 లాగౌట్ అయి కస్టమర్ పేజీకి వెళ్లండి</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, role='customer', bookings=bookings)

@app.route('/book', methods=['POST'])
def book():
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    device = request.form.get('device')
    issue = request.form.get('issue')
    
    b_id = "RER" + datetime.now().strftime("%H%M%S")
    time_str = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    bookings[b_id] = {
        'name': name,
        'phone': phone,
        'address': address,
        'device': device,
        'issue': issue,
        'time': time_str
    }
    
    # WhatsApp message text formatting
    raw_msg = f"కొత్త రిపేర్ బుకింగ్ వచ్చింది!\n\nఐడీ: {b_id}\nపేరు: {name}\nఫోన్: {phone}\nఅడ్రస్: {address}\nపరికరం: {device}\nసమస్య: {issue}\nసమయం: {time_str}"
    wa_message = urllib.parse.quote(raw_msg)
    
    return render_template_string(HTML_TEMPLATE, role='customer', bookings=bookings, success_id=b_id, wa_message=wa_message)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "తప్పు యూజర్ నేమ్ లేదా పాస్‌వర్డ్!"
            
    return render_template_string(HTML_TEMPLATE, role='login', error=error)

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
        
    return render_template_string(HTML_TEMPLATE, role='admin', bookings=bookings)

@app.route('/logout')
def logout():
    session.pop('admin_logged', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
