from PIL import Image
import numpy as np

class SGFWriter:
    @staticmethod
    def save_from_pixels(path, pixels, size):
        '''Saves an sgf file from an array of pixel data
        
        Args:
            pixels (array): The pixel data stored in a 1D array
        '''

        pixels = np.array(pixels)

        data = bytearray()

        # --- Header --- #
        # size
        data += size[0].to_bytes(1)
        data += size[1].to_bytes(1)

        # --- Body --- #
        # pixel data
        data += pixels.tobytes()

        with open(path, 'wb') as file:
            file.write(data)

    @staticmethod
    def save_from_image(path, image: Image):
        SGFWriter.save_from_pixels(path, image.getdata(), image.size)