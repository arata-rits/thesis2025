from flask import Flask, request, jsonify, render_template, url_for, redirect
import sqlite3
import os
import cv2
from pyzbar.pyzbar import decode
from datetime import datetime
from PIL import Image
import base64
import io
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
DB_PATH = 'db.sqlite3'

# SQLiteデータベースの初期化
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# # 画像を保存する関数
# def save_image(image_data):
#     # Base64で送られてきた画像データをデコードして保存
#     image_data = image_data.split(",")[1]
#     image = Image.open(io.BytesIO(base64.b64decode(image_data)))
#     filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
#     image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     image.save(image_path)
    
#     # データベースに保存
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute('INSERT INTO images (filename) VALUES (?)', (filename,))
#     conn.commit()
#     conn.close()
    
#     return image_path

def save_image_formdata(image):
    # POSTリクエストの中に 'image' ファイルが含まれているかを確認
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "画像ファイルがありません"}), 400
    
    image_file = request.files['image']

    # 撮影日時を取得してファイル名を設定
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # 例: "20241021213045"
    filename = f"{timestamp}.png"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # 画像ファイルを保存
    image_file.save(file_path)

    return file_path


# 色抽出と画像の保存
def extract_color_and_save_HSV(image_path, color_index):
    image = cv2.imread(image_path)
    color = hsv_extract_to_mono(image, color_index)
    color_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{['red', 'green', 'blue'][color_index]}.png"
    color_path = os.path.join(app.config['UPLOAD_FOLDER'], color_filename)
    cv2.imwrite(color_path, color)
    
    return color_path

# ====================================色の抽出をHSV空間で行う===================================================
def hsv_extract_to_mono(image, i):

    # jsonify({'status': 'error', 'message': '125まで実行'})

    # BGRからHSVに変換
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 赤要素の抽出
    if i == 0:
                # 白色範囲
        lower_white = np.array([0, 0, 100])
        upper_white = np.array([180, 60, 255])

        # 赤色範囲（0〜180の範囲で設定）
        lower_red1 = np.array([0, 80, 100])
        upper_red1 = np.array([15, 255, 255])
        lower_red2 = np.array([165, 80, 100])
        upper_red2 = np.array([180, 255, 255])

        # 黄色範囲
        lower_yellow = np.array([15, 80, 100])
        upper_yellow = np.array([45, 255, 255])

        # マゼンタ範囲
        lower_magenta = np.array([135, 80, 100])
        upper_magenta = np.array([165, 255, 255])

        # 各色のマスクを作成
        mask_white = cv2.inRange(hsv_image, lower_white, upper_white)
        mask_red1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
        mask_yellow = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
        mask_magenta = cv2.inRange(hsv_image, lower_magenta, upper_magenta)

        # 赤色の2つのマスクを結合
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        # 白、赤、黄、マゼンタのマスクを結合して黒にする領域を指定
        mask_to_black = cv2.bitwise_or(mask_white, mask_red)
        mask_to_black = cv2.bitwise_or(mask_to_black, mask_yellow)
        mask_to_black = cv2.bitwise_or(mask_to_black, mask_magenta)

        # すべての領域を白に塗りつぶし
        result = np.ones_like(image) * 255

        # マスクで指定された領域を黒に変換
        result[mask_to_black > 0] = [0, 0, 0]

        return result

    
    #緑要素の抽出
    elif i == 1:
        # 白色範囲
        lower_white = np.array([0, 0, 100])
        upper_white = np.array([180, 60, 255])

        # 緑色範囲（0〜180の範囲で設定）60
        lower_green = np.array([45, 80, 100])
        upper_green = np.array([75, 255, 255])

        # 黄色範囲
        lower_yellow = np.array([15, 80, 100])
        upper_yellow = np.array([45, 255, 255])

        # シアン範囲
        lower_magenta = np.array([85, 80, 100])
        upper_magenta = np.array([105, 255, 255])

        # 各色のマスクを作成
        mask_white = cv2.inRange(hsv_image, lower_white, upper_white)
        mask_green = cv2.inRange(hsv_image, lower_green, upper_green)
        mask_yellow = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
        mask_magenta = cv2.inRange(hsv_image, lower_magenta, upper_magenta)

        # 緑色の2つのマスクを結合
        # mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        # マスクを結合して黒にする領域を指定
        mask_to_black = cv2.bitwise_or(mask_white, mask_green)
        mask_to_black = cv2.bitwise_or(mask_to_black, mask_yellow)
        mask_to_black = cv2.bitwise_or(mask_to_black, mask_magenta)

        # すべての領域を白に塗りつぶし
        result = np.ones_like(image) * 255

        # マスクで指定された領域を黒に変換
        result[mask_to_black > 0] = [0, 0, 0]

        return result
    
    
    # 青要素の抽出
    elif i == 2:
        # 白色範囲
        lower_white = np.array([0, 0, 100])
        upper_white = np.array([180, 60, 255])

        # 青色範囲（0〜180の範囲で設定）120
        lower_blue = np.array([105, 80, 100])
        upper_blue = np.array([135, 255, 255])

        # シアン色範囲
        lower_yellow = np.array([75, 80, 100])
        upper_yellow = np.array([105, 255, 255])

        # マゼンタ範囲300
        lower_magenta = np.array([135, 80, 100])
        upper_magenta = np.array([165, 255, 255])

        # 各色のマスクを作成
        mask_white = cv2.inRange(hsv_image, lower_white, upper_white)
        mask_blue = cv2.inRange(hsv_image, lower_blue, upper_blue)
        mask_yellow = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
        mask_magenta = cv2.inRange(hsv_image, lower_magenta, upper_magenta)

        # 青色の2つのマスクを結合
        # mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        # マスクを結合して黒にする領域を指定
        mask_to_black = cv2.bitwise_or(mask_white, mask_blue)
        mask_to_black = cv2.bitwise_or(mask_to_black, mask_yellow)
        mask_to_black = cv2.bitwise_or(mask_to_black, mask_magenta)

        # すべての領域を白に塗りつぶし
        result = np.ones_like(image) * 255

        # マスクで指定された領域を黒に変換
        result[mask_to_black > 0] = [0, 0, 0]

        return result
    

# ==========================================================================================   

# Dilation（膨張）処理の後にErosion（収縮）処理を行う関数
def apply_dilation_then_erosion(image_path):
    image = cv2.imread(image_path, 0)  # 画像をグレースケールで読み込み
    kernel = np.ones((5, 5), np.uint8)  # カーネルサイズは調整可能です
    
    # Dilation処理
    dilated_image = cv2.dilate(image, kernel, iterations=1)
    
    # Erosion処理
    processed_image = cv2.erode(dilated_image, kernel, iterations=1)
    
    # 処理後の画像を保存
    processed_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_processed.png"
    processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
    cv2.imwrite(processed_path, processed_image)
    
    return processed_path

# QRコードを検出する関数
def detect_qr_code(image_path):
    image = cv2.imread(image_path)
    decoded_objects = decode(image)
    qr_codes = [obj.data.decode('utf-8') for obj in decoded_objects]
    return qr_codes

@app.route('/')
def index():
    return render_template('index_phone1106.html')


@app.route('/capture', methods=['POST'])
def capture():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "画像ファイルが見つかりません"}), 400
    
    color = request.form.get('color')
    image = request.files['image']
    # color_choice = data.get('color')  # 'red', 'green', or 'blue'
    color_index = {'red': 0, 'green': 1, 'blue': 2}[color]

    image_path = save_image_formdata(image)
    # mono_image_path = hsv_extract_to_mono(image_path, color_index)
    mono_image_path = extract_color_and_save_HSV(image_path, color_index)
    
     # DilationとErosion処理を実行
    processed_image_path = apply_dilation_then_erosion(mono_image_path)
    
    qr_codes = detect_qr_code(processed_image_path)


    if qr_codes:
        return jsonify({'status': 'success', 'qr_code': qr_codes[0]})
    else:
        return jsonify({'status': 'error', 'message': 'QRコードが検出されませんでした。'})


if __name__ == '__main__':
    # 証明書と秘密鍵のパスを指定
    context = ('server.crt', 'server.key')
    # HTTPSでサーバーを起動
    app.run(host='0.0.0.0', port=5000, ssl_context=context)