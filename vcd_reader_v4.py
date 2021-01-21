from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import threading
import time
import numpy
import matplotlib.pyplot as plt

path = ""	# ex: "C:\Users\user\Downloads"
flag = 0	# the flag of is_auto_run
is_exit = 0 # determine "find x" is overtime 

def read_until(file,find):
	time_start = time.time()
	r = file.read(len(find))
	while r != find:
		r = r[1:] + file.read(1) 
		time_used = time.time() -time_start
		if time_used>0.3:
			break
	return 0

def read_word(file,find):
	global is_exit
	time_start = time.time()
	r = ""
	word = ""
	for i in range(len(find)):
		while r!=find[i]:
			r = file.read(1)
			if r == "" :
				is_exit = 1
				break
			word  = word + r
			time_used = time.time() - time_start
			if time_used>0.3:
				break
	word = word[:-1]
	return word

def RecursiveGcd(x,y):
  if y == 0:
    return x
  else:
    return RecursiveGcd(y, x%y)


def data_reader():
	global signal,is_exit
	symbol = []
	signal = []
	timing = []
	file = open(path)
	read_until(file,"$timescale")
	# symbol & signal
	while not is_exit:
		read_until(file,"reg 1 ")
		word = read_word(file," ")
		if is_exit:
			break		
		# print("symbol",len(symbol),"= ",word,end="")
		symbol.append(word)
		word = read_word(file," ")
		# print("\tsignal",len(signal),"= ",word)	
		signal.append(word)
	is_exit = 0			# refresh
	file.close()		# refresh
	file = open(path)	# refresh 
	# timing 
	while not is_exit:
		read_until(file,"\n#")
		word = read_word(file,"\n")	
		if is_exit:
			break					
		timing.append(int(word))	
	# print("timing",timing)
	is_exit = 0			# refresh
	file.close()		# refresh
	file = open(path)	# refresh
	# determine arr shape(size) 
	a = timing[1]
	for i in range(2,len(timing)):
		a = RecursiveGcd(a,timing[i])
	# print(a)	# a <= the Greatest COmmon Factor of all timing
	x = len(symbol)
	y = int(timing[-1]/a+1)
	arr = numpy.zeros((x, y))
	# set arr
	read_until(file,"$dumpvars\n")
	word = file.read(1)
	word2 = file.read(1)
	for i in range(len(symbol)):
		if word2 == symbol[i]:
			arr[i][0] = word
	file.read(1)	
	read_until(file,("#"+str(timing[1])+"\n"))
	for k in range(1,len(timing)-1):
		for j in range(len(symbol)):
			word = file.read(1)
			if word == "#":
				break
			word2 = file.read(1)
			for i in range(len(symbol)):				
				if word2 == symbol[i]:
					arr[i][k] = word
			file.read(1)
		read_until(file,"\n")
		if k<len(timing)-1:
			for j in range(arr.shape[0]):
				arr[j][k+1] = arr[j][k]
	# print(arr)
	return arr

def plot(arr):
  fig,axes=plt.subplots(arr.shape[0]) 
  fig.canvas.set_window_title(path[path.rfind("/")+1:]+" : plot")  
  for j in range(arr.shape[0]):
    axes[j].plot(label="x")
    for i in range(arr.shape[1]-1):
      axes[j].plot([i,i+1],[int(arr[j][i]),int(arr[j][i])], color='r')
      axes[j].plot([i+1,i+1],[int(arr[j][i]),int(arr[j][i+1])], color='r')
    axes[j].plot([arr.shape[1],arr.shape[1]],[0,0],label=signal[j],color='r')
    axes[j].legend(loc="upper right")
    if j != arr.shape[0]-1:
    	plt.setp(axes[j].get_xticklabels(), visible=False) 
  plt.show()

def change(self):
	s = scale.get()
	# print(s)
	for i in range(arr.shape[0]):
		label[i].config(image = img[bool(arr[i][s])])	
	return 0	

def forward():
	global arr
	txt = button[0].cget("text")	
	if scale.get() == (arr.shape[1]-1):
		scale.set(0)
	else:
		scale.set(scale.get()+1)
	return 0	

def backward():
	txt = button[1].cget("text")
	if scale.get() == 0:
		scale.set(arr.shape[1]-1)
	else:
		scale.set(scale.get()-1)
	return 0

def run():
	global flag
	txt = button[2].cget("text")
	if txt == " ▶|| ":
		button[2].config(text="  ||  ")
		flag = 1;
	else:
		button[2].config(text=" ▶|| ")	
		flag = 0;
	while flag:
		if scale.get() == (arr.shape[1]-1):
			scale.set(0)
		else:
			scale.set(scale.get()+1)
		time.sleep(0.5)	
		# print("runing")
	return 0

def select_path():
	# load "path"
	global arr,path,label
	file_path = filedialog.askopenfilename()
	is_vcd = file_path[len(file_path)-4:]==".vcd"
	if file_path != "" and is_vcd:
		text_path.delete(1.0,"end")
		text_path.insert(1.0,file_path)
		path = file_path
		arr = data_reader()
		# print(arr)
		# refresh layout
		tk.geometry(str(arr.shape[0]*100)+"x220")
		label=[]
		label_signal=[]
		for i in range(arr.shape[0]):
			label.append(Label(image=img[0]))
			label[i].place(x=i*100,y=40)
			label_signal.append(Label(text=signal[i]))
			label_signal[i].place(x=i*100+40,y=145)
		scale.config(to=(arr.shape[1]-1))
		for i in range(4):
			button[i].config(state="active")				
	else:
		messagebox.showinfo("Invalid File","File can only be .vcd")
	return 0

class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()
        
        self.func = func
        self.args = args
        
        self.setDaemon(True)
        self.start()
        
    def run(self):
        self.func(*self.args)

def layout():
	# tkinter initial
	global tk,img,button,scale,text_path
	tk = Tk()
	tk.title(".vcd Simulation")
	tk.geometry("500x220")
	tk.resizable(0,0) #不可以更改大⼩
	# img on/off import
	img=[]
	img.append(PhotoImage(file='off.png'))
	img.append(PhotoImage(file='on.png'))
	scale = Scale(resolution=1,to=((0)),orient=HORIZONTAL,length=300,command=change)
	scale.place(x=20,y=160)
	button=[0,0,0,0]
	button[0]=Button(text=" ◀ ",command=backward,state="disable")
	button[0].place(x=340,y=175)
	button[1]=Button(text=" ▶ ",command=forward,state="disable")
	button[1].place(x=370,y=175)
	button[2]=Button(text=" ▶|| ",command=lambda :MyThread(run),state="disable")
	button[2].place(x=410,y=175)
	button[3]=Button(text="plot",command=lambda :plot(arr),state="disable")
	button[3].place(x=450,y=175)
	text_path=Text(width=50, height=1)
	text_path.insert(1.0, path)
	text_path.place(x=0,y=5)
	text_path.configure(font=("Courier", 11, "italic"))
	button_open=Button(text="open",command=select_path)
	button_open.place(x=455,y=4)
	# tkinter run
	tk.mainloop()


if __name__ == '__main__':
	layout()








