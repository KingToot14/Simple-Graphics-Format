import struct

class SGFParser:
    '''A class that reads files and parses them, returning raw pixel data'''

    @staticmethod
    def parse_file(path: str):
        '''Reads the file at the given path and attempts to parse it as an sgf file
        
        Args:
            path (str): The path to load from
        
        Returns:
            array: the pixel data of the image
        '''
        
        with open(path, 'rb') as file:
            return SGFParser.parse_data(file.read())
    
    @staticmethod
    def parse_data(data: bytes):
        '''Parses the given bytes as an sgf file
        
        Args:
            data (bytes): The bytes to parse
        
        Returns:
            array: the pixel data of the image
        '''

        bp: int = 0

        def parse_bytes(format: str):
            nonlocal bp

            return struct.unpack(format, data[bp:bp+struct.calcsize(format)])
        
        
        
