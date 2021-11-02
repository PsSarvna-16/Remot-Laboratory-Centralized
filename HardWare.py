import socket
from tkinter import *
from tkinter import messagebox
from SendMail import *
from pyfirmata import Arduino,util,STRING_DATA

def sendOTP(msg):
	try:
		gmail = Mail(os.environ.get("REMOTE_MAIL"),os.environ.get("REMOTE_PASSWORD"))
		gmail.sendMail(msg[0],msg[1],msg[2],msg[3])
		return True
	except:
		return False

class Ardino:`

	def __init__(self):
		pass

	def connectArd(self):
		try:
			self.board = Arduino('COM3')
			self.lcd(" ")
			self.ser = self.board.get_pin('d:6:s')
			return True
		except:
			return False
                    
	def lcd(self,text):
		try:
		    if text:
		        self.board.send_sysex( STRING_DATA, util.str_to_two_byte_iter( text ))
		    return
		except:
			return

	def servo(self,val):
		try:
			self.ser.write(int(val))
			self.lcd(str(val))
			return
		except:
			return

	def disConnectArd(self):
		try:
			self.ser.write(0)
			self.lcd('0')
			self.lcd("S")
			sleep(2)
			self.board.exit()
			return True
		except:
			return False

class Socket():

	def __init__(self,ip,port):
		self.ip = ip
		self.port = port

	def connectServer(self):
		self.con = socket.socket()
		self.con.connect((self.ip,self.port))
		self.sendData("Connected")
		return

	def sendData(self,msg):
		print("sent : " + msg)
		self.con.send(bytes(msg,'utf-8'))
		return
	
	def sendByte(self,msg):
		print("sent : " + str(msg))
		self.con.send(msg)
		return
	
	def recvData(self):
		msg = self.con.recv(1024).decode()
		print("rec  : "+ msg)
		return msg

try:
	hard = Socket('45.79.126.16',5050)
	hard.connectServer()
except Exception as e:
	messagebox.showerror(f"Warning", e)

ard = Ardino()

while True:
	msg = hard.recvData()
	print(msg)
	if msg[0] == "%":
		msg = msg.split("%")[1:]
		if sendOTP(msg):
			hard.sendData("OTP-Sent")
		else:
			hard.sendData("OTP-NotSent")
	elif msg == "ConnectArduino":
		if ard.connectArd():
			hard.sendData("Arduino-Connected")
		else:
			hard.sendData("Arduino-NotConnected")
	elif msg == "DisConnectArduino":
		if ard.disConnectArd():
			hard.sendData("Arduino-DisConnected")
		else:
			hard.sendData("Arduino-NotDisConnected")
	elif msg[0] == '$':
		ard.servo(int(msg.split("$")[1]))
	elif msg == "Exit":
		hard.closeCon()
		break
