import pandas as pd
from sqlalchemy import create_engine, text

# Konfigurasi database PostgreSQL
DB_USER = "postgres"
DB_PASS = "zano0911"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"

# Buat koneksi database
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# === Anomaly Thresholds ===
ANOMALY_THRESHOLDS = {
    "arm_left": (None, 90),
    "arm_right": (None, 90),
    "backpose_left": (None, 30),
    "backpose_right": (None, 30),
    "leg_left": (None, 60),
    "leg_right": (None, 60),
    "neck_right": (None, 30),
    "neck_left": (None, 30)
}


def find_anomalous_seconds(grouped_df, body_part, lower, upper):
    """Mendeteksi detik yang memiliki anomali berdasarkan threshold."""
    anomalous_seconds = []
    prev_anomalous = False
    selected_second = None

    for _, row in grouped_df.iterrows():
        is_anomalous = (row[body_part] < lower) | (row[body_part] > upper) if lower is not None else (row[body_part] > upper)

        if is_anomalous:
            if not prev_anomalous:
                selected_second = row["second"]
            prev_anomalous = True
        else:
            if prev_anomalous and selected_second is not None:
                anomalous_seconds.append((selected_second, row[body_part]))
            prev_anomalous = False
            selected_second = None

    if prev_anomalous and selected_second is not None:
        anomalous_seconds.append((selected_second, grouped_df[grouped_df["second"] == selected_second][body_part].values[0]))

    return anomalous_seconds

def process_and_store_anomalies(unique_id):
    """
    1. Membaca file CSV berdasarkan `unique_id`.
    2. Menghitung median setiap detik untuk setiap bagian tubuh.
    3. Mendeteksi anomali berdasarkan threshold.
    4. Menyimpan hasil ke dalam database PostgreSQL.
    """

    csv_file = f"DATA/{unique_id}/output.csv"
    
    try:
        # === Load CSV ===
        df = pd.read_csv(csv_file)

        # === Tambahkan kolom detik (30 row = 1 detik) ===
        df["second"] = df.index // 30

        # === Hitung median per detik ===
        grouped_df = df.groupby("second").median().reset_index()

        # === Buat sesi baru di `sessions` ===
        with engine.connect() as conn:
            result = conn.execute(text("INSERT INTO sessions (activity_name) VALUES ('Memasang Baut') RETURNING id;"))
            session_id = result.scalar()  # Ambil session_id
            conn.commit()

        print(f"Sesi baru dibuat dengan ID: {session_id}")

        # === Cari anomali dan masukkan ke database ===
        anomalies = []

        for body_part, (lower, upper) in ANOMALY_THRESHOLDS.items():
            anomalous_seconds = find_anomalous_seconds(grouped_df, body_part, lower, upper)

            for second, anomalous_angle in anomalous_seconds:
                # Menentukan status postur
                posture_status = "NG" if (lower is None and anomalous_angle > upper) or (lower is not None and (anomalous_angle < lower or anomalous_angle > upper)) else "Good"

                anomalies.append({
                    "session_id": session_id,
                    "second": second,
                    "body_part": body_part,
                    "anomalous_angle": anomalous_angle,
                    "posture_status": posture_status
                })

        # === Simpan ke Database ===
        anomalies_df = pd.DataFrame(anomalies)
        if not anomalies_df.empty:
            anomalies_df.to_sql("posture_anomalies", con=engine, if_exists="append", index=False)

        print("Data anomali berhasil disimpan ke database!")

    except Exception as e:
        print(f"❌ Error saat memproses CSV {csv_file}: {e}")

def get_all_posture_data():
    query = """
        SELECT pa.*, s.activity_name FROM posture_anomalies pa
        JOIN sessions s ON pa.session_id = s.id
        ORDER BY pa.session_id, pa.second
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df.to_dict(orient="records")