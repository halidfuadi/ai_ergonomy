# AI ERGONOMY

AI Ergonomy adalah sistem yang mendeteksi postur duduk ergonomis menggunakan AI. Proyek ini terdiri dari backend berbasis Python (Flask) dan frontend berbasis Next.js.

## 📌 Fitur
- **Deteksi Postur**: Mengidentifikasi postur duduk pengguna menggunakan YOLO dan memberikan umpan balik.
- **Analisis Data**: Menyimpan dan menganalisis data postur pengguna.
- **Antarmuka Interaktif**: Frontend yang intuitif untuk memantau dan mendapatkan rekomendasi.

---

## 🛠️ Instalasi & Menjalankan Proyek

### 🔹 Instalasi dan Menjalankan Proyek
Jika Anda baru pertama kali menjalankan proyek ini, gunakan langkah-langkah berikut:

#### Windows
Jalankan file batch `install_and_run.bat`:
```sh
install_and_run.bat
```
Skrip ini akan menginstal dependensi dan menjalankan backend serta frontend.

#### Linux/macOS
Gunakan perintah berikut:
```sh
chmod +x install_and_run.sh
./install_and_run.sh
```

### 🔹 Jalankan Tanpa Instalasi
Jika semua dependensi telah diinstal sebelumnya, gunakan skrip berikut untuk langsung menjalankan proyek:

#### Windows
Jalankan file batch `run_ai_ergonomy.bat`:
```sh
run_ai_ergonomy.bat
```
Skrip ini akan otomatis menjalankan backend dan frontend.

#### Linux/macOS
Gunakan perintah berikut:
```sh
chmod +x run_ai_ergonomy.sh
./run_ai_ergonomy.sh
```

### 🔹 Backend (Manual)
1. Masuk ke direktori backend:
   ```sh
   cd backend
   ```
2. Buat dan aktifkan virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # Untuk Mac/Linux
   venv\Scripts\activate     # Untuk Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Jalankan backend:
   ```sh
   python main_live.py
   ```

### 🔹 Frontend (Manual)
1. Masuk ke direktori frontend:
   ```sh
   cd frontend
   ```
2. Install dependencies:
   ```sh
   npm i
   ```
3. Jalankan aplikasi:
   ```sh
   npm run dev
   ```

---

## 🚀 Teknologi yang Digunakan
- **Backend**: Flask, PostgreSQL
- **Frontend**: Next.js
- **Machine Learning**: YOLO untuk deteksi postur

---

## 🔍 Cara Kerja
1. **Pendeteksian Postur**: Kamera menangkap gambar pengguna dan YOLO digunakan untuk mendeteksi posisi tubuh.
2. **Analisis Data**: Data postur yang dideteksi dikirim ke backend untuk diproses dan disimpan di database PostgreSQL.
3. **Umpan Balik**: Frontend mengambil data dari backend dan menampilkan status postur pengguna serta memberikan rekomendasi jika diperlukan.

---
