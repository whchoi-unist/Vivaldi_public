# small helper functions go here
import time, numpy, sys, copy, ast, os
import getpass
import socket
from StringIO import StringIO

import Image

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_green(source, location=' '):
	return 
	print bcolors.OKGREEN, source, location,  bcolors.ENDC

def print_red(source, location=' '):
	return
	print bcolors.FAIL, source, location, bcolors.ENDC

def print_blue(source, location=' '):
	return
	print bcolors.OKBLUE, source, location, bcolors.ENDC

def print_bblue(source, location=' '):
	return
	print '%s%s%s%s%s'%(bcolors.OKBLUE, bcolors.BOLD, source, location, bcolors.ENDC)

def print_bred(source, location=' '):
	return
	print '%s%s%s%s%s'%(bcolors.FAIL, bcolors.BOLD, source, location, bcolors.ENDC)

def print_bpurple(source, location=' '):
	return
	print '%s%s%s%s%s'%(bcolors.HEADER, bcolors.BOLD, source, location, bcolors.ENDC)

def print_yellow(source, location=' '):
	return
	print bcolors.WARNING, source, location, bcolors.ENDC

def print_purple(source, location=' '):
	return
	print bcolors.HEADER, source, location, bcolors.ENDC

def print_bold(source, location=' '):
	return
	print bcolors.BOLD, source, location, bcolors.ENDC

VIVALDI_PATH = os.environ.get('vivaldi_path')

path = VIVALDI_PATH + "/src"
if path not in sys.path:
	sys.path.append(path)
	
from common import *

GIGA = float(1024*1024*1024)
MEGA = float(1024*1024)
KILO = float(1024)
AXIS = ['x','y','z','w']
SPLIT_BASE = {'x':1,'y':1,'z':1,'w':1}
modifier_list = ['execid','split','range','merge','halo','output_halo']

log_type = ""
GPUDIRECT = "on"

BLOCK_SIZE = 16

OPERATORS = ["==",'+=','-=','*=','/=','=','+','-','*','/',"<=","=>","<",">","."]

def log(a, ptype, type):
	# log print type
	# time
	# parsing
	# general
	# detail
	# all
	flag = False
	if ptype == 'all' or type == 'all':
		flag = True

	if type == 'detail' and ptype in ['detail', 'general']:
		flag = True

	if type == ptype:
		flag = True
	
	if flag == True:
		print "[%.2f] %s"%(time.time(), a)

def read_file(name):
	"read a file into a string"
	f = open(name)
	x = f.read()
	f.close()
	return x
    
def write_file(name, x):
    "write string into a file"
    f = open(name, "w")
    f.write(x)
    f.close()
    
def normalize(v):
    return v / sqrt(dot(v, v))
    
def cross(a, b):
    return array([a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0]])

def mk_frame(position, target, up):
    "create camera frame"
    
    z = normalize(target - position)
    x = normalize(cross(z, up))
    y = normalize(cross(z, x))
    
    return r_[x, y, z, position]

def find_index(p, l):
    "find first index in l that satisfies predicate p"
    for i, x in enumerate(l):
        if p(x):
            return i
    return None
    
def rotation_matrix(axis, angle):
    x, y, z = axis
    c = cos(angle)
    u_cross = r_[0, -z, y, z, 0, -x, -y, x, 0]
    u_cross.shape = 3, 3
    return c * eye(3) + sin(angle) * u_cross + (1-c) * outer(axis, axis)

# etc
##########################################################################################################################
def make_bytes(in1=None, in2=None, in3=None):
	bytes = 1
	temp_list = [in1,in2,in3]

	for elem in temp_list:
		if elem == None:
			pass
		elif type(elem) in [tuple,list]:
			for x in elem: bytes *= x
		elif type(elem) == dict:
			for x in elem: bytes *= elem[x][1]-elem[x][0]
		else:
			bytes *= elem

	return bytes

def make_split_position(split_shape, n):
	if n == 0:
		print "I assumed n start from 1. if you want to set n as zero, please double check"

	p = 0
	split_position = dict(SPLIT_BASE)
	ss = split_shape
	sp = split_position
	sp[AXIS[0]] = n
	for axis in AXIS:
		if axis not in split_shape:
			split_shape[axis] = 1


	for axis in AXIS[0:-1]:
		q = sp[AXIS[p]]
		w = ss[AXIS[p]]
		a = int(q/w)

		if a*w == q: a -= 1
		sp[AXIS[p]] -= a*w
		sp[AXIS[p+1]] += a
		p += 1

	return split_position
		
def shape_to_range(shape):
	full_data_range = {}
	n = len(shape)
	if n >= 1:full_data_range['x'] = (0, shape[n-1])
	if n >= 2:full_data_range['y'] = (0, shape[n-2])
	if n >= 3:full_data_range['z'] = (0, shape[n-3])
	if n >= 4:full_data_range['w'] = (0, shape[n-4])

	return full_data_range
		
def range_to_shape(rg):
	temp = []
	for axis in AXIS[::-1]:
		if axis in rg:
			temp.append(rg[axis][1]-rg[axis][0])
	return tuple(temp)

def shape_to_count(shape):
	count = 1
	for num in shape:
		count *= shape[num]
	return count

def make_cuda_list(rg, size=-1, order=False):
	temp = []
	if size == -1: size = len(rg)
	if order == True: LT = AXIS[0:size]
	else: LT = AXIS[0:size][::-1]
	for axis in LT:
		if axis in rg:
			temp.append(numpy.int32(rg[axis][0]))
			temp.append(numpy.int32(rg[axis][1]))
		else:
			temp.append(numpy.int32(0))
			temp.append(numpy.int32(0))
	return temp

def range_to_block_grid(rg, size=8, div=1):
	block = []
	grid = []
	for axis in AXIS[:3]:
		if axis in rg:
			block.append(int(size))
			grid.append((rg[axis][1] - rg[axis][0]-1)/size + 1)
		else:
			block.append(int(1))
			grid.append(int(1))
	block = tuple(block)
	grid = tuple(grid)
	return block, grid

def make_memory_shape(shape, cms):
	memory_shape = tuple(shape)
	if cms != [1]: memory_shape = tuple(list(shape) + cms)
	return tuple(memory_shape)


def load_from_hdfs_block(data_package, hdfs_addr, hdfs_path):
#def load_from_hdfs(data_package, file_name='CThead_uchar.raw'):
	if log_type in ['time','all']: st = time.time()
	dp = data_package
	ds = dp.data_range
	ds_seq = [ds[elem][1]-ds[elem][0] for elem in ['z', 'y', 'x'] if elem in ds]


	while True:
		try:
			client = InsecureClient(hdfs_addr, user=getpass.getuser())
			
		
			file_python_dtype = Vivaldi_dtype_to_python_dtype(dp.file_dtype)
			file_bytes = get_bytes(file_python_dtype)
		
			#print "START TO CONNECT HDFS"
			bef = time.time()
			with client.read(hdfs_path, offset=(ds_seq[1]*ds_seq[2]*ds['z'][0]*file_bytes),length=ds_seq[0]*ds_seq[1]*ds_seq[2]*file_bytes) as reader:
				buf = reader.read()
			aft = time.time()
		
			diff = aft - bef
		
			print_bold( "DATA LOADING ENDS from %s -- time elapsed = %.03f (sec) , reading speed = %.03f MB/sec"%(socket.gethostname(), diff, len(buf) / diff * (1024 ** -2)))
			data = numpy.fromstring(buf, dtype=file_python_dtype).reshape(ds_seq)

			break

		except:
			print bcolors.WARNING + "Connection Broken" + bcolors.ENDC
	

	return data

def load_file_list_from_hdfs(data_package):
	if log_type in ['time','all']: st = time.time()
	hdfs_str  = data_package.stream_hdfs_file_name
	hdfs_addr = hdfs_str[:hdfs_str.rfind('0/')+1]
	hdfs_path = hdfs_str[hdfs_str.rfind('0/')+2:]


	client = InsecureClient(hdfs_addr, user=getpass.getuser())
	return client.list(hdfs_path), hdfs_path
	
def load_from_hdfs(data_package, file_name):
#def load_from_hdfs(data_package, file_name='CThead_uchar.raw'):
	hdfs_str  = data_package.stream_hdfs_file_name
	hdfs_addr = hdfs_str[:hdfs_str.rfind('0/')+1]
	hdfs_path = hdfs_str[hdfs_str.rfind('0/')+2:]

	if log_type in ['time','all']: st = time.time()
	client = InsecureClient(hdfs_addr, user=getpass.getuser())


	with client.read('%s/%s'%(hdfs_path, file_name)) as reader:
		data = numpy.array(Image.open(StringIO(reader.read())))

	print_purple("LOADED")

	return data
	
	
		
#FREYJA STREAMING
def load_data(data_package, data_range, fp=None):

	if log_type in ['time','all']: st = time.time()
	dp = data_package
	file_name = dp.file_name

	data_range = dict(data_range)

	p = file_name.find('.')
	extension = file_name[p+1:].lower()

	if fp != None:
		f = fp
	else:
		f = open(file_name,'rb')

	# creat data for memroy read
	chan = dp.data_contents_memory_shape
	shape = range_to_shape(data_range)
	data_memory_shape = list(shape)
	if chan != [1]: data_memory_shape = list(shape) + chan
	data_contents_memory_dtype = dp.data_contents_memory_dtype

	length = 1
	for elem in data_memory_shape:
		length *= elem

	file_size = {}
	i = 0
	for axis in AXIS[::-1]:
		if axis in data_range:
			file_size[axis] = dp.full_data_range[axis][1]-dp.full_data_range[axis][0]
		else:
			file_size[axis] = 0
		i += 1


	# index of start point
	data_start = {}
	for axis in AXIS:
		if axis not in data_range:	data_start[axis] = 0
		else: data_start[axis] = data_range[axis][0]

	dim = len(data_range)
	if dim == 2:
		W = file_size['w']
		Z = file_size['z']
		Y = file_size['y']
		X = file_size['x']
		
		ss = ''
		idx = data_start['y']*X
		file_python_dtype = Vivaldi_dtype_to_python_dtype(dp.file_dtype)
		file_bytes = get_bytes(file_python_dtype)

		for y in range(data_range['y'][0], data_range['y'][1]):
			idx = y * (X) * file_bytes
			f.seek(idx,0)
			ts = f.read((X) * file_bytes)
			ss += ts

		buf = numpy.fromstring(ss, dtype=file_python_dtype)
		height = data_range['y'][1]-data_range['y'][0]
		buf = buf.reshape((height,X))
		buf = buf[:, data_range['x'][0]:data_range['x'][1]]

		buf = buf.astype(data_contents_memory_dtype)
	
	elif dim == 3:
		W = file_size['w']
		Z = file_size['z']
		Y = file_size['y']
		X = file_size['x']
		
		ss = ''
		idx = data_start['z']*X*Y
		file_python_dtype = Vivaldi_dtype_to_python_dtype(dp.file_dtype)
		file_bytes = get_bytes(file_python_dtype)*chan[0]

		for z in range(data_range['z'][0], data_range['z'][1]):
			idx = z * (X*Y) * file_bytes
			f.seek(idx,0)
			ts = f.read((X*Y) * file_bytes)
			ss += ts

		#import time
		#prev = time.time()
		buf = numpy.fromstring(ss, dtype=file_python_dtype)
		#diff = time.time()-prev
		#print "From string to numpy array, speed = %.03f MB/sec"%(len(ss) /diff * 1024 ** -2)
		depth = data_range['z'][1]-data_range['z'][0]

		if chan == [1]:
			buf = buf.reshape((depth,Y,X))
		else:
			buf = buf.reshape((depth,Y,X,chan[0]))

		#buf = buf[:,data_range['y'][0]:data_range['y'][1], data_range['x'][0]:data_range['x'][1]]
		if file_python_dtype != data_contents_memory_dtype:
			buf = buf.astype(data_contents_memory_dtype)

	if log_type in ['time','all']:
		u = dp.unique_id
		bytes = buf.nbytes
		t = MPI.Wtime()-st
		ms = 1000*t
		bw = bytes/GIGA/t
		name = dp.data_name


	return buf


# Work only for Z axis read

def load_data_from_local(file_name):
	data = numpy.array(Image.open(file_name))

	return data

def load_data_from_local_old(data_package, file_name, halo=None, loc=None):
	f = open(file_name, "rb")
	dp = data_package
	data_shape = dp.data_shape

	if len(data_shape) == 3:
		z = data_shape[0]
		y = data_shape[1]
		x = data_shape[2]

		bytes = get_bytes(dp.data_contents_memory_dtype)

		if halo != None:
			z = halo
	
			if loc == 'end':
				loc = 2
				f.seek(-x*y*z*bytes, loc)

			data = f.read(x*y*z*bytes)

		else:
			data = f.read()
			z = len(data) / (bytes * x* y)


		data = numpy.fromstring(data, dtype=Vivaldi_dtype_to_python_dtype(dp.data_contents_memory_dtype)).reshape(z, y, x)
		
		#print_bold(data.shape)

	return data


def make_range_list(full_range, split, halo=0):
	# make data range list
	range_list = []
	for axis in AXIS:
		if axis in full_range:
			temp = []
			w = full_range[axis][1] - full_range[axis][0]
			n = split[axis] if axis in split else 1
			full_start = full_range[axis][0]
			for m in range(n): 
				start = m*w/n+full_start-halo
				if start < full_range[axis][0]: start = full_range[axis][0]
				end = (m+1)*w/n+full_start+halo
				if end > full_range[axis][1]: end = full_range[axis][1]
				
				temp.append( {axis:(start, end)} )
				
			if len(range_list) == 0:
				for elem in temp: range_list.append(elem)
			else:
				temp2 = []
				for elem2 in temp:
					for elem1 in range_list:
						t = {}
						t.update(elem1)
						t.update(elem2)
						temp2.append(t)
				range_list = temp2

	return range_list

def make_depth(data_range,mmtx):
	x,y,z,depth = 0, 0, 0, 0
	for axis in data_range:
		if axis in ['x','y','z']:
			if axis == 'x':x = (data_range[axis][0] + data_range[axis][1])/2
			if axis == 'y':y = (data_range[axis][0] + data_range[axis][1])/2
			if axis == 'z':z = (data_range[axis][0] + data_range[axis][1])/2
		
	#X = mmtx[0][0]*x+mmtx[0][1]*y+mmtx[0][2]*z+mmtx[0][3]
	#Y = mmtx[1][0]*x+mmtx[1][1]*y+mmtx[1][2]*z+mmtx[1][3]
	Z = mmtx[2][0]*x+mmtx[2][1]*y+mmtx[2][2]*z+mmtx[2][3]
	depth = Z*Z
	return depth

def dtype_to_contents_memory_shape(dtype=None):
	data_shape = [1]
	if dtype == 'Rgba':data_shape = [4]
	if dtype == 'Rgb':data_shape = [3]
	if dtype == 'float4':data_shape = [4]
	if dtype == 'float3':data_shape = [3]
	if dtype == 'float2':data_shape = [2]
	return data_shape

def shape_to_int3(ttt):
	outDim = numpy.zeros((3), dtype=numpy.int32)
	if len(ttt) == 3:
		outDim[0] = numpy.int32(ttt[2])
		outDim[1] = numpy.int32(ttt[1])
		outDim[2] = numpy.int32(ttt[0])
		
	if len(ttt) == 2:
		outDim[0] = numpy.int32(ttt[1])
		outDim[1] = numpy.int32(ttt[0])

	if len(ttt) == 1:
		outDim[0] = numpy.int32(ttt[0])
		outDim[1] = numpy.int32(0)

	return outDim

def get_start_end(rg, halo=0):
	s = numpy.zeros((3), dtype=numpy.int32)
	e = numpy.zeros((3), dtype=numpy.int32)

	if type(rg) == 'str': rg = ast.literal_eval(rg)
	i = 0
	for axis in AXIS:
		if axis in rg:
			s[i] = rg[axis][0] + halo
			e[i] = rg[axis][1] - halo
		i += 1
	return s,e

def make_func_name_with_dtypes(name, func_args, dtype_dict):
	# compatiablily
	#########################
	dtypes = dtype_dict
	#############################

	new_name = str(name)

	for data_name in func_args:
		if data_name in dtype_dict:
#			new_name += data_name.replace('.','_') + dtypes[data_name].replace('.','_')
			new_name += dtype_dict[data_name].replace('.','_')
	return new_name

def data_range_minus_halo(data_range, halo):
	temp = {}
	for axis in AXIS:
		if axis in data_range:
			temp[axis] = (data_range[axis][0]+halo, data_range[axis][1]-halo)
			
	return temp

def apply_halo(data_range, halo, full_data_range=None):

	if full_data_range == None:
		temp = {}
		for axis in AXIS:
			if axis in data_range:
				temp[axis] = (data_range[axis][0]-halo, data_range[axis][1]+halo)
	else:
		temp = {}
		for axis in AXIS:
			if axis in data_range:

				start = data_range[axis][0]-halo
				end = data_range[axis][1]+halo

				start = full_data_range[axis][0] if start < full_data_range[axis][0] else start
				end = full_data_range[axis][1] if full_data_range[axis][1] < end else end

				temp[axis] = (start, end)
	

	return temp

def python_dtype_to_bytes(python_dtype):
	bcmb = -1
	bytes = bcmb
	if python_dtype in [numpy.int8, numpy.uint8]: bytes = 1
	if python_dtype in [numpy.int16, numpy.uint16]: bytes = 2
	if python_dtype in [numpy.int32, numpy.uint32, int]: bytes = 4
	if python_dtype in [numpy.float32]: bytes = 4
	if python_dtype in [numpy.float64, float]: bytes = 8

	return bytes

def Vivaldi_dtype_to_bytes(Vivaldi_dtype):
	bytes = -1
	try:
		if Vivaldi_dtype in ['RGB','RGBA']: bytes = 1
		if Vivaldi_dtype in ['char','char1','char2','char3','char4']: bytes = 1
		if Vivaldi_dtype in ['uchar','uchar1','uchar2','uchar3','uchar4']: bytes = 1
		if Vivaldi_dtype in ['short','short1','short2','short3','short4']: bytes = 2
		if Vivaldi_dtype in ['ushort','ushort1','ushort2','ushort3','ushort4']: bytes = 2
		if Vivaldi_dtype in ['int','int1','int2','int3','int4']: bytes = 4
		if Vivaldi_dtype in ['uint','uint1','uint2','uint3','uint4']: bytes = 4
		if Vivaldi_dtype in ['float','float1','float2','float3','float4']: bytes = 4
		if Vivaldi_dtype in ['double','double1','double2','double3','double4']: bytes = 8
	
		if bytes == -1:
			# not Vivaldi dtype
			pass
			
	except:
		pass
		
	return bytes

def get_bytes(type):
	
	bytes = Vivaldi_dtype_to_bytes(type)
	if bytes == -1:
		bytes = python_dtype_to_bytes(type)
	
	return bytes

def Vivaldi_dtype_to_python_dtype(Vivaldi_dtype):
	python_dtype = None
	if Vivaldi_dtype in ['char','char1','char2','char3','char4']: python_dtype = numpy.int8
	if Vivaldi_dtype in ['uchar','uchar1','uchar2','uchar3','uchar4']: python_dtype = numpy.uint8
	if Vivaldi_dtype in ['short','short1','short2','short3','short4']: python_dtype = numpy.int16
	if Vivaldi_dtype in ['ushort','ushort1','ushort2','ushort3','ushort4']: python_dtype = numpy.uint16
	if Vivaldi_dtype in ['int','int1','int2','int3','int4']  : python_dtype = numpy.int32
	if Vivaldi_dtype in ['uint','uint1','uint2','uint3','uint4']  : python_dtype = numpy.uint32
	if Vivaldi_dtype in ['float','float1','float2','float3','float4']: python_dtype = numpy.float32
	if Vivaldi_dtype in ['double','double1','double2','double3','double4']: python_dtype = numpy.float64
	if Vivaldi_dtype in ['RGB','RGBA']: python_dtype = numpy.uint8

	if type(Vivaldi_dtype) != str: python_dtype = Vivaldi_dtype
	return python_dtype

def python_dtype_to_Vivaldi_dtype(python_dtype):
	Vivaldi_dtype = ''
	if python_dtype == None and python_dtype != numpy.float64: return None
	if python_dtype in [numpy.int8]: Vivaldi_dtype += 'char'
	if python_dtype in [numpy.uint8]: Vivaldi_dtype += 'uchar'
	if python_dtype in [numpy.int16]: Vivaldi_dtype += 'short'
	if python_dtype in [numpy.uint16]: Vivaldi_dtype += 'ushort'
	if python_dtype in [numpy.int32,numpy.int64, int]: Vivaldi_dtype += 'int'
	if python_dtype in [numpy.uint32]: Vivaldi_dtype += 'uint'
	if python_dtype in [numpy.float32]: Vivaldi_dtype += 'float'
	if python_dtype in [numpy.float64, float]: Vivaldi_dtype += 'double'
	if type(python_dtype) == str: Vivaldi_dtype = python_dtype
	assert(Vivaldi_dtype!='')
	return Vivaldi_dtype

def make_type_name(dtype, shape, last):
	type_name = python_dtype_to_Vivaldi_dtype(dtype)
	
	if last in [2,3,4]:
		chan = [last]
		type_name += str(last)
		shape.pop()
	
	return type_name, shape

# Vivaldi reader
####################################################################################################################3
def get_data_start(data_range):
	data_start = None
	n = len(data_range)
	if n == 1:
		data_start = (data_range['x'][0])
	elif n == 2:
		data_start = (data_range['y'][0], data_range['x'][0])
	elif n == 3:
		data_start = (data_range['z'][0], data_range['y'][0], data_range['x'][0])
	elif n == 4:
		data_start = (data_range['w'][0], data_range['z'][0], data_range['y'][0], data_range['x'][0])
	if data_start == None:
		assert(False)
	return data_start

def get_data_end(data_range):
	data_end = None
	n = len(data_range)
	if n == 1:
		data_end = (data_range['x'][1])
	elif n == 2:
		data_end = (data_range['y'][1], data_range['x'][1])
	elif n == 3:
		data_end = (data_range['z'][1], data_range['y'][1], data_range['x'][1])
	elif n == 4:
		data_end = (data_range['w'][1], data_range['z'][1], data_range['y'][1], data_range['x'][1])
	if data_end == None:
		assert(False)
	return data_end

def get_empty_block(block_size, dim, ms, dtype):
	temp = []
	for elem in range(dim):
		temp.append(block_size)

	if ms != [1]:
		temp += ms

	block = numpy.empty(tuple(temp), dtype=dtype)
	return block

def copy_to_block(data, data_start, data_end, block, block_position, block_size, dim):
#	block_position and data_start is different
#	so we need something mathematics

	s = [0]*dim
	e = [0]*dim
	cmd1 = ''
	cmd2 = ''
	bytes = 0
	for i in range(dim):
		# decide copy range
		if data_start[i] <= block_position[i]:
			s[i] = block_position[i]
		elif block_position[i] < data_start[i]:
			s[i] = data_start[i]
		else:
			assert(False)

		if block_position[i]+block_size <= data_end[i]:
			e[i] = block_position[i]+block_size
		elif data_end[i] < block_position[i]+block_size:
			e[i] = data_end[i]
		else:
			assert(False)

		cmd1 += "%d:%d,"%(s[i]-block_position[i],e[i]-block_position[i])
		cmd2 += "%d:%d,"%(s[i]-data_start[i],e[i]-data_start[i])
		if bytes == 0:
			bytes = e[i]-s[i]
		else:
			bytes *= e[i]-s[i]

	cmd = 'block['+cmd1[:-1]+'] = data['+cmd2[:-1]+']'
	exec cmd
	return block, bytes

def copy_to_data(data, data_start, data_end, block, block_position, block_size, dim):
#	block_position and data_start is different
#	so we need something mathematics

	s = [0]*dim
	e = [0]*dim
	cmd1 = ''
	cmd2 = ''
	bytes = 0
	for i in range(dim):
		# decide copy range
		if data_start[i] <= block_position[i]:
			s[i] = block_position[i]
		elif block_position[i] < data_start[i]:
			s[i] = data_start[i]
		else:
			assert(False)

		if block_position[i]+block_size <= data_end[i]:
			e[i] = block_position[i]+block_size
		elif data_end[i] < block_position[i]+block_size:
			e[i] = data_end[i]
		else:
			assert(False)

		cmd1 += "%d:%d,"%(s[i]-block_position[i],e[i]-block_position[i])
		cmd2 += "%d:%d,"%(s[i]-data_start[i],e[i]-data_start[i])
		if bytes == 0:
			bytes = e[i]-s[i]
		else:
			bytes *= e[i]-s[i]

	cmd = 'data['+cmd2[:-1]+'] = block['+cmd1[:-1]+']'
	exec cmd

def get_block_maximum(block_size, full_data_start, full_data_end, block_position, dim):
	s = [0]*dim
	e = [0]*dim
	bytes = 0
	for i in range(dim):
		# decide copy range
		if full_data_start[i] <= block_position[i]:
			s[i] = block_position[i]
		elif block_position[i] < full_data_start[i]:
			s[i] = full_data_start[i]
		else:
			assert(False)

		if block_position[i]+block_size <= full_data_end[i]:
			e[i] = block_position[i]+block_size
		elif full_data_end[i] < block_position[i]+block_size:
			e[i] = full_data_end[i]
		else:
			assert(False)
		
		if bytes == 0:
			bytes = e[i]-s[i]
		else:
			bytes *= e[i]-s[i]

	return bytes

def next_block_position(block_position, block_size, adjusted_data_start, data_end):
	block_position = list(block_position)
	block_position[0] += 8
	i = 0
	n = len(block_position)
	while True:
		if block_position[i] >= data_end[i]:
			block_position[i] = adjusted_data_start[0]
			if i + 1 == n: return False
			block_position[i+1] += block_size
		else:
			break
		i += 1
	return tuple(block_position)

# etc
################################################################################################
def divide_args(args):
	### <Summary> :: divide arguments and return list of args
	### Type of args :: str
	### Return type :: list
	args_list = []
	t = args
	last = 0
	bcnt = 0
	i = 0
	temp = ''
	#remove blanket
	for s in args:
		if s in ['[','{','(']:bcnt = bcnt + 1
		if s in [']','}',')']:bcnt = bcnt - 1
		if s == ',' and bcnt == 0:
			temp = args[last:i]
			if temp.isdigit(): temp = int(args[last:i])
			args_list.append(temp)
			last = i + 1
		i = i + 1
	if last < i:
		temp = args[last:i]
		if temp.isdigit(): temp = int(args[last:i])
		args_list.append(temp)

	return args_list

def as_python(input):
	aa = ''
	if type(input) == dict:
		aa += '{'
		cnt = 0

		for key in input:
			if cnt > 0:
				aa += ','
			cnt += 1	
			aa += key+":"
			aa += as_python(input[key])
		aa += '}'
			
	elif type(input) in [list, tuple]:
		aa += '('
		cnt = 0
		for elem in input:
			if cnt > 0 :
				aa += ','
			cnt += 1
			aa += as_python(elem)
		aa += ')'
	else:
		aa += str(input)
	return aa

def split_file_name_and_extension(file_name):
	p = file_name.rfind('.')
	extension = file_name[p+1:]
	file_name = file_name[:p]
	return file_name, extension

def write_dat(file_name, data_shape, chan, dtype):
	e = os.system("mkdir -p result")
	block_size = 8
	
	f = open('./result/%s.dat'%(file_name),'w')
	f.write("ObjectFileName: %s.raw\n"%(file_name))
	sfw = ''
	for elem in data_shape:
		sfw += str(elem) + ' '
		
	f.write('Resolution: %s\n'%(sfw))
	f.write('chan: %s\n'%(str(chan)))
	f.write('Format: %s\n'%(dtype))
	f.close()

def print_bytes(bytes):
	ss = ''
	units = ['','K','M','G','T']
	unit = ''
	bytes = float(bytes)
	for alpha in units:
		unit = alpha
		if bytes > 1024:
			bytes /= 1024
		else:
			break

	return "%.2f%sBytes"%(bytes,unit)

def remove_comment(in_code, flag='#'):
	new_code = ""
	for line in in_code.splitlines():
		# remove comment
		n = len(line)
		i = 0
		qcnt=0
		dqcnt = 0
		while i < n:
			if line[i] == "'": qcnt = (qcnt+1)%2
			if line[i] == '"': dqcnt = (dqcnt+1)%2
			if qcnt == 1 or dqcnt == 1:
				i += 1
				continue
			if line[i] == flag:
				line = line[:i]
				break
			i += 1
		# remove empty line
		if len(line) == 0:continue
		# find every writing occur
		new_code += line + '\n'
		
	if len(new_code) == 0: return new_code
	return new_code[:-1]

def remove_enter(in_code):
	new_code = ""
	
	for line in in_code.splitlines():
		contents = line.strip()
		# remove empty line
		if len(contents) == 0:continue
		# find every writing occur
		if contents.lstrip().startswith('.'):
			new_code = new_code.rstrip() + contents.lstrip() + '\n'
		else:
			new_code += line + '\n'

	if len(new_code) == 0: return new_code				
	return new_code[:-1]
	
	
def	get_valid_range(full_data_range, split_shape, split_position):
	valid_range = {}
	split_shape = eval(str(split_shape))
	split_position = eval(str(split_position))
	for axis in full_data_range:
		s = full_data_range[axis][0]
		e = full_data_range[axis][1]
		w = e - s
		n = split_shape[axis]
		c = split_position[axis] - 1
		start = w*c/n + s
		end = w*(c+1)/n + s
		valid_range[axis] = (start, end)
		
	return valid_range


# FREYJA STREAMING
def get_hdfs_locations(hdfs_str, ratio_location, computing_unit_dict):
	hdfs_addr = hdfs_str[:hdfs_str.rfind('/')]
	hdfs_path = hdfs_str[hdfs_str.rfind('/')+1:]
	url = "%s/webhdfs/v1/user/%s/%s?op=GET_BLOCK_LOCATIONS"%(hdfs_addr, getpass.getuser(), hdfs_path)

	curl = pycurl.Curl()
	buf = StringIO()

	curl.setopt(pycurl.URL, url)
	curl.setopt(pycurl.WRITEFUNCTION, buf.write)

	curl.perform()

	data = buf.getvalue()


	# configuration
	replications = 3
	owner = "emerald"

	total_count = data.count(owner) / replications - 1
	
	#if total_count >= ratio_location* total_count

	head_buf = (1 + int(ratio_location*total_count)) * replications
	hdfs_location = []
	while data.find(owner)!=-1:
		start = data.find(owner)
		end = start + data[start:].find('"')
		hey = data[start:end]
		if len(hdfs_location) >= replications:
			break
	
		key = hey
	
		data = data[data.find(owner)+len(owner):]
	
		if head_buf <= 0:
			#logging[key] += 1
			hdfs_location.append(key)
		else:
			head_buf -= 1

	return hdfs_location


