import unittest
from unittest.mock import MagicMock
from sensors.pzem import Pzem_004, SERIAL_COMMANDS

class TestStringMethods(unittest.TestCase):

    def test_checksum(self):
        p = Pzem_004()
        byteseq = SERIAL_COMMANDS['V'][0]
        assert(p.validate_checksum(byteseq))

        new_byteseq = byteseq[-2:-1] + byteseq[0:-1]
        assert(not p.validate_checksum(new_byteseq))

    def test_read_V(self):
        p = Pzem_004()
        p.send = MagicMock(return_value=b'\xA0\x00\xE6\x02\x00\x00\x88')
        self.assertEqual(p.read_parameter('V'), 230.2)

    def test_read_A(self):
        p = Pzem_004()
        p.send = MagicMock(return_value=b'\xA1\x00\x11\x20\x00\x00\xD2')
        self.assertEqual(p.read_parameter('A'), 17.32)

    def test_read_W(self):
        p = Pzem_004()
        p.send = MagicMock(return_value=b'\xA2\x08\x98\x00\x00\x00\x42')
        self.assertEqual(p.read_parameter('W'), 2200)

    def test_read_Wh(self):
        p = Pzem_004()
        p.send = MagicMock(return_value=b'\xA3\x01\x86\x9F\x00\x00\xC9')
        self.assertEqual(p.read_parameter('Wh'), 99999)

    def test_real_all(self):
        #TODO: this one is a composite of others
        pass
        
if __name__ == '__main__':
    unittest.main()