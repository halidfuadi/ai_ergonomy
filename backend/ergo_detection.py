import cv2
import uuid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import glob 
from ultralytics import YOLO 
#from utils_ergo import createFolder, draw_circle, draw_line, skeletons, color_list, calculate_angle, findDirection, color_pallete, point_configuration, angle_cluster, convert_dict_to_csv, getAdvice, calculate_perspective, add_text_to_image, angle_ranges, extract_time
from ergo_config import skeletons, color_pallete, color_list, point_configuration, angle_cluster, angle_ranges
from ergo_draw import draw_circle, draw_line, add_text_to_image
from ergo_math import calculate_angle, calculate_perspective, getAdvice
from ergo_utils import createFolder, convert_dict_to_csv, extract_time
import random 
import time

class VideoCamera():
    def __init__(self, camera, size):
       # Menyimpan parameter kamera yang diberikan ke dalam variabel instance
        self.camera = camera
        # Menyimpan ukuran yang diberikan ke dalam variabel instance
        self.size = size
        # Membuat objek VideoCapture dengan parameter kamera
        self.video = cv2.VideoCapture(camera)
        # Mengatur codec video ke MJPG
        self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        # Memuat model YOLO untuk deteksi objek
        self.model = YOLO('runs/pose/train/weights/best.pt') 
        # Inisialisasi dictionary untuk menyimpan data pendeteksian
        self.data_detect = dict()
        # Inisialisasi status mulai sebagai False
        self.start = False
        # Inisialisasi ID unik sebagai string kosong
        self.unique_id = ''
        # Inisialisasi dictionary untuk menyimpan data akhir
        self.final_data = {
            'unique_id': '-',
            'pie_graph': '',
            'image_sample': [],
            'start': False,
            'ergo_status': dict(),
            'all_images': []
        }
        # Inisialisasi dictionary untuk menyimpan waktu mulai badpose
        self.bad_action_start_times = {}
        # Inisialisasi dictionary untuk menyimpan data
        self.data = dict()
        # Inisialisasi list untuk menyimpan frame yang diproses
        self.processed_frames = []
        # Menyimpan waktu mulai
        self.start_time = time.time()
        # Menyimpan URL prefix
        self.url_prefix = "http://127.0.0.1:5001/"

    def createGraph(self, data_dict, unique_id):
        # Menggabungkan data
        # Membuat dictionary kosong untuk menyimpan data yang telah digabungkan
        combined_data = {}
        # Iterasi melalui setiap kunci dalam dictionary data_dict
        for key in data_dict:
            # Mengambil awalan key (sebelum underscore)
            prefix = key.split("_")[0]
            # Jika awalan sudah ada di combined_data, tambahkan data ke kunci tersebut
            if prefix in combined_data:
                combined_data[prefix].extend(data_dict[key])
            # Jika tidak, buat kunci baru dengan awalan dan data yang ada
            else:
                combined_data[prefix] = data_dict[key]

        # Menyimpan daftar judul berdasarkan kunci dari combined_data
        title = list(combined_data.keys())

        # Menghitung jumlah subplots yang dibutuhkan
        num_subplots = len(combined_data)

        # Membuat subplots untuk grafik pie
        fig, axs = plt.subplots(1, num_subplots, figsize=(6 * num_subplots, 4))

        # Iterasi melalui dictionary data yang digabungkan
        try:
            for i, (keys, data) in enumerate(combined_data.items()):
                # Inisialisasi panjang cluster
                ranges = angle_ranges[keys]
                cluster_lengths = [0] * len(ranges)

                # Mengelompokkan sudut ke dalam cluster
                for angle in data:
                    for j, angle_range in enumerate(ranges):
                        if angle_range[0] <= angle < angle_range[1]:
                            cluster_lengths[j] += 1
                            break

                # Menentukan warna untuk setiap range
                colors = ['green', 'yellow', 'red']

                # Membuat grafik pie di subplot yang sesuai
                axs[i].pie(cluster_lengths, explode=(0.05, 0.05, 0.1), labels=[f'{angle_range[0]}°-{angle_range[1]}°' for angle_range in ranges], counterclock=False, startangle=90, colors=colors, autopct='%1.1f%%')
                axs[i].set_aspect('equal')
                axs[i].set_title(f'Pie Chart {title[i].upper()} Angle')
        except Exception as e:
            print(e)

        # Mengatur jarak antara subplots
        plt.tight_layout()
        # Menyimpan grafik sebagai gambar png
        plt.savefig(f"DATA/{unique_id}/figpie.png")
        plt.close(fig)

    def randomImageSample(self, unique_id):
        # Mendapatkan semua file jpeg dalam direktori dengan unique_id
        total = glob.glob(f'DATA/{unique_id}/*.jpeg')
        # Memfilter gambar yang berhubungan dengan arm
        arm_images = [image for image in total if 'arm_' in image]
        # Memfilter gambar yang berhubungan dengan backpose
        backpose_images = [image for image in total if 'backpose_' in image]

        # Memilih satu gambar acak dari arm dan backpose
        random_arm_image = random.choice(arm_images) if arm_images else None
        random_backpose_image = random.choice(backpose_images) if backpose_images else None

        # Menyimpan gambar yang dipilih ke dalam list
        random_image = []

        if random_arm_image:
            random_image.append(random_arm_image)

        if random_backpose_image:
            random_image.append(random_backpose_image)

        # Mengembalikan list gambar yang dipilih
        return random_image

    def saveImg(self, key, img, unique_id, time):
        # Menghitung jumlah gambar yang sudah ada dengan unique_id
        total = glob.glob(f'DATA/{unique_id}/{key}_*')
        n = len(total)
        # Menyimpan gambar ke direktori
        cv2.imwrite(f"DATA/{unique_id}/{key}_{n}_{time}.jpeg", img)

    def startButton(self):
        # Inisialisasi awal sebelum perekaman dimulai
        self.unique_id = ''
        self.start = True
        self.start_time = time.time()
        self.data = dict()
        self.unique_id = str(uuid.uuid4())
        self.final_data = {
            'unique_id': self.unique_id,
            'pie_graph': '',
            'image_sample': [''],
            'start': True,
            'ergo_status': dict(),
            'all_images': []
        }
        # Membuat folder dengan unique_id sebagai nama
        createFolder(self.unique_id)

    def saveWid(self, unique_id):
        # Mendapatkan informasi video seperti fps, lebar, dan tinggi frame
        fps = self.video.get(cv2.CAP_PROP_FPS)
        width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # Menentukan codec untuk menyimpan video
        # fourcc = cv2.VideoWriter_fourcc(*'H264')
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        # Menentukan path untuk menyimpan video yang diproses
        processed_video_path = f'DATA/{unique_id}/processed_video.mp4'
        # Membuat objek VideoWriter untuk menyimpan video
        writer = cv2.VideoWriter(processed_video_path, fourcc, fps, (width, height))
        # Menulis frame yang telah diproses ke file video
        for frame in self.processed_frames:
            writer.write(frame)
        # Menutup writer
        writer.release()

    def stopButton(self):
        # Aksi yang dilakukan ketika tombol stop ditekan
        self.start = False
        # Mengambil sampel gambar secara acak
        image_sample = self.randomImageSample(self.unique_id)
        try:
            # Membuat grafik, mengonversi data ke CSV, dan menyimpan video
            self.createGraph(self.data, self.unique_id)
            convert_dict_to_csv(self.data, self.unique_id)
            self.saveWid(self.unique_id)
        except Exception as e:
            print("GRAPH DICT CSV ", e)
        # Mengosongkan daftar frame yang telah diproses
        self.processed_frames = []
        # Menyusun data akhir untuk dikirim sebagai respon
        self.final_data = {
            'unique_id': self.unique_id,
            'pie_graph': f"{self.url_prefix}DATA/{self.unique_id}/figpie.png",
            'image_sample': image_sample,
            'start': False,
            'ergo_status': getAdvice(self.data, point_configuration),
            'csv_data': f"{self.url_prefix}DATA/{self.unique_id}/output.csv",
            'all_images': sorted(glob.glob(f'DATA/{self.unique_id}/*.jpeg'), key=extract_time)
        }

    def get_list_all(self):
        # Return kembali data final
        return self.final_data

    def get_frame(self):
        try:
            self.success, self.frame = self.video.read(cv2.IMREAD_ANYCOLOR)
            self.frame_original = self.frame.copy()
            self.orr = self.frame
        except Exception as e:
            print("EXCEPTION TRIGGERED!", e)
            self.video.release()
            self.video = cv2.VideoCapture(self.camera)
            self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
            self.success, self.frame = self.video.read(cv2.IMREAD_ANYCOLOR)
            self.frame_original = self.frame.copy()
            self.orr = self.frame
        
        try:
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            
            if self.start:
                # Get model results
                self.results = self.model(self.frame)
                
                # Check if any detections exist
                if len(self.results) > 0 and len(self.results[0].keypoints.data) > 0:
                    # Extract keypoints properly from YOLO format
                    # Convert to numpy and get the first person's keypoints
                    keypoints_data = self.results[0].keypoints.data.cpu().numpy()
                    if len(keypoints_data) > 0:
                        self.kpts = keypoints_data[0]  # Shape should be (17, 3) for YOLO pose
                        
                        # Draw visualizations only if keypoints are valid
                        if self.kpts is not None and len(self.kpts) > 0:
                            # Convert keypoints to the expected format if needed
                            keypoints_xy = self.kpts[:, :2]  # Only take x,y coordinates
                            draw_circle(frame=self.orr, kpts=keypoints_xy)
                            draw_line(frame=self.orr, kpts=keypoints_xy)
                            
                            # Calculate elapsed time
                            elapsed_time = int(time.time() - self.start_time)
                            elapsed_time = time.strftime("%H.%M.%S", time.gmtime(elapsed_time))
                            cv2.putText(self.orr, f"TIME :{elapsed_time}", (10, 3*50), 1, 1, (255,255,255), 1)
                            
                            # Process each point configuration
                            for key in point_configuration.keys():
                                if point_configuration[key]['active']:
                                    key_dict = key
                                    key_angle = key.split('_')[0]
                                    
                                    if key_dict not in self.data:
                                        self.data[key_dict] = []
                                    
                                    try:
                                        # Pass only x,y coordinates to angle calculation
                                        angle = calculate_angle(keypoints_xy, 
                                                            *point_configuration[key]['points'],
                                                            quadrant=point_configuration[key]['quadrant'])
                                        
                                        if isinstance(angle, (int, float)):  # Verify angle is a number
                                            self.data[key_dict].append(angle)
                                            
                                            # Update color palette based on angle
                                            if angle_cluster[key_angle][0] <= angle <= angle_cluster[key_angle][1]:
                                                for c in point_configuration[key]['color_pallete']:
                                                    color_pallete[c] = 1
                                            elif angle_cluster[key_angle][1] < angle <= angle_cluster[key_angle][2]:
                                                for c in point_configuration[key]['color_pallete']:
                                                    color_pallete[c] = 3
                                                    if angle > point_configuration[key]['bad_pose']:
                                                        color_pallete[c] = 2
                                                        self._handle_bad_pose(key_dict, elapsed_time)
                                            else:
                                                for c in point_configuration[key]['color_pallete']:
                                                    color_pallete[c] = 2
                                                    if angle > point_configuration[key]['bad_pose']:
                                                        self._handle_bad_pose(key_dict, elapsed_time)
                                    except Exception as e:
                                        print(f"Error processing angle for {key}: {e}")
                            
                            # Add text annotations with keypoints_xy instead of self.kpts
                            add_text_to_image(self.orr, self.data, calculate_perspective(keypoints_xy))
                
                # Always append the processed frame
                self.processed_frames.append(self.orr)
                
            ret, jpeg = cv2.imencode('.jpg', self.orr)
            return jpeg.tobytes(), self.orr
        
        except Exception as e:
            print("Frame processing error:", e)
            ret, jpeg = cv2.imencode('.jpg', self.orr)
            return jpeg.tobytes(), self.orr

    def _handle_bad_pose(self, key_dict, elapsed_time):
        """Helper method to handle bad pose detection and image saving"""
        if key_dict not in self.bad_action_start_times:
            self.bad_action_start_times[key_dict] = time.time()
        elif time.time() - self.bad_action_start_times[key_dict] > 1:
            try:
                self.saveImg(key_dict, self.orr, self.unique_id, elapsed_time)
                self.bad_action_start_times.pop(key_dict, None)

            except Exception as e:
                print(f"Error saving image for bad pose: {e}")

    def processVidioUpload(self, path):
        # Membuat dictionary untuk menyimpan data yang dihasilkan
        data_vid = dict()
        # Membuat ID unik untuk setiap proses unggah
        unique_id = str(uuid.uuid4())
        # Membuat folder dengan unique_id sebagai nama
        createFolder(unique_id)
        # Dictionary untuk menyimpan waktu mulai badpose
        bad_action_start_times = {}
        # Membuka video dari path yang diberikan
        video = cv2.VideoCapture(path)
        # Menghitung jumlah frame dalam video
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        # Mengambil frame per detik (fps) dari video
        fps = video.get(cv2.CAP_PROP_FPS)
        # Mengambil lebar dan tinggi frame dari video
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # Menentukan codec untuk video output
        # fourcc = cv2.VideoWriter_fourcc(*'H264')
        fourcc = cv2.VideoWriter_fourcc(*'avc1')

        # Menghitung durasi video dalam detik
        durations = int((frame_count / fps) % 60)

        # List untuk menyimpan frame yang telah diproses
        processed_frames = []
        self.start_time = time.time()
        # Iterasi melalui setiap frame dalam video
        for _ in range(frame_count):
            ret, frame = video.read()
            if ret:
                # Menghitung waktu 
                elapsed_time = int(time.time() - self.start_time)
                elapsed_time = time.strftime("%H.%M.%S", time.gmtime(elapsed_time))
                try:
                    # Mendeteksi keypoints pada frame dengan model
                    results = self.model(frame)
                    kpts = results[0].keypoints[0]
                    # Menggambar lingkaran dan garis pada frame berdasarkan keypoints
                    draw_circle(frame=frame, kpts=kpts)
                    draw_line(frame=frame, kpts=kpts)
                    cv2.putText(frame,f"TIME : {elapsed_time}", (10, 3*50), 1, 1, (255,255,255), 1)
                    # Memproses setiap konfigurasi titik
                    for key in point_configuration.keys():
                        active_status = point_configuration[key]['active']
                        key_dict = key
                        key_angle = key.split('_')[0]
                        if key_dict not in data_vid.keys():
                            data_vid[key_dict] = []
                        # Memeriksa status aktif dan menghitung sudut
                        if active_status == True:
                            angle = calculate_angle(kpts, *point_configuration[key]['points'], quadrant=point_configuration[key]['quadrant'])
                            data_vid[key_dict].append(angle)
                            # Memeriksa rentang sudut dan menetapkan warna berdasarkan sudut
                            # juga menyimpan gambar jika sudut menunjukkan pose yang buruk
                            if angle >= angle_cluster[key_angle][0] and angle <= angle_cluster[key_angle][1]:
                                for c in point_configuration[key]['color_pallete']:
                                    color_pallete[c] = 1
                            elif angle >= angle_cluster[key_angle][1] and angle <= angle_cluster[key_angle][2]:
                                for c in point_configuration[key]['color_pallete']:
                                    color_pallete[c] = 3
                                if angle > point_configuration[key]['bad_pose']:
                                    for c in point_configuration[key]['color_pallete']:
                                        color_pallete[c] = 2
                                    if key_dict not in bad_action_start_times.keys():
                                        bad_action_start_times[key_dict] = time.time()
                                    elif time.time() - bad_action_start_times[key_dict] > 1:
                                        try:
                                            self.saveImg(key, frame, unique_id, elapsed_time)
                                            bad_action_start_times.pop(key_dict, None)
                                        except Exception as e:
                                            print("EXCEPT SAVE IMG ", e)
                            elif angle > angle_cluster[key_angle][2]:
                                for c in point_configuration[key]['color_pallete']:
                                    color_pallete[c] = 2
                                if angle > point_configuration[key]['bad_pose']:
                                    for c in point_configuration[key]['color_pallete']:
                                        color_pallete[c] = 2
                                    if key_dict not in bad_action_start_times.keys():
                                        bad_action_start_times[key_dict] = time.time()
                                    elif time.time() - bad_action_start_times[key_dict] > 1:
                                        try:
                                            self.saveImg(key, frame, unique_id, elapsed_time)
                                            bad_action_start_times.pop(key_dict, None)
                                        except Exception as e:
                                            print("EXCEPT SAVE IMG ", e)
                    # Menambahkan teks ke frame berdasarkan data yang dihasilkan
                    add_text_to_image(frame, data_vid, calculate_perspective(kpts))
                    # Menambahkan frame yang telah diproses ke list
                    processed_frames.append(frame)
                except Exception as e:
                    # Jika terjadi kesalahan, tetap simpan frame dan lanjutkan
                    processed_frames.append(frame)
        try:
            # Menyimpan video yang telah diproses ke file mp4
            processed_video_path = f'DATA/{unique_id}/processed_video.mp4'
            writer = cv2.VideoWriter(processed_video_path, fourcc, fps, (width, height))
            for frame in processed_frames:
                writer.write(frame)
            writer.release()
            # Membuat grafik dari data yang dihasilkan
            self.createGraph(data_vid, unique_id)
            # Mengonversi dictionary data ke file CSV
            convert_dict_to_csv(data_vid, unique_id)
            # Mengambil sampel gambar acak
            image_sample = self.randomImageSample(unique_id)
        except Exception as e:
            print(e)

        # Mengembalikan dictionary dengan informasi tentang proses yang selesai
        return {
            'unique_id': unique_id,
            'pie_graph': f"{self.url_prefix}DATA/{unique_id}/figpie.png",
            'image_sample': image_sample,
            'ergo_status': getAdvice(data_vid, point_configuration),
            'vide_url': f"{self.url_prefix}DATA/{unique_id}/processed_video.mp4",
            'time': durations,
            'csv_data': f"{self.url_prefix}DATA/{unique_id}/output.csv",
            'all_images': sorted(glob.glob(f'DATA/{unique_id}/*.jpeg'), key=extract_time)
        }

    def gen(self):
        while True:
            frame,_ = self.get_frame()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    
    def reinitialize_camera(self):
        self.video.release()
        self.video = cv2.VideoCapture(self.camera)
        self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        self.success, self.frame = self.video.read(cv2.IMREAD_ANYCOLOR)
        self.frame_original = self.frame.copy()
        self.orr = self.frame