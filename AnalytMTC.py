#!/usr/bin/env python3

# 09.05.2016
# Alexander Schuetz

# cloned from https://subversion.isas.de/svn
# alexander.schuetz@uni-dortmund.de

"""
Python module for Analyt-MTC flow controller and flow meter. Set FlowControler to serial mode to use it!
"""

__version__ = '0.1'

import serial, time, sys

###################################################################################################


class AnalytMTC(object):
    
    
    def __init__(self, serialport='/dev/ttyUSB0', baudrate=19200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, unitid=None, maxflow=None):
        self.Serialport = serialport
        self.Baudrate = baudrate
        self.Parity = parity
        self.Stopbits = stopbits
        self.Bytesize = bytesize
        self.Timeout = 0.25        
        self.Eol = b"\r"
        
        self.UnitID = unitid
        self.Maxflow = maxflow
        
        
        
    def startCommunication(self,debug=False):
        try:
           self.Ser = serial.Serial(self.Serialport, self.Baudrate, self.Bytesize, self.Parity, self.Stopbits, self.Timeout)
        except:
            print("Error opening serial port.") 
            sys.exit(0)
        if debug is True:    
            print(("Opening " + self.Ser.portstr)) 
             
            
            
    def stopCommunication(self,debug=False):
        self.Ser.close() 
        if debug is True:  
            print(("Closing " + self.Ser.portstr)) 
      
               
    
    def _receiveAns(self):
            line = bytearray()
            while True:
                c = self.Ser.read(1)
                #c = self.Ser.readline()
                if c:
                    line += c
                    if line[-len(self.Eol):] == self.Eol:
                        break
                else:
                    break                   
            try:
                #return line.decode() 
                return line.decode("utf-8").strip()
            except:
                return None    
                             
        
    
    # private: send function    
    def _sendCommand(self, cmd):
        # workaround: works well if command is send two times with a delay of 0.05 secs...   
        time.sleep(0.25)
        self.Ser.write(str.encode(cmd))
        self.Ser.write(str.encode(chr(13)))
        time.sleep(0.05)
        ans = self._receiveAns()
        return ans

      
         
###################################################################################################   

    # public get methods 
    
    def getMaxFlow(self):
        return self.Maxflow
            
  
    # get data as splitted string -> set to @
    def getData(self):          
        self._sendCommand(self.UnitID)
        time.sleep(0.1)
        return self._sendCommand(self.UnitID).split(" ")

        
    
    # get atmospheric pressure [mBar] 
    def getAirPressure(self):
        return self.getData(self.UnitID)[0]
        
   
   # get athmospheric pressure [mBar] 
    def getTemperature(self):
        return self.getData(self.UnitID)[1]      
               
    
    # get gas    
    def getGas(self):
        return self.getData(self.UnitID)[9]
        
     
    # get current flow    
    def getCurrentFlow(self):
        return self.getData(self.UnitID)[2]
        
    # get target flow    
    def getTargetFlow(self):
        return self.getData(self.UnitID)[4]    
        
        
    # public send methods ...    
        
        
    # set flow in ml/min
    def setFlow(self, flow=0):
        c = (flow*64000)//(self.Maxflow)
        return self._sendCommand(self.UnitID+str(c))
        
    # ...    
  
 
###################################################################################################

# This class can be used to mix gases from different flow controller.
      
class MultiAnalytMTC(object):  

    def __init__(self, fc1, fc2):
        self.FlowC1 = fc1
        self.FlowC2 = fc2

        
    def setSplittedFlow(self, totalflow, ratio):
        ratio1 = round(totalflow*ratio)
        ratio2 = round(totalflow*(1-ratio))        
        #print(ratio1,ratio2)       
        self.FlowC1.setFlow(ratio1)
        #time.sleep(0.07)              
        self.FlowC2.setFlow(ratio2)
        
        
###################################################################################################
                  
