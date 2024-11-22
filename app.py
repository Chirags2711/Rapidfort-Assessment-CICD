import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from docx2pdf import convert
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_and_protect(docx_path, output_pdf_path, password=None):
    """
    Convert .docx to .pdf using docx2pdf and optionally add a password to the PDF.
    
    Args:
        docx_path (str): Path to the input .docx file.
        output_pdf_path (str): Path to save the converted .pdf file.
        password (str, optional): Password to encrypt the PDF. Defaults to None.
    """
    try:
        # Convert .docx to .pdf
        convert(docx_path, output_pdf_path)

        # Add password protection if a password is provided
        if password:
            # Read the existing PDF
            reader = PdfReader(output_pdf_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            # Encrypt the PDF with the password
            writer.encrypt(password)

            # Save the password-protected PDF
            with open(output_pdf_path, "wb") as f:
                writer.write(f)

        print(f"Conversion successful! PDF saved at: {output_pdf_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise ValueError(f"Failed to convert and protect PDF: {e}")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    password = request.form.get('password')  # Get the password if provided

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.pdf')

        file.save(file_path)

        try:
            # Convert and protect the PDF
            convert_and_protect(file_path, pdf_path, password=password)
            return send_file(pdf_path, as_attachment=True)
        except ValueError as e:
            return jsonify({'error': f"File conversion failed: {e}"}), 500

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)