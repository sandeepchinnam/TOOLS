from flask import Flask, request, redirect, render_template, url_for, send_from_directory
from io import BytesIO
import os
import qrcode
import base64
import pyshorteners
import string
import random
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename

app = Flask(__name__)
base_url = ""
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

@app.route('/jpg_png')
def jpg_png():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('JPG_PNG.html', files=files)

@app.route('/convert_jpg_to_png', methods=['POST'])
def convert_jpg_to_png():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        img = Image.open(filepath)
        png_filename = f"{os.path.splitext(filename)[0]}.png"
        png_filepath = os.path.join(app.config['UPLOAD_FOLDER'], png_filename)
        img.save(png_filepath, 'PNG', quality=70)
        
        return redirect(url_for('jpg_png'))

@app.route('/convert_png_to_jpg', methods=['POST'])
def convert_png_to_jpg():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        img = Image.open(filepath)
        jpg_filename = f"{os.path.splitext(filename)[0]}.jpg"
        jpg_filepath = os.path.join(app.config['UPLOAD_FOLDER'], jpg_filename)
        img = img.convert('RGB')
        img.save(jpg_filepath, 'JPEG', quality=70)
        
        return redirect(url_for('jpg_png'))

@app.route('/convert_pdf_to_jpg', methods=['POST'])
def convert_pdf_to_jpg():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        images = convert_from_path(filepath)
        for i, image in enumerate(images):
            jpg_filename = f"{os.path.splitext(filename)[0]}_{i + 1}.jpg"
            jpg_filepath = os.path.join(app.config['UPLOAD_FOLDER'], jpg_filename)
            image.save(jpg_filepath, 'JPEG', quality=70)
        
        return redirect(url_for('jpg_png'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/<short_url>')
def redirect_to_url(short_url):
    return "URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)
