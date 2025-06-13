import os
os.environ['TORCH_HOME'] = '/tmp/torch'
os.environ['EASYOCR_CACHE_DIR'] = '/tmp/.EasyOCR'
import cv2
import easyocr
import difflib

# Set environment agar EasyOCR & Torch cache disimpan di folder /tmp (writable)


# Definisikan seluruh key yang muncul pada KTP
expected_keys = [
    'NIK', 'Nama', 'Tempat/Tgl Lahir', 'Jenis Kelamin', 'Alamat', 'RT/RW',
    'Kel/Desa', 'Kecamatan', 'Agama', 'Status Perkawinan', 'Pekerjaan',
    'Kewarganegaraan', 'Berlaku Hingga'
]

def preprocess(img):
    # Grayscaling
    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return grayscale

# Fungsi untuk mengekstrak data pada KTP
def extract_data(img):
    extracted_data = {}
    reader = easyocr.Reader(['id'])
    results = reader.readtext(img)

    for i, (bbox, text, _) in enumerate(results):
        cleaned_text = text.strip()
        if ":" in cleaned_text:
            fragment = cleaned_text.split(":", 1)
            raw_key = fragment[0].strip()
            raw_value = fragment[1].strip()

            # Fuzzy match pada key
            matches = difflib.get_close_matches(raw_key, expected_keys, n=1, cutoff=0.8)
            if matches:
                key = matches[0]
                extracted_data[key] = raw_value
            continue

        # Fuzzy match jika format tidak pakai ":"
        matches = difflib.get_close_matches(cleaned_text, expected_keys, n=1, cutoff=0.8)
        if matches:
            key = matches[0]
            key_y = (bbox[0][1] + bbox[2][1]) / 2

            for j in range(i + 1, len(results)):
                value_bbox, value_text, _ = results[j]
                value_y = (value_bbox[0][1] + value_bbox[2][1]) / 2

                if abs(key_y - value_y) < 20:
                    extracted_data[key] = value_text.strip()
                    break
            else:
                extracted_data[key] = ""
    return extracted_data

# Fungsi untuk ekstraksi NIK dari gambar
def extract_nik(img):
    target_field = "NIK"
    reader = easyocr.Reader(['id'])
    results = reader.readtext(img)

    for i, (_, text, _) in enumerate(results):
        if target_field.lower() in text.lower():
            if i + 1 < len(results):
                return results[i + 1][1].strip()

# Fungsi untuk validasi jumlah digit NIK
def validate_nik(img):
    nik_number = extract_nik(img)
    return len(nik_number) == 16 if nik_number else False


"""
    CODE BELOW USED FOR TESTING PURPOSE
    UNCOMMENT IF YOU WANT TO TEST AND COMPARE THE OCR
"""
# img = cv2.imread("images/sample.png")

# def test_ocr(img):
#     reader = easyocr.Reader(['id'])
#     results = reader.readtext(img)
#     for i, (_, text, _) in enumerate(results):
#         print(text)

# gray_img = preprocess(img)
# print(validate_nik(gray_img))
# print(extract_data(img))
# print(test_ocr(img))
# plt.imshow(gray_img)
# plt.show()
