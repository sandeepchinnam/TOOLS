from flask import Flask, request, redirect, render_template, url_for
from io import BytesIO
import qrcode
import base64
import pyshorteners
import string
import random

app = Flask(__name__)
base_url = "" 

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choices(characters, k=length))
    return password

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['url']
        features = qrcode.QRCode(version=1, box_size=10, border=3)
        features.add_data(url)
        features.make(fit=True)
        generate_image = features.make_image(fill_color="black", back_color="white")
        img_buffer = BytesIO()
        generate_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        return render_template('index.html', qr_code=img_base64)
    return render_template('index.html')

@app.route('/shorten', methods=['GET', 'POST'])
def shorten_url():
    if request.method == 'POST':
        original_url = request.form['url']
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(original_url)
        return render_template('shorten.html', short_url=short_url)
    return render_template('shorten.html')

@app.route('/password', methods=['GET', 'POST'])
def generate_password_route():
    if request.method == 'POST':
        length = int(request.form['length'])
        password = generate_password(length)
        return render_template('password.html', password=password)
    return render_template('password.html')

@app.route('/<short_url>')
def redirect_to_url(short_url):
    return "URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)
