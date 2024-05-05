import cv2
import os
import numpy as np
import json

# Global variables
drawing = False
ix, iy = -1, -1
rects = []
annotations = {}
logo_path = './logo/customcolor_logo.png'  # Adjust path to your logo file

# Colors based on provided style
PRIMARY_COLOR = (72, 20, 44)  # Deep maroon (BGR)
RECT_COLOR = (240, 196, 73)  # Yellow for bounding boxes (BGR)
HEADER_COLOR = (72, 20, 44)  # Deep maroon for the header (BGR)
WHITE_COLOR = (255, 255, 255)  # Pure white

# Font settings
FONT = cv2.FONT_HERSHEY_SIMPLEX
HEADER_FONT_SCALE = 2.0  # Doubling the font size for the header
HEADER_FONT_THICKNESS = 4  # Increase the thickness to match the scale
FONT_SCALE = 1.0  # Annotation font scale unchanged
FONT_THICKNESS = 2

# Adjust the height of the header window
HEADER_HEIGHT = 270
INPUT_HEIGHT = 50  # Height of the input field

def display_help(img):
    """ Display help commands on the header at the far right """
    commands = ["'S' - Save", "'Q' - Quit", "'N' - Next Image", "'R' - Remove Box"]
    max_width = img.shape[1]
    start_y = 50
    for command in commands:
        text_size = cv2.getTextSize(command, FONT, FONT_SCALE, FONT_THICKNESS)[0]
        cv2.putText(img, command, (max_width - text_size[0] - 10, start_y), FONT, FONT_SCALE, WHITE_COLOR, FONT_THICKNESS)
        start_y += 30

def display_prompt(img, prompt_text):
    """ Display prompt text for annotations """
    cv2.rectangle(img, (0, HEADER_HEIGHT), (img.shape[1], HEADER_HEIGHT + INPUT_HEIGHT), (0, 0, 0), -1)
    cv2.putText(img, prompt_text, (10, HEADER_HEIGHT + 30), FONT, FONT_SCALE, WHITE_COLOR, FONT_THICKNESS)
    cv2.imshow('Image with Header', img)

def get_label_via_opencv(img):
    """ A non-blocking way to collect user input for annotations """
    label = ""
    while True:
        display_prompt(img, "Enter label: " + label)
        key = cv2.waitKey(0) & 0xFF
        if key in [13, 10]:  # Enter key
            break
        elif key == 8:  # Backspace
            label = label[:-1]
        elif 32 <= key <= 126:  # Printable characters
            label += chr(key)
    return label.strip()

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, rects, annotations
    img, img_with_header = param

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            temp_img = img_with_header.copy()
            cv2.rectangle(temp_img, (ix, iy), (x, y), RECT_COLOR, 2)
            cv2.imshow('Image with Header', temp_img)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        current_rect = [ix, iy, x, y]
        label = get_label_via_opencv(img_with_header.copy())  # Collect label from user input
        rects.append(current_rect)  # Use list instead of tuple
        annotations[str(current_rect)] = label  # Convert rect to a string key
        img_with_boxes = redraw_boxes(img_with_header)
        cv2.imshow('Image with Header', img_with_boxes)
    elif event == cv2.EVENT_RBUTTONDOWN:
        for i, rect in enumerate(rects):
            if min(rect[0], rect[2]) <= x <= max(rect[0], rect[2]) and min(rect[1], rect[3]) <= y <= max(rect[1], rect[3]):
                del annotations[str(rect)]  # Use string key to remove annotation
                del rects[i]
                break
        img_with_boxes = redraw_boxes(img_with_header)
        cv2.imshow('Image with Header', img_with_boxes)

def redraw_boxes(img):
    """ Redraw bounding boxes and labels on the image """
    img_copy = img.copy()
    for rect in rects:
        label = annotations.get(str(rect), "")
        cv2.rectangle(img_copy, tuple(rect[:2]), tuple(rect[2:]), RECT_COLOR, 2)
        cv2.putText(img_copy, label, (rect[0], rect[1] - 10), FONT, FONT_SCALE, WHITE_COLOR, FONT_THICKNESS)
    return img_copy

def add_header(img):
    header_img = np.full((HEADER_HEIGHT, img.shape[1], 3), HEADER_COLOR, np.uint8)

    # Add the logo, resize it to 270 while maintaining proportions
    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    if logo is not None:
        logo_h, logo_w = logo.shape[:2]
        scale_factor = 270 / logo_h
        new_logo_w = int(logo_w * scale_factor)
        logo_resized = cv2.resize(logo, (new_logo_w, 270), interpolation=cv2.INTER_AREA)

        logo_h_resized, logo_w_resized = logo_resized.shape[:2]
        alpha = logo_resized[:, :, 3] / 255.0 if logo_resized.shape[2] == 4 else None
        for c in range(3):
            if alpha is not None:
                header_img[:logo_h_resized, :logo_w_resized, c] = (alpha * logo_resized[:, :, c] + (1 - alpha) * header_img[:logo_h_resized, :logo_w_resized, c])
            else:
                header_img[:logo_h_resized, :logo_w_resized] = logo_resized

    # Add the text centered
    text = "AgriDrone Bounding Boxes & Annotation Tool"
    text_size = cv2.getTextSize(text, FONT, HEADER_FONT_SCALE, HEADER_FONT_THICKNESS)[0]
    text_x = logo_resized.shape[1] + 50  # Adjusted to add some spacing after the logo
    text_y = (HEADER_HEIGHT + text_size[1]) // 2

    cv2.putText(header_img, text, (text_x, text_y), FONT, HEADER_FONT_SCALE, WHITE_COLOR, HEADER_FONT_THICKNESS)

    display_help(header_img)

    return np.vstack([header_img, img])

def annotate_images(image_dir):
    global rects, annotations
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))]
    current_image_index = 0
    total_images = len(image_files)

    while current_image_index < total_images:
        img_name = image_files[current_image_index]
        img_path = os.path.join(image_dir, img_name)
        img = cv2.imread(img_path)

        img_with_header = add_header(img)
        img_with_boxes = redraw_boxes(img_with_header)
        cv2.namedWindow('Image with Header')
        cv2.setMouseCallback('Image with Header', draw_rectangle, [img, img_with_boxes])

        while True:
            cv2.imshow('Image with Header', img_with_boxes)
            key = cv2.waitKey(0) & 0xFF
            if key == ord('s'):
                output_file = os.path.join(image_dir, f"{os.path.splitext(img_name)[0]}_annotations.json")
                with open(output_file, 'w') as f:
                    json.dump({'image': img_name, 'rects': rects, 'annotations': annotations}, f)
                rects = []
                annotations = {}
                current_image_index += 1  # Add this to move to the next image
                break
            elif key == ord('q'):
                cv2.destroyAllWindows()
                return
            elif key == ord('n'):
                rects = []
                annotations = {}
                current_image_index += 1
                break

image_dir = './Training/Fir'
annotate_images(image_dir)
