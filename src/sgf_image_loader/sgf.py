import struct
import gzip

from PIL import Image
import numpy as np

class SGF:
    @staticmethod
    def save_sgf(path, image: Image):
        '''Saves an sgf file from an array of pixel data
        
        Args:
            image (Image): The image to save
        '''

        image = image.convert("RGBA")

        size = image.size
        pixels = list(image.getdata())

        data = bytearray()

        # --- Header --- #
        # size
        data += struct.pack('HH', size[0], size[1])

        # color palette
        colors = [color[1] for color in image.getcolors()]

        data += struct.pack('B', len(colors))
        data += np.array(colors, dtype=np.uint8).tobytes()

        # --- Body --- #
        # pixel data
        palette = {colors[index]: index for index in range(len(colors))}

        # check for repetition
        prev = None
        reps = 0

        total = 0

        for pixel in pixels:
            if prev != palette[pixel]:
                if prev != None:
                    data += struct.pack('BB', reps, prev)
                    total += reps
                reps = 1
                prev = palette[pixel]
            else:
                if reps >= 255:
                    data += struct.pack('BB', reps, prev)
                    total += reps
                    reps = 0
                reps += 1
        
        data += struct.pack('BB', reps, prev)
        total += reps

        with open(path, 'wb') as file:
            file.write(gzip.compress(data))

    @staticmethod
    def load_sgf(source: str | bytes | bytearray) -> Image:
        '''Reads the file at the given path and attempts to load it as an sgf file
        
        Args:
            source (str | bytes | bytearray): If a string, the path to load from. Else, a binary stream manually passed in and decompressed through the gzip algorithm. This method only uses gzip when a string is passed in.
        
        Returns:
            array: the pixel data of the image
        '''
        
        data: np.ndarray = None

        if isinstance(source, str):
            with gzip.open(source, 'rb') as file:
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

            if len(out) == 1:
                return out[0]
            return out

        # --- Header --- #
        # size
        size = parse_bytes('HH')

        # palette
        color_count = parse_bytes('B')
        palette = {}
        i = 0

        while i < color_count:
            palette[i] = parse_bytes('BBBB')

            i += 1

        # --- Body --- #
        pixel_count = size[0] * size[1]
        i = 0

        pixels = []

        # load palette
        while i < pixel_count:
            reps, index = parse_bytes('BB')
            pixels += [palette[index] for _ in range(reps)]
            i += reps

        return [size, np.array(pixels, dtype=np.uint8)]
