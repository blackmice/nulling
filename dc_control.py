class dc_control:

	def __init__(self,devName ='ASRL4::INSTR'):
		import pyvisa
		rm = pyvisa.ResourceManager()
		self.dev = rm.get_instrument('ASRL4::INSTR',read_termination='\r', write_termination='\r', baud_rate=115200)
		idn = self.dev.query('IDN')
		self.dev_name = idn[0:6];
		
	def setVoltage(self,channel, voltage):
		if channel <10:
			channel_id = 'CH0'+ str(channel)+' ';
		else :
			channel_id = 'CH' + str(channel)+' ';

		voltage_s = (voltage+100)/200.0; 
		str_v = "{:7.5f}".format(voltage_s)
		self.dev.query(self.dev_name+channel_id+str_v);
		return None


