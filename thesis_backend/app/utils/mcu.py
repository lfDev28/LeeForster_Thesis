import serial
import time
import pyvisa as visa


class Arduino_Controller:

    def __init__(self, port, baudrate=9600):
        """
        Initialize the connection to the Arduino.
        Args:
        - port (str): The port Arduino is connected to. e.g., "COM3" on Windows or "/dev/ttyACM0" on Linux.
        - baudrate (int): Baudrate for the serial connection. Default is 9600, which is commonly used with Arduino.
        """



        self.connection = serial.Serial(port=port, baudrate=9600, timeout=1, parity=serial.PARITY_NONE, stopbits=1, bytesize=8)
      


    def control_aux_lamp(self, state):
        """
        Control the auxiliary lamp.
        Args:
        - state (bool): True to turn on, False to turn off.

        Need to send RLY,1 to turn on and RLY,0 to turn off but without the quotation marks. 
        # Need to set the termination character to 0x0A (LF) in Arduino code
        """
        try:
            if state == True:
            # We can use the THM command to check if the connection is availble, if the length of that response is 0 then the connection is not available

                if not self.wait_for_connection():
                    raise Exception("Failed to connect to Arduino")
                else:
                    self.connection.write(b'RLY,1\n')

                
            else:
                if not self.wait_for_connection():
                    raise Exception("Failed to connect to Arduino")
                else:
                    self.connection.write(b'RLY,0\n')
                
                
                


                
        

                   

        except Exception as e:
            # print(e)
            print(f"Error Type: {type(e).__name__}, Error Message: {str(e)}")

            raise Exception("Failed to control auxiliary lamp: " + str(e))

    def close(self):
        """Close the serial connection."""
        self.connection.close()

    def wait_for_connection(self, retries=10):
        for i in range(retries):
            self.connection.write(b'THM\n')
            time.sleep(0.1)
            response = self.connection.readline().decode('utf-8').strip()

            if len(response) > 0:
                return True
        
        return False




