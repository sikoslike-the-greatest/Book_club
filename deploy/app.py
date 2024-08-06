#!/bin/python3
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
import random
import string
import threading

app = Flask(__name__)
app.secret_key = 'sUp3rs3cRetk3Y<as]12@'

users = {
    1: {
        'id': 1,
        'username': 'admin',
        'email': 'admin-adsfad123weq@book-club.com',
        'password': 'Uc4n7Gue$$1Tlol',
        'books': [
            {'title': 'Secret Book', 'rating': 5, 'comment': 'Something interesting in private note...', 'private_note': 'Flag is in admin panel:)'}
        ]
    }
}

pending_logins = {}
generating_tokens = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if any(user['username'] == username for user in users.values()):
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('register'))

        if any(user['email'] == email for user in users.values()):
            flash('Email already registered. Please use a different email.', 'error')
            return redirect(url_for('register'))

        user_id = max(users.keys()) + 1
        users[user_id] = {'id': user_id, 'username': username, 'email': email, 'password': password, 'books': []}
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = next((user for user in users.values() if user['email'] == email and user['password'] == password), None)
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('profile', user_id=user['id']))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = users.get(user_id)
    if not user:
        return 'User not found', 404
    current_user = users.get(session['user_id'])
    return render_template('profile.html', user=user, current_user=current_user)

@app.route('/api/user/<int:user_id>/books')
def api_user_books(user_id):
    user = users.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user['books'])

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = users[session['user_id']]
    
    if user['username'] == 'admin':
        flash('Admin cannot add books.', 'error')
        return redirect(url_for('profile', user_id=session['user_id']))
    
    if request.method == 'POST':
        title = request.form['title']
        try:
            rating = int(request.form['rating'])
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except ValueError:
            flash('Invalid rating. Please enter a number between 1 and 5.', 'error')
            return redirect(url_for('add_book'))
        
        comment = request.form['comment']
        private_note = request.form['private_note']
        
        if any(book['title'].lower() == title.lower() for book in user['books']):
            flash('A book with this title already exists in your list.', 'error')
            return redirect(url_for('add_book'))
        
        new_book = {
            'title': title,
            'rating': rating,
            'comment': comment,
            'private_note': private_note
        }
        user['books'].append(new_book)
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('profile', user_id=session['user_id']))
    
    return render_template('add_book.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

def generate_token(email):
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    pending_logins[email] = token
    del generating_tokens[email]
    
@app.route('/login/byemail', methods=['POST'])
def login_by_email():
    email = request.form['email']
    if not any(user['email'] == email for user in users.values()):
        return 'Email not found', 404
    
    if email not in generating_tokens:
        generating_tokens[email] = True
        threading.Thread(target=generate_token, args=(email,)).start()
    
    return 'Token generation started'

@app.route('/login/byemail/verify', methods=['POST'])
def verify_email_login():
    email = request.form['email']
    token = request.form.get('token')
    
    if email in generating_tokens:
        # Токен все еще генерируется, уязвимость Race Condition
        for user in users.values():
            if user['email'] == email:
                session['user_id'] = user['id']
                return redirect(url_for('profile', user_id=user['id']))
    
    if email not in pending_logins:
        return 'No pending login for this email', 400
    
    if pending_logins[email] == token:
        for user in users.values():
            if user['email'] == email:
                session['user_id'] = user['id']
                del pending_logins[email]
                return redirect(url_for('profile', user_id=user['id']))
    
    return 'Invalid token', 400

@app.route('/admin')
def admin():
    if 'user_id' not in session or session['user_id'] != 1:
        return 'Access denied', 403
    with open('flag.txt','r') as f:
        return f'Admin panel. Flag: {f.readline()}'

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")