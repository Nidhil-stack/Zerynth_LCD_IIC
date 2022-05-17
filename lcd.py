"""
.. module:: bmp180

*************
BMP180 Module
*************

This module contains the driver for BOSCH BMP180 Digital Barometric Pressure Sensor. The ultra-low power, low voltage electronics of the BMP180 is optimized for use in mobile devices and the I2C interface allows for easy
system integration with a microcontroller. The BMP180 is based on piezo-resistive technology for EMC robustness, high accuracy and linearity as
well as long term stability (`datasheet <https://ae-bst.resource.bosch.com/media/_tech/media/datasheets/BST-BMP180-DS000-121.pdf>`_).
    """


import i2c

# BMP180 default address.
LCD_I2CADDR           = 0x27

#basic commands
LCD_CMD_CLEARDISPLAY  = 0x01
LCD_CMD_RETURNHOME    = 0x02
LCD_CMD_ENTRYMODESET  = 0x04
LCD_CMD_DISPLAYCONTROL = 0x08
LCD_CMD_CURSORSHIFT   = 0x10
LCD_CMD_FUNCTIONSET   = 0x20
LCD_CMD_SETCGRAMADDR  = 0x40
LCD_CMD_SETDDRAMADDR  = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT        = 0x00
LCD_ENTRYLEFT         = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON         = 0x04
LCD_DISPLAYOFF        = 0x00
LCD_CURSORON          = 0x02
LCD_CURSOROFF         = 0x00
LCD_BLINKON           = 0x01
LCD_BLINKOFF          = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE       = 0x08
LCD_CURSORMOVE        = 0x00
LCD_MOVERIGHT         = 0x04
LCD_MOVELEFT          = 0x00

# flags for function set
LCD_8BITMODE          = 0x10
LCD_4BITMODE          = 0x00
LCD_2LINE             = 0x08
LCD_1LINE             = 0x00
LCD_5x10DOTS          = 0x04
LCD_5x8DOTS           = 0x00

# flags for backlight control
LCD_BACKLIGHT         = 0x08
LCD_NOBACKLIGHT       = 0x00

#define En B00000100  // Enable bit
#define Rw B00000010  // Read/Write bit
#define Rs B00000001  // Register select bit

# mode flags for transmissions
LCD_MODE_ENABLE = 0x04
LCD_MODE_RW = 0x02
LCD_MODE_RS = 0x01

class LCD(i2c.I2c):
    """
.. class:: BMP180(i2cdrv, addr=0x77, clk=100000)

    Creates an intance of a new BMP180.

    :param i2cdrv: I2C Bus used '( I2C0, ... )'
    :param addr: Slave address, default 0x77
    :param clk: Clock speed, default 100kHz

    Example: ::

        from bosch.bmp180 import bmp180

        ...

        bmp = bmp180.BMP180(I2C0)
        bmp.start()
        bmp.init()
        temp, pres = bmp.get_temp_pres()

    """

    #Init
    def __init__(self, drvname, addr=LCD_I2CADDR, clk=400000):
        i2c.I2c.__init__(self, addr, drvname, clk)
        self._addr = addr
        self._oss = 0
        self.init()


    def init(self):
        """
        .. method:: init()

        Initialize the LCD.

        """

        self._backlightval = LCD_BACKLIGHT
        self._displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self._displaymode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT

        # Try to set 4 bit mode
        self._write4bits(0x03 << 4)
        sleep(5)
        self._write4bits(0x03 << 4)
        sleep(5)
        self._write4bits(0x03 << 4)
        sleep(5)

        # Set 4 bit interface
        self._write4bits(0x02 << 4)

        # # Set 2 line mode
        self._command(LCD_CMD_FUNCTIONSET | LCD_4BITMODE | LCD_2LINE | LCD_5x8DOTS)

        # Set display settings
        self._command(LCD_CMD_DISPLAYCONTROL | self._displaycontrol)
        self._command(LCD_CMD_ENTRYMODESET | self._displaymode)

        # Clear the display
        self.clear()

        # Home cursor
        self.home()



    ######High level public functions######

    def clear(self):
        """
        .. method:: clear()

        Clear the LCD screen.

        """
        self._command(LCD_CMD_CLEARDISPLAY)
        sleep(2)

    def home(self):
        """
        .. method:: home()

        Move the cursor to the home position.

        """
        self._command(LCD_CMD_RETURNHOME)
        sleep(2)

    def setBacklight(self, val):
        """
        .. method:: setBacklight(val)

        Set the backlight value.

        :param val: Backlight value (0 or 1)

        """
        if val == 0:
            self._backlightval = LCD_NOBACKLIGHT
        else:
            self._backlightval = LCD_BACKLIGHT
        self._expanderWrite(0)

    # Load custom characters
    def loadCustomCharacter(self, char_arr, location):
        """
        .. method:: loadCustomCharacter(char_arr, location)

        Load a custom character into the LCD.

        :param char_arr: 8-byte array of custom character
        :param location: Character location (0 to 7)

        """
        self._command(LCD_CMD_SETCGRAMADDR | (location << 3))
        for char_byte in char_arr:
            self._writeChar(char_byte)

    # Set autoscroll
    def setAutoscroll(self, state):
        """
        .. method:: setAutoscroll(state)

        Set the autoscroll state.

        :param state: Autoscroll state (0 or 1)

        """
        if state:
            self._displaymode |= LCD_ENTRYSHIFTINCREMENT
        else:
            self._displaymode &= ~LCD_ENTRYSHIFTINCREMENT
        self._command(LCD_CMD_DISPLAYCONTROL | self._displaymode)

    # Set text direction (0 = left to right)
    def setTextDirection(self, direction = 0):
        """
        .. method:: setTextDirection(direction = 0)

        Set the text direction.

        :param direction: Text direction (0 = left to right)

        """
        if direction:
            self._displaymode |= LCD_ENTRYLEFT
        else:
            self._displaymode &= ~LCD_ENTRYLEFT
        self._command(LCD_CMD_DISPLAYCONTROL | self._displaymode)

    #scroll display left
    def scrollLeft(self):
        """
        .. method:: scrollLeft()

        Scroll the display left.

        """
        self._command(LCD_CMD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)

    #scroll display right
    def scrollRight(self):
        """
        .. method:: scrollRight()

        Scroll the display right.

        """
        self._command(LCD_CMD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)

    # Set the cursor blinking
    def blinkOn(self, state):
        """
        .. method:: blinkOn(state)

        Set the cursor blinking.

        :param state: Blinking state (0 or 1)

        """

        if state:
            self._displaycontrol |= LCD_BLINKON
        else:
            self._displaycontrol &= ~LCD_BLINKON
        self._command(LCD_CMD_DISPLAYCONTROL | self._displaycontrol)

    # Turn the display on/off
    def displayOn(self, state):
        """
        .. method:: displayOn(state)

        Turn the display on/off.

        :param state: Display state (0 or 1)

        """
        if state:
            self._displaycontrol |= LCD_DISPLAYON
        else:
            self._displaycontrol &= ~LCD_DISPLAYON
        self._command(LCD_CMD_DISPLAYCONTROL | self._displaycontrol)


    # Set cursor position
    def cursorOn(self, state):
        """
        .. method:: cursorOn(state)

        Turn the cursor on/off.

        :param state: Cursor state (0 or 1)

        """
        if state:
            self._displaycontrol |= LCD_CURSORON
        else:
            self._displaycontrol &= ~LCD_CURSORON
        self._command(LCD_CMD_DISPLAYCONTROL | self._displaycontrol)

    # Home the cursor
    def home(self):
        """
        ..method:: home()

        Home the cursor.

        """
        self._command(LCD_CMD_RETURNHOME)
        sleep(2)

    # Set the cursor position
    def setCursorPosition(self, col, row):
        """
        .. method:: setCursorPosition(col, row)

        Set the cursor position.

        :param col: Column (0 to 15)
        :param row: Row (0 to 1)

        """
        self._command(LCD_CMD_SETDDRAMADDR | (col + row*0x40))


    def writeString(self, string):
        """
        .. method:: writeString(string)

        Write a string to the LCD.

        :param string: String to write

        """
        # data = [c for c in string]
        # for c in data:
        #     self._writeChar(ord(c))
        for char in string:
            self._writeChar(char)

    ######## Less low level functions ########

    def _command(self, cmd):
        self._send(cmd, 0)

    def _writeChar(self, char):
        self._send(ord(char), LCD_MODE_RS)
        return 1

    ######## Low level commands #########

    def _send(self, data, mode):
        highBits = data & 0xF0
        lowBits = (data << 4) & 0xF0
        self._write4bits(highBits | mode)
        self._write4bits(lowBits | mode)

    def _write4bits(self, data):
        self._expanderWrite(data)
        self._pulseEnable(data)

    def _pulseEnable(self, data):
        self._expanderWrite(data | LCD_MODE_ENABLE)
        sleep(1)
        self._expanderWrite(data & ~LCD_MODE_ENABLE)
        sleep(1)

    def _expanderWrite(self, data):
        self._write(data | self._backlightval)

    def _write(self, data):
        buffer = bytearray(1)
        buffer.append(data)
        self.write(bytearray(buffer))
        sleep(3)




    #Reading functions, to review
    # def _read_uint_from_16_to_19(self, reg):
    #     data = self.write_read(bytearray([reg,]), 3) #data[0] --> MSB, data[1] --> LSB, data[2] --> XLSB
    #     res = (((data[0] << 16) + (data[1] << 8) + data[2]) >> (8-self._oss))
    #     return res

    # #Read raw temperature or uint16 register
    # def _read_uint16(self, reg):
    #     data = self.write_read(bytearray([reg,]), 2) #data[0] --> MSB, data[1] --> LSB
    #     res = ((data[0] << 8 | (data[1])) & 0xFFFF)
    #     return res

    # #Read int16 register
    # def _read_int16(self, reg):
    #     res = self._read_uint16(reg)
    #     if res > 32767:
    #         res -= 65536
    #     return res
