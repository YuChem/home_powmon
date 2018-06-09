import serial
from time import sleep
'''
Description:
PZEM-004T Energy monitor sensor

Init:
dmesg | egrep --color 'serial|tty'
usermod -a -G dialout pi

Help:
http://www.instructables.com/id/Read-and-write-from-serial-port-with-Raspberry-Pi/

Example:
sensor = TPzem_004('/dev/serial0')
if (sensor.IsReady()):
    print("Reading voltage")
    print(sensor.GetVoltage())
'''
SERIAL_COMMANDS = {
    'V':  (b'\xB0\xC0\xA8\x01\x01\x00\x1A', lambda b: b[2] + b[3] / 10.0),
    'A':  (b'\xB1\xC0\xA8\x01\x01\x00\x1B', lambda b: b[2] + b[3] / 100.0),
    'W':  (b'\xB2\xC0\xA8\x01\x01\x00\x1C', lambda b: b[1] * 2**8 + b[2]),
    'Wh': (b'\xB3\xC0\xA8\x01\x01\x00\x1D', lambda b: b[1] * 2**16 + b[2] * 2**8 + b[3])
}

class Pzem_004():
    def open(self):
        self.uart=serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
   
    def validate_checksum(self, byteseq: bytes):
        return sum(byteseq[:-1])%256 == byteseq[-1]

    def read_parameter(self, parameter):
        (command, calc) = SERIAL_COMMANDS[parameter]

        return calc(self.send(command))

    def read_all(self):
        return {k:p.read_parameter(k) for k in SERIAL_COMMANDS.keys()}

    def send(self, command: bytes, read_len=7):
        self.uart.write(command)
        sleep(0.05)
        res = self.uart.read(read_len)
        assert self.validate_checksum(res)

        return res

if __name__ == '__main__':
    # read all parameters from serial
    p = Pzem_004()
    p.open()
    print(p.read_all())
