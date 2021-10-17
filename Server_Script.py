#--------------------------------------Modules------------------------------------------------
import socket
import bcrypt
import rsa, os
from time import sleep
from pyfirmata import Arduino,util,STRING_DATA
from random import randint
import threading,json

#--------------------------------------Encrypted Key------------------------------------------------

private = rsa.key.PrivateKey(72197395526160633030554118496234289569625855085660915915118801205090674214579, 65537, 70026086699359549555521355819333030910193842644411380649853020745670061704641, 63263233427758951304101718942519092713347, 1141222027618991512670775157258845457)

#--------------------------------------Socket------------------------------------------------

def loginAuth(ser):
	ser.sendData(ser.ccon,"Ok")
	reg = ser.recvData(ser.ccon)
	ser.sendData(ser.ccon,"Ok")
	pwd =bytes(rsa.decrypt(ser.recvByte(ser.ccon), private).decode(),'utf-8')
	with open("cred.json", 'r') as f:
		data = json.load(f)
	if reg in data:
		if bcrypt.checkpw(pwd,bytes(data[reg]['pwd'],'utf-8')):
			ser.sendData(ser.ccon,"Ok")
			return
	ser.sendData(ser.ccon,"Not")

def sendOTP(ser):
	global name,mail
	ser.sendData(ser.ccon,"Ok")
	msg = ser.recvData(ser.ccon)
	name,mail = msg.split("%") 
	otp = randint(100000,999999)
	print(otp)
	subj = f"Remote Login OTP [{otp}]"
	body = "Hi " + name + ",\n\n\tYour One Time Password for Remote Login Laboratory is " + str(otp) +"."
	ser.sendData(ser.hcon,"%" + mail+ "%" +"Remote Laboratory"+ "%" +subj+ "%" +body)
	if ser.recvData(ser.hcon) == "OTP-Sent":
		ser.sendData(ser.ccon, str(otp))
	else:
		ser.sendData(ser.ccon, "Not-Sent")
	return

def signupAuth(ser):
	global name,mail
	reg = ser.recvData(ser.ccon)
	pwd = ser.recvData(ser.ccon)
	with open("cred.json", 'r') as f:
		data = json.load(f)
	ndata =  { 'name' : name,'id' : reg ,'pwd' : pwd ,'email':mail}
	data[reg] = ndata
	with open("cred.json", 'w') as f:
		json.dump(data, f, indent=2)
	ser.sendData(ser.ccon,"Ok")

class SerSocket:

	def __init__(self,hport,cport):
		self.hport = hport
		self.cport = cport
		
	def startCon(self):
		self.hsoc = socket.socket()
		self.hname = socket.gethostname()
		self.hip = socket.gethostbyname(self.hname)
		self.hsoc.bind(('',self.hport))
		self.hsoc.listen(1)

		print("Hardware Socket Created")
		print("Waiting for Hardware Connection")
		self.hcon, self.haddr = self.hsoc.accept()
		msg = self.recvData(self.hcon)
		if msg == "Connected":
			print(msg)
			print("Connected to HardWare")
		else:
			print(msg)
			print("Hardware Connection Failed")
			print("reconnecting Hardware")
			try:
				self.hcon.close()
			except:
				pass
			self.hsoc.close()
			self.startCon()

		self.csoc = socket.socket()
		self.cname = socket.gethostname()
		self.cip = socket.gethostbyname(self.cname)
		self.csoc.bind(('',self.cport))
		print("Client Socket Created")
		return
		
	def acceptClients(self):
		self.csoc.listen(3)
		print("Waiting for Client Connection")
		self.ccon, self.addr = self.csoc.accept()
		self.recvData(self.ccon)
		while self.ccon:
			try:
				msg = self.recvData(self.ccon)

				if msg == "ConnectArduino":
					self.sendData(self.hcon, "ConnectArduino")
					if self.recvData(self.hcon) == "Arduino-Connected":
						print("Arduino-Connected")
					else:
						print("Arduino-Connection Failed")

				elif msg == "DisConnectArduino" or msg == "Back":
					self.sendData(self.hcon,"DisConnectArduino")
					if self.recvData(self.hcon) == "Arduino-DisConnected":
						print("Arduino-DisConnected")
					else:
						print("Arduino-DisConnection Failed")
						
				elif msg == "Login":
					loginAuth(self)

				elif msg == "Signup":
					signupAuth(self)

				elif msg[0] == '$':
					self.sendData(self.hcon,msg)

				elif msg == "OTP":
					sendOTP(self)

				elif msg == "Exit":
					self.sendData(self.hcon, "Exit")
					self.closeCon()
					break
				else:
					pass
			except Exception as e:
				print(e)

	def sendData(self,con,msg):
		con.sendall(bytes(msg,'utf-8'))
		print("sent : " + msg)
		return
	
	def recvData(self,con):
		msg = con.recv(1024).decode()
		print("rec : " + msg)
		return msg

	def recvByte(self,con):
		msg = con.recv(1024)
		return msg

	def closeCon(self):
		self.hcon.close()
		self.ccon.close()
		self.hsoc.close()
		self.csoc.close()
		print("Socket closed")

#--------------------------------------------------------------------------------------

ser = SerSocket(5050,5100)
ser.startCon()
thread = threading.Thread(target = ser.acceptClients )
thread.start()

#------------------------------------------END-------------------------------------------

