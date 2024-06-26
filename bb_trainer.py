import cv2
import os
import numpy as np
import json

# Global variables
drawing = False
ix, iy = -1, -1
rects = []
annotations = {}
logo_path = './logo/logo.jpeg'  # Ensure this path is correct

# Colors and font settings
PRIMARY_COLOR = (44, 20, 72)  # Deep maroon (BGR)
RECT_COLOR = (73, 196, 240)  # Yellow (BGR)
HEADER_COLOR = (44, 20, 72)  # Deep maroon for the header (BGR)
WHITE_COLOR = (255, 255, 255)  # White for text
FONT = cv2.FONT_HERSHEY_SIMPLEX
HEADER_FONT_SCALE = 0.8  # Increased for better visibility of header text
HEADER_FONT_THICKNESS = 1
FONT_SCALE = 0.5  # Increased for better visibility of annotations and help text
FONT_THICKNESS = 1
HEADER_HEIGHT = 90
HEADER_WIDTH = 1280  # Fixed width for the header and window
INPUT_HEIGHT = 50  # Increased for larger annotation input field

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 1024

# Display help commands on the header
def display_help(img):
    commands = ["'S' - Save", "'Q' - Quit", "'N' - Next Image", "'R' - Remove Box"]
    max_width = HEADER_WIDTH
    start_y = 20
    for command in commands:
        text_size = cv2.getTextSize(command, FONT, FONT_SCALE, FONT_THICKNESS)[0]
        cv2.putText(img, command, (max_width - text_size[0] - 20, start_y), FONT, FONT_SCALE, WHITE_COLOR, FONT_THICKNESS)
        start_y += 20  # Increased space between help commands

# Display prompt text for annotation input
def display_prompt(img, prompt_text):
    prompt_img = img.copy()
    cv2.rectangle(prompt_img, (0, HEADER_HEIGHT), (HEADER_WIDTH, HEADER_HEIGHT + INPUT_HEIGHT), HEADER_COLOR, -1)
    cv2.putText(prompt_img, prompt_text, (10, HEADER_HEIGHT + 40), FONT, FONT_SCALE, WHITE_COLOR, FONT_THICKNESS)
    cv2.imshow('Image with Header', prompt_img)

# Collect user input for annotations with backspace functionality
def get_label_via_opencv(img):
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

# Mouse callback function for drawing rectangles and handling events
def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, rects, annotations
    img, img_with_header = param

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        temp_img = img_with_header.copy()
        for rect in rects:
            cv2.rectangle(temp_img, (rect[0], rect[1]), (rect[2], rect[3]), RECT_COLOR, 2)
            label = annotations.get(str(rect), "")
            cv2.putText(temp_img, label, (rect[0], rect[1] - 10), FONT, FONT_SCALE, WHITE_COLOR, FONT_THICKNESS)
        cv2.rectangle(temp_img, (ix, iy), (x, y), RECT_COLOR, 2)
        cv2.imshow('Image with Header', temp_img)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rect = (min(ix, x), min(iy, y), max(ix, x), max(iy, y))
        rects.append(rect)
        label = get_label_via_opencv(img_with_header.copy())
        annotations[str(rect)] = label
        redraw_boxes(img_with_header)  # Refresh the display after adding a rectangle
    elif event == cv2.EVENT_RBUTTONDOWN:
        to_remove = None
        for rect in rects:
            if rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]:
                to_remove = rect
                break
        if to_remove:
            rects.remove(to_remove)
            annotations = {key: val for key, val in annotations.items() if val != to_remove}
            redraw_boxes(img_with_header)  # Refresh the display after removing a rectangle

# Redraw all bounding boxes and annotations on the image
def redraw_boxes(img):
    img_copy = img.copy()
    for rect in rects:
        label = annotations.get(str(rect), "")
        cv2.rectangle(img_copy, (rect[0], rect[1]), (rect[2], rect[3]), RECT_COLOR, 2)
        cv2.putText(img_copy, label, (rect[0], rect[1] - 10), FONT, FONT_SCALE, WHITE_COLOR, FONT_THICKNESS)
    cv2.imshow('Image with Header', img_copy)

# Add header with logo and text to the image
def add_header(img):
    # Ensure the header width is fixed
    header_img = np.full((HEADER_HEIGHT, HEADER_WIDTH, 3), HEADER_COLOR, dtype=np.uint8)
    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    if logo is not None and logo.any():
        # Maintain aspect ratio while resizing
        logo_height = HEADER_HEIGHT
        aspect_ratio = logo.shape[1] / logo.shape[0]
        logo_width = int(logo_height * aspect_ratio)
        resized_logo = cv2.resize(logo, (logo_width, logo_height), interpolation=cv2.INTER_AREA)
        # Set background color for the logo area to match the header color
        for c in range(0, 3):
            header_img[:, :logo_width, c] = resized_logo[:, :, c]
    text = "AgriDrone Bounding Boxes & Annotation Tool"
    text_size = cv2.getTextSize(text, FONT, HEADER_FONT_SCALE, HEADER_FONT_THICKNESS)[0]
    text_x = logo_width + 20  # Increased space after the logo
    text_y = (HEADER_HEIGHT + text_size[1]) // 2
    cv2.putText(header_img, text, (text_x, text_y), FONT, HEADER_FONT_SCALE, WHITE_COLOR, HEADER_FONT_THICKNESS)
    display_help(header_img)
    
    return header_img

# Resize and pad image to maintain aspect ratio
def resize_and_pad_image(img):
    aspect_ratio = img.shape[1] / img.shape[0]
    if aspect_ratio > 1:
        img_resized = cv2.resize(img, (WINDOW_WIDTH, int(WINDOW_WIDTH / aspect_ratio)))
        padding_top_bottom = max(0, (WINDOW_HEIGHT - HEADER_HEIGHT - INPUT_HEIGHT - img_resized.shape[0]) // 2)
        img_resized = cv2.copyMakeBorder(img_resized, padding_top_bottom, padding_top_bottom, 0, 0, cv2.BORDER_CONSTANT, value=HEADER_COLOR)
    else:
        img_resized = cv2.resize(img, (int((WINDOW_HEIGHT - HEADER_HEIGHT - INPUT_HEIGHT) * aspect_ratio), WINDOW_HEIGHT - HEADER_HEIGHT - INPUT_HEIGHT))
        padding_left_right = max(0, (WINDOW_WIDTH - img_resized.shape[1]) // 2)
        img_resized = cv2.copyMakeBorder(img_resized, 0, 0, padding_left_right, padding_left_right, cv2.BORDER_CONSTANT, value=HEADER_COLOR)
    
    return img_resized

# Combine header, image, and prompt into one display image
def combine_images(header_img, img, prompt_img):
    full_img = np.vstack([header_img, img])
    full_img = np.vstack([full_img, prompt_img])
    return full_img

# Main function to handle the annotation process
def annotate_images(image_dir):
    global rects, annotations
    if not os.path.exists(image_dir):
        print(f"Directory not found: {image_dir}")
        return
    files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))]
    cv2.namedWindow('Image with Header', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Image with Header', WINDOW_WIDTH, WINDOW_HEIGHT)
    for file in files:
        img_path = os.path.join(image_dir, file)
        img = cv2.imread(img_path)
        if img is None:
            continue
        header_img = add_header(img)
        img_resized = resize_and_pad_image(img)
        prompt_img = np.full((INPUT_HEIGHT, HEADER_WIDTH, 3), HEADER_COLOR, dtype=np.uint8)
        img_with_header = combine_images(header_img, img_resized, prompt_img)
        cv2.imshow('Image with Header', img_with_header)
        cv2.setMouseCallback('Image with Header', draw_rectangle, [img_resized, img_with_header])
        while True:
            key = cv2.waitKey(0) & 0xFF
            if key == ord('s'):
                save_annotations(file, image_dir, annotations)
                rects = []
                annotations = {}
                break
            elif key == ord('q'):
                cv2.destroyAllWindows()
                return
            elif key == ord('n'):  # Move to the next image
                rects = []
                annotations = {}
                break

# Save annotations to a JSON file
def save_annotations(filename, directory, annotations):
    output_path = os.path.join(directory, f"{os.path.splitext(filename)[0]}_annotations.json")
    with open(output_path, 'w') as f:
        json.dump(annotations, f, indent=4)

if __name__ == '__main__':
    image_dir = './Training/Fir'
    annotate_images(image_dir)
