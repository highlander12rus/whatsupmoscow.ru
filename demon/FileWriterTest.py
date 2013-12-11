__author__ = 'илья'
import unittest
import FileWriter
import os


class TestBinaryFileWriter(unittest.TestCase):

    def test_fileWriteRead(self):
        file = FileWriter.FileWriterBinary('test.test')
        for i in range(0, 5):
            file.write(i,15,16)

        data = file.read()
        self.assertEqual(5, len(data))

        for i in range(0, 5):
             portion =  data[i]
             self.assertEqual(i, portion[0])

    def tearDown(selfself):
        os.remove('test.test')

if __name__ == '__main__':
    unittest.main()