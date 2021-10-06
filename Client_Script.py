#--------------------------------------Modules------------------------------------------------

import socket
import pickle
import bcrypt
import rsa,os
import pickle
from time import sleep
from tkinter import *
from tkinter import messagebox

#--------------------------------------Tkinter------------------------------------------------

public_l = rsa.key.PublicKey(72197395526160633030554118496234289569625855085660915915118801205090674214579, 65537)

publRem = rsa.key.PublicKey(76037163286527079097001769718316251637926036926725617216612747235251018583779, 65537)
privRem = rsa.key.PrivateKey(76037163286527079097001769718316251637926036926725617216612747235251018583779, 65537, 26487761689296324454652339940326228292130484211569005500103807739194971616673, 57488641403364535190096194188479472043961, 1322646725168164917637242845972521339)

root = Tk()
root.title("Remote-Laboratory")
root.geometry("430x400")
root.iconbitmap(r'Image.ico')

#--------------------------------------functions------------------------------------------------
def connect(frame):
	stat = frame.conn_S.cget('text')
	print(stat)
	global cli
	if stat == "Connect":
		cli.sendData("ConnectArduino")
		frame.conn_S.config(text = "DisConnect")
		frame.slider.config(state = NORMAL)
		frame.ang_S.config(state = NORMAL)
		frame.upd_S.config(state = NORMAL)
	else:
		cli.sendData("DisConnectArduino")
		frame.conn_S.config(text = "Connect")
		frame.slider.config(state = DISABLED)
		frame.ang_S.config(state = DISABLED)
		frame.upd_S.config(state = DISABLED)
	return

def writeServo(frame):
	val = frame.ang_S.get()
	frame.slider.set(int(val))
	cli.sendData("S" + val)
	return

def authLogin(frame,root):
	global cli
	user = frame.user_L.get().strip()
	pwd = frame.pwd_L.get().strip()

	msg = "Login"
	cli.sendData(msg)
	if(cli.recvData()) == "Ok":
		cli.sendData(user)
		if(cli.recvData()) == "Ok":
			cli.sendByte(rsa.encrypt(pwd.encode(),public_l))
			if(cli.recvData()) == "Ok":
				messagebox.showinfo(f"Succes", "Logged-In")
				if frame.check.get():
					pwd =rsa.encrypt(pwd.encode(),publRem)
					data = {"id" : user , "pwd" : pwd}
					with open('data','wb') as f:
						pickle.dump(data,f)
				window.bringExperiments(root)
				return 1
	messagebox.showwarning(f"Warning", "Credentials Not Matched")

def closeSer():
	global cli

	if(messagebox.askyesno(f"Warning", "Want to Exit?")):
		try:
			cli.sendData("DisConnectArduino")
			sleep(1)
			cli.sendData("Exit")
			sleep(1)
			cli.con.close()
			root.destroy()
			exit()
		except:
			exit()

def onlyDigit(dig):
	if re.search("[0-9]$",dig) and len(str(dig)) <= 6:
		return True
	elif dig == "":
		return True
	return False

def validFrame(frame):
	if not Student.validReg(frame.reg_S.get()):
		messagebox.showwarning(f"Warning", "Enter Valid Register number.")
	elif not Student.validEmail(frame.email_S.get()):
		messagebox.showwarning(f"Warning", "Enter Valid E-Mail Id.")
	elif (frame.pwd_S.get() != frame.cpwd_S.get()):
		messagebox.showwarning(f"Warning", "Password not Matched.")
	return True

def onlyDigitAng(dig):
	if re.search("[0-9]$",dig) and len(str(dig)) <= 3 and int(dig) <=180 and int(dig) >=0:
		return True
	elif dig == "":
		return True
	return False

def getOTP(frame):
	if validFrame(frame):
		global cli,otp
		
		name = frame.name_S.get().strip()
		email = frame.email_S.get().strip()

		cli.sendData("OTP")
		if cli.recvData() == "Ok":
			cli.sendData(name+"%"+email)
			otp = cli.recvData()
			frame.sign_S.config(state = NORMAL)
			messagebox.showinfo(f"Done", "OTP Sent Succesfully.")
		return False

def createAccount(frame):
	global cli,otp
	cli.sendData("Signup")
	salt = bcrypt.gensalt()
	reg = frame.reg_S.get().strip()
	pwd = bytes(frame.pwd_S.get().strip(),'utf-8')
	pwd = bcrypt.hashpw(pwd,salt)
	userotp = frame.otp_S.get()
	if userotp == frame.otp_S.get():
		cli.sendData(reg)
		cli.sendByte(pwd)
		if cli.recvData() == "Ok":
			messagebox.showinfo(f"Done", "Account Created Succesfully.")
			frame.bringLogin(root)
	else:
		messagebox.showerror(f"Error", "OTP Not Matched")


#--------------------------------------Student------------------------------------------------

class Student():

	def createStudent(self,name,reg,email,pwd):
		self.name = name
		self.reg = reg
		self.email = email
		self.pwd = pwd

	@staticmethod
	def validReg(reg):
		if re.search("\d{2}[a-zA-Z][\d]{3}$",reg):
			return True
		return False

	def validEmail(email):
		if re.search("[a-zA-z]{3,50}@student.tce.edu$",email):
			return True
		return False

	def validPwd(pwd):
		if len(pwd) > 5:
			return True
		return False

#--------------------------------------Socket------------------------------------------------

class Socket():

	def __init__(self,ip,port):
		self.ip = ip
		self.port = port

	def connectServer(self):
		self.con = socket.socket()
		self.con.connect((self.ip,self.port))
		self.sendData("Ok")
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

#--------------------------------------TkFrame------------------------------------------------


class TkFrame:
	
	def __init__(self,root):
		pass

	def Login(self,root):
		self.check = IntVar() 

		self.Login_f = Frame(root,width = 430,height=350,bg= "#0A2472")
		self.Login_f.place(x=0,y=0)

		Label(self.Login_f,text= "Remote Login",fg= "white",bg= "#0A2472",font = ("Engravers MT",14)).place(x=125,y=30,width=200,height=40)

		self.user_L = Entry(self.Login_f,width = 15,fg= "#0B0B0A",text= "User Id",background= "#CEEAF3")
		self.user_L.place(x=150,y=100,width=150,height=25)
		self.user_L.insert(END,"Username")

		self.pwd_L = Entry(self.Login_f,width = 15,fg = "#0B0B0A",show="*",background= "#CEEAF3")
		self.pwd_L.place(x=150,y=140,width=150,height=25)
		self.pwd_L.insert(END,"Password")
		
		try:
			with open('data', 'rb') as f:
				global privRem
				data = pickle.load(f)
				self.user_L.delete(0,END)
				self.pwd_L.delete(0,END)
				self.user_L.insert(END,data['id'])
				self.pwd_L.insert(END,rsa.decrypt(data['pwd'], privRem).decode())
		except Exception as e:
			pass

		self.rem = Checkbutton(self.Login_f,text= "Remember",onvalue = 1, offvalue=0,variable = self.check,fg= "cyan",bg= "#0A2472")
		self.rem.place(x=170,y=180)
		self.check.set(True)

		self.login_L = Button(self.Login_f, text ="LOGIN",fg="black",bg="#32A6C3",font = ("Georgia",16) ,command = lambda: authLogin(self,root))
		self.login_L.place(x=150,y=220,width=150,height=30)

		self.sign_L = Button(self.Login_f, text ="SIGN UP" ,fg="white",bg="#0A2472",font = ("Georgia",10),command =lambda: self.bringSignUp(root))
		self.sign_L.place(x=225,y=300,width=150,height=30)
		
		self.exit_L = Button(self.Login_f, text ="EXIT",fg="black",bg="#FAA34C",font = ("Georgia",8)  ,command = lambda: closeSer())
		self.exit_L.place(x=35,y=300,width=100,height=30)

		self.Login_f.place_forget()

	def signUp(self,root):
		
		root.geometry("430x400")
		self.signUp_f = Frame(root,width = 430,height=400,bg= "#0A2472")
		self.signUp_f.place(x=0,y=0)

		Label(self.signUp_f,text= "SIGN UP",fg= "white",bg= "#0A2472",font = ("Engravers MT",18)).place(x=150,y=15,width=130,height=40)
		
		self.namel_S = Label(self.signUp_f,text= "First Name",fg= "white",bg= "#0A2472",font = ("Fixedsys",4))
		self.namel_S.place(x=50,y=65,width=80,height=10)

		self.name_S = Entry(self.signUp_f,width = 15,background= "#EBEBEB",highlightthickness=2)
		self.name_S.place(x=50,y=80,width=150,height=25)
	
		self.regl_S = Label(self.signUp_f,text= "Reg No",fg= "white",bg= "#0A2472",font = ("Fixedsys",4))
		self.regl_S.place(x=222,y=62,width=65,height=15)

		self.reg_S = Entry(self.signUp_f,width = 15,background= "#EBEBEB",highlightthickness=2)
		self.reg_S.place(x=230,y=80,width=150,height=25)

		self.lemail_S = Label(self.signUp_f,text= "E-Mail",fg= "white",bg= "#0A2472",font = ("Fixedsys",4))
		self.lemail_S.place(x=50,y=110,width=50,height=15)

		self.email_S = Entry(self.signUp_f,width = 15,background= "#EBEBEB",highlightthickness=2)
		self.email_S.place(x=50,y=125,width=330,height=25)

		self.pwdl_S = Label(self.signUp_f,text= "Password",fg= "white",bg= "#0A2472",font = ("Fixedsys",4))
		self.pwdl_S.place(x=50,y=160,width=65,height=10)

		self.pwd_S = Entry(self.signUp_f,width = 15,background= "#EBEBEB",text= "Password",show= "*",highlightthickness=2)
		self.pwd_S.place(x=50,y=175,width=150,height=25)

		self.cpwdl_S = Label(self.signUp_f,text= "Confirm Password",fg= "white",bg= "#0A2472",font = ("Fixedsys",4))
		self.cpwdl_S.place(x=222,y=160,width=150,height=10)

		self.cpwd_S = Entry(self.signUp_f,width = 15,background= "#EBEBEB",text= "Confirm Password",show= "*",highlightthickness=2)
		self.cpwd_S.place(x=230,y=175,width=150,height=25)
		
		self.otpb_S = Button(self.signUp_f, text ="GET OTP" ,command = lambda: getOTP(self))
		self.otpb_S.place(x=175,y=225,width=80,height=20)	

		self.otp_S = Entry(self.signUp_f,width = 15,background= "#EBEBEB",text= "OTP")
		self.otp_S.place(x=175,y=255,width=80,height=20)		

		self.sign_S = Button(self.signUp_f, text ="CREATE ACCOUNT",fg="black",bg="#32A6C3",state = DISABLED,font = ("Georgia",8)  ,command = lambda: createAccount(self))
		self.sign_S.place(x=150,y=285,width=130,height=30)

		self.back_S = Button(self.signUp_f, text ="Back" ,fg="black",bg="cyan",font = ("Georgia",8),command =lambda: self.bringLogin(root))
		self.back_S.place(x=50,y=335,width=60,height=25)

		self.signUp_f.place_forget()

		digit = root.register(onlyDigit)
		reg = root.register(self.validReg)
		email = root.register(self.validEmail)
		pwd = root.register(self.validPwd)
		cpwd = root.register(self.validCpwd)
		name = root.register(self.validName)

		self.name_S.config(validate = "key",validatecommand = (name,'%P'))
		self.pwd_S.config(validate = "key",validatecommand = (pwd,'%P'))
		self.cpwd_S.config(validate = "key",validatecommand = (cpwd,'%P'))
		self.email_S.config(validate = "key",validatecommand = (email,'%P'))
		self.reg_S.config(validate = "key",validatecommand = (reg,'%P'))
		self.otp_S.config(validate = "key",validatecommand = (digit,'%P'))
	
	def experiments(self,root):

		root.geometry("430x350")
		self.exp_f = Frame(root,width = 430,height=350,bg= "#0A2472")
		self.exp_f.place(x=0,y=0)

		Label(self.exp_f,text= "experiments",fg= "white",bg= "#0A2472",font = ("Engravers MT",16)).place(x=120,y=30,width=200,height=40)
		
		self.user_e = Button(self.exp_f,fg="white",bg="#0A2472",font = ("Georgia",6))
		self.user_e.place(x=200,y=20)

		self.ser_b = Button(self.exp_f, text ="SERVO MOTOR CONTROL",fg="black",bg="#32A6C3",font = ("Georgia",8) ,command = lambda: self.bringServo(root))
		self.ser_b.place(x=140,y=100,width=170,height=30)

		self.step_b = Button(self.exp_f, text ="STEPPER MOTOR CONTROL",fg="black",bg="#32A6C3",state= DISABLED,font = ("Georgia",8) ,command = lambda: self.bringServo(root))
		self.step_b.place(x=140,y=150,width=170,height=30)

		self.step_b = Button(self.exp_f, text ="FEEDBACK   AMPLIFIERS",fg="black",bg="#32A6C3",state= DISABLED,font = ("Georgia",8) ,command = lambda: self.bringServo(root))
		self.step_b.place(x=140,y=200,width=160,height=30)

		self.exit_L = Button(self.exp_f, text ="EXIT",fg="black",bg="#FAA34C",font = ("Georgia",8)  ,command = lambda: closeSer())
		self.exit_L.place(x=35,y=300,width=100,height=30)

		self.logout_L = Button(self.exp_f, text ="LOGOUT",fg="black",bg="#FAA34C",font = ("Georgia",8) , command =lambda: self.bringLogin(root))
		self.logout_L.place(x=275,y=300,width=100,height=30)

		self.exp_f.place_forget()

	def servoMotor(self,root):
		self.var = IntVar()
		self.updcont = IntVar() 
		root.geometry("430x350")
		self.ser_f = Frame(root,width = 430,height=350,bg= "#0A2472")
		self.ser_f.place(x=0,y=0)

		Label(self.ser_f,text= "SERVO MOTOR",fg= "white",bg= "#0A2472",font = ("Engravers MT",16)).place(x=115,y=15,width=200,height=40)
		
		self.conn_S = Button(self.ser_f, text ="Connect" ,fg="black",bg="cyan",font = ("Georgia",12),command =lambda: connect(self))
		self.conn_S.place(x=175,y=90,width=80,height=25)

		self.slider = Scale(self.ser_f,state = DISABLED,from_ = 0, to = 180,highlightbackground = "#0A2472",bg= "#0A2472",fg="white",orient = HORIZONTAL)
		self.slider.place(x=120,y=140,width = 120)

		self.ang_S = Entry(self.ser_f,textvariable = self.var,state = DISABLED,width = 3,background= "#EBEBEB",text= "Angle")
		self.ang_S.place(x=260,y=160,width=30,height=20)		

		self.slider.bind("<B1-Motion>",lambda event: self.updateEntry())

		self.ang_S.bind("<Return>",lambda event: self.changeSlider())
		digite = root.register(onlyDigitAng)

		self.ang_S.config(validate = "key",validatecommand = (digite,'%P'))
		
		self.upd_C = Checkbutton(self.ser_f,text= "Update Continously",onvalue = 1, offvalue=0,variable = self.updcont,fg= "cyan",bg= "#0A2472")
		self.upd_C.place(x=150,y=190)
		self.updcont.set(0)

		self.upd_S = Button(self.ser_f,state = DISABLED, text ="Update" ,fg="black",bg="cyan",font = ("Georgia",12),command =lambda: writeServo(self))
		self.upd_S.place(x=175,y=220,width=80,height=25)

		self.back_S = Button(self.ser_f, text ="Back" ,fg="black",bg="#FAA34C",font = ("Georgia",8),command =lambda: self.bringExperiments(root))
		self.back_S.place(x=50,y=300,width=65,height=27)

		self.ser_f.place_forget()
	
	def updateEntry(self):
		self.ang_S.delete(0,END)
		self.ang_S.insert(END,self.slider.get())	
		print( self.updcont.get())
		if self.updcont.get():
			writeServo(self)
			sleep(0.05)
			
	def changeSlider(self):
		try:
			self.slider.set(int(self.ang_S.get()))
		except:
			pass

	def bringExperiments(self,root):
		self.ser_f.place_forget()
		root.geometry("430x350")
		self.exp_f.place(x=0,y=0)	

	def bringServo(self,root):
		self.exp_f.place_forget()
		root.geometry("430x350")
		self.ser_f.place(x=0,y=0)

	def bringLogin(self,root):
		self.signUp_f.place_forget()
		self.exp_f.place_forget()
		root.geometry("430x350")
		self.Login_f.place(x=0,y=0)	

	def bringSignUp(self,root):
		self.Login_f.place_forget()
		root.geometry("430x400")
		self.signUp_f.place(x=0,y=0)

	def validReg(self,val):
		if Student.validReg(val):
			self.reg_S.config(highlightbackground = "green", highlightcolor= "green")
			return True
		self.reg_S.config(highlightbackground = "red", highlightcolor= "red")
		return True	

	def validEmail(self,email):
		if Student.validEmail(email):
			self.email_S.config(highlightbackground = "green", highlightcolor= "green")
			return True
		self.email_S.config(highlightbackground = "red", highlightcolor= "red")
		return True

	def validPwd(self,pwd):
		cpwd = self.cpwd_S.get()
		if cpwd == pwd and (len(cpwd)>5 and len(pwd)>5):
			self.cpwd_S.config(highlightbackground = "green", highlightcolor= "green")
			self.pwd_S.config(highlightbackground = "green", highlightcolor= "green")
		else:
			self.cpwd_S.config(highlightbackground = "red", highlightcolor= "red")
			self.pwd_S.config(highlightbackground = "red", highlightcolor= "red")
		return True

	def validCpwd(self,cpwd):
		pwd =self.pwd_S.get()
		if cpwd == pwd and (len(cpwd)>5 and len(pwd)>5):
			self.cpwd_S.config(highlightbackground = "green", highlightcolor= "green")
			self.pwd_S.config(highlightbackground = "green", highlightcolor= "green")
		else:
			self.cpwd_S.config(highlightbackground = "red", highlightcolor= "red")
			self.pwd_S.config(highlightbackground = "red", highlightcolor= "red")
		return True

	def validName(self,name):
		if len(name) >= 3:
			self.name_S.config(highlightbackground = "green", highlightcolor= "green")
			return True
		self.name_S.config(highlightbackground = "red", highlightcolor= "red")
		return True

#--------------------------------------------------------------------------------------------

window = TkFrame(root)
window.Login(root)
window.signUp(root)
window.experiments(root)
window.servoMotor(root)
window.bringLogin(root)
root.protocol('WM_DELETE_WINDOW',closeSer)
otp =""
try:
	cli = Socket('192.168.43.179',5000)
	cli.connectServer()
except Exception as e:
	messagebox.showerror(f"Warning", e)

root.mainloop()

#--------------------------------------END------------------------------------------------