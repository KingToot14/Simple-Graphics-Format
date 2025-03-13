import struct
import gzip
from enum import Enum

from PIL import Image
import numpy as np

class PaletteSize(Enum):
    ONE_BYTE = 0
    TWO_BYTE = 1
    FOUR_BYTE = 2

class SGF:
    @staticmethod
    def save_sgf(path, image: Image, vertical_stacking: bool = False, find_best: bool = False):
        '''Saves an sgf file from an array of pixel data
        
        Args:
            image (Image): The image to save

            palette_size (PaletteSize): How large the palette should be (from 1 to 4 bytes)
            transparency (int): The uniform alpha value of all pixels. If -1, each pixel has its own alpha value
            verbose (bool): If true, each pixel is stored directly instead of in a palette
            vertical_stacking (bool): If true, pixels are stacked vertically instead of horizontally

            find_best (bool): If true, other settings are overridden in order to find the best settings to use
        '''

        data = None

        color_count = len(image.getcolors())
        palette_size = 0

        while color_count > 256:
            palette_size += 1
            color_count //= 256 

        palette_size = PaletteSize(palette_size)

        if find_best:
            best = SGF.convert_to_sgf(image, False)
            best_size = len(best)

            d = SGF.convert_to_sgf(image, True)
            if best_size > len(d):
                best = d
                best_size = len(d)
            
            data = best
        else:
            data = SGF.convert_to_sgf(image, vertical_stacking)

        with open(path, 'wb') as file:
            file.write(gzip.compress(data))

    @staticmethod
    def convert_to_sgf(image: Image, vertical_stacking: bool = False):
        image = image.convert("RGBA")

        size = image.size
        pixels = list(image.getdata())

        data = bytearray()

        # --- Header --- #
        flags = 0

        flags |= 1 if vertical_stacking else 0

        data += struct.pack('B', flags)

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
        row = 1
        pixel_count = size[0] * size[1]

        for i in range(len(pixels)):
            pixel = None

            if vertical_stacking:
                if (i * size[0] + row - 1) > row * pixel_count:
                    row += 1
                pixel = pixels[(i * size[0] + row - 1) % pixel_count]
            else:
                pixel = pixels[i]

            check = False

            check = prev != palette[pixel]

            if check:
                if prev != None:
                    data += struct.pack('BB', reps, prev)
                reps = 1
                prev = palette[pixel]
            else:
                if reps >= 255:
                    data += struct.pack('BB', reps, prev)
                    reps = 0
                reps += 1
        
        data += struct.pack('BB', reps, prev)

        return data

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
        # flag byte
        flags = parse_bytes('B')

        vertical = (flags & 1) == 1

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
        row = 1

        pixels = [None for _ in range(pixel_count)]

        # load palette
        while i < pixel_count:
            reps, index = parse_bytes('BB')

            # stacking
            if vertical:
                for rep in range(reps):
                    if ((i + rep) * size[0] + row - 1) >= row * pixel_count:
                        row += 1

                    pixels[((i + rep) * size[0] + row - 1) % pixel_count] = palette[index]
            else:
                pixels[i:i+reps] = [palette[index] for _ in range(reps)]
            
            i += reps

        return [size, np.array(pixels, dtype=np.uint8)]
