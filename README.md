# SGF Image Loader
A small package for loading and saving files in the SGF format. SGF stands for <ins>S</ins>imple <ins>G</ins>raphic <ins>F</ins>ormat, and it's a custom file format I designed to help me learn various different topics.
## Limitations
SGF is primarily geared towards simpler pixel art images. Additionally, due to SGF's simple implementation, images are limited by two factors:

 1. SGF has a max palette size of 256 colors
 2. SGF has a max image size of 65,535 x 65,535 pixels

## Usage
The SGF Image Loader requires a Pillow Image object for loading and saving files in the SGF format.

To store a Pillow Image:
```python
from PIL import Image
from sgf_image_loader.sgf import SGF

# load image using Pillow
image = Image.open("file_name.png")

# save image in the SGF format
SGF.save_sgf("file_name.sgf", image, find_best=True)
```
Note: The `find_best` parameter causes the image loader to try every parameter combination to find the best possible parameters (more information below). This causes slower save times, but a generally smaller file.

In order to load an SGF image:
```python
image = SGF.load_sgf("file_name.sgf")
```

assuming all previously imported packages were also imported.

## Parameters
**Vertical Stacking** (bool):
The SGF format combines similar pixels into one "chunk" that is made up of a repetition value, and a color index. By default, this chunk is created by scanning the pixels horizontally, combining any continuous pixels with the same color. Enabling `vertical_stacking` causes the chunk to be created by scanning pixels vertically.

**Disable Repetition** (bool):
By default, the SGF format attempts to compress groups of similar pixels into a smaller chunk. However, sometimes this may end up making the file size larger. Enabling `disable_repetition` causes each pixel to be stores as just a color index, with no repetition value.