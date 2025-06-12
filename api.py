from fileinput import filename
import os
import cv2
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, redirect
from model.ocr import validate_nik as vn, extract_data as ed
from flask_cors import CORS

app  = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = 'pdf', 'png', 'jpg', 'jpeg'
UPLOAD_FOLDER = '/tmp/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/extract-ktp", methods=["POST"])
def extract_ktp():
    try:
        if 'image' not in request.files:
            print("❌ No image in request")
            return jsonify({"message": "No file uploaded"}), 400
        
        file = request.files['image']
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({"message": "No file name"}), 400
        
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            print(f"💾 Saving to: {save_path}")
            file.save(save_path)

            print(f"📷 Reading image...")
            process_img = cv2.imread(save_path, 0)
            if process_img is None:
                raise Exception("cv2.imread returned None. Check image format.")

            print("🔍 Running OCR extract_data")
            data = ed(process_img)

            return jsonify({
                "message": "Data extract successfully",
                "data": data
            })
        else:
            return jsonify({"message": "Invalid file type"})
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return jsonify({"message": f"Error processing image: {str(e)}"}), 500


@app.route("/validate-nik", methods=["POST"])
def validate_nik():
    if 'image' not in request.files:
        return jsonify({"message": "No file uploaded"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)
    if allowed_file(file.filename):
        # Save file to local storage/folder
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        try:
            process_img = cv2.imread(save_path,0)
            res = vn(process_img)
            if res:
                return jsonify({"message": "NIK valid"}) 
            else: 
                return jsonify({"message": "NIK tidak valid"})
        except Exception as e:
            return jsonify({"message": f"Error processing image: {str(e)}"}), 500
    else:
        return jsonify({"message": "Invalid file type"})



""" FOR DEVELOPMENT PURPOSE
    Code below used for further development. Use it by uncomment the code
"""
""" Endpoint -> /upload
    Keyword arguments:
    images -- multipart/form-data
    Return: response message that file uploaded to images folder.
"""
""
# @app.route("/upload", methods=["POST"])
# def validate_nik():
#     file = request.files['image']
#     if file.filename == '':
#         return redirect(request.url)
#     if allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(UPLOAD_FOLDER, filename))
#         response = {
#             "message":"Data Uploaded successfully",
#             "filename": filename
#         }
#     else:
#         response = {
#             "message": "Invalid file type"
#         }
#     return jsonify(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(debug=True, host="0.0.0.0", port=port)