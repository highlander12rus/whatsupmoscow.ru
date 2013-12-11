__author__ = 'meanwhile'
import struct

#writing data into binary file
class FileWriterBinary:
    SIZE_STRUCT_IN_BYTE = 12 #4 + 4 + 4 bytes

    def __init__(self, file_name):
        self.file_name = file_name

    def write(self, date, lat, lng):
        with open(self.file_name, "ab") as f:
            f.write(struct.pack("3I", date, lat, lng))

    def read(self):
        res = []
        with open(self.file_name, "rb") as f:
            byte = f.read(self.SIZE_STRUCT_IN_BYTE)
            while byte != "":
                res.append(struct.unpack("3I", byte))
                byte = f.read(self.SIZE_STRUCT_IN_BYTE)
        return res