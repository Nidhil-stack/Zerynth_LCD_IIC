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
    .. class:: LCD(i2cdrv, addr=LCD_I2CADDR, clk=400000)

    Creates an intance of a new LCD1602.

    :param i2cdrv: The I2C bus to use.
    :param addr: The I2C address of the LCD.
    :param clk: The I2C clock speed.

    Example: ::

        from lcd import lcd

        ...

        lcd = lcd.LCD(i2cdrv, 0x27, 400000)
        lcd.writeString("Hello World!")
    """

    def __init__(self, drvname, addr=LCD_I2CADDR, clk=400000):
        i2c.I2c.__init__(self, addr, drvname, clk)                                                          #initialize the I2C bus
        self._addr = addr                                                                                   #save the address
        self.init()                                                                                         #start the init


    def init(self):
        """
        .. method:: init()

        Initialize the LCD.

        """

        self._backlightval = LCD_BACKLIGHT                                                                  # set backlight to on
        self._displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF                                 # turn display on, cursor off, blink off
        self._displaymode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT                                         # set the entry mode

        # Try to set 4 bit mode
        self._write4bits(0x03 << 4)                                                                         #try to set 4bit mode, wait and try again
        sleep(5)
        self._write4bits(0x03 << 4)
        sleep(5)
        self._write4bits(0x03 << 4)
        sleep(5)

        # Set 4 bit interface
        self._write4bits(0x02 << 4)

        # # Set 2 line mode
        self._command(LCD_CMD_FUNCTIONSET | LCD_4BITMODE | LCD_2LINE | LCD_5x8DOTS)                         #set 4 bit mode, 2 line, 5x8 dots

        # Set display settings
        self._command(LCD_CMD_DISPLAYCONTROL | self._displaycontrol)                                        #turn display on, cursor off, blink off
        self._command(LCD_CMD_ENTRYMODESET | self._displaymode)                                             #set the entry mode

        # Clear the display
        self.clear()

        # Home cursor
        self.home()



    ######High level public functions######

    def clear(self):                                                                                        #clear the LCD
        """
        .. method:: clear()

        Clear the LCD screen.

        """
        self._command(LCD_CMD_CLEARDISPLAY)
        sleep(2)

    def home(self):                                                                                         #go to the home position
        """
        .. method:: home()

        Move the cursor to the home position.

        """
        self._command(LCD_CMD_RETURNHOME)
        sleep(2)

    def setBacklight(self, val):                                                                            #set backlight on/off
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

    def loadCustomCharacter(self, char_arr, location):                                                      #load custom characters in the LCD memory
        """
        .. method:: loadCustomCharacter(char_arr, location)

        Load a custom character into the LCD.

        :param char_arr: 8-byte array of custom character
        :param location: Character location (0 to 7)

        """
        self._command(LCD_CMD_SETCGRAMADDR | (location << 3))
        for char_byte in char_arr:
            self._writeChar(char_byte)

    def setAutoscroll(self, state):                                                                         #turns on/off autoscroll
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


    def setTextDirection(self, direction = 0):                                                              # 0 = left to right, 1 = right to left
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

    def scrollLeft(self):                                                                                   #scroll display left
        """
        .. method:: scrollLeft()

        Scroll the display left.

        """
        self._command(LCD_CMD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)

    def scrollRight(self):                                                                                  #scroll display right
        """
        .. method:: scrollRight()

        Scroll the display right.

        """
        self._command(LCD_CMD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)

    def blinkOn(self, state):                                                                               #turn the blinking cursor on/off
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

    def displayOn(self, state):                                                                             #turn the display on/off
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

    def cursorOn(self, state):                                                                              #turns the cursor on/off
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

    def home(self):                                                                                         #sets the cursor to the home position (0,0)
        """
        ..method:: home()

        Home the cursor.

        """
        self._command(LCD_CMD_RETURNHOME)
        sleep(2)

    def setCursorPosition(self, col, row):                                                                  #sets the cursor position on the LCD
        """
        .. method:: setCursorPosition(col, row)

        Set the cursor position.

        :param col: Column (0 to 15)
        :param row: Row (0 to 1)

        """
        self._command(LCD_CMD_SETDDRAMADDR | col + row * 0x40)


    def writeString(self, string):                                                                          #write an entire string to the LCD
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

    def _command(self, cmd):                                                                                #send a command to the LCD
        self._send(cmd, 0)

    def _writeChar(self, char):                                                                             #write a character to the LCD
        self._send(ord(char), LCD_MODE_RS)
        return 1

    ######## Low level commands #########

    def _send(self, data, mode):                                                                            #send a byte or data to the LCD
        highBits = data & 0xF0
        lowBits = (data << 4) & 0xF0
        self._write4bits(highBits | mode)
        self._write4bits(lowBits | mode)

    def _write4bits(self, data):                                                                            #the data is sent 4 bits at a time with the last 4 bits being screen controls
        self._expanderWrite(data)
        self._pulseEnable(data)

    def _pulseEnable(self, data):                                                                           #pulses the enable pin to send data to the LCD
        self._expanderWrite(data | LCD_MODE_ENABLE)
        sleep(1)
        self._expanderWrite(data & ~LCD_MODE_ENABLE)
        sleep(1)

    def _expanderWrite(self, data):                                                                         #sends the data to the LCD appending the backlight value
        self._write(data | self._backlightval)

    def _write(self, data):                                                                                 #sends the data to the LCD
        buffer = bytearray(1)
        buffer.append(data)
        self.write(bytearray(buffer))
        sleep(2)
