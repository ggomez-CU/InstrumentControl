import numpy as np
import pyvisa
from .InstrumentClass import *
import sys

import datetime
import os
# import PowerMeterClass
# import PowerSupplyClass
# import MultimeterClass
# import InstrumentClass
# import DCBiasingSupplyClass

def WriteReadMe(additonal_string, Freq1, Freq2, 
    TestType = "Unknown",
    Drain = None,
    Gate = None,
    InputPower = None,
    OutputPower = None,
    RFInput = None,
    Sampler1 = None,
    Sampler2 = None,
    OpAmp = None):

    

    # now = datetime.datetime.now().strftime("%m-%d-%y_%H%M%S")
    path = "./README/"
    try:
        os.mkdir(path)
    except FileExistsError:
        pass
    filename = "README_" + TestType + ".md"
    f = open(path + filename,"a")

    f.write("These tests were run for frequencies between" + str(Freq1) + " MHz and " + str(Freq2) + " MHz\n")

    if Drain:
        f.write("<h2>Drain  DC Power Supply</h2>\n")
        f.write("Drain instrument was " + Drain.IDN + "</br>\n")
        f.write("Drain channel was " + Drain.channel + "</br>\n")
        f.write("Starting conditions for the Drain was current limit of "
            + Drain.instr.query("CURR:LIM?")
            + " and voltage set to "
            + Drain.instr.query("VOLT?")
            + "</br>\n")

    if Gate:
        f.write("<h2>Gate DC Power Supply</h2>\n")
        f.write("Gate instrument was " + Gate.IDN +  "</br>\n")
        f.write("Gate channel was " + Gate.channel +"</br>\n")
        f.write("Starting conditions for the Gate was current limit of "
            + Gate.instr.query("CURR:LIM?")
            + " and voltage set to "
            + Gate.instr.query("VOLT?")
            + "</br>\n")

    if InputPower:
        f.write("<h2>Input Power Meter</h2>")
        f.write("Input Power Meter instrument was " + InputPower.IDN + "</br>\n")
        if InputPower.HP:
            f.write("The cal factor file was " + InputPower.CalFile)
        if InputPower.RS:
            f.write("The average samples are set to " + InputPower.AvgSamples)

    if OutputPower:
        f.write("<h2>Output Power Meter</h2>\n")
        f.write("Output Power Meter instrument was " + OutputPower.IDN + "</br>\n")
        if OutputPower.HP:
            f.write("The cal factor file was " + OutputPower.CalFile)
        if OutputPower.RS:
            f.write("The average samples are set to " + OutputPower.AvgSamples)

    if RFInput:
        f.write("<h2>RF Input Power Supply</h2>\n")
        f.write("Output Power Meter instrument was " + RFInput.IDN + "</br>\n")

    if Sampler1:
        f.write("<h2>Multimeter for Sampler 1</h2>\n")
        f.write("multimeter for sampler 1 instrument was " + Sampler1.IDN + "</br>\n")

    if Sampler2:
        f.write("<h2>Multimeter for Sampler 2</h2>\n")
        f.write("multimeter for sampler 2 instrument was " + Sampler2.IDN + "</br>\n")

    if OpAmp:
        f.write("<h2>Multimeter for Op Amp Output</h2>\n")
        f.write("multimeter for Op Amp Output instrument was " + OpAmp.IDN + "</br>\n")

    f.write("<h2>Additional</h2>\n")
    f.write(additonal_string)

    f.close

    return

class InstrumentClass():

    """
    Base instrument class class. 

    Parameters
    ---------- 
    port: int
        the port number of gpib connection 
    channel = None: int
        used with instrument with more than one channel 
    ConnectionType = 'GPIB1'
    """

    def __init__(self, port, channel = None, ConnectionType = 'GPIB1'):
        self.connected = False
        self.port = str(port)
        self.ConnectionType = ConnectionType
        self.IDN = ""
        self.instr = None

        if channel:
            channel = str(channel)

        self.channel = channel

        #Run functions
        self.InstrumentConnection()

    def InstrumentConnection(self):
        rm = pyvisa.ResourceManager()
        #rm.list_resources()

        print('Attempting connection to port ' + self.port +'... ', end='')
        try:
            self.instr = rm.open_resource(self.ConnectionType + '::' + self.port + '::INSTR')
        except:
            print('connection unsuccessful')
            return

        self.IDN = self.instr.query("*IDN?").rstrip()
        print('Instrument Identified as ' + self.IDN + "...", end='')
        print('connection successful\n')
        self.connected = 1

class PowerSupplyClass(InstrumentClass):

    def __init__(self, port, ConnectionType = 'GPIB0'):
        InstrumentClass.__init__(self,port, ConnectionType)
        self.SetUp()

    def SetUp(self):
        self.instr.write("POW -60 DBM")
        self.instr.write("OUTP:STAT OFF")

    def SetPower(self, PowerLevel, UnitType = "DBM"):
        self.instr.write("POW " + str(PowerLevel) + " " + UnitType)

    def SetFrequency(self, Frequency, UnitType = "GHZ"):
        self.instr.write("FREQ " + str(Frequency) + " " + UnitType)

class PowerMeterClass(InstrumentClass):

    def __init__(self, port, CalFile = None, AvgSamples = 0):
        InstrumentClass.__init__(self,port)
        self.CalFile = CalFile
        self.AvgSamples = AvgSamples
        self.CalData = None
        self.CalReferenceFactor = 100
        self.Freq = None
        self.CalFreq = None
        self.HP = False
        self.RS = False

        if "HEWLETT-PACKARD" in self.IDN:
            self.CalData = self.SetUpHP_PowerMeter(CalFile)
            self.HP = True

        if "RS" in self.IDN:
            self.SetUpRS_PowerMeter(self, AvgSamples)
            self.RS = True

    def SetUpHP_PowerMeter(self, CalFile):
        print('Attempting HP power meter set up... ', end='')
        if (CalFile):
            try:
                CalData = np.loadtxt(CalFile)
                print("set up sucessful\n")
                return CalData
            except:
                print("set up failed\n")
                exit()

    def SetUpRS_PowerMeter(self, AvgSamples):
        print('Attempting Keysite power meter set up... ', end='')
        self.instr.write('INIT:CONT OFF')
        self.instr.write('SENS:FUNC "POW:AVG"')
        self.instr.write('SENS:AVER:COUN:AUTO OFF')
        self.instr.write('SENS:AVER:COUN ' + str(AvgSamples))
        self.instr.write('SENS:AVER:STAT ON')
        self.instr.write('SENS:AVER:TCON REP')
        #self.instr.write('FORMAT ASCII')
        print("set up complete")

    def SetCalFreq_HP(self, Freq):

        #This aligns with a text file of the format: Freq column1 and cal factor column 2
        self.CalReferenceFactor = self.CalData [self.CalData['Freq']==Freq][2]
        self.CalFreq = Freq
        print(self.instr.write("KB" + str(self.CalReferenceFactor) + "EN"))

    def SetFrequency(self, Freq):
        self.Freq = Freq

    def MeasurePower(self):
        if self.HP:
            #Check Calibration
            if self.CalFreq != self.Freq:
                self.SetCalFreq_HP(self.Freq)

            return self.instr.query("MEAS1?").rstrip()

        elif self.RS:
            self.instr.write('SENS:FREQ ' + self.Freq)
            self.instr.query('INIT:IMM')
            while int(self.instr.query('STAT:OPER:COND?')) >0: pass
            return self.instr.query('FETCH?').rstrip()

        else:
            print("Unrecognized Power Meter")
            exit()


class MultimeterClass(InstrumentClass):
    
    def __init__(self, port, channel = None, ConnectionType = 'GPIB1', Sampler = None):
        InstrumentClass.__init__(self, port, channel, ConnectionType)
        
        if Sampler:
            self.SamplerNumber = Sampler

    def MeasureDC(self, QueryType = "VOLT"):
        MeasurementQuery = "MEAS:" + QueryType +":DC?"
        return self.instr.query(MeasurementQuery)

class DCPowerSupply(InstrumentClass):

	def __init__(self, port, channel=1, ConnectionType = 'GPIB0', SupplyType = None):
		InstrumentClass.__init__(self, port, channel, ConnectionType)
		self.writable = False
		self.gate = False
		self.drain = False
		self.channel = channel

		if SupplyType == 'Gate':
			self.gate = True
		elif SupplyType == 'Drain':
			self.drain = True
		else:
			print("Unrecognizable Supply Type. Ending Program.")
			exit()

	def MeasureDC(self, Channel = None, QueryType = "VOLT"):
		if not(Channel):
			Channel = self.channel
	   # the other option for query type is CURR
		
		MeasurementQuery = "MEAS:SCAL:" + QueryType +":DC? (@" + str(Channel) + ")"
		return self.instr.query(MeasurementQuery)

	def SetDC(self, SetVal, Channel = None, WriteType = "VOLT"):
		if not(Channel):
			Channel = self.channel
		if not(self.writable):
			if (self.drain):
				print("There is an attempt to change Drain Voltage through the program. Please ensure the Drain is on Port: " + str(self.port) + " before continuing")
				print("Drain Suuply IDN is: " + str(self.IDN))
				if Channel is not None:
					print("Drain channel is " + str(Channel))
					user_input = input("Enter 'q' to quit or ENTER to continue: ")
					if user_input == 'q':
						sys.exit("You chose to quit the program. ")
					else:
						self.writable = True
			elif self.gate:
				print("There is an attempt to change Gate Voltage through the program. Please ensure the Gate is on Port: " + str(self.port) + " before continuing")
				print("Gate Supply IDN is: " + self.IDN)
				if Channel:
					print("Gate channel is " + str(Channel))
					user_input = input("Enter 'q' to quit or ENTER to continue: ")
					if user_input == 'q':
						sys.exit("You chose to quit the program. ")
					else:
						self.writable = True
			else:
				print("There is an attempt to change Port: " + str(self.port) + " voltage.\nThe connection type is unknown. Please double check before continuing")
				if Channel:
					print("The channel is " + str(Channel))
				user_input = input("Enter 'q' to quit or ENTER to continue: ")
				if user_input == 'q':
					sys.exit("You chose to quit the program. ")
				else:
					self.writable = True
                


		MeasurementQuery = WriteType +":LEV " + str(SetVal) + ", (@" + str(Channel) + ")"
		self.instr.write(MeasurementQuery)
