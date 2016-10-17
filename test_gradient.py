def paraboloid(x,y):
	return (x+10)**2+(y-20)**2


# path ID is defined relative to the current position
# thres is the number we want to reach below
def gradient(x,y,thres, fun, step=2,pathID =0):
	z = fun(x,y);
	if z<thres:
		return (x,y);
	# id=1 go up
	elif (pathID !=3) & (fun(x,y+step)<z):
		return gradient(x,y+step,thres,fun,step,1);
	# id=2 turn right
	elif (pathID != 4)&( fun(x+step,y)<z ):
		return gradient(x+step,y, thres,fun, step,2);
	# id =3 go down
	elif ( pathID!=1 ) & ( fun(x,y-step)<z ):
		return gradient(x,y-step, thres,fun,step,3);

	# id= 4 turn left
	elif ( pathID!=2) & ( fun(x-step,y)<z ):
		return gradient(x-step,y,thres,fun,step,4);
	else:
		return gradient(x,y,thres,fun,step/2,pathID);


def optimize(x,y,thres, fun):
	
	cur = fun(x,y)
	while cur > thres:
		try:
			return gradient(x,y,thres,fun);
		except







# to print the massage

try:
	gradient();
except RuntimeError,e:
	print('Run time error: {0}'.format(e))