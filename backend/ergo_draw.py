import cv2
from ergo_config import skeletons, color_list, color_pallete

def draw_line(frame, kpts):
    """
    Draw skeleton lines using existing skeleton configuration
    
    Args:
        frame: The image frame to draw on
        kpts: Keypoints from YOLO pose detection
    """
    if hasattr(kpts, 'cpu'):
        kpts = kpts.cpu().numpy()
        
    def is_valid_point(p):
        return not (p[0] == 0 and p[1] == 0)
    
    # YOLO v8 keypoint indices are 0-based, so adjust skeleton indices
    for idx, (p1, p2) in enumerate(skeletons):
        # Convert 1-based to 0-based indexing
        p1_idx, p2_idx = p1-1, p2-1
        
        if p1_idx < len(kpts) and p2_idx < len(kpts):
            point1, point2 = kpts[p1_idx], kpts[p2_idx]
            
            if is_valid_point(point1) and is_valid_point(point2):
                start_point = (int(point1[0]), int(point1[1]))
                end_point = (int(point2[0]), int(point2[1]))
                
                # Use color from color_list based on color_pallete index
                color = color_list[color_pallete[idx]][0]
                
                cv2.line(frame, start_point, end_point, color, 2)

import cv2

def draw_circle(frame, kpts):
    """
    Draw keypoint circles with index labels.
    
    Args:
        frame: The image frame to draw on.
        kpts: Keypoints from YOLO pose detection.
    """
    if hasattr(kpts, 'cpu'):
        kpts = kpts.cpu().numpy()
        
    for idx, kpt in enumerate(kpts):
        if not (kpt[0] == 0 and kpt[1] == 0):  # Skip invalid keypoints
            x, y = int(kpt[0]), int(kpt[1])
            cv2.circle(frame, (x, y), 3, (255, 255, 0), 4, cv2.LINE_AA)
            cv2.putText(frame, str(idx), (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, (0, 255, 0), 1, cv2.LINE_AA)


def add_text_to_image(image, angle, direction):
    """
    Add angle and direction information to the image
    
    Args:
        image: The image frame to draw on
        angle: Dictionary of angles
        direction: Direction string
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_color = (255, 255, 255)  # White text
    thickness = 2
    padding = 10
    
    # Calculate the maximum text width for background rectangle
    max_width = 0
    for key, value in angle.items():
        text = f"{key.upper().replace('_', ' ')} ANGLE: {value[-1]:.1f}"
        (text_width, _), _ = cv2.getTextSize(text, font, font_scale, thickness)
        max_width = max(max_width, text_width)
    
    # Draw semi-transparent background for text area
    overlay = image.copy()
    for idx, (key, value) in enumerate(angle.items()):
        y_pos = (idx + 1) * 40
        cv2.rectangle(overlay, 
                     (padding - 5, y_pos - 30),
                     (padding + max_width + 10, y_pos + 10),
                     (0, 0, 0),  # Black background
                     -1)
    
    # Apply transparency
    alpha = 0.6
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
    
    # Draw text
    for idx, (key, value) in enumerate(angle.items()):
        text = f"{key.upper().replace('_', ' ')} ANGLE: {value[-1]:.1f}"
        cv2.putText(image, text, 
                    (padding, (idx + 1) * 40), 
                    font, font_scale, font_color, thickness)
    
    # Add direction text if provided
    if direction:
        cv2.putText(image, 
                    f"DIRECTION: {direction}", 
                    (padding, 5 * 50), 
                    font, font_scale, font_color, thickness)