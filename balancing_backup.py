import pyvisa
import labrad
from qnl_ctrl import util
from labrad.units import GHz, MHz, Hz, dBm
import time




def connect_spectrum_analyzer():
	# connect to labrad server
	cxn = labrad.connect()

	# start node server and device servers
	node_server = util.get_node_server(cxn)
	# list of servers to start
	start_servers = ['GPIB Bus', 'GPIB Device Manager', 'Spectrum Analyzer Server']

	running_servers = util.start_servers(node_server, start_servers, False)
	# get server handles
	cfg_server = cxn[running_servers['Config Server']]
	sa_server = cxn[running_servers['Spectrum Analyzer Server']]
	bus_server = cxn[running_servers['GPIB Bus']]
	dm_server = cxn[running_servers['GPIB Device Manager']]

	# choose correct spectrum analyzer
	sa_server.list_devices()
	sa_server.select_device(0)
	return sa_server

def connect_Stahl(devName ='ASRL4::INSTR'):
	import pyvisa
	rm = pyvisa.ResourceManager()
	dev = rm.get_instrument('ASRL4::INSTR',read_termination='\r', write_termination='\r', baud_rate=115200)
	idn = dev.query('IDN')
	id_dev = idn[0:6];
	print('Connected to Stahl DC source')
	return (dev,id_dev)


# channel in string; voltage in float from 0 to 1;
def setVoltage(channel, voltage, dev, dev_name):
	str_v = "{:7.5f}".format(voltage)
	dev.query(dev_name+channel+str_v);
	return None


# stepID denotes which direction of the step
# stepID =1 when in y direction 
# stepID =2 when in x direction
def read(v_a,v_b,sleep_time=0.1):
	# if stepID ==1:
	# 	str_v_a = "{:7.5f}".format(v_a)
	# 	dev.query(id_dev+id_a+str_v_a)
	# elif stepID ==2:
	# 	str_v_b = "{:7.5f}".format(v_b)
	# 	dev.query(id_dev+id_b+str_v_b)
	# else:
	vol_a="{:7.5f}".format(v_a)
	vol_b="{:7.5f}".format(v_b)
	dev.query(dev_name+channel_a+vol_a);
	dev.query(dev_name+channel_b+vol_b);
	#time.sleep(0.2)
	#sa_server.center_frequency(fre_lo)
	time.sleep(sleep_time)
	#print(sleep_time)
	int_lo = sa_server.marker_position()[1]
	#sa_server.center_frequency(fre_sb)
	#time.sleep(1)
	#int_sb = sa_server.marker_position(fre_sb)[1]
	#print(v_a,v_b,int_lo,int_sb)
	return int_lo-int_sb





def gradient(x,y,thres, fun, step=2,pathID =0, resolution =0,sleep_time=0.2):
	z = fun(x,y,sleep_time);
	print(z)
	if z<thres:
		print(z)
		return (x,y);

	if (z<-40*dBm)&(z>-60*dBm)&(resolution<1):
		print('stage 1')
		resolution=1
		sleep_time=0.4
		sa_server.resolution_bandwidth(100*Hz);
		sa_server.span(100*Hz);
		time.sleep(0.5);
		sa_server.set_marker_to_peak()
		time.sleep(0.5)	
	elif (z<-60*dBm)&(z>-67*dBm)&(resolution<2):
		print('stage 2')
		resolution=2
		sleep_time=0.6
		sa_server.resolution_bandwidth(30*Hz);
		sa_server.span(0*Hz);
		time.sleep(0.5);
		sa_server.set_marker_to_peak()
		time.sleep(0.5)
	elif (z<-67*dBm)&(resolution<3):
		print('stage 3')
		resolution=3
		sleep_time=0.5
		sa_server.resolution_bandwidth(10*Hz);
		sa_server.span(0*Hz);
		time.sleep(0.8);
		sa_server.set_marker_to_peak()
		time.sleep(0.8)	

	# id=1 go up
	if (pathID !=3) & (fun(x,y+step,sleep_time)<z):
		return gradient(x,y+step,thres,fun,step,1, resolution,sleep_time);
	# id=2 turn right
	elif (pathID != 4)&( fun(x+step,y,sleep_time)<z ):
		return gradient(x+step,y, thres,fun, step,2, resolution,sleep_time);
	# id =3 go down
	elif ( pathID!=1 ) & ( fun(x,y-step,sleep_time)<z ):
		return gradient(x,y-step, thres,fun,step,3, resolution,sleep_time);

	# id= 4 turn left
	elif ( pathID!=2) & ( fun(x-step,y,sleep_time)<z ):
		return gradient(x-step,y,thres,fun,step,4, resolution,sleep_time);
	else:
		return gradient(x,y,thres,fun,step/2,pathID, resolution,sleep_time);


def gradient2(x,y,thres,fun,step=0.2,pathID=0,current_val=0, resolution =0,sleep_time=0.15):

	if pathID==0:
		current_val = fun(x,y,sleep_time)
	print(current_val)

	if current_val<thres:
		print step
		return (x,y)
		#set the spectrum analyzer to different configuration

	if (current_val<-40*dBm)&(current_val>-60*dBm)&(resolution<1):
		print('stage 1')
		resolution=1
		sleep_time=0.5#0.6
		sa_server.resolution_bandwidth(100*Hz);
		sa_server.span(100*Hz);
		time.sleep(0.5);
		sa_server.set_marker_to_peak()
		time.sleep(0.5)	
		#step =0.0125
		#print step
	elif (current_val<-60*dBm)&(current_val>-67*dBm)&(resolution<2):
		print('stage 2')
		resolution=2
		sleep_time=0.4#0.7
		sa_server.resolution_bandwidth(30*Hz);
		sa_server.span(100*Hz);
		time.sleep(0.5);
		sa_server.set_marker_to_peak()
		time.sleep(0.5)

		#step =0.0008
	elif (current_val<-67*dBm)&(resolution<3):
		print('stage 3')
		resolution=3
		sleep_time=0.5
		sa_server.resolution_bandwidth(10*Hz);
		sa_server.span(100*Hz);
		time.sleep(0.8);
		sa_server.set_marker_to_peak()
		time.sleep(0.8)	
		step =0.01


		# choose different paths according to previous step
	paths={0:(1,2,3,4),1:(1,2,4),2:(2,3,1),3:(3,4,2),4:(4,1,3)}
	# 1 ==go up, 3== go down, 2==turn right, 4==turn left
	step_dir={1:(0,1),2:(1,0),3:(0,-1),4:(-1,0)}
	# traverse the path
	for i in paths[pathID]:
		next_val =fun(x+step_dir[i][0]*step,y+step_dir[i][1]*step,sleep_time) 
		if next_val < current_val:
			return gradient2(x+step_dir[i][0]*step,y+step_dir[i][1]*step,thres,fun,step,i,next_val, resolution,sleep_time)
	# if all the direction fails
	return gradient2(x,y,thres,fun,step/2,pathID,current_val, resolution,sleep_time)



def chnl_str(chnl_num):
	if chnl_num<10:
		chnl_str = 'CH0{} '.format(chnl_num);
	else:
		chnl_str= 'CH{} '.format(chnl_num);
	return chnl_str


def nulling(chnl_a,chnl_b,thres):
	print('looking for optimal point')

	# resolution bandwidth and read time , and scope window !!!!!!!!!!!
	#results = gradient2(0.33,0.46,-80*dBm,read, 0.1);
	results = gradient2(0,0,thres,read, 0.1);
	return (results[0],results[1])




# remember to pass current value
def recalibrate(chnl_a,chnl_b,x,y,fre_lo,fre_sb,sa_server,dev,dev_name):
	gradient2(x,y,thres,fun,0.1,0,-45*dBm)
	step =0.0004






# print('looking for optimal point')

# # resolution bandwidth and read time , and scope window !!!!!!!!!!!



# gradient2(0.33,0.46,-70*dBm,read, 0.1);
# dev.close()
time_start = time.time();
sa_server = connect_spectrum_analyzer();
# connect to the DC source
temp = connect_Stahl()
dev_name = temp[1]
dev = temp[0]
# the space in the end of the string is critical
channel_a = chnl_str(1)

channel_b = chnl_str(2)

# initialize the DC source to 0mV, 0mV
setVoltage(channel_a,0.5,dev,dev_name);
setVoltage(channel_b,0.5,dev,dev_name);

# default value of the frequencies
fre_lo = 5*GHz;
fre_detuning = 0.1*GHz;
fre_sb = fre_lo- fre_detuning;

print('Correcting side band frequency')
sa_server.resolution_bandwidth(1000*Hz);
sa_server.span(8000*Hz);
sa_server.center_frequency(fre_sb)
time.sleep(0.8)
sa_server.set_marker_to_peak()
time.sleep(0.8)
temp = sa_server.marker_position()
time.sleep(1)
int_sb = temp[1]
fre_sb = temp[0].inUnitsOf(GHz)
print('side band = ',int_sb)

#find the lo peak
print('Correcting LO frequency')
sa_server.resolution_bandwidth(1000*Hz);
sa_server.span(0.1*MHz);
sa_server.center_frequency(fre_lo)
time.sleep(0.6)
sa_server.set_marker_to_peak()
time.sleep(0.4)
fre_peak = sa_server.marker_position()[0]
time.sleep(0.4)
sa_server.center_frequency(fre_peak)
time.sleep(0.4)

print('stage 0')
sa_server.resolution_bandwidth(3000*Hz);
sa_server.span(5000*Hz);
time.sleep(0.6)
sa_server.set_marker_to_peak()
time.sleep(0.6)
fre_lo = sa_server.marker_position()[0]
sa_server.center_frequency(fre_lo)
time.sleep(0.4)

temp =nulling(1,2,-70*dBm)
elapsed_time = time.time()-time_start;
print('elapsed time {0}'.format(elapsed_time))

time_start = time.time();
gradient2(temp[0]+0.05,temp[1]+0.05,-80*dBm,read)
elapsed_time = time.time()-time_start;
print('elapsed time {0}'.format(elapsed_time))


####################################### full map scan
# step = 0.1;
# n = 1/step;
# n= int(n);
# tolerance = 60 # in dB

# diff = int_lo-int_sb;
# min_index_a =0;
# min_index_b =0;

# for i in range(0,n+1):
# 	str_v_a = "{:7.5f}".format(i*step)
# 	dev.query(id_dev+id_a+str_v_a)
# 	for j in range(0,n+1):
# 		str_v_b = "{:7.5f}".format(j*step)
# 		# write to DC
# 		dev.query(id_dev+id_b+str_v_b)
# 		# read from sa
# 		time.sleep(0.1)
# 		int_lo = sa_server.marker_position(fre_lo)[1]
# 		int_sb = sa_server.marker_position(fre_sb)[1]
# 		print(int_lo-int_sb)
		
# 		if  int_lo-int_sb < diff:
# 			min_index_b = j;
# 			min_index_a = i;
# 			diff = int_lo-int_sb;


# # set the voltage to the optimal points
# str_v_a = "{:7.5f}".format(min_index_a*step)
# str_v_b = "{:7.5f}".format(min_index_b*step)
# dev.query(id_dev+id_a+str_v_a)
# dev.query(id_dev+id_b+str_v_b)

# print(diff)
#############################################




# #connect to spectrum analyzer
# sa_server = connect_spectrum_analyzer();
# # connect to the DC source
# temp = connect_Stahl()
# dev_name = temp[1]
# dev = temp[0]


# # the space in the end of the string is critical
# channel_a = 'CH0{} '.format(1);
# channel_b = 'CH0{} '.format(2);

# # initialize the DC source to 0mV, 0mV
# setVoltage(channel_a,0.5,dev,dev_name);
# setVoltage(channel_b,0.5,dev,dev_name);


# fre_lo = 5*GHz;
# fre_detuning = 0.1*GHz;
# fre_sb = fre_lo- fre_detuning;





# print('Correcting side band frequency')
# sa_server.resolution_bandwidth(1000*Hz);
# sa_server.span(8000*Hz);
# sa_server.center_frequency(fre_sb)

# time.sleep(0.8)
# sa_server.set_marker_to_peak()
# time.sleep(0.8)
# temp = sa_server.marker_position()
# time.sleep(1)
# int_sb = temp[1]

# fre_sb = temp[0].inUnitsOf(GHz)

# print('side band = ',int_sb)






# #find the lo peak
# print('Correcting LO frequency')
# sa_server.resolution_bandwidth(1000*Hz);
# sa_server.span(0.1*MHz);
# sa_server.center_frequency(fre_lo)
# time.sleep(0.6)
# sa_server.set_marker_to_peak()
# time.sleep(0.4)
# fre_peak = sa_server.marker_position()[0]
# time.sleep(0.4)
# sa_server.center_frequency(fre_peak)
# time.sleep(0.4)
# # stage 1
# sa_server.resolution_bandwidth(1000*Hz);
# sa_server.span(6000*Hz);
# time.sleep(0.6)
# sa_server.set_marker_to_peak()
# time.sleep(0.6)
# fre_lo = sa_server.marker_position()[0]
# sa_server.center_frequency(fre_lo)
# time.sleep(0.4)