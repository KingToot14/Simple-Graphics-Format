import struct

from PIL import Image
import numpy as np

class SGF:
    @staticmethod
    def save_from_pixels(path, pixels, size):
        '''Saves an sgf file from an array of pixel data
        
        Args:
            pixels (array): The pixel data stored in a 1D array
        '''

        pixels = np.array(pixels, dtype=np.uint8)

        data = bytearray()

        # --- Header --- #
        # size
        data += struct.pack('HH', size[0], size[1])

        # --- Body --- #
        # pixel data
        data += pixels.tobytes()

        with open(path, 'wb') as file:
            file.write(data)

    @staticmethod
    def save_from_image(path, image: Image):
        image = image.convert('RGBA')

        SGF.save_from_pixels(path, image.getdata(), image.size)

    @staticmethod
    def load_sgf(source: str | bytes | bytearray) -> Image:
        '''Reads the file at the given path and attempts to load it as an sgf file
        
        Args:
            source (str | bytes | bytearray): The path to load from
        
        Returns:
            array: the pixel data of the image
        '''
        
        data: np.ndarray = None

        if isinstance(source, str):
            with open(source, 'rb') as file:
                data = SGF.load_sgf_data(file.read())
        elif isinstance(source, bytes) or isinstance(source, bytearray):
            data = SGF.load_sgf_data(source)
        
        return Image.frombytes(mode="RGBA", size=data[0], data=data[1])
    
    @staticmethod
    def load_sgf_data(data: bytes | bytearray) -> tuple[tuple[int,int], np.ndarray]:
        '''Loads the given bytes as an sgf file
        
        Args:
            data (bytes | bytearray): The bytes to parse
        
        Returns:
            tuple[tuple[int,int], np.ndarray]: a tuple consisting of the image's size
        '''

        bp: int = 0

        def parse_bytes(format: str):
            nonlocal bp

            out = struct.unpack(format, data[bp:bp+struct.calcsize(format)])
            bp += struct.calcsize(format)

            return out[0]

        # --- Header --- #
        size = [parse_bytes('H'), parse_bytes('H')]

        # --- Body --- #
        pixels = np.frombuffer(data, offset=bp, dtype=np.uint8)

        return [size, pixels]
