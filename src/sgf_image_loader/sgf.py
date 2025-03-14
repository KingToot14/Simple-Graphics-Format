import struct
import gzip

from PIL import Image
import numpy as np

class SGF:
    @staticmethod
    def save_sgf(path, image: Image, vertical_stacking: bool = False, disable_repetition: bool = False, find_best: bool = False):
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

        if find_best:
            # Horizontal Stacking with Repetition
            best = SGF.convert_to_sgf(image, False, False)
            best_size = len(best)

            # Vertical Stacking with Repetition
            d = SGF.convert_to_sgf(image, True, False)
            if best_size > len(d):
                best = d
                best_size = len(d)
            
            # Horizontal Stacking without Repetition
            d = SGF.convert_to_sgf(image, False, True)
            if best_size > len(d):
                best = d
                best_size = len(d)
            
            # Vertical Stacking without Repetition
            d = SGF.convert_to_sgf(image, True, True)
            if best_size > len(d):
                best = d
                best_size = len(d)

            data = best
        else:
            data = SGF.convert_to_sgf(image, vertical_stacking)

        with open(path, 'wb') as file:
            file.write(gzip.compress(data))

    @staticmethod
    def convert_to_sgf(image: Image, vertical_stacking: bool = False, disable_repetition: bool = False):
        image = image.convert("RGBA")

        size = image.size
        pixels = list(image.getdata())

        data = bytearray()

        # --- Header --- #
        flags = 0

        flags |= 1 if vertical_stacking else 0
        flags |= 2 if disable_repetition else 0

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
        index = 0
        pixel_count = size[0] * size[1]

        for i in range(len(pixels)):
            pixel = None

            if vertical_stacking:
                pixel = pixels[index]

                index += size[0]
                if index >= pixel_count:
                    index %= pixel_count
                    index += 1
            else:
                pixel = pixels[i]

            if prev != palette[pixel]:
                if prev != None:
                    if not disable_repetition:
                        data += struct.pack('BB', reps, prev)
                    else:
                        for rep in range(reps):
                            data += struct.pack('B', prev)
                reps = 1
                prev = palette[pixel]
            else:
                if reps >= 255:
                    if not disable_repetition:
                        data += struct.pack('BB', reps, prev)
                    else:
                        for rep in range(reps):
                            data += struct.pack('B', prev)
                    reps = 0
                reps += 1
        
        if not disable_repetition:
            data += struct.pack('BB', reps, prev)
        else:
            for rep in range(reps):
                data += struct.pack('B', prev)

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

        vertical = (flags & 1) != 0
        disable_reps = (flags & 2) != 0

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
        v_index = 0

        pixels = [None for _ in range(pixel_count)]

        # load palette
        while i < pixel_count:
            reps = 1
            if not disable_reps:
                reps = parse_bytes('B')
            index = parse_bytes('B')

            # stacking
            if vertical:
                for rep in range(reps):
                    pixels[v_index] = palette[index]

                    v_index += size[0]
                    if v_index >= pixel_count:
                        v_index %= pixel_count
                        v_index += 1
            else:
                pixels[i:i+reps] = [palette[index] for _ in range(reps)]
            
            i += reps

        return [size, np.array(pixels, dtype=np.uint8)]
