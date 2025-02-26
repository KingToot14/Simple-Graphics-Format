import os
from time import time

from PIL import Image

from sgf_image_loader.sgf import SGF

class Tester:
    def __init__(self):
        self.colors = 0
        self.time = 0
        self.png_size = 0
        self.sgf_size = 0
        self.diff_size = 0
        self.count = 0

        self.test_folder('.testing\\png_in', '.testing\\sgf', '.testing\\png_out', '')

        print("<tr>")
        print("    <td>Average</td>")
        print("    <td>-</td>")
        print(f"    <td>{int(self.colors / self.count)} colors</td>")
        print(f"    <td>{round(self.time / self.count, 2)}ms</td>")
        print(f"    <td>{self.format_bytes(round(self.png_size / self.count))}</td>")
        print(f"    <td>{self.format_bytes(round(self.png_size / self.count))}</td>")
        print(f"    <td>{round(self.diff_size / self.count, 2):,.2f}%</td>")
        print("</tr>")

    def format_bytes(self, bytes):
        if bytes >= 1000000:
            return f"{round(bytes / 1000000, 2)} MB"
        if bytes >= 1000:
            return f"{round(bytes / 1000, 2)} KB"
        
        return f"{bytes:,} B"

    def calc_time(self, start: float) -> str:
        return round((time() - start) * 1000)

    def test_image(self, png_in: str, sgf_out: str, png_out: str, depth: str):
        depth += "    "

        image = Image.open(png_in)

        sgf_out = sgf_out.replace('.png', '.sgf')

        # convert png to sgf
        t = time()
        SGF.save_from_image(sgf_out, image)
        e = self.calc_time(t)
        
        # convert sgf to png
        converted: Image = SGF.load_sgf(sgf_out)
        converted.save(png_out)

        self.colors += len(image.getcolors())
        self.time += e
        self.png_size += os.path.getsize(png_in)
        self.sgf_size += os.path.getsize(sgf_out)
        self.diff_size += (os.path.getsize(sgf_out) / os.path.getsize(png_in)) * 100
        self.count += 1

        print("<tr>")
        print(f"    <td>{png_in.split("\\")[-1]}</td>")
        print(f"    <td>{image.size}</td>")
        print(f"    <td>{len(image.getcolors())} colors</td>")
        print(f"    <td>{e}ms</td>")
        print(f"    <td>{self.format_bytes(os.path.getsize(png_in))}</td>")
        print(f"    <td>{self.format_bytes(os.path.getsize(sgf_out))}</td>")
        print(f"    <td>{(os.path.getsize(sgf_out) / os.path.getsize(png_in)) * 100:,.2f}%</td>")
        print("</tr>")

    def test_folder(self, png_in: str, sgf_out: str, png_out: str, depth: str):
        for file in os.listdir(png_in):
            if os.path.isdir(os.path.join(png_in, file)):
                self.test_folder(os.path.join(png_in, file), os.path.join(sgf_out, file), os.path.join(png_out, file), depth + "    ")
            else:
                self.test_image(os.path.join(png_in, file), os.path.join(sgf_out, file), os.path.join(png_out, file), depth + "    ")    
    

if __name__ == "__main__":
    Tester()