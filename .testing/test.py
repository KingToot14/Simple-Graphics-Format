import os
from time import time

from PIL import Image

from sgf_image_loader.sgf import SGF

def calc_time(start: float) -> str:
    return f"{round((time() - start) * 1000)}ms"

def test_image(png_in: str, sgf_out: str, png_out: str, depth: str):
    print(f"{depth}{png_in.split("\\")[-1]}")
    depth += "    "

    image = Image.open(png_in)

    sgf_out = sgf_out.replace('.png', '.sgf')

    # image info
    print(f"{depth}Image size  : {image.size}")
    print(f"{depth}Colors used : {len(image.getcolors())}")

    # convert png to sgf
    print(f"{depth}Converting  : ", end="")
    t = time()
    SGF.save_from_image(sgf_out, image)
    print(calc_time(t))

    # convert sgf to png
    converted: Image = SGF.load_sgf(sgf_out)
    converted.save(png_out)

    # output sizes
    print(f"{depth}png size    : {os.path.getsize(png_in)} Bytes")
    print(f"{depth}sgv size    : {os.path.getsize(sgf_out)} Bytes")
    print(f"{depth}Difference  : {(os.path.getsize(sgf_out) / os.path.getsize(png_in)) * 100:.2f}%")

def test_folder(png_in: str, sgf_out: str, png_out: str, depth: str):
    print(f"{depth}Testing '{png_in}'")

    for file in os.listdir(png_in):
        if os.path.isdir(os.path.join(png_in, file)):
            test_folder(os.path.join(png_in, file), os.path.join(sgf_out, file), os.path.join(png_out, file), depth + "    ")
        else:
            test_image(os.path.join(png_in, file), os.path.join(sgf_out, file), os.path.join(png_out, file), depth + "    ")

def main():
    test_folder('.testing\\png_in', '.testing\\sgf', '.testing\\png_out', '')
    
    

if __name__ == "__main__":
    main()