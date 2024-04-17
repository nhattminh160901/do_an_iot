import pyrebase
from tkinter import *
from tkinter import messagebox
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import ttk
import pickle as pk

class FirstPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
       
        Label(self, text="BỘ ĐO NHIỆT ĐỘ VÀ ĐỘ ẨM", font=("TkDefaultFont", 14),
                            wraplengt=250).place(x=100, y=0)

        labelEmail = Label(self, text="Email")
        labelEmail.place(x=80, y=60)
        entryEmail = Entry(self)
        entryEmail.place(x=80*2, y=60)
      
        def verify(event=None):
            email = entryEmail.get()
            password = entryPassword.get()
            # emailEntry.delete(0, 'end')
            # passwordEntry.delete(0, 'end')

            global db

            firebaseConfig = {
            'apiKey': "AIzaSyCt60H3fUGiPv973_fMMN51lp2XXRazjF0",
            'authDomain': "arduino-firebase-vippro.firebaseapp.com",
            'databaseURL': "https://arduino-firebase-vippro-default-rtdb.firebaseio.com",
            'projectId': "arduino-firebase-vippro",
            'storageBucket': "arduino-firebase-vippro.appspot.com",
            'messagingSenderId': "437474413862",
            'appId': "1:437474413862:web:92d2b1c67528bf994fc5e7",
            'measurementId': "G-HMRKLR9EVW",
            'serviceAccount': "serviceAccountKey.json"
            }

            try:
                firebase = pyrebase.initialize_app(firebaseConfig)
                auth = firebase.auth()
                auth.sign_in_with_email_and_password(email, password)
                db = firebase.database()
                messagebox.showinfo("Login", "Successfully signed in!")
                controller.geometry("900x600")
                controller.show_frame(SecondPage)
            except:
                messagebox.showerror("Login", "Login error!")
        
        labelPassword = Label(self, text="Password")
        labelPassword.place(x=80, y=90)
        entryPassword = Entry(self, show="*")
        entryPassword.place(x=80*2, y=90)
        entryPassword.bind("<Return>", verify)

        buttonLogin = Button(self, text="Login", command=verify)
        buttonLogin.place(x=80, y=120)

        buttonExit = Button(self, text="Exit", command=lambda: controller.destroy())
        buttonExit.place(x=350, y=120)

        
class SecondPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.datas = []
        self.index = count()
        self.xList = []
        self.yList = []
        self.y2List = []

        thirdPage = Button(self, text="Open more", command=lambda: controller.show_frame(ThirdPage))
        thirdPage.place(x=750, y=550)

        firstPage = Button(self, text="Back", command=lambda: [controller.show_frame(FirstPage),
                                                                controller.geometry("400x200")])
        firstPage.place(x=100, y=550)

        labelFileName = Label(self, text="File Name")
        labelFileName.place(x=20, y=30)

        self.entryFileName = Entry(self)
        self.entryFileName.place(x=20, y=60)
        self.entryFileName.insert(0, "Enter file name")
        self.entryFileName.bind("<Button-1>", self.clear_entry)

        self.button1 = Button(self, text="Create File and Start", command=self.start)
        self.button1.place(x=20, y=90)

    def run_after(self, ms:int, command):
        run_after = self.after(ms, command)
        return run_after

    def cancel_after(self, id):
        self.after_cancel(id)

    def clear_entry(self, event=None):
        self.entryFileName.delete(0, END)

    def start(self):
        fileName = self.entryFileName.get()+".csv"
        self.f = open("data/"+fileName, "w", encoding="utf-8", newline="")
        self.writeFile = csv.writer(self.f)
        self.writeFile.writerow([("times"), ("day"), ("time"), ("temp"), ("hr")])
        self.entryFileName.destroy()

        labelFileName = Label(self, text=fileName)
        labelFileName.place(x=20, y=60) 

        self.button1.configure(text="Cancel and Save", command=self.cancel)

        fig = Figure()
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Realtime Data")
        self.ax.set_xlabel("times")
        self.ax.set_ylabel("Temperature")
        # self.ax.set_ylim(20, 35)
        self.ax2 = self.ax.twinx()
        self.ax2.set_ylabel("Humidity")
        # self.ax2.set_ylim(50, 100)
        
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().place(x=150, y=10)
        self.canvas.draw()
        self.runAfter = self.run_after(1000, self.plotData)

    def cancel(self):
        self.entryFileName = Entry(self)
        self.entryFileName.place(x=20, y=60)
        self.entryFileName.insert(0, "Enter file name")
        self.entryFileName.bind("<Button-1>", self.clear_entry)

        self.button1.configure(text="Create File", command=self.start)
        
        self.f.close()
        
        self.datas = []
        self.index = count()
        self.xList = []
        self.yList = []
        self.y2List = []

        self.cancel_after(self.runAfter)
        self.canvas.get_tk_widget().destroy()

    # self.create.writerows(tuple())

    def plotData(self):
        try:
            if db.child("new_world").child("get").get().val():
                times = next(self.index)+1
                day = db.child("new_world").child("day").get().val()
                time = db.child("new_world").child("time").get().val()
                temp = db.child("new_world").child("temp").get().val()
                hud = db.child("new_world").child("humidity").get().val()
                db.child("new_world").update({"get":False})
                self.writeFile.writerow([times, day, time, temp, hud])
                self.xList.append(times)
                self.yList.append(temp)
                self.y2List.append(hud)
                self.ax.plot(self.xList, self.yList, color="red")
                self.ax2.plot(self.xList, self.y2List, color="blue")
            self.canvas.draw()
        except:
            print("Reconnecting........")

        self.runAfter = self.run_after(1000, self.plotData)

class ThirdPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.knn = pk.load(open("model/knn.sav", "rb"))

        secondPage = Button(self, text="Back", command=lambda: controller.show_frame(SecondPage))
        secondPage.place(x=100, y=550)

        labelFN = Label(self, text="File Name")
        labelFN.place(x=20, y=30)

        buttonStart = Button(self, text="Start", command=self.start)
        buttonStart.place(x=20, y=90)

        self.entryFileName = Entry(self)
        self.entryFileName.place(x=20, y=60)
        self.entryFileName.insert(0, "Enter file name")
        self.entryFileName.bind("<Button-1>", self.clear_entry)

        buttonClear = Button(self, text="Clear Data", command=self.clearFrame)
        buttonClear.place(x=150, y=550)

        buttonPlot = Button(self, text="Plot Data Type 1", command=self.plotDataType1)
        buttonPlot.place(x=225, y=550)

        buttonPlot = Button(self, text="Plot Data Type 2", command=self.plotDataType2)
        buttonPlot.place(x=330, y=550)

        buttonPlot = Button(self, text="Prediction", command=self.sendData)
        buttonPlot.place(x=440, y=550)      

    def clear_entry(self, event=None):
        self.entryFileName.delete(0, END)
    
    def start(self):      
        self.frame = LabelFrame(self, text="Data")
        self.frame.place(x=150, y=10, height=500, width=500)
        self.frame2 = LabelFrame(self, text="Describe")
        self.frame2.place(x=670, y=10, height=300, width=200)
        fileName = self.entryFileName.get()+".csv"
        try:
            global df
            df = pd.read_csv("data/"+fileName)
            df2 = df[["temp", "hr"]].describe()

        #load data
            scrollbar=Scrollbar(self.frame, orient='vertical')
            scrollbar.pack(side=RIGHT, fill=Y)

            treeview = ttk.Treeview(self.frame, yscrollcommand=scrollbar.set)
            column_list = df.columns.to_list()
            treeview["columns"] = column_list[1:]
            treeview.column("#0", width=50, anchor=CENTER)
            treeview.heading("#0", text=column_list[0])

            for i in column_list[1:]:
                treeview.column(i, width=100, anchor=CENTER)
                treeview.heading(i, text=i)
            
            for i, row in df.iterrows():
                treeview.insert("", "end", text=str(i), values=(row["day"], row["time"], row["temp"], row["hr"]))

            treeview.pack(fill="both", expand=True, side="top")
            scrollbar.config(command=treeview.yview)

        #describe
            scrollbar2=Scrollbar(self.frame2, orient='horizontal')
            scrollbar2.pack(side=BOTTOM, fill=X)

            treeview2 = ttk.Treeview(self.frame2, xscrollcommand=scrollbar2.set)
            column_list2 = df2.columns.to_list()
            treeview2["columns"] = column_list2
            treeview2.column("#0", width=75, anchor=CENTER)
            treeview2.heading("#0", text="")

            for i in column_list2:
                treeview2.column(i, width=100, anchor=CENTER)
                treeview2.heading(i, text=i)

            for i, row in df2.iterrows():
                treeview2.insert("", "end", text=str(i), values=(row["temp"], row["hr"]))

            treeview2.pack(fill="both", expand=True, side="top")
            scrollbar2.config(command=treeview2.xview)
        except:
            messagebox.showerror("Open file error!", "No such file or directory")
  
    def plotDataType1(self):
        df[['temp', 'hr']].plot()
        plt.show()

    def plotDataType2(self):
        x = df.values[:, 3:5].astype(None)
        plt.scatter(x[:, 0], x[:, 1], c=self.knn.predict(x))
        plt.show()

    def sendData(self):
        global du_doan
        try:
            x = df.values[:, 3:5].astype(None)
            y_pred = self.knn.predict(x)
            if sum(y_pred)/len(y_pred)>0.5:
                data = {
                    "ndtb":df["temp"].mean(),
                    "datb":df["hr"].mean(),
                    "hienthi_lcd":True,
                    "trang_thai":"Nang"
                    }
                du_doan = Label(self, text="Troi nang, di choi thoi!", font=("TkDefaultFont",15))
                du_doan.place(x=525, y=547)
            else:
                data = {
                    "ndtb":df["temp"].mean(),
                    "datb":df["hr"].mean(),
                    "hienthi_lcd":True,
                    "trang_thai":"Mua"
                    }
                du_doan = Label(self, text="Troi mua roi, di choi nho mang ao mua!", font=("TkDefaultFont",15))
                du_doan.place(x=525, y=547)
            db.child("new_world").update(data)
        except:
            messagebox.showerror("Error", "Can't send data")

    def clearFrame(self):
        self.frame.destroy()
        self.frame2.destroy()
        du_doan.destroy()

        # fileName = self.enterFileName.get()+".csv"
        # self.df = pd.read_csv("data/"+fileName)


        
# class NewWindow(Toplevel):
#     def __init__(self, parent):
#         Toplevel.__init__(self, parent)
        
#         ico = Image.open("logo.png")
#         photo = ImageTk.PhotoImage(ico)
#         self.wm_iconphoto(False, photo)
#         self.geometry('300x100')
#         self.title('Toplevel Window')

#         button = Button(self, text='Close', command=self.destroy)
#         button.pack()

class Application(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        
        window = Frame(self)
        window.pack()

        window.grid_rowconfigure(0, minsize=600)
        window.grid_columnconfigure(0, minsize=900)
        
        self.frames = {}
        for F in (FirstPage, SecondPage, ThirdPage):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame(ThirdPage)
        
    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()

    # def openWindow(self):
    #     nWd = NewWindow(self)
    #     nWd.grab_set()