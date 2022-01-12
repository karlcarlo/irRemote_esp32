from machine import Pin
from IRremote import IrReceiver

# 初始化管脚
receiver = IrReceiver(15) # 红外接收
p12 = Pin(12, Pin.OUT) # LED

def getBtnVal(val):
    '''21键红外遥控器'''
    btnVal = 'None'

    btnList = {
        '0xffa25d': 'A',
        '0xff629d': 'B',
        '0xffe21d': 'C',
        '0xff22dd': 'D',
        '0xff02fd': 'Up',
        '0xffc23d': 'E',
        '0xffe01f': 'Left',
        '0xffa857': 'Set',
        '0xff906f': 'Right',
        '0xff6897': '0',
        '0xff9867': 'Down',
        '0xffb04f': 'F',
        '0xff30cf': '1',
        '0xff18e7': '2',
        '0xff7a85': '3',
        '0xff10ef': '4',
        '0xff38c7': '5',
        '0xff5aa5': '6',
        '0xff42bd': '7',
        '0xff4ab5': '8',
        '0xff52ad': '9'
    }

    key = '0x' + val

    if key in btnList:
        btnVal = btnList[key]

    return btnVal


while True:
    if receiver.decode():
        code = getBtnVal(receiver.decodedData)
        print(receiver.decodedData, code)

        if code == 'A':
            p12.off()
        elif code == 'C':
            p12.on()
