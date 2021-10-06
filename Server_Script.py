#--------------------------------------Modules------------------------------------------------
import socket
import bcrypt
import rsa, os
from time import sleep
from pyfirmata import Arduino,util,STRING_DATA
from SendMail import *
from random import randint
import threading,json

#--------------------------------------Encrypted Key------------------------------------------------

private = rsa.key.PrivateKey(72197395526160633030554118496234289569625855085660915915118801205090674214579, 65537, 70026086699359549555521355819333030910193842644411380649853020745670061704641, 63263233427758951304101718942519092713347, 1141222027618991512670775157258845457)

#--------------------------------------Socket------------------------------------------------

def loginAuth(ser):
	ser.sendData("Ok")
	reg = ser.recvData()
	ser.sendData("Ok")
	pwd =bytes(rsa.decrypt(ser.recvByte(), private).decode(),'utf-8')
	with open("cred.json", 'r') as f:
		data = json.load(f)
	if reg in data:
		if bcrypt.checkpw(pwd,bytes(data[reg]['pwd'],'utf-8')):
			ser.sendData("Ok")
			return
	ser.sendData("Not")

def sendOTP(ser):
	global Email,name,mail
	ser.sendData("Ok")
	msg = ser.recvData()
	name,mail = msg.split("%") 
	otp = randint(100000,999999)
	subj = f"Remote Login OTP [{otp}]"
	body = "Hi " + name + ",\n\n\tYour One Time Password for Remote Login Laboratory is " + str(otp) +"."
	Email.sendMail(mail,"Remote Laboratory",subj,body)
	ser.sendData(str(otp))
	
def signupAuth(ser):
	global name,mail
	reg = ser.recvData()
	pwd = ser.recvData()
	with open("cred.json", 'r') as f:
		data = json.load(f)
	ndata =  { 'name' : name,'id' : reg ,'pwd' : pwd ,'email':mail}
	data[reg] = ndata
	with open("cred.json", 'w') as f:
		json.dump(data, f, indent=2)
	ser.sendData("Ok")
	
class HardWare:

	def __init__(self,port):
		self.port = port;
		self.soc = socket.socket()
		self.name = socket.gethostname()
		self.ip = socket.gethostbyname(self.name)
		self.soc.bind(('',self.port))
		return

	def acceptHardware(self):
		self.soc.listen(1)
		self.client, self.addr = self.soc.accept()
		if self.recvData() == "Connected":
			pass
		else:
			print("Error in hardware Connection")
		return

	def sendData(self,msg):
		self.client.send(bytes(msg,'utf-8'))
		return
	
	def recvData(self):
		msg = self.client.recv(1024).decode()
		return msg	

	def closeHardWare(self):
		try:
			hardware.sendData("DisConnectArduino")
			self.client.close()
		except:
			pass
		try:
			self.soc.close()
		except:
			pass
	

class Socket:

	def __init__(self,port):
		self.port = port
		
	def startCon(self):
		self.soc = socket.socket()
		self.name = socket.gethostname()
		self.ip = socket.gethostbyname(self.name)
		self.soc.bind(('',self.port))
		
	def acceptClients(self):
		self.soc.listen(3)
		self.client, self.addr = self.soc.accept()
		self.recvData()
		while self.client:
			try:
				msg = self.client.recv(1024).decode()
				if msg == "ConnectArduino":
					hardware.sendData("ConnectArduino")
				elif msg == "DisConnectArduino":
					hardware.sendData("DisConnectArduino")
				elif msg == "Back":
					hardware.sendData("DisConnectArduino")
				elif msg == "Login":
					loginAuth(self)
				elif msg == "Signup":
					signupAuth(self)
				elif msg[0] == '$':
					hardware.sendData(msg)
				elif msg == "OTP":
					sendOTP(self)
				elif msg == "Exit":
					self.closeCon()
					break
				else:
					pass
			except Exception as e:
				pass

	def sendData(self,msg):
		self.client.send(bytes(msg,'utf-8'))
		return
	
	def recvData(self):
		msg = self.client.recv(1024).decode()
		return msg	

	def recvByte(self):
		msg = self.client.recv(1024)
		return msg

	def closeCon(self):
		try:
			ard.disconnect()
		except:
			pass
		try:
			self.client.close()
		except:
			pass
		try:
			self.soc.close()
		except:
			pass
		

def startCon():
	global ser
	try:
		ser.closeCon()
	except:
		pass

	ser = Socket(port)
	ser.startCon()
	thread = threading.Thread(target = ser.acceptClients )
	thread.start()

#--------------------------------------------------------------------------------------

hardware = HardWare(5050)
port= 5000

try:
	ser = Socket(port)
	startCon()
except:
	pass

Email = Mail(os.environ.get('REMOTE_MAIL') , os.environ.get('REMOTE_PASSWORD'))

#------------------------------------------END-------------------------------------------