




def connect_Stahl(devName ='ASRL4::INSTR'):
	import pyvisa
	rm = pyvisa.ResourceManager()
	dev = rm.get_instrument('ASRL4::INSTR',read_termination='\r', write_termination='\r', baud_rate=115200)
	idn = dev.query('IDN')
	id_dev = idn[0:6];
	return (dev,id_dev)



def setVoltage(channel, voltage, dev, dev_name):
	if channel <10:
		channel_id = 'CH0'+ str(channel)+' ';
	else :
		channel_id = 'CH' + str(channel)+' ';

	voltage_s = (voltage+100)/200.0; 
	str_v = "{:7.5f}".format(voltage_s)
	dev.query(dev_name+channel_id+str_v);
	return None


# method call
temp = connect_Stahl()
dev = temp[0]
dev_name = temp[1]


# voltage goes from -100mV to 100mV
setVoltage(1,50,dev,dev_name)