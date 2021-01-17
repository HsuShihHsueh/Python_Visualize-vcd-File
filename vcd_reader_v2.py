from tkinter import *
from tkinter import filedialog
import threading
import time
import numpy
import matplotlib.pyplot as plt
path = "C:/Users/user/Downloads/vmf_reader/LAB1.sim.vcd"
in_out = 5
flag=0

def read_until(file,find):
	time_start = time.time()
	r = file.read(len(find))
	while r != find:
		r = r[1:] + file.read(1) 
		time_used = time.time() -time_start
		if time_used>1.0:
			exit()

def read_word(file,find):
	time_start = time.time()
	r = ""
	word = ""
	for i in range(len(find)):
		while r!=find[i]:
			r = file.read(1)
			word  = word + r
			time_used = time.time() - time_start
			if time_used>1.0:
				exit()
	word = word[:len(word)-1]
	return word

def RecursiveGcd(x,y):
    if y == 0:
        return x
    else:
        return RecursiveGcd(y, x%y)

def data_reader():
	symbol = []
	signal = []
	timing = []
	file = open(path)
	read_until(file,"$timescale")
	# symbol & signal
	for i in range(5):
		read_until(file,"reg 1 ")
		word = read_word(file," ")
		# print("symbol",i,"= ",word,end="")
		symbol.append(word)
		word = read_word(file," ")
		# print("\tsignal",i,"= ",word)
		signal.append(word)
	# timing 
	for i in range(10):
		read_until(file,"\n#")
		word = read_word(file,"\n")
		timing.append(int(word))
	# print(timing)
	file.close()
	# determine arr shape(size) 
	a = timing[1]
	for i in range(2,len(timing)):
		a = RecursiveGcd(a,timing[i])
	# print(a)
	x = len(symbol)
	y = int(timing[-1]/a+1)
	arr = numpy.zeros((x, y))

	file = open(path)
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
	# arr = arr[:,:-1]
	print(arr)
	return arr

def plot(arr):
  fig,axes=plt.subplots(arr.shape[0])
  for j in range(arr.shape[0]):
    for i in range(arr.shape[1]-1):
      axes[j].plot([i,i+1],[int(arr[j][i]),int(arr[j][i])], color='r')
      axes[j].plot([i+1,i+1],[int(arr[j][i]),int(arr[j][i+1])], color='r')
  plt.show()

def change(self):
	s = scale.get()
	# print(s)
	for i in range(arr.shape[0]):
		label[i].config(image = img[bool(arr[i][s])])	
	return 0	

def forward():
	global arr
	txt = button_1.cget("text")	
	if scale.get() == (arr.shape[1]-1):
		scale.set(0)
	else:
		scale.set(scale.get()+1)
	return 0	

def backward():
	txt = button_2.cget("text")
	if scale.get() == 0:
		scale.set(arr.shape[1]-1)
	else:
		scale.set(scale.get()-1)
	return 0

def run():
	global flag
	txt = button_3.cget("text")
	if txt == " ▶|| ":
		button_3.config(text="  ||  ")
		flag = 1;
	else:
		button_3.config(text=" ▶|| ")	
		flag = 0;
	while flag:
		if scale.get() == (arr.shape[1]-1):
			scale.set(0)
		else:
			scale.set(scale.get()+1)
		time.sleep(0.5)	
		print("runing")
	return 0

def select_path():
	global arr
	file_path = filedialog.askopenfilename()
	# print("path = \"",file_path,"\"")
	if file_path != "":
		text_path.delete(1.0,"end")
		text_path.insert(1.0,file_path)
	arr = data_reader()
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



# import arr from .vcd
arr = data_reader()
# tkinter initial
tk = Tk()
tk.title(".vmf Simulation")
tk.geometry(str(arr.shape[0]*100)+"x200")
tk.resizable(0,0) #不可以更改大⼩
# img on/off import
img=[]
img.append(PhotoImage(file='picture\off.png'))
img.append(PhotoImage(file='picture\on.png'))
# gui layout
label=[]
for i in range(arr.shape[0]):
	label.append(Label(image=img[0]))
	label[i].place(x=i*100,y=40)
scale = Scale(resolution=1,to=((arr.shape[1]-1)),orient=HORIZONTAL,length=300,command=change)
scale.place(x=20,y=140)
button_1=Button(text=" ◀ ",command=backward)
button_1.place(x=340,y=155)
button_2=Button(text=" ▶ ",command=forward)
button_2.place(x=370,y=155)
button_3=Button(text=" ▶|| ",command=lambda :MyThread(run))
button_3.place(x=410,y=155)
button_4=Button(text="plot",command=lambda :plot(arr))
button_4.place(x=450,y=155)
text_path=Text(width=50, height=1)
text_path.insert(1.0, path)
text_path.place(x=0,y=5)
text_path.configure(font=("Courier", 11, "italic"))
button_open=Button(text="open",command=select_path)
button_open.place(x=455,y=4)
# tkinter run
tk.mainloop()





