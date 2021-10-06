#--------------------------------------Modules------------------------------------------------
import socket
import bcrypt
import rsa, os
from time import sleep
from pyfirmata import Arduino,util,STRING_DATA
from SendMail import *
from tkinter import *
from random import randint
import threading,json

#--------------------------------------Tkinter------------------------------------------------

private = rsa.key.PrivateKey(72197395526160633030554118496234289569625855085660915915118801205090674214579, 65537, 70026086699359549555521355819333030910193842644411380649853020745670061704641, 63263233427758951304101718942519092713347, 1141222027618991512670775157258845457)

root = Tk()
root.title("Remote-Lab-Server")
root.iconbitmap(r'Image.ico')

#--------------------------------------Socket------------------------------------------------


def loginAuth(ser):
	ser.sendData("Ok")
	reg = ser.recvData()
	ser.sendData("Ok")
	pwd =bytes(rsa.decrypt(ser.recvByte(), private).decode(),'utf-8')
	Interface.send(f"Username : " + reg)
	Interface.send(f"Password : " + len(pwd)*"*")
	with open("cred.json", 'r') as f:
		data = json.load(f)
	if reg in data:
		if bcrypt.checkpw(pwd,bytes(data[reg]['pwd'],'utf-8')):
			Interface.send(f"**** Login Sucessfull ****")
			Interface.send(f"-------------------------------")
			ser.sendData("Ok")
			return
	Interface.send(f"**** Login Failed ****")
	Interface.send(f"-------------------------------")
	ser.sendData("Not")

def sendOTP(ser):
	global Email,name,mail
	ser.sendData("Ok")
	msg = ser.recvData()
	name,mail = msg.split("%") 
	Interface.send(f"name : " + name)
	Interface.send(f"mail : " + mail)
	otp = randint(100000,999999)
	subj = f"Remote Login OTP [{otp}]"
	body = "Hi " + name + ",\n\n\tYour One Time Password for Remote Login Laboratory is " + str(otp) +"."
	Email.sendMail(mail,"Remote Laboratory",subj,body)
	ser.sendData(str(otp))
	Interface.send(f"OTP sent Succesfully")
	Interface.send(f"\n*******************")
	
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
	Interface.send(f"\nUser Account Created : {reg}")
	Interface.send(f"\n****Authentication Sucessfull****")
	Interface.send(f"-------------------------------")
	
class Ardino:

	def __init__(self):
		pass

	def connectArd(self):
		try:
			self.board.exit()
		except:
			pass
		self.board = Arduino('COM4')
		self.lcd(" ")
		self.ser = self.board.get_pin('d:6:s')
		return

	def lcd(self,text):
	    if text:
	        self.board.send_sysex( STRING_DATA, util.str_to_two_byte_iter( text ))
	    return

	def servo(self,val):
		self.ser.write(int(val))
		self.lcd(str(val))
		return

	def disconnectArd(self):
		try:
			self.ser.write(0)
			self.lcd('0')
			self.lcd("S")
			sleep(2)
			self.board.exit()
			return
		except:
			pass

class Socket:

	def __init__(self,port):
		self.port = port
		
	def startCon(self):
		self.soc = socket.socket()
		Interface.send("Socket Created..")
		print("Socket Created..")
		self.name = socket.gethostname()
		self.ip = socket.gethostbyname(self.name)
		self.soc.bind(('',self.port))
		Interface.send(f"\nName : {self.name} \nIP   : {self.ip}\nPort : {self.port}")
		print(f"\nName : {self.name} \nIP   : {self.ip}\nPort : {self.port}")
	
	def acceptClients(self):
		self.soc.listen(3)
		Interface.send("\nWaiting For Clients..")
		print("\nWaiting For Clients..")
		self.client, self.addr = self.soc.accept()
		Interface.send(f"\nConnected with {self.addr}")
		print(f"\nConnected with {self.addr}")
		self.recvData()
		while self.client:
			try:
				msg = self.client.recv(1024).decode()
				if msg == "ConnectArduino":
					Interface.send(f"\n******Servo  Connected******")
					ard.connectArd()
				elif msg == "DisConnectArduino":
					Interface.send(f"\n*****Servo DisConnected*****")
					ard.disconnectArd()
				elif msg == "Back":
					ard.disconnectArd()
				elif msg == "Login":
					Interface.send(f"\n---------Login-----------")
					loginAuth(self)
				elif msg == "Signup":
					signupAuth(self)
				elif msg[0] == 'S':
					Interface.send(f"\nPosition : " + msg[1:])
					ard.servo(int(msg[1:]))
				elif msg == "OTP":
					Interface.send(f"\n----------Send OTP-------------")
					sendOTP(self)
				elif msg == "Exit":
					Interface.send(f"\n----------EXIT-------------")
					self.closeCon()
					break
				else:
					Interface.send(msg)
			except Exception as e:
				print(e)

	def sendData(self,msg):
		print("sent : " + msg)
		self.client.send(bytes(msg,'utf-8'))
		return
	
	def recvData(self):
		msg = self.client.recv(1024).decode()
		print("rec  : "+ msg)
		return msg	

	def recvByte(self):
		msg = self.client.recv(1024)
		print("rec  : "+ str(msg))
		return msg

	def closeCon(self):
		try:
			ard.disconnect()
			Interface.send("\nArduino Closed !!")
		except:
			pass
		try:
			self.client.close()
		except:
			pass
		try:
			self.soc.close()
			Interface.send("\nSocket Closed !!")
		except:
			pass
		
#-------------------------------------TkFrame----------------------------------------------------

class TkFrame:
	
	def __init__(self,root):
		Main = Frame(root)

		global ser
		self.start_b = Button(Main,text= "Start", command = lambda: startCon())
		self.start_b.grid(row=0,column=0)
		self.terminate_b = Button(Main,text = "Terminate",command = lambda:  ser.closeCon())
		self.terminate_b.grid(row=0,column=1)
		self.text = Text(Main ,width = 40,height = 25,state = DISABLED,background= "#88F7FB",xscrollcommand = True)
		self.text.grid(row=1,columnspan=2)

		Main.grid()

	def send(self,msg):
		self.text.config(state = NORMAL)
		self.text.insert(END ,msg + "\n")
		self.text.config(state = DISABLED)

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

Interface = TkFrame(root)
ard = Ardino()
port= 5000

try:
	ser = Socket(port)
	startCon()
except:
	pass

Email = Mail( os.environ.get('REMOTE_MAIL') , os.environ.get('REMOTE_PASSWORD'))

root.mainloop()
#------------------------------------------END-------------------------------------------