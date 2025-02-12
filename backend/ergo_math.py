
import math

def calculate_perspective(joint_positions):
    left_pose_visible = sum(joint_positions[idx][2] for idx in [1, 3, 5, 7, 9, 11, 13, 15])
    right_pose_visible = sum(joint_positions[idx][2] for idx in [2, 4, 6, 8, 10, 12, 14, 16])

    nose_pose_visibility = joint_positions[0][2]
    left_eye_visibility = joint_positions[1][2]
    right_eye_visibility = joint_positions[2][2]

    if nose_pose_visibility > 0.9 and left_eye_visibility > 0.9 and right_eye_visibility > 0.9:
        return "Front"
    elif nose_pose_visibility < 0.6 and left_eye_visibility < 0.6 and right_eye_visibility < 0.6:
        return "Back"
    elif left_pose_visible > right_pose_visible:
        return "Left Side"
    elif right_pose_visible > left_pose_visible:
        return "Right Side"
    else:
        return "Unknown"
    
def calculate_angle(kpts, p1, p2, p3, quadrant=False):
    P1 = kpts[p1]
    P2 = kpts[p2]
    P3 = kpts[p3]
    # Hitung vektor antara titik-titik
    vector1 = (P1[0] - P2[0], P1[1] - P2[1])
    vector2 = (P3[0] - P2[0], P3[1] - P2[1])

    # Hitung produk titik dari vektor
    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]

    # Hitung besaran vektor
    magnitude1 = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
    magnitude2 = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)

    # Hitung kosinus sudut menggunakan perkalian titik dan besaran
    cosine_angle = dot_product / (magnitude1 * magnitude2)

    # Hitung sudut dalam radian menggunakan fungsi arccosine
    angle_rad = math.acos(cosine_angle)

    # Hitung sudut dalam derajat
    angle_deg = math.degrees(angle_rad)

    if quadrant:
        if angle_deg > 92:
            angle_deg = 180 - angle_deg
            return float(angle_deg)
        else:
            return float(angle_deg)
    else:
        return float(angle_deg)
    

def getAdvice(data, point_configuration):
    output = {}
    for key, values in data.items():
        threshold = point_configuration[key]['bad_pose']
        if threshold is not None:
            exceeds_threshold = any(value > threshold for value in values)
            output[key] = exceeds_threshold

        # Tambahkan evaluasi postur leher
    if "neck" in point_configuration:
        neck_threshold = point_configuration["neck"]["bad_pose"]
        neck_angle = data.get("neck", [0])[0]  # Ambil sudut leher pertama
        output["neck"] = neck_angle > neck_threshold

    return output

def get_neck_position(kpts):
    """Menghitung posisi leher sebagai titik tengah bahu kiri dan kanan."""
    shoulder_left = kpts[5]
    shoulder_right = kpts[6]

    neck_x = (shoulder_left[0] + shoulder_right[0]) / 2
    neck_y = (shoulder_left[1] + shoulder_right[1]) / 2
    neck_visibility = (shoulder_left[2] + shoulder_right[2]) / 2  # Rata-rata confidence

    return (neck_x, neck_y, neck_visibility)
