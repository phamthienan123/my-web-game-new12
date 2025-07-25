from flask import Flask, render_template, request, redirect, session
import json, os

app = Flask(__name__)
app.secret_key = 'matkhau_bimat'

# Load users
if os.path.exists('users.json'):
    with open('users.json', 'r') as f:
        USERS = json.load(f)
else:
    USERS = {
        "admin": {
            "password": "admin",
            "item": 1000,
            "inventory": []
        }
    }
    with open('users.json', 'w') as f:
        json.dump(USERS, f)

# Load items
if os.path.exists('items.json'):
    with open('items.json', 'r') as f:
        ITEMS = json.load(f)
else:
    ITEMS = {
        "kiếm rồng": {"buy": 20, "sell": 10},
        "giáp vàng": {"buy": 35, "sell": 18},
        "khiên băng": {"buy": 40, "sell": 20}
    }
    with open('items.json', 'w') as f:
        json.dump(ITEMS, f)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USERS and USERS[username]['password'] == password:
            session['username'] = username
            if username == 'admin':
                return redirect('/admin')
            return redirect('/home')
        else:
            error = 'Sai tài khoản hoặc mật khẩu!'
    return render_template('index.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USERS:
            error = 'Tài khoản đã tồn tại!'
        else:
            USERS[username] = {"password": password, "item": 0, "inventory": []}
            with open('users.json', 'w') as f:
                json.dump(USERS, f)
            return redirect('/')
    return render_template('register.html', error=error)

@app.route('/home')
def home():
    if 'username' not in session or session['username'] == 'admin':
        return redirect('/')
    user = USERS[session['username']]
    return render_template('home.html', username=session['username'], diamonds=user['item'], inventory=user['inventory'], items=ITEMS)

@app.route('/buy/<item>', methods=['POST'])
def buy(item):
    if 'username' not in session or session['username'] == 'admin':
        return redirect('/')
    username = session['username']
    user = USERS[username]
    if item in ITEMS and item not in user['inventory']:
        price = ITEMS[item]['buy']
        if user['item'] >= price:
            user['item'] -= price
            user['inventory'].append(item)
            with open('users.json', 'w') as f:
                json.dump(USERS, f)
    return redirect('/home')

@app.route('/sell/<item>', methods=['POST'])
def sell(item):
    if 'username' not in session or session['username'] == 'admin':
        return redirect('/')
    username = session['username']
    user = USERS[username]
    if item in user['inventory']:
        sell_price = ITEMS[item]['sell']
        user['item'] += sell_price
        user['inventory'].remove(item)
        with open('users.json', 'w') as f:
            json.dump(USERS, f)
    return redirect('/home')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'username' not in session or session['username'] != 'admin':
        return redirect('/')
    if request.method == 'POST':
        for item in ITEMS:
            buy_key = f"{item}_buy"
            sell_key = f"{item}_sell"
            if buy_key in request.form and sell_key in request.form:
                try:
                    ITEMS[item]['buy'] = int(request.form[buy_key])
                    ITEMS[item]['sell'] = int(request.form[sell_key])
                except:
                    pass
        with open('items.json', 'w') as f:
            json.dump(ITEMS, f)
    users = {u: USERS[u] for u in USERS if u != 'admin'}
    return render_template('admin.html', users=users, items=ITEMS)

@app.route('/give/<username>', methods=['POST'])
def give(username):
    if 'username' not in session or session['username'] != 'admin':
        return redirect('/')
    amount = int(request.form.get('amount', 0))
    if username in USERS:
        USERS[username]['item'] += amount
        with open('users.json', 'w') as f:
            json.dump(USERS, f)
    return redirect('/admin')

@app.route('/delete/<username>')
def delete(username):
    if 'username' not in session or session['username'] != 'admin':
        return redirect('/')
    if username in USERS and username != 'admin':
        del USERS[username]
        with open('users.json', 'w') as f:
            json.dump(USERS, f)
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
