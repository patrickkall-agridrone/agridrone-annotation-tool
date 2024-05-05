# agridrone-annotation-tool
This is a tool designed to annotate images by drawing bounding boxes and adding labels. It offers an intuitive way to navigate and annotate images using simple keyboard shortcuts.

# Requirements
- Python 3.6+
- OpenCV
- Numpy
# Installation
Clone the repository:

Copy code
```bash
git clone https://github.com/patrickkall-agridrone/agridrone-annotation-tool.git
cd agridrone-annotation-tool
```
## Install dependencies:
Ensure you have pip installed. Then run:
Copy code
```bash
pip install opencv-python numpy
```
## Add a custom logo (Optional):
If you have a custom logo you'd like to use, place the logo in the logo folder with the filename customcolor_logo.png. The image should ideally have a transparent background.
# Usage
## Prepare your images:
Place all images you want to annotate inside a directory, for example, Training/Fir.
## Run the tool:
Replace the image_dir in the code with the actual path to your image directory.

Copy code
```python
image_dir = './Training/Fir'
annotate_images(image_dir)
```
## Annotate images:
### Draw Bounding Boxes: 
Click and drag with the left mouse button.
### Add Labels: 
After drawing a box, type the label in the popup that appears below the header.
### Remove Boxes: 
Right-click on an existing bounding box to remove it.
### Save Annotations: 
Press 's' to save the annotations for the current image.
### Next Image: 
Press 'n' to move to the next image.
### Quit: 
Press 'q' to quit the program.

# License
GNU General Public License v2.0
