from machine import Pin,PWM
import time
import _thread
import machine
import gc
# machine.freq(160000000)


class _Const:
    """ NEC Const """
    # 引导码：9000us 的载波+ 4500us  的空闲
    # 比特值“0”：560us 的载波+ 560us 的空闲
    # 比特值“1”：560us 的载波+ 1690us 的空闲
    NEC_HDR_MARK = 9000
    NEC_HDR_SPACE = 4500

    NEC_BIT_MARK = 560
    NEC_ONE_SPACE = 1690
    NEC_ZERO_SPACE = 560

    NEC_RPT_SPACE = 2250

    TOLERANCE = 0.3
    STARTDATAINDEX = 2


class IrReceiver():
    """ IR Decode """

    decodedData = None

    def __init__(self, pin):
        self.pulse_buffer = []
        self._prev_time = 0
        self.callback = None
        self.recv = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.recv.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                      handler=self._pulse_width_record)
        self.lenth = 0
        self.waittime = 150000

        self.debug = False


    def _pulse_width_record(self, pin):
        """record the width of th IR remote signal."""
        self._time = time.ticks_us()
        if self._prev_time == 0:
            self._prev_time = self._time
            return
        self.pulse_buffer.append(self._time - self._prev_time)
        self._prev_time = self._time
        self.lenth = self.lenth + 1

    def _lead_cheak(self,pulse_width_list):
        """function to cheak the lead code """
        return (abs(pulse_width_list[0] - _Const.NEC_HDR_MARK) <
                _Const.NEC_HDR_MARK * _Const.TOLERANCE) and (
                    abs(pulse_width_list[1] - _Const.NEC_HDR_SPACE) <
                    _Const.NEC_HDR_SPACE * _Const.TOLERANCE)


    def _ir_recv_daemon(self):
        """ background handles ir signal """
        while True:
            if (time.ticks_us()-self._prev_time) > self.waittime and self.pulse_buffer != []:
                dec = self.decode_buff()
                if self.callback:
                    self.callback(dec)

    def decode(self):
        hasCode = False
        if (time.ticks_us()-self._prev_time) > self.waittime and self.pulse_buffer != []:
            self.decodedData = self.decode_buff()
            hasCode = True
        return hasCode

    def daemon(self):
        """ daemon start """
        _thread.start_new_thread(self._ir_recv_daemon, ())

    def set_callback(self,callback = None):
        """ function to allow the user to set or change the callback function """
        self.callback = callback


    def find_start_index(self,pulse_width_list):
        """ find the acceptable start of the pulse_buffer. """
        for i in range(len(pulse_width_list)):
            if abs(pulse_width_list[i] - _Const.NEC_HDR_MARK) < _Const.NEC_HDR_MARK * _Const.TOLERANCE:
                return i
        return

    def decode_buff(self):
        """ decode pulse to hex str """
        decstr = ''
        if self.debug:
            print(self.pulse_buffer)
        if len(self.pulse_buffer) > 66:
            pulse_width_list = self.pulse_buffer[self.find_start_index(self.pulse_buffer):]
            if self._lead_cheak(pulse_width_list):
                decstr = self.bin2hex(self.pulse_width2bit_line(pulse_width_list))
            else:
                print("Warning: Buffer lead code error!")
        else:
            print("Warning: Buffer length too short!")
        self._prev_time = 0
        self.pulse_buffer.clear()
        gc.collect()
        return decstr


    @staticmethod
    def pulse_width2bit_line(pulse_width_list):
        """ pulses width list to bit list"""
        bit_list = list()
        for i in range(_Const.STARTDATAINDEX,len(pulse_width_list),2):
            if i+1 < len(pulse_width_list):
                if abs(pulse_width_list[i+1] - _Const.NEC_ONE_SPACE) < _Const.NEC_ONE_SPACE * _Const.TOLERANCE:
                    bit_list.append(1)
                elif abs(pulse_width_list[i+1] - _Const.NEC_ZERO_SPACE) < _Const.NEC_ZERO_SPACE * _Const.TOLERANCE:
                    bit_list.append(0)
                else:
                    break
        bit_line = ''.join([str(i) for i in bit_list])
        return bit_line

    @staticmethod
    def bin2hex(bit_line):
        """ bit str to hex str """
        return '{:x}'.format(int(bit_line,2))
