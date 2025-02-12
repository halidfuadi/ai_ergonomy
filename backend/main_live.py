from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
import numpy as np
from PIL import Image
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
from ergo_detection import VideoCamera
import cv2 
import uuid
import json

app = Flask(__name__, static_url_path='/DATA', static_folder='DATA')
CORS(app)
config_file = 'config.json'

@app.route('/live')
def livedet():
    return Response(cam.gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detect')
@cross_origin()
def detect():
    return {
        'message': 'okay',
        'detect': cam.get_list_all()
    }

@app.route('/start')
@cross_origin()
def start():
    cam.startButton()
    return {
        'message': 'okay_start',
    }

@app.route('/stop')
@cross_origin()
def stop():
    cam.stopButton()
    return {
        'message': 'okay_stop',
        'detect': cam.get_list_all()
    }

@app.route('/')
def index():
    return {
        'message': 'hello_worlds!',
        'file': "O"
    }

@app.route('/api/upload', methods=['POST'])
def upload_video():
    file = request.files['file']
    if file:
        try:
            uuid_data = str(uuid.uuid4())
            video_path = f'VIDIO_UPLOAD/video_{uuid_data}.mp4'
            file.save(video_path)
            result = cam.processVidioUpload(video_path)

            return jsonify({'message': 'Video processed successfully', 'detect': result})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'No file provided'}), 400

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'GET':
        try:
            with open(config_file, 'r') as file:
                config_data = json.load(file)
            return jsonify(config_data)
        except FileNotFoundError:
            return jsonify({'error': 'Config file not found'})
    elif request.method == 'POST':
        try:
            config_data = request.get_json()
            with open(config_file, 'w') as file:
                json.dump(config_data, file)
            return jsonify({'message': 'Config saved successfully'})
        except Exception as e:
            return jsonify({'error': str(e)})
  
@app.route('/change_camera/<camera_input>')
def change_camera(camera_input):
    if camera_input.isdigit():
        camera_index = int(camera_input)
        cam.camera = camera_index
        cam.reinitialize_camera()
        return f"Camera changed to index {camera_index}"
    else:
        cam.camera = camera_input
        cam.reinitialize_camera()
        return f"Camera changed to file {camera_input}"



if __name__ == "__main__":
    cam = VideoCamera(0, 640) #Ganti angka ke 0 untuk menggunakan kamera laptop, dan 1 untuk menggunakan kamera webcam
    app.run(host='0.0.0.0', debug=False, port=5001)
