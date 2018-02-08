import socket
import re
import pyautogui

i = 0
n = 0
line = 1

data_list = []

mag_data = []
mag_calib_y = 0
mag_offset_y = 0

z_calib = 0
z_offset = 0
z_moving_offset = 0
z_diff = 0
z_real = 0
z_velo = 0
z_pos = 0

keep_offset = False
first_data = True

f = open("Accel Data.txt", "a")

def startServer():
	global i
	global first_data
	# initialize server socket
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	# Server IP address and port
	host = "149.160.251.3"
	port = 12347
	server_address = (host, port)
	
	# Open the server and listen for incoming connections
	print ('Starting server on %s port %s' % server_address)
	serversocket.bind(server_address)
	serversocket.listen(5)
	
	# Wait for connections...
	while True:
		print ('Waiting for connection...')
		
		# Accept an incoming connection
		(clientsocket, address) = serversocket.accept()
		
		# Try to parse data received
		try:
			print ('Connection established from ', address)
			
			while True:
				# Receive the data and send it for processing
				data = clientsocket.recv(25)
				accel_data = re.split('[:]', str(data))	
				accel_data[0] = accel_data[0][2:]
				accel_data[1] = accel_data[1]
				accel_data[2] = accel_data[2][1:-1]
				print(accel_data)
				i+=1
				if(i < 51):
					calibData(accel_data)
				else:
					movingAccel(accel_data[0])
					processData(accel_data)
					first_data = False
		finally:
			# Close the socket to prevent unnecessary data leak
			clientsocket.close()
			
def calibData(list):
	global z_calib
	global z_offset
	global mag_data
	global mag_calib_y
	global mag_offset_y
	
	z_calib += float(list[0])
	mag_calib_y += float(list[1])
	
	if(i==50):
		z_offset = z_calib / 50
		mag_offset_y = mag_calib_y / 50
		z_calib = 0
		mag_calib_y = 0
		mag_data.append(mag_offset_y)

def movingAccel(num):
	global z_calib
	global z_diff
	global z_moving_offset
	global z_offset
	global data_list
	global n
	global keep_offset
	
	if(n < 10):
		n += 1
		z_calib += float(num)
		data_list.append(float(num))
	else:
		z_moving_offset = z_calib / 10
		for entry in data_list:
			z_diff = float(entry) - z_moving_offset
			if(z_diff > 0.2 or z_diff < -0.2): # motion detected within data, restart
				keep_offset = True
				n = 0
				z_calib = 0
				z_moving_offset = 0
				z_diff = 0
				data_list = []
				break
		if not keep_offset: # stationary in data, set new z_offset
			z_offset = z_moving_offset
			print("New z_offset: ")
			print(z_offset)
			n = 0
			z_calib = 0
			z_moving_offset = 0
			z_diff = 0
			data_list = []
			keep_offset = False
		keep_offset = False
			
def processData(list): #[accel.z, mag.y]
	global z_offset
	global z_real
	global z_velo
	global z_pos
	global first_data
	global mag_data

	z_real = float(list[0]) - z_offset
	mag_y = list[1]
	mag_z = list[2]
	left = False
	right = False
	
	# Don't process acceleration until absolutely sure it has accelerated
	# Prevents mechanical noise from contributing to position
	if(z_real < 0.20 and z_real > -0.20):
		z_real = 0
	
	#Begin integrations to find position
	if(first_data):
		mag_data.append(mag_y)
		z_pos = (0.5 * z_real * 0.25 * 0.25) + (z_velo * 0.25) + z_pos
		z_velo = z_real * 0.25
		pyautogui.moveTo(1500,1000)
	else:
		z_pos = (0.5 * z_real * 0.25 * 0.25) + (z_velo * 0.25) + z_pos
		z_velo = (z_real * 0.25) + z_velo
		
		del mag_data[0]
		mag_data.append(mag_y)
		if(float(mag_data[1]) - float(mag_data[0]) > 0.03):
			right = True
		elif(float(mag_data[1]) - float(mag_data[0]) < -0.03):
			left = True
		
		if(right):
			movement(50, int(z_pos*1000))
		elif(left):
			movement(-50, int(z_pos*1000))
		z_velo = 0
		z_pos = 0

def movement(x, y):
	print("moving to", x, -y)
	pyautogui.dragRel(x,-y)

def writeData(accel, vel, pos):
	global f
	global line
	f.write(str(line*0.25))
	f.write("	")
	f.write(str(accel))
	f.write("	")
	f.write(str(vel))
	f.write("	")
	f.write(str(pos))
	f.write("\n")
	line += 1
	
# Calls the function to begin the server
startServer()