import discord
import asyncio
import pymongo
import os
import tkinter as tk
import urllib.request

from PIL import Image
from PIL import ImageTk
from PIL import ImageOps
from tkinter import Canvas
from tkinter import Grid
from tkinter import Label
from tkinter import Scrollbar
from tkinter import Listbox
from tkinter import Frame
from tkinter import Button
from tkinter import Entry
from tkinter import StringVar
from tkinter import IntVar
from tkinter import Checkbutton
from tkinter import Toplevel
from tkinter import Message
from tkinter import OptionMenu
from tkinter import filedialog
#move one directory up for the executable version since both programs need to be kept in seperate directories
#os.chdir('..')
#open settings file
guiCheck = True
try:
    file = open('settings.txt','r+')
except FileNotFoundError:
    file = open('settings.txt', 'w+')

class settings():
    botToken = ""
    mongo = ""
    DBname = "db"
    spawnChannel = ""
    arenaChannel = ""
    mongoDB = pymongo.MongoClient()
    client = discord.Client()
    db = None
    flavors = None
    monsters = None
    users = None
    arenas = None
    
class FailedApplication(tk.Frame):              
    def __init__(self, master=None):
        super().__init__(master)
        top = Toplevel(self)
        top.title("Failed connection")

        msg = Message(top, text='Connection Error Please ensure that your internet connection and mongoDB server are up and running and that your credentials are correct')
        msg.pack()

        button = Button(top, text="Dismiss", command=lambda: top.destroy())
        button.pack()
        
class Application(tk.Frame):              
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand = 1,fill = 'both')
        self.header = Frame(self)
        self.header.pack()
        self.content = Frame(self)
        self.content.pack(expand = 1,fill='both')
        self.createWidgets()
        self.highlightValidate = (self.register(self.callback),'%W')
        self.validateIntCom = (self.register(self.validateInt),'%S')
        self.validateFloatCom = (self.register(self.validateFloat),'%S')
        self.validateIntArenaCom = (self.register(self.validateIntArena),'%S','%W')
        self.validateFloatArenaCom = (self.register(self.validateFloatArena),'%S','%W')
        #self.grid()
        #self.window()
        
        #self.placeWidgets()
    def createWidgets(self):
        

        self.settings = tk.Button(self.header, text = "Settings",command = self.settingsDisplay, width =8)
        self.monsters = tk.Button(self.header, text = "Monsters",command = self.monsterDisplay, width =8)
        self.flavorText = tk.Button(self.header, text = "Flavor Text",command = self.flavorDisplay, width =8)
        self.arenas = tk.Button(self.header, text = "Arenas",command = self.arenaDisplay, width =8)
        self.imports = tk.Button(self.header, text = "Imports",command = self.importsDisplay, width =8)
        self.exports = tk.Button(self.header, text = "Exports",command = self.exportsDisplay, width =8)
       
        #test = Image.open('arenaDisplay.png')
        #testTK = ImageTk.PhotoImage(test)
        #self.label = Label(self, image=testTK)
        #self.label.image = testTK
       

        self.settings.pack(side = 'left',expand = 1)
        self.monsters.pack(side = 'left')
        self.flavorText.pack(side = 'left')
        self.arenas.pack(side = 'left')
        self.imports.pack(side = 'left')
        self.exports.pack(side = 'left')
        self.settingsDisplay()

    def checkConnection(self):
        
        try:
            settings.monsters.find_one({'monsterID':0})
            updateDBrefGUI()   
        except pymongo.errors.OperationFailure:
            self.settingsDisplay()
            self.content.connectionLabel.config(text='A connection error has occured.\nTry re-entering your credentials or checking your internet connection and restart the program')
            return True
        except pymongo.errors.ServerSelectionTimeoutError:
            self.settingsDisplay()
            print('timeout')
            self.content.connectionLabel.config(text='Server timeout error. \n Ensure that your server and internet connection are functioning properly and restart the program')
            return True
        except AttributeError:
            self.settingsDisplay()
            print('attribute error')
            self.content.connectionLabel.config(text='Server timeout error. \n Ensure that your server and internet connection are functioning properly and restart the program')
            return True
        return False
    def settingsDisplay(self):
        print('Displaying settings')
        
        self.clearContent()

        self.content.connectionLabel = Label(self.content)
        
        botLabel = Label(self.content,text = 'Bot Token')
        loginLabel = Label(self.content,text = 'MongoDB login')
        dbLabel = Label(self.content,text = 'Database Name')
        encounterLabel = Label(self.content,text = 'Monster Encounter Channel')
        battleLabel = Label(self.content,text = 'Monster Battle Channel')

        botEntry = Entry(self.content,width =75)
        botEntry.insert('end',settings.botToken)
        loginEntry = Entry(self.content,width =75)
        loginEntry.insert('end',settings.mongo)
        dbEntry = Entry(self.content,width =75)
        dbEntry.insert('end',settings.DBname)
        encounterEntry = Entry(self.content,width =75)
        encounterEntry.insert('end',settings.spawnChannel)
        battleEntry = Entry(self.content,width =75)
        battleEntry.insert('end',settings.arenaChannel)

        self.content.connectionLabel.pack()
        botLabel.pack()
        botEntry.pack()
        loginLabel.pack()
        loginEntry.pack()
        dbLabel.pack()
        dbEntry.pack()
        encounterLabel.pack()
        encounterEntry.pack()
        battleLabel.pack()
        battleEntry.pack()

        saveButton = Button(self.content,text = 'Save',command = self.saveSettingsButton)
        saveButton.pack()
        
    def saveSettingsButton(self):
        s = {}
        i = 0
        for x in self.content.winfo_children():
            if type(x) == Entry:
                s[i] = x.get()
                i+=1
        print(str(s))

        try:
            file = open('settings.txt','r+')
        except FileNotFoundError:
            file = open('settings.txt', 'w+')
        settings.botToken = s[0]
        settings.mongo = s[1]
        settings.DBname = s[2]
        settings.spawnChannel = s[3]
        settings.arenaChannel = s[4]
        file.write(settings.botToken+'\n'+settings.mongo+'\n'+settings.DBname+'\n'+settings.spawnChannel+'\n'+settings.arenaChannel+'\n')

        
                
    def monsterDisplay(self):
        print('Displaying monsters')
        if self.checkConnection():
            return
        self.clearContent()
        self.createScrollTable()
        if (self.addEntries(getMonsterDocs())):
            self.content.updateButton.config(command =lambda: self.updateButton(0))
            self.content.detailButton.config(command =lambda: self.monsterDetail(1))
        else:
            self.content.updateButton.destroy()
            self.content.detailButton.destroy()
        self.content.addButton.config(command =lambda: self.addMonster())

    def onFrameConfigure(self, event):
       self.content.scrollCanvas.configure(scrollregion=self.content.scrollCanvas.bbox("all"),height = 100)

       
    def flavorDisplay(self):
        print('Displaying flavor text')
        if self.checkConnection():
            return
        self.clearContent()
        self.createScrollTable()
        if (self.addEntries(getFlavorDocs())):
            self.content.updateButton.config(command =lambda: self.updateButton(1))
            self.content.detailButton.config(command =lambda: self.flavorDetail(0))
        else:
            self.content.updateButton.destroy()
            self.content.detailButton.destroy()
        self.content.addButton.config(command =lambda: self.addFlavor())

    def arenaDisplay(self):
        print('Displaying arenas')
        if self.checkConnection():
            return
        self.clearContent()
        self.createScrollTable()
        if (self.addEntries(getArenaDocs())):
            self.content.updateButton.config(command =lambda: self.updateButton(2))
            self.content.detailButton.config(command =lambda: self.arenaDetail(0))
        else:
            self.content.updateButton.destroy()
            self.content.detailButton.destroy()
        self.content.addButton.config(command =lambda: self.addArena())

        
        
        
        #self.arenaHeader = tk.Label(self,image =tkImage)
        #self.arenaHeader.grid(column = 0,row = 1)

    def exportsDisplay(self):
        print('Displaying exports')
        if self.checkConnection():
            return
        self.clearContent()
        #self.createScrollTable()
        monsterDownload = Button(self.content,text = 'Download Monsters',bd = 2,width = 20,command = lambda: self.downloadFile(0))
        monsterDownload.pack(pady = 10)

        flavorDownload = Button(self.content,text = 'Download Flavors',bd = 2,width = 20,command = lambda: self.downloadFile(1))
        flavorDownload.pack(pady = 10)

        arenaDownload = Button(self.content,text = 'Download Arenas',bd = 2,width = 20,command = lambda: self.downloadFile(2))
        arenaDownload.pack(pady = 10)

        usersDownload = Button(self.content,text = 'Download Users',bd = 2,width = 20,command = lambda: self.downloadFile(3))
        usersDownload.pack(pady = 10)

        self.content.status = Label(self.content,text='')
        self.content.status.pack()

    def importsDisplay(self):
        print('Displaying Imports')
        if self.checkConnection():
            return
        self.clearContent()
        monsterUpload = Button(self.content,text = 'Upload Monsters',bd = 2,width = 20,command = lambda: self.uploadFile(0))
        monsterUpload.pack(pady = 10)

        flavorUpload = Button(self.content,text = 'Upload Flavors',bd = 2,width = 20,command = lambda: self.uploadFile(1))
        flavorUpload.pack(pady = 10)

        arenaUpload = Button(self.content,text = 'Upload Arenas',bd = 2,width = 20,command = lambda: self.uploadFile(2))
        arenaUpload.pack(pady = 10)

        usersUpload = Button(self.content,text = 'Upload Users',bd = 2,width = 20,command = lambda: self.uploadFile(3))
        usersUpload.pack(pady = 10)

        self.content.status = Label(self.content,text='')
        self.content.status.pack()

    def uploadFile(self,case):
        # Ask the user to select a single file name.
        question = 'Upload Monster Backup'
        if case == 1:
            question = "Upload Flavor Backup"
        if case == 2:
            question = "Upload Arena Backup"
        if case == 3:
            question = "Upload User Backup"
        answer = filedialog.askopenfilename(parent=self,initialdir=os.getcwd(),title="Please select a file:",filetypes=[('text files', '.txt')])
        print(str(answer))
        self.content.status.config(text='Please wait...')
        self.update()
        if case == 0:
            if validateMonsterPack(answer):
                self.content.status.config(text=DBuploadMonsterPack(answer))
            else:
                self.content.status.config(text='Operation Failure. Pack was formatted incorrectly')
        elif case == 1:
            if validateFlavorPack(answer):
                self.content.status.config(text=DBuploadFlavorPack(answer))
            else:
                self.content.status.config(text='Operation Failure. Pack was formatted incorrectly')
        elif case == 2:
            if validateArenaPack(answer):
                self.content.status.config(text=DBuploadArenaPack(answer))
            else:
                self.content.status.config(text='Operation Failure. Pack was formatted incorrectly')
        elif case == 3:
            if validateUserPack(answer):
                self.content.status.config(text=DBuploadUserPack(answer))
            else:
                self.content.status.config(text='Operation Failure. Pack was formatted incorrectly')
        #operationhere

    def downloadFile(self,case):
        # Ask the user to select a single file name.
        question = 'Download Monster Backup'
        if case == 1:
            question = "Download Flavor Backup"
        elif case == 2:
            question = "Download Arena Backup:"
        elif case == 3:
            question = "Download User Backup:"
        
        answer = filedialog.asksaveasfilename(parent=self,initialdir=os.getcwd(),title="Please select a file:",filetypes=[('text files', '.txt')],defaultextension='txt')
        print(str(answer))

        self.content.status.config(text='Please wait...')
        
        self.update()
        if case == 0:
            
            self.content.status.config(text=DBdownloadMonsters(answer))
        elif case == 1:
            self.content.status.config(text=DBdownloadFlavors(answer))
        elif case == 2:
            self.content.status.config(text=DBdownloadArenas(answer))
        elif case == 3:
            self.content.status.config(text=DBdownloadUsers(answer))
        
        #operationhere
    def monsterDetail(self,choice):

        choice = int(choice)
        doc = settings.monsters.find_one({'monsterID':choice})


        
        
        
        if doc == None:
            print('No doc found')
            return
        #create frame
        self.clearContent()
        self.createScrollTable()
        #header
        #headerLabel = Label(self.content.frame.labelCanvas.labelFrame,text='Monster Details',anchor = 'center',justify='center',relief='raised')
        #headerLabel.pack(expand = 1,fill='x')
        #displaypage
        #header
        count = settings.monsters.count()
        headerLabel = Label(self.content.frame.canvas,text = str(choice)+'/'+str(count))
        #frame
        self.content.frame.canvas.choiceFrame = Frame(self.content.frame.canvas)
        #entry number
        self.content.frame.canvas.choiceFrame.selectEntry = Entry(self.content.frame.canvas.choiceFrame,width = 5, justify = 'center')
        self.content.frame.canvas.choiceFrame.selectEntry.insert('end',str(choice))
        #buttons
        #need a serparate validation
        
        self.content.frame.canvas.choiceFrame.left = Button(self.content.frame.canvas.choiceFrame,text = '<',command = lambda: self.monsterDetail(choice-1))
        self.content.frame.canvas.choiceFrame.right = Button(self.content.frame.canvas.choiceFrame,text = '>',command = lambda: self.monsterDetail(choice+1))
            
        headerLabel.pack()
        self.content.frame.canvas.choiceFrame.left.pack(side = 'left')
        self.content.frame.canvas.choiceFrame.selectEntry.pack(side = 'left')
        self.content.frame.canvas.choiceFrame.right.pack(side = 'left')
        self.content.frame.canvas.choiceFrame.pack()
        #go button
        self.content.frame.canvas.go = Button(self.content.frame.canvas,text = 'Go',command = lambda: self.monsterDetail(self.content.frame.canvas.choiceFrame.selectEntry.get()))
        self.content.frame.canvas.go.pack()
        #draw doc
        self.docDetails(doc)
        #reset buttons
        self.content.updateButton.config(command =lambda: self.detailUpdateConfirm(0))
        self.content.detailButton.config(command =lambda: self.monsterDisplay(),text = 'Table View')
        self.content.addButton.config(command =lambda: self.addMonster())
        #selection buttons
        
        
        self.calibrateScrollbars() 
                
    def flavorDetail(self,choice):

        choice = int(choice)
        doc = settings.flavors.find_one({'id':choice})
        
        if doc == None:
            
            return
        #create frame
        self.clearContent()
        self.createScrollTable()
        
        #displaypage
        #header
        count = settings.flavors.count()
        headerLabel = Label(self.content.frame.canvas,text = str(choice)+'/'+str(count-1))
        #frame
        self.content.frame.canvas.choiceFrame = Frame(self.content.frame.canvas)
        #entry number
        self.content.frame.canvas.choiceFrame.selectEntry = Entry(self.content.frame.canvas.choiceFrame,width = 5, justify = 'center')
        self.content.frame.canvas.choiceFrame.selectEntry.insert('end',str(choice))
        #buttons
        #need a serparate validation
        
        self.content.frame.canvas.choiceFrame.left = Button(self.content.frame.canvas.choiceFrame,text = '<',command = lambda: self.flavorDetail(choice-1))
        self.content.frame.canvas.choiceFrame.right = Button(self.content.frame.canvas.choiceFrame,text = '>',command = lambda: self.flavorDetail(choice+1))
            
        headerLabel.pack()
        #disable if there are no more
        if choice == 0:
            self.content.frame.canvas.choiceFrame.left.config(state='disabled')
        if choice == count-1:
            self.content.frame.canvas.choiceFrame.right.config(state='disabled')
        self.content.frame.canvas.choiceFrame.left.pack(side = 'left')
        self.content.frame.canvas.choiceFrame.selectEntry.pack(side = 'left')
        self.content.frame.canvas.choiceFrame.right.pack(side = 'left')
        self.content.frame.canvas.choiceFrame.pack()
        #go button
        self.content.frame.canvas.go = Button(self.content.frame.canvas,text = 'Go',command = lambda: self.flavorDetail(self.content.frame.canvas.choiceFrame.selectEntry.get()))
        self.content.frame.canvas.go.pack()
        #draw doc
        self.docDetails(doc)
        #reset buttons
        self.content.updateButton.config(command =lambda: self.detailUpdateConfirm(0))
        self.content.detailButton.config(command =lambda: self.flavorDisplay(),text = 'Table View')
        self.content.addButton.config(command =lambda: self.addFlavor())
        #selection buttons
        
        
        self.calibrateScrollbars()

    def arenaDetail(self,choice):

        choice = int(choice)
        doc = settings.arenas.find_one({'id':choice})
        
        if doc == None:
            
            return
        #create frame
        self.clearContent()
        self.createScrollTable()
        
        #displaypage
        #header
        count = settings.arenas.count()
        headerLabel = Label(self.content.frame.canvas,text = str(choice)+'/'+str(count-1))
        #frame
        self.content.frame.canvas.choiceFrame = Frame(self.content.frame.canvas)
        #entry number
        self.content.frame.canvas.choiceFrame.selectEntry = Entry(self.content.frame.canvas.choiceFrame,width = 5, justify = 'center')
        self.content.frame.canvas.choiceFrame.selectEntry.insert('end',str(choice))
        #buttons
        #need a serparate validation
        
        self.content.frame.canvas.choiceFrame.left = Button(self.content.frame.canvas.choiceFrame,text = '<',command = lambda: self.arenaDetail(choice-1))
        self.content.frame.canvas.choiceFrame.right = Button(self.content.frame.canvas.choiceFrame,text = '>',command = lambda: self.arenaDetail(choice+1))
            
        headerLabel.pack()
        self.content.frame.canvas.choiceFrame.left.pack(side = 'left')
        self.content.frame.canvas.choiceFrame.selectEntry.pack(side = 'left')
        self.content.frame.canvas.choiceFrame.right.pack(side = 'left')
        self.content.frame.canvas.choiceFrame.pack()
        #go button
        self.content.frame.canvas.go = Button(self.content.frame.canvas,text = 'Go',command = lambda: self.arenaDetail(self.content.frame.canvas.choiceFrame.selectEntry.get()))
        self.content.frame.canvas.go.pack()
        #draw doc
        self.docDetailsArena(doc)
        #reset buttons
        self.content.updateButton.config(command =lambda: self.detailUpdateConfirm(0))
        self.content.detailButton.config(command =lambda: self.arenaDisplay(),text = 'Table View')
        self.content.addButton.config(command =lambda: self.addArena())
        #selection buttons
        
        
        self.calibrateScrollbars()

        
    def addFlavor(self):

        
        self.clearContent()
        self.createScrollTable()
        #destroy buttons cause im too lazy to make another method for making these windows
        self.content.updateButton.destroy()
        self.content.detailButton.destroy()
        self.content.addButton.destroy()
        
        textLabel = Label(self.content.frame.canvas,text = 'Text')                         
        typeLabel = Label(self.content.frame.canvas,text = 'Type')
        
        textEntry = Entry(self.content.frame.canvas)
        typeEntry = Entry(self.content.frame.canvas)
        

        textLabel.pack()
        textEntry.pack()
        typeLabel.pack()
        typeEntry.pack()
        

        confirmButton = Button(self.content.frame.canvas,text = 'Add',command =lambda: self.DBaddConfirm(1))
        confirmButton.pack()

    #def DBnewArena(x1,y1,x2,y2,halign,valign,arenaImage):
    def addArena(self):

        
        self.clearContent()
        self.createScrollTable()
        #destroy buttons cause im too lazy to make another method for making these windows
        self.content.updateButton.destroy()
        self.content.detailButton.destroy()
        self.content.addButton.destroy()
        
        x1Label = Label(self.content.frame.canvas,text = 'Character 1 X coordinate')                         
        y1Label = Label(self.content.frame.canvas,text = 'Character 1 Y coordinate')
        x2Label = Label(self.content.frame.canvas,text = 'Character 2 X coordinate')                         
        y2Label = Label(self.content.frame.canvas,text = 'Character 2 Y coordinate')
        halignLabel = Label(self.content.frame.canvas,text = 'Horizontal Alignment')
        valignLabel = Label(self.content.frame.canvas,text = 'Vertical Alignment')
        arenaImageLabel = Label(self.content.frame.canvas,text = 'Arena Image URL')


        
        x1Entry = Entry(self.content.frame.canvas)
        y1Entry = Entry(self.content.frame.canvas)
        x2Entry = Entry(self.content.frame.canvas)
        y2Entry = Entry(self.content.frame.canvas)
        halignEntry = Entry(self.content.frame.canvas)
        valignEntry = Entry(self.content.frame.canvas)
        arenaImageEntry = Entry(self.content.frame.canvas)
        
        x1Label.pack()
        x1Entry.pack()
        y1Label.pack()
        y1Entry.pack()
        x2Label.pack()
        x2Entry.pack()
        y2Label.pack()
        y2Entry.pack()
        halignLabel.pack()
        halignEntry.pack()
        valignLabel.pack()
        valignEntry.pack()
        arenaImageLabel.pack()
        arenaImageEntry.pack()
        
        
        

        confirmButton = Button(self.content.frame.canvas,text = 'Add',command =lambda: self.DBaddConfirm(2))
        confirmButton.pack()

        
    def DBaddConfirm (self,case):
        self.content.top = Toplevel(self.content)
        
        self.content.top.title("Confirm data operation")
        msg = Message(self.content.top, text='Confirm you are ready to perform the operation on the database\n',justify = 'center')
        msg.grid(column=1,row=0)
        confirm = Button(self.content.top, text="Confirm", command= lambda: self.DBadd(case))
        confirm.grid(column=0,row=1)
        cancel = Button(self.content.top, text="Cancel", command=self.content.top.destroy)
        cancel.grid(column=2,row=1)

    def DBadd (self,case):
        
        children = self.content.frame.canvas.winfo_children()
        editValues= {}
        i = 1
        for x in children:
            if type(x) is Entry:
                print(x.get())
                editValues[i] = x.get()
                i+=1
        dbResult = None
        if case == 0:
            print('monsters')
            #validate values
            try:
                editValues[2] = int(editValues[2])
                #insert values
                dbresult = DBnewMonster(editValues[1], editValues[2], editValues[3], editValues[4])
            except:
                dbResult = 'Rarity must be an integer'
        elif case == 1:
            print('flavors')
            #dbResult = DBeditFlavor (editValues[2], editValues[3], editValues[1])
        elif case == 2:
            print('arenas')
            #dbResult = DBeditArena (editValues[2], editValues[3], editValues[4], editValues[5],editValues[6],editValues[7],editValues[8],editValues[1])
        elif case == 3:
            print('users')
        print(dbResult)
        if dbResult != None:
            #if it gets here then it failed
            success = False
            print(dbResult)
            self.content.top.destroy()
            top = Toplevel()
            top.title("Operation failed")

            msg = Message(top, text='Database operation stopped\n'+dbResult,justify='center')
            msg.pack()

            button = Button(top, text="Dismiss", command=top.destroy)
            button.pack()
            return
        
        self.content.top.destroy()
        top = Toplevel()
        top.title("Operation complete")

        msg = Message(top, text='The operation was completed successfully',justify='center')
        msg.pack()

        button = Button(top, text="Dismiss", command=top.destroy)
        button.pack()
            
    def detailUpdateConfirm(self,case):
        self.content.top = Toplevel(self.content)
        
        self.content.top.title("Confirm data operation")
        msg = Message(self.content.top, text='Confirm you are ready to perform the operation on the database\n',justify = 'center')
        msg.grid(column=1,row=0)
        confirm = Button(self.content.top, text="Confirm", command= lambda: self.detailUpdate(case))
        confirm.grid(column=0,row=1)
        cancel = Button(self.content.top, text="Cancel", command=self.content.top.destroy)
        cancel.grid(column=2,row=1)
        
    def detailUpdate(self,case):
        print('Detail Update')
        children = self.content.frame.canvas.gridFrame.winfo_children()
        
        editValues= {}
        i = 1
        for x in children:
            if type(x) is Entry:
                #print(x.get())
                editValues[i] = x.get()
                i+=1

        #upload to DB
        dbResult = ''
        if case == 0:
            print('monsters')
            dbResult = DBeditMonster (editValues[2], editValues[3], editValues[4], editValues[5],editValues[1])
        elif case == 1:
            print('flavors')
            dbResult = DBeditFlavor (editValues[2], editValues[3], editValues[1])
        elif case == 2:
            print('arenas')
            dbResult = DBeditArena (editValues[2], editValues[3], editValues[4], editValues[5],editValues[6],editValues[7],editValues[8],editValues[1])
        elif case == 3:
            print('users')
        if dbResult != None:
            #if it gets here then it failed
            success = False
            print(dbResult)
            self.content.top.destroy()
            top = Toplevel()
            
            top.title("Operation failed")

            msg = Message(top, text='Database operation stopped\n'+dbResult,justify='center')
            msg.pack()

            button = Button(top, text="Dismiss", command=top.destroy)
            button.pack()
            return
        self.content.top.destroy()
        top = Toplevel()
        top.title("Operation complete")

        msg = Message(top, text='The operation was completed successfully',justify='center')
        msg.pack()

        button = Button(top, text="Dismiss", command=top.destroy)
        button.pack()
            
    def docDetails(self,doc):
        self.content.keyCount = len(doc.keys())
        keyDict = dict()
        #default for no image
        self.content.frame.canvas.label = Label(self.content.frame.canvas, text='image could not be found')
        
        for i in range(1,self.content.keyCount):
            s = list(doc)[i]
            
            label = Label(self.content.frame.canvas.gridFrame,text=s,borderwidth=1,anchor='w',justify = 'left')
            label.pack(fill='x')
            #check if it is an image
            imageExists= False
            if  'Image' in s:
                text = str(doc[s])
                
                self.content.frame.canvas.gridFrame.entryURL = Entry(self.content.frame.canvas.gridFrame,justify = 'left')
                
                self.content.frame.canvas.gridFrame.entryURL.insert('end',str(text))
                self.content.frame.canvas.gridFrame.entryURL.pack(fill='x')
                imageExists= True
                
            else:
                
                entry = Entry(self.content.frame.canvas.gridFrame,justify = 'left')
                entry.pack(fill='x')
                entry.insert('end',str(doc[s]))
        #image functions
        if imageExists:
            refresh = Button(self.content.frame.canvas.gridFrame,text= 'Refresh',command=lambda: self.refreshImage())
            refresh.pack()
            self.refreshImage()
            
        
        
    def docDetailsArena(self,doc):
        self.content.keyCount = len(doc.keys())
        keyDict = dict()
        #default for no image
        self.content.frame.canvas.label = Label(self.content.frame.canvas, text='image could not be found')
        entryFrame = {}
        for i in range(1,self.content.keyCount):
            s = list(doc)[i]
            
            label = Label(self.content.frame.canvas.gridFrame,text=s,borderwidth=1,anchor='w',justify = 'left')
            label.pack(fill='x')
            #check if it is an image
            imageExists= False

            
            
            if  'Image' in s:
                text = str(doc[s])
                
                self.content.frame.canvas.gridFrame.entryURL = Entry(self.content.frame.canvas.gridFrame,justify = 'left')
                
                self.content.frame.canvas.gridFrame.entryURL.insert('end',str(text))
                self.content.frame.canvas.gridFrame.entryURL.pack(fill='x')
                imageExists= True
                
            else:
                if i >1 and i<6:#coordinates
                    entryFrame[i] = Frame(self.content.frame.canvas.gridFrame)
                    entryFrame[i].entry = Entry(entryFrame[i],justify = 'left',width = 10)
                    
                    entryFrame[i].leftButton = Button(entryFrame[i],text='<',command =lambda i=i: self.increaseEntry(entryFrame[i].entry,-1))

                    entryFrame[i].rightButton = Button(entryFrame[i],text='>',command =lambda i=i: self.increaseEntry(entryFrame[i].entry,1))
                    entryFrame[i].leftButton.pack(side='left')
                    entryFrame[i].entry.pack(side = 'left',fill='x')
                    entryFrame[i].rightButton.pack(side='left')
                    entryFrame[i].entry.insert('end',str(doc[s]))
                    #config needs to be done here for entry
                    entryFrame[i].entry.config(validate = 'key',validatecommand= self.validateIntArenaCom)
                    entryFrame[i].pack(fill='x')
                elif i==6: #horizontal alignment
                    entryFrame[i] = Frame(self.content.frame.canvas.gridFrame)
                    entryFrame[i].entry = Entry(entryFrame[i],justify = 'left',width = 5) 
                    entryFrame[i].entry.pack(side = 'left',fill='x')
                    
                    entryFrame[i].variable = StringVar(entryFrame[i])
                    #default value
                    if(doc[s]== 1.0):
                        entryFrame[i].variable.set("Left") # default value
                    elif(doc[s]== -0.5):
                        entryFrame[i].variable.set("Middle")
                    elif(doc[s]== -1.0):
                        entryFrame[i].variable.set("Right")
                    entryFrame[i].horizontalChoice = OptionMenu(entryFrame[i], entryFrame[i].variable, "Left", "Middle", "Right",command = lambda i=i: self.setHalignment(entryFrame[6].variable,entryFrame[6].entry))
                    entryFrame[i].horizontalChoice.pack(side='left')
                    
                    entryFrame[i].entry.insert('end',str(doc[s]))
                    #config needs to be done here for entry
                    entryFrame[i].entry.config(validate = 'key',validatecommand=self.validateFloatArenaCom)
                    entryFrame[i].pack(fill='x')
                elif i == 7: #vertical alignment
                    entryFrame[i] = Frame(self.content.frame.canvas.gridFrame)
                    entryFrame[i].entry = Entry(entryFrame[i],justify = 'left',width = 5) 
                    entryFrame[i].entry.pack(side = 'left',fill='x')
                    
                    entryFrame[i].variable = StringVar(entryFrame[i])
                    if(doc[s]== 1.0):
                        entryFrame[i].variable.set("Top") # default value
                    elif(doc[s]== -0.5):
                        entryFrame[i].variable.set("Middle")
                    elif(doc[s]== -1.0):
                        entryFrame[i].variable.set("Bottom")
                    entryFrame[i].verticalChoice = OptionMenu(entryFrame[i], entryFrame[i].variable, "Top", "Middle", "Bottom",command = lambda i=i: self.setValignment(entryFrame[7].variable,entryFrame[7].entry))
                    entryFrame[i].verticalChoice.pack(side='left')
                    
                    entryFrame[i].entry.insert('end',str(doc[s]))
                    #config needs to be done here for entry
                    entryFrame[i].entry.config(validate = 'key',validatecommand=self.validateFloatArenaCom)
                    entryFrame[i].pack(fill='x')
                else:
                    entryFrame[i] = Frame(self.content.frame.canvas.gridFrame)
                    entryFrame[i].entry = Entry(entryFrame[i],justify = 'left',width = 10)
                    entryFrame[i].entry.pack(fill='x')
                    entryFrame[i].entry.insert('end',str(doc[s]))
                    entryFrame[i].pack(fill='x')
        #test monsters
        test1Frame = Frame(self.content.frame.canvas.gridFrame)
        test1Label = Label (self.content.frame.canvas.gridFrame,text = 'Test Monster 1')
        test1Entry = Entry(test1Frame,justify = 'left',width = 10)
        test1Entry.insert('end',str(1))
        leftButton1 = Button(test1Frame,text='<',command = lambda: self.monsterEntryIncrease(test1Entry,-1))
        rightButton1 = Button(test1Frame,text='>',command = lambda: self.monsterEntryIncrease(test1Entry,1))

        test2Frame = Frame(self.content.frame.canvas.gridFrame)
        test2Label = Label (self.content.frame.canvas.gridFrame,text = 'Test Monster 2')
        test2Entry = Entry(test2Frame,justify = 'left',width = 10)
        test2Entry.insert('end',str(1))
        leftButton2 = Button(test2Frame,text='<',command = lambda: self.monsterEntryIncrease(test2Entry,-1))
        rightButton2 = Button(test2Frame,text='>',command = lambda: self.monsterEntryIncrease(test2Entry,1))

        test1Label.pack()
        leftButton1.pack(side='left')
        test1Entry.pack(side='left')
        rightButton1.pack(side='left')
        test1Frame.pack()

        
        test2Label.pack()
        leftButton2.pack(side='left')
        test2Entry.pack(side='left')
        rightButton2.pack(side='left')
        test2Frame.pack()

        #compileArenaImage (arena,monsterA,monsterB,xPos1,yPos1,xPos2,yPos2,halign,valign)
        
        #image functions
        #used to store images in memory
        print('create image')
        self.arenaGatherData()
        self.arenaGatherImages()
        if imageExists:

            refresh = Button(self.content.frame.canvas.gridFrame,text= 'Refresh', command= lambda: self.fullArenaRefresh())
            refresh.pack()
            self.refreshImageArena()

    def fullArenaRefresh(self):
        self.arenaGatherData()
        self.arenaGatherImages()
        self.refreshImageArena()

    def monsterEntryIncrease(self,entry,amount):
        #no negatives
        #print(entry)
        current = 0
        try:
            current = int(entry.get())+amount
        except ValueError:
            current = 0;
        if current <0:
            current = 0
        entry.delete(0, 'end')
        entry.insert('end',str(current))
        self.fullArenaRefresh()

        
    def validateInt(self,n):
        print('validate: '+str(n))
        if n in '1234567890':
            try:
                a = int(n)
                return True
            except:
                return False
        return False

    def validateFloat(self,n):
        print('validate: '+str(n))
        if n in '1234567890.-':
            return True
        return False
    
    #arena versions will also update the image
    def validateIntArena(self,n,w):
        print('validate int')
        print('widget: '+str(w))
        #print('length'+str(len(n)))
        #print('content'+str(n))
        #needs to do one char at a time
        for x in str(n):
            if x in '1234567890':
                try:
                    a = int(n)
                    
                except:
                    return False
        print('refreshing arena')
        
        return True

    def validateFloatArena(self,n,w):
        print('validate float')
        #print('length: '+str(len(n)))
        print('widget: '+str(w))
        #needs to do one char at a time
        for x in n:
            if x in '1234567890.-':
                print('valid float character')
            else:
                return False
        
        return True
    
    def increaseEntry(self,entry,amount):
        #no negatives
        #print(entry)
        current = 0
        try:
            current = int(entry.get())+amount
        except ValueError:
            current = 0;
        if current <0:
            current = 0
        entry.delete(0, 'end')
        entry.insert('end',str(current))
        self.arenaGatherData()
        self.refreshImageArena()

    def setHalignment(self,var,entry):
        print(var.get())
        entry.delete(0, 'end')
        if var.get() == 'Left':
            entry.insert('end','0.0')
        elif var.get() == 'Middle':
            entry.insert('end','-0.5')
        elif var.get() == 'Right':
            entry.insert('end','-1.0')
        self.arenaGatherData()
        self.refreshImageArena()

    def setValignment(self,var,entry):
        print(var.get())
        entry.delete(0, 'end')
        if var.get() == 'Top':
            entry.insert('end','0.0')
        elif var.get() == 'Middle':
            entry.insert('end','-0.5')
        elif var.get() == 'Bottom':
            entry.insert('end','-1.0')
        self.arenaGatherData()
        self.refreshImageArena()
        
    def refreshImage(self):
        print(self.content.frame.canvas.gridFrame.entryURL.get())
        try:
            i = urllib.request.urlopen(self.content.frame.canvas.gridFrame.entryURL.get())
        except:
            self.content.frame.canvas.label.destroy()
            self.content.frame.canvas.label = Label(self.content.frame.canvas, text='image could not be found')
            self.content.frame.canvas.label.pack(side='right')
            return
        image = Image.open(i)
        imageTK = ImageTk.PhotoImage(image)
        self.content.frame.canvas.label.destroy()
        self.content.frame.canvas.label = Label(self.content.frame.canvas, image=imageTK)
        self.content.frame.canvas.label.image = imageTK
        self.content.frame.canvas.label.pack(side='right',anchor = 'n')

    def refreshImageArena(self):
        
        print('refreshImageArena')
        data = self.content.data
        #print(str(data))
        x1 = 0
        y1 = 0
        x2 = 0
        y2 = 0
        halign = 1.0
        valign = 1.0

        #validate values
        try:
            x1 = int(data[1])
        except ValueError:
            x1 = 0
        try:
            y1 = int(data[2])
        except ValueError:
            y1 = 0
        try:
            x2 = int(data[3])
        except ValueError:
            x2 = 0
        try:
            y2 = int(data[4])
        except ValueError:
            y2 = 0
        try:
            halign = float(data[5])
        except ValueError:
            halign = 1.0
        try:
            valign = float(data[5])
        except ValueError:
            valign = 1.0 
        
        print('x1 '+str(x1))
        print('y1 '+str(y1))
        print('x2 '+str(x2))
        print('y2 '+str(y2))
        print('halign '+str(halign))
        print('valign '+str(valign))
        image = compileArenaImage (self.content.arena,self.content.monster1,self.content.monster2,x1,y1,x2,y2,halign,valign)
        imageTK = ImageTk.PhotoImage(image)
        self.content.frame.canvas.label.destroy()
        self.content.frame.canvas.label = Label(self.content.frame.canvas, image=imageTK)
        self.content.frame.canvas.label.image = imageTK
        self.content.frame.canvas.label.pack(side='right',anchor = 'n')          


    #hold status of current screen
    def arenaGatherData(self):
        print('arena garther data')
        children = self.content.frame.canvas.gridFrame.winfo_children()
        #getMonsterImage(monsterID)
        #data order 
        #arenaid
        #x1
        #y1
        #x2
        #y2
        #halign
        #valign
        #mon1
        #mon2
        self.content.data = {}
        dataCount = 0
        for x in children:
            if type(x) is Frame:
                frameChildren = x.winfo_children()
                for i in frameChildren:
                    if type(i) is Entry:
                        #print (str(i)+' data '+i.get())
                        
                        self.content.data[dataCount] = i.get()
                        dataCount +=1
        
    #hold images in memory
    def arenaGatherImages(self):
        data = self.content.data
        self.content.arena = Image.new('RGBA',(1,1))
        self.content.monster1 = Image.new('RGBA',(1,1))
        self.content.monster2 = Image.new('RGBA',(1,1))
        try:
            image = urllib.request.urlopen(self.content.frame.canvas.gridFrame.entryURL.get())
            self.content.arena = Image.open(image)
        except:
            #cant find arena image so just end it here
            self.content.frame.canvas.label.destroy()
            self.content.frame.canvas.label = Label(self.content.frame.canvas, text='image could not be found')
            self.content.frame.canvas.label.pack(side='right')
            return
        try:
            self.content.monster1 = getMonsterImage(int(data[7]))
        except TypeError:
            print('monster 1 not found')
            self.content.monster1 = Image.new('RGBA',(1,1))
        try: 
            self.content.monster2 = getMonsterImage(int(data[8]))
        except TypeError:
            print('monster 2 not found')
            self.content.monster2 = Image.new('RGBA',(1,1))

            
    def scrollMouseY(self,event):
        
        self.content.frame.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        if(self.content.frame.canvas.yview() == (0.0,1.0)):
            self.content.frame.canvas.yview_moveto(0.0)
        
    def scrollMouseX(self,event):
        self.content.frame.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        self.content.frame.labelCanvas.xview_scroll(int(-1*(event.delta/120)), "units")
        if(self.content.frame.canvas.xview() == (0.0,1.0)):
            self.content.frame.canvas.xview_moveto(0.0)
        if(self.content.frame.labelCanvas.xview() == (0.0,1.0)):
            self.content.frame.labelCanvas.xview_moveto(0.0)
            
    def scrollManualX(self,*args):
        print(args)
        point = float(args[1])
        self.content.frame.canvas.xview_moveto(point)
        self.content.frame.labelCanvas.xview_moveto(point)
    
        
    def createScrollTable(self):
        #frame creation
        self.content.frame = Frame(self.content, bd=2, relief='sunken')
        #scrollbar creation
        self.content.yscrollbar = Scrollbar(self.content)
        
        self.content.xscrollbar = Scrollbar(self.content,orient='horizontal')
        #scroll pack must be after buttons
        
        #labels
        self.content.frame.labelCanvas = Canvas(self.content.frame,highlightthickness=0, height = 18, bd= 1, scrollregion=(0, 0, 0, 0),xscrollcommand=self.content.xscrollbar.set)

        self.content.frame.labelCanvas.labelFrame = Frame(self.content.frame.labelCanvas)
        self.content.frame.labelCanvas.create_window((0,0),anchor='nw',window = self.content.frame.labelCanvas.labelFrame)

        
        self.content.frame.labelCanvas.pack(fill='x',side = 'top')

        #grid canvas
        self.content.frame.canvas = Canvas(self.content.frame,highlightthickness=0,bd= 0,  scrollregion=(0, 0, 0, 0),yscrollcommand=self.content.yscrollbar.set,xscrollcommand=self.content.xscrollbar.set)
        self.content.frame.canvas.pack(expand = 1,fill='both',side = 'top')
        #command scrollbars
        self.content.yscrollbar.config(command=self.content.frame.canvas.yview)        
        self.content.xscrollbar.config(command=self.scrollManualX)
        #xscrollbar.config(command=self.content.frame.labelCanvas.xview) 
        #create and add grid frame
        self.content.frame.canvas.gridFrame = Frame(self.content.frame.canvas)
        
        self.content.frame.canvas.create_window((0,0),anchor='nw',window = self.content.frame.canvas.gridFrame)
        
        
        #bind scroll bars
        self.content.frame.bind_all("<MouseWheel>",self.scrollMouseY)
        self.content.frame.bind_all("<Shift-MouseWheel>",self.scrollMouseX)
        
        #buttons

        self.content.buttonFrame = Frame(self.content)
        self.content.updateButton = Button(self.content.buttonFrame, text='Update',width=8)
        self.content.updateButton.grid(row=0, column=0)
        self.content.detailButton = Button(self.content.buttonFrame, text='Detail View',width=8)
        self.content.detailButton.grid(row=0, column=1)
        self.content.addButton = Button(self.content.buttonFrame, text='Add',width=8)
        self.content.addButton.grid(row=0, column=2)
        self.content.buttonFrame.pack(side='bottom')
        self.content.xscrollbar.pack(side = 'bottom',fill = 'x')
        self.content.yscrollbar.pack(side = 'right',fill = 'y')
        #insert the new frame last so the buttons can be in the bottom
        self.content.frame.pack(side = 'right', expand = 1,fill = 'both')
        return self.content.frame

    def addFakeEntries(self):
        for x in range(20):
            headerLabel = Label(self.content.frame.labelCanvas.labelFrame,text='testtesttesttesttest'+str(x),relief="raised",borderwidth=1,anchor='w',justify = 'left')
            headerLabel.grid(column=x,row=0,sticky='wens')
        for x in range(20):
            for i in range(100):
                label = Label(self.content.frame.canvas.gridFrame,text=str(i+(40*x*x)+10000),anchor='w',justify = 'left',borderwidth=1, relief="ridge")
                label.grid(row=i,column = x,sticky='wens')
        
    
        
        self.update()
        #compare min widths of label and content and set sizes to higher one
        for x in range(20):
            headerWidth = self.content.frame.labelCanvas.labelFrame.grid_bbox(x,0)[2]
            contentWidth = self.content.frame.canvas.gridFrame.grid_bbox(x,0)[2]
            if(headerWidth>contentWidth):
                self.content.frame.canvas.gridFrame.grid_columnconfigure(x,minsize = headerWidth)
            else:
                self.content.frame.labelCanvas.labelFrame.grid_columnconfigure(x,minsize = contentWidth)
                
        self.update()
        height = self.content.frame.canvas.gridFrame.winfo_height()
        width = self.content.frame.canvas.gridFrame.winfo_width()
        
        self.content.frame.canvas.config(scrollregion=(0, 0, width, height))
        self.content.frame.labelCanvas.config(scrollregion=(0, 0, width, 0))

    #highlight 
    def callback(self,e):
       
        #the first entry does not have a number at the end so there must be an exception made
        widgetID = 1
        #This is used to count backwords from the string
        stringCount = 1
        while str(e)[-stringCount:].isnumeric():
            widgetID = int(str(e)[-stringCount:])
            stringCount+=1
            if(stringCount > 100):
                break
        #changet widget color to yellow
        #keycount is one more than the number of keys that actually exist 
        trueKC = self.content.keyCount-1

        row = int((widgetID-1)/trueKC)
        column = ((widgetID-1)%trueKC)+1

        grid =self.content.frame.canvas.gridFrame.grid_slaves()
        cellCount = len(grid)
        #print('grid cell count: ' + str(cellCount))
        #since 0 is invalid i will have to subtract 1 to it if it is 0
        
        cellID = cellCount-widgetID
        #if its negative 1 then that means its one its first wave during creations
        if cellID !=-1 :
            cell =grid[cellID]
            cell.config(bg = 'yellow')
            self.content.editMarks[row] = True
            print(str(self.content.editMarks.keys()))
        
        
       
        return True

        
    def addEntries(self,docs):
        #returns true or false if it found docs to display
        try:
            self.content.keyCount = len(docs[0].keys())
        except IndexError:
            return False
        keyDict = dict()
        self.content.deletionMarks = {}
        self.content.editMarks = {}
        deleteLabel = Label(self.content.frame.labelCanvas.labelFrame,text='Delete',relief="raised",borderwidth=1,anchor='w',justify = 'left')
        deleteLabel.grid(column=0,row=0,sticky='wens')
        for i in range(1,self.content.keyCount):
            s = list(docs[0])[i]
            keyDict[i] = s
            headerLabel = Label(self.content.frame.labelCanvas.labelFrame,text=s,relief="raised",borderwidth=1,anchor='w',justify = 'left')
            headerLabel.grid(column=i,row=0,sticky='wens')
        #cant use d to traverse doc list so im gonna use x as a counter
        x = -1
        for d in docs:
            x+=1
            
            for i in range(1,self.content.keyCount):
                e = d[keyDict[i]]
                
                
                #v = self.register(self.callback) self.highlightValidate
                entry = Entry(self.content.frame.canvas.gridFrame,justify = 'left',width = len(str(e)),validate='key',validatecommand=self.highlightValidate)
                entry.insert('end',e)
                entry.grid(row=x,column = i,sticky='wens')
                #entry.config(bg='white')
        docsCount = x
        #check boxes
        self.content.check = dict()
        for x in range(0,docsCount+1):
            self.content.check[x] = IntVar()
            deleteCheck = Checkbutton(self.content.frame.canvas.gridFrame,variable = self.content.check[x])
            deleteCheck.grid(column=0,row=x,sticky='wens')
        
        #format the table
        self.update()
        #compare min widths of label and content and set sizes to higher one
        
        for x in range(0,self.content.keyCount):
            headerWidth = self.content.frame.labelCanvas.labelFrame.grid_bbox(x,0)[2]
            contentWidth = self.content.frame.canvas.gridFrame.grid_bbox(x,0)[2]
            if(headerWidth>contentWidth):
                self.content.frame.canvas.gridFrame.grid_columnconfigure(x,minsize = headerWidth)
            else:
                self.content.frame.labelCanvas.labelFrame.grid_columnconfigure(x,minsize = contentWidth)

        self.calibrateScrollbars()
        return True
    def calibrateScrollbars(self):
        self.update()
        height = self.content.frame.canvas.gridFrame.winfo_height()
        width = self.content.frame.canvas.gridFrame.winfo_width()
        print(str('height: ')+ str(height))
        print('width: '+ str(width))
        self.content.frame.canvas.config(scrollregion=(0, 0, width, height))
        self.content.frame.labelCanvas.config(scrollregion=(0, 0, width, 0))

        
    def updateButton(self,case):
        #calculate number of updates and prompt for update
        print('update')
        grid =self.content.frame.canvas.gridFrame
        size = self.content.frame.canvas.gridFrame.grid_size()[1]
        deleteCount = 0
        editCount = 0
        deleteDict = dict()
        editDict = dict()
        
        x = 0
        ID = grid.grid_slaves(column = 1)
        
        for i in grid.grid_slaves(column = 0):
            check = int(self.content.check[x].get())
            #grid slaves returns the list backwords
            target = len(ID)-x-1
            IDtoDelete = int(ID[target].get())
           
            if check == 1:
                deleteDict[IDtoDelete]= True
                deleteCount+=1
            else:
                deleteDict[IDtoDelete]= False

            x+=1
        print('deletedict '+str(deleteDict))
        #compares edit marks to delete marks to get a corrected value byt removing edits that are also being deleted
        for i in self.content.editMarks.keys():
            print(str(i))
            try:
                if deleteDict[i] == False:
                    editDict[i] = True
                    editCount +=1
                else:
                    editDict[i] = False
            except KeyError:
                #if its not found then it can just be false
                editDict[i] = False
                print('key not found')
                

        editsMessage = 'Edits: ' + str(editCount)+'\n'
        deletesMessage = 'Deletes: ' + str(deleteCount)+'\n'

        self.content.top = Toplevel(self.content)
    
        self.content.top.title("Confirm data operation")
        msg = Message(self.content.top, text='Confirm you are ready to perform the operation on the database\n'+editsMessage+deletesMessage,justify = 'center')
        msg.grid(column=1,row=0)
        confirm = Button(self.content.top, text="Confirm", command= lambda: self.sendDBOperation(case,deleteDict,editDict))
        confirm.grid(column=0,row=1)
        cancel = Button(self.content.top, text="Cancel", command=self.content.top.destroy)
        cancel.grid(column=2,row=1)

    def sendDBOperation(self,case, deleteDict,editDict):
        grid =self.content.frame.canvas.gridFrame
        size = self.content.frame.canvas.gridFrame.grid_size()
        success = True
        editValues=dict()
        for x in editDict.keys():
            if editDict[x]:
                editMonster = dict()
                for i in range(1,size[0]):
                    result = grid.grid_slaves(row = x,column = i)[0].get()
                    print (result)
                    editValues[i] = result
                    print('entry: '+str(editMonster))


                dbResult = ''
                if case == 0:
                    print('monsters')
                    dbResult = DBeditMonster (editValues[2], editValues[3], editValues[4], editValues[5],editValues[1])
                elif case == 1:
                    print('flavors')
                    dbResult = DBeditFlavor (editValues[2], editValues[3], editValues[1])
                elif case == 2:
                    print('arenas')
                    dbResult = DBeditArena (editValues[2], editValues[3], editValues[4], editValues[5],editValues[6],editValues[7],editValues[8],editValues[1])
                elif case == 3:
                    print('users')   
                if dbResult != None:
                    success = False
                    print(dbResult)
                    top = Toplevel()
                    top.title("Operation failed")

                    msg = Message(top, text='Database operation stopped\n'+dbResult,justify='center')
                    msg.pack()

                    button = Button(top, text="Dismiss", command=top.destroy)
                    button.pack()
        print(deleteDict.keys())
        print(deleteDict)
        #deletions must be done in order from smallest to largest
        # i dont feel like sorting so im just gonna subtract 1 since each call of the deletefunction
        #shifts higher ids by 1
        deleteCount = 0
        for x in deleteDict.keys():
           
            if deleteDict[x]:
                if case == 0:
                    print('monsters')
                    print('deleting monster'+str(x))
                    dbResult = DBdeleteMonster(int(x-deleteCount))
                    deleteCount+=1
                elif case == 1:
                    print('flavors')
                    dbResult = DBdeleteFlavor(int(x-deleteCount))
                    deleteCount+=1
                elif case == 2:
                    print('arenas')
                    dbResult = DBdeleteArena(int(x-deleteCount))
                    deleteCount+=1
                elif case == 3:
                    print('users')  
                
                if dbResult != None:
                    success = False
                    print(dbResult)
                    top = Toplevel()
                    top.title("Operation failed")

                    msg = Message(top, text='Database operation stopped\n'+dbResult,justify='center')
                    msg.pack()

                    button = Button(top, text="Dismiss", command=top.destroy)
                    button.pack()
                
        if (success):           
            top = Toplevel()
            top.title("Operation complete")

            msg = Message(top, text='The operation was completed successfully',justify='center')
            msg.pack()

            button = Button(top, text="Dismiss", command=top.destroy)
            button.pack()
            
        
        self.content.top.destroy()
        self.monsterDisplay()
    def clearContent(self):
        
        self.content.destroy()
        self.content = Frame(self)
        self.content.pack(expand = 1,fill='both')
        #for Widget in self.content.winfo_children():
            #Widget.pack_forget()









class connections():
    mongoConnection = False


def connectionError():
    return 'Operation failed please check your network connection, the server connection, and ensure that your mongoDB credentials were entered correctly'
def getEndOfFile(s):
    f = open(s,'r')
    f.readlines()
    eof = f.tell()
    file.close()
    # could probably use the seek method instead
    return eof

def confirm(message):
    
    userInput = input(message).lower()
    if(userInput == "y" or userInput == "yes"):
        print("Action confirmed")
        return True
    else:
        print("Action cancelled")
        return False
def updateSettings():
    try:
        file = open('settings.txt','w')
    except FileNotFoundError:
        file = open('settings.txt', 'w+')
    
        
    if guiCheck:
        try:
            updateDBrefGUI()
        except :
            print('just ignore it so you can still write settings to file')
    else:
        updateDBref()
    
    file.write(settings.botToken+'\n'+settings.mongo+'\n'+settings.DBname+'\n'+settings.spawnChannel+'\n'+settings.arenaChannel+'\n')

def updateDBref():
    print("Updating database references")
    mongoException = True
    DBException = True
    while (mongoException):
        print('mongo exception')
        try:
            settings.mongoDB = pymongo.MongoClient(settings.mongo)
            mongoException = False
        except pymongo.errors.ConfigurationError:
            if guiCheck:
                
                print('Connection Failure Ensure a connection to the MongoDB and restart the program')
                return
            else:
                settings.mongo = input('ConfigurationError Please enter the mongoDB credentials\n')
            updateSettings()
    while (DBException):
        print('mongo exception')
        try:
            settings.db = settings.mongoDB[settings.DBname]
            DBException = False
        except pymongo.errors.InvalidName:
            if guiCheck:
                
                print('Connection Failure Ensure a connection to the MongoDB and restart the program')
                return
            else:
                settings.DBname = input('Invalid Name Error Please enter the database name\n')
            updateSettings()
            
    settings.flavors = settings.db.flavors
    settings.users = settings.db.users
    settings.monsters = settings.db.monsters
    settings.arenas = settings.db.arenas
    
def updateDBrefGUI():
    print('updateDBrefGUI')
    settings.mongoDB = pymongo.MongoClient(settings.mongo)
    settings.db = settings.mongoDB[settings.DBname]
    settings.flavors = settings.db.flavors
    settings.users = settings.db.users
    settings.monsters = settings.db.monsters
    settings.arenas = settings.db.arenas

    
def getIntArgs(s):
    arg = ''.join(char for char in s if char.isdigit())
    if(arg.isnumeric()):
        return int(arg)
    return "c"
def getIntInputC(message): # can return cancel to check if the user changed their mind 
    
    while (True): 
        i = input(message+" Type !cancel to cancel\n")
        if(i.lower() == "!cancel"):
            return "c"
        if(i.isnumeric()):
            return int(i)
        print("Invalid input")
def inputConfirm(message):
    while(True):
        i = input(message).lower()
        if(i == "yes" or i == "y"):
            return True
        if(i == "no"or i == "n"):
            return False
        print("Invalid input")
        
def getToken():
    return settings.botToken

def getMongo():
    return settings.mongo

def getEChannel():
    return settings.spawnChannel

def getBChannel():
    return settings.arenaChannel

def getFlavor(n):
    if (not isinstance(n, int)):
        return "invalid arguement"
    s = ""
    try:
        doc = settings.flavors.find_one({"id":n})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    if(doc == None):
        return "No flavor with that ID found"
    s = s+"ID: "+ str(doc['id'])+"\n"+"Type:"+ str(doc['type'])+"\n"+"Text:"+doc['text']+"\n"
    return s


def getFlavorType(n):
    if (not isinstance(n, int)):
        return "invalid arguement"
    s = ""
    try:
        for doc in settings.flavors.find({'type':n}):
            s = s+"ID: "+ str(doc['id'])+"\n"+"Type:"+ str(doc['type'])+"\n"+"Text:"+doc['text']+"\n"
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
            
    if (s == ""):
        return "No flavors found" 
    return s


def getFlavors():
    s = ""
    try:
        for doc in settings.flavors.find():
            s = s+"ID: "+ str(doc['id'])+"\n"+"Type:"+ str(doc['type'])+"\n"+"Text:"+doc['text']+"\n"
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    if (s == ""):
        return "No flavors found"
    return s

def newFlavor():
    flavorType = getIntInputC("Enter a number for the type. ")
    if (not isinstance(flavorType, int)):
        return "New flavor entry cancelled"
    flavorText = input("Input the flavor text\n")
    if (flavorText == "!cancel"):
        return "New flavor entry cancelled"
    
    print("The following Document will be added")
    print("ID: "+str(settings.flavors.count()))
    print("Type: "+str(flavorType))
    print("Text: "+flavorText)
    
    if(inputConfirm("Are you sure you want to continue? Y/N\n")):
        DBnewFlavor(flavorType, flavorText)
        return"The document was added"
        #Might want to look up a validation method for failed documents.
    return "New flavor entry cancelled"

def deleteFlavor(n):
    #validate arguement
    if (not isinstance(n, int)):
        return "invalid arguement"
    #check if doc exists
    s = getFlavor(n)
    if (s == "No flavor with that ID found"):
        return s
    #show the user the doc they are going to delete
    print("This is the flavor text you are going to delete")
    print(getFlavor(n))
    #confirm deletion
    if(inputConfirm("Are you sure you want to continue? Y/N\n")):
        DBdeleteFlavor(n)
        return "The document was deleted"
    return "The document was not deleted"

def editFlavor(n):
    #validate arguement
    if (not isinstance(n, int)):
        return "invalid arguement"
    #check if doc exists
    s = getFlavor(n)
    if (s == "No flavor with that ID found"):
        return s
    #show the user the doc they are going to edit
    print("This is the flavor text you are going to edit")
    print(getFlavor(n))
    #ask for input
    print("which attribute do you wish to edit")
    print("type - 1")
    print("text - 2")
    flavorDoc = settings.flavors.find_one({"id":n})
    flavorType = flavorDoc['type']
    flavorText = flavorDoc['text']
    while(True):
        selection = input("Enter the number of the attribute you wish to edit or !cancel to cancel\n")
        if (selection == '1'):
            flavorType = getIntInputC("Enter a number for the type. ")
            
            if (not isinstance(flavorType, int)):
               return "Edit flavor entry cancelled"
            break
        if (selection == '2'):
            flavorText = input("Input the flavor text or !cancel to cancel\n")
            
            if (flavorText == "!cancel"):
                return "Edit flavor entry cancelled"
            break
        if (selection == '!cancel'):
            return "Edit flavor entry cancelled"
        print("invalid input")
        
    
    
    
    #Show user the new document and confirm
    print("The edited document will now look like this")
    print("ID: "+str(n))
    print("Type: "+str(flavorType))
    print("Text: "+flavorText)
    
    if(inputConfirm("Are you sure you want to continue? Y/N\n")):
        DBeditFlavor(flavorType, flavorText,n)
        return"The document was edited"
        #Might want to look up a validation method for failed documents.
    return "Edit flavor entry cancelled"

def downloadFlavors():
    #ask for file name
    s = input("What will the file be called? A .txt extension will be given to it. Type !cancel to cancel\n")
    if(s=="!cancel"):
        return "File download was canceled"
    s = s +".txt"
    
    #check if file exists
    if(os.path.isfile(s)):
        if(not inputConfirm(s+" already exists. Overwrite? \n")):
            return "File download was canceled"
    return DBdownloadFlavors(s)

def DBdownloadFlavors(s):   
    f = open(s, 'w+')
    
    try:    
        for doc in settings.flavors.find():
            f.write(str(doc['type'])+'\n')
            f.write(str(doc['text'])+'\n')
        f.close()
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    return "File was downloaded"

def validateFlavorPack(filename):
    #flavor packs should have one string that can be converted to an int and
    #followed by a string
    try:
        f = open(filename, 'r')
    except FileNotFoundError:
        print("File could not be found")
        return False
    boolReturn = True
    eof = getEndOfFile(filename)
    
    lineCount = 0
    while (f.tell()!=eof and boolReturn):
        #should be able to convert first line to int with no issue then read one more line
        lineCount +=1
        try:
            lineOne = (f.readline()[:-1])
        except:
            boolReturn = False
            print("line "+str(lineCount)+ " could not be read as int")
        #since there must be an even number of lines if the eof is reached it is invalid
        if (f.tell() == eof):
            boolReturn = False
            print("End of file reached prematurely. There should be an even number of lines. One for an int followed by a string.")
        #read next line
        lineCount +=1
        f.readline()
    f.close()
    return boolReturn


        
def uploadFlavorPack(filename):
    # validate
    if(validateFlavorPack(filename) and inputConfirm("You are about to upload the whole pack into your database. Are you sure you want to continue?")):
        return DBuploadFlavorPack(filename)
    return "Upload cancelled"

def DBuploadFlavorPack(filename):
    eof = getEndOfFile(filename)
    f = open(filename,"r")
       
    while (f.tell()!=eof):
        DBnewFlavor(int(f.readline().strip("\n")),f.readline().strip("\n"))
    f.close()
        
    return "Upload completed"


def getFlavorDoc(i):
    return settings.flavors.find_one({'id':i})
def getFlavorDocs():
    return settings.flavors.find()

def DBnewFlavor(flavorType, flavorText):
    newID = settings.flavors.count()
    try:
        settings.flavors.insert_one({'id':newID, 'type':flavorType ,'text':flavorText})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()

def DBdeleteFlavor(n):
    try:
        settings.flavors.delete_one({'id':n})
        #update the IDs of flavors above
        settings.flavors.update_many({ 'id': { '$gt': n } },{'$inc':{'id':-1}})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
                

    
def DBeditFlavor (flavorType, flavorText,n):
    try:
        settings.flavors.find_and_modify(query={'id':n},update={'id':n,'type':flavorType ,'text':flavorText})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()

def parseHalignment(n):
    #this method is used to parse a horizontal arguement for the arena from number to word
    if (n == 0):
        return "Left"
    elif (n == -1):
        return "Right"
    else:
        return "Center"

def parseHalignmentInput(n):
    #this method is used to alignment words into a number for setting alignment
    
    while(True):
        i = input(n+"\n").lower()
        if (i == "left"):
            return 0
        elif (i == "center"):
            return -.5
        elif (i == "right"):
            return -1
        elif (i == "!cancel"):
            return "!cancel"
        print("Invalid response. Please input left, center, right or cancel\n")
def parseValignment(n):
    #this method is used to parse a horizontal arguement for the arena from number to word
    if (n == 0):
        return "Top"
    elif (n == -1):
        return "Bottom"
    else:
        return "Center"

def parseValignmentInput(n):
    #this method is used to alignment words into a number for setting alignment
    
    while(True):
        i = input(n+"\n").lower()
        if (i == "top"):
            return 0
        elif (i == "center"):
            return -.5
        elif (i == "bottom"):
            return -1
        elif (i == "!cancel"):
            return "!cancel"
        print("Invalid response. Please input top, center, bottom or cancel\n")
              

def getArena(n):
    if (not isinstance(n, int)):
        return "invalid arguement"
    s = ""
    try:
        doc = settings.arenas.find_one({"id":n})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    if(doc == None):
        return "No arena with that ID found"
    s = s+"ID: "+ str(doc['id'])+"\n"+"x1:"+ str(doc['x1'])+"\n"+"y1:"+str(doc['y1'])+"\n"+"x2:"+str(doc['x2'])+"\n"+"y2:"+str(doc['y2'])+"\n"
    s = s+"Horizontal alignment: "+ parseHalignment(doc['halign'])+"\n"
    s = s+"Vertical alignment: "+ parseValignment(doc['valign'])+"\n"
    s = s+"Url: "+ str(doc['arenaImage'])+"\n"
    return s



def getArenas():
    s = ""
    try:
        for doc in settings.arenas.find():
            s = s+"ID: "+ str(doc['id'])+"\n"+"x1:"+ str(doc['x1'])+"\n"+"y1:"+str(doc['y1'])+"\n"+"x2:"+str(doc['x2'])+"\n"+"y2:"+str(doc['y2'])+"\n"
            s = s+"Horizontal alignment: "+ parseHalignment(doc['halign'])+"\n"
            s = s+"Vertical alignment: "+ parseValignment(doc['valign'])+"\n"
            s = s+"Url: "+ str(doc['arenaImage'])+"\n"
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    if (s == ""):
        return "No arenas found"
    return s

def newArena():
    x1 = getIntInputC("Enter a number for the x coordinate of player 1. ")
    if (not isinstance(x1, int)):
        return "New arena entry cancelled"
    y1 = getIntInputC("Enter a number for the y coordinate of player 1. ")
    if (not isinstance(y1, int)):
        return "New arena entry cancelled"
    x2 = getIntInputC("Enter a number for the x coordinate of player 2. ")
    if (not isinstance(x2, int)):
        return "New arena entry cancelled"
    y2 = getIntInputC("Enter a number for the y coordinate of player 2. ")
    if (not isinstance(y2, int)):
        return "New arena entry cancelled"

    halign = parseHalignmentInput("Enter left center or right for the horizontal alignment")
    if (isinstance(halign, str)):
        return "New arena entry cancelled"

    valign = parseValignmentInput("Enter top center or bottom for the vertical alignment")
    if (isinstance(valign, str)):
        return "New arena entry cancelled"
    
    arenaImage = input("Input the image url\n")
    if (arenaImage == "!cancel"):
        return "New arena entry cancelled"
    
    print("The following Document will be added")
    print("ID: "+str(settings.arenas.count()))
    print("x1: "+str(x1))
    print("y1: "+str(y1))
    print("x2: "+str(x2))
    print("y2: "+str(y2))
    print("Horizontal Alignment: "+parseHalignment(halign))
    print("Horizontal Alignment: "+parseValignment(valign))
    print("ArenaImage: "+arenaImage)
    
    if(inputConfirm("Are you sure you want to continue? Y/N\n")):
        DBnewArena(x1,y1,x2,y2,halign,valign,arenaImage)
        return"The document was added"
        #Might want to look up a validation method for failed documents.
    return "New arena entry cancelled"

def deleteArena(n):
    #validate arguement
    if (not isinstance(n, int)):
        return "invalid arguement"
    #check if doc exists
    s = getArena(n)
    if (s == "No arena with that ID found"):
        return s
    #show the user the doc they are going to delete
    print("This is the arena you are going to delete")
    print(getArena(n))
    #confirm deletion
    if(inputConfirm("Are you sure you want to continue? Y/N\n")):
        DBdeleteArena(n)
        return "The document was deleted"
    return "The document was not deleted"

def editArena(n):
    #validate arguement
    if (not isinstance(n, int)):
        return "invalid arguement"
    #check if doc exists
    s = getArena(n)
    if (s == "No arena with that ID found"):
        return s
    #show the user the doc they are going to edit
    print("This is the arena you are going to edit")
    print(getArena(n))
    #ask for input
    print("which attribute do you wish to edit")
    print("x1 - 1")
    print("y1 - 2")
    print("x2 - 3")
    print("y2 - 4")
    print("horizontal alignment - 5")
    print("vertical alignment - 6")
    print("arena image - 7")
    arenaDoc = settings.arenas.find_one({"id":n})
    x1 = arenaDoc['x1']
    y1 = arenaDoc['y1']
    x2 = arenaDoc['x2']
    y2 = arenaDoc['y2']
    halign = arenaDoc['halign']
    valign = arenaDoc['valign']
    arenaImage = arenaDoc['arenaImage']
              
    
    while(True):
        selection = input("Enter the number of the attribute you wish to edit or !cancel to cancel\n")
        if (selection == '1'):
            x1 = getIntInputC("Enter a number for the x coordinate of player 1. ")
            if (not isinstance(x1, int)):
                return "New arena entry cancelled"
            break
        if (selection == '2'):
            y1 = getIntInputC("Enter a number for the y coordinate of player 1. ")
            if (not isinstance(y1, int)):
                return "New arena entry cancelled"
            break
        if (selection == '3'):
            x2 = getIntInputC("Enter a number for the x coordinate of player 2. ")
            if (not isinstance(x2, int)):
                return "New arena entry cancelled"
            break
        if (selection == '4'):
            y2 = getIntInputC("Enter a number for the y coordinate of player 2. ")
            if (not isinstance(y2, int)):
                return "New arena entry cancelled"
            break
        if (selection == '5'):
            halign = parseHalignmentInput("Enter left center or right for the horizontal alignment")
            if (isinstance(halign, str)):
                return "New arena entry cancelled"
            break
        if (selection == '6'):
            valign = parseValignmentInput("Enter top center or bottom for the vertical alignment")
            if (isinstance(valign, str)):
                return "New arena entry cancelled"
            break
        if (selection == '7'):
            arenaImage = input("Input the image url\n")
            if (arenaImage == "!cancel"):
                return "New arena entry cancelled"
            break
        if (selection == '!cancel'):
            return "Edit Arena entry cancelled"
        print("invalid input")
        
    
    
    
    #Show user the new document and confirm
    print("The edited document will now look like this")
    print("ID: "+str(n))
    print("x1: "+str(x1))
    print("y1: "+str(y1))
    print("x2: "+str(x2))
    print("y2: "+str(y2))
    print("Horizontal Alignment: "+parseHalignment(halign))
    print("Horizontal Alignment: "+parseValignment(valign))
    print("ArenaImage: "+arenaImage)
    
    if(inputConfirm("Are you sure you want to continue? Y/N\n")):
        DBeditArena(x1,y1,x2,y2,halign,valign,arenaImage,n)
        return"The document was edited"
        #Might want to look up a validation method for failed documents.
    return "Edit arena entry cancelled"

def downloadArenas():
    #ask for file name
    s = input("What will the file be called? A .txt extension will be given to it. Type !cancel to cancel\n")
    if(s=="!cancel"):
        return "File download was canceled"
    s = s +".txt"
    
    #check if file exists
    if(os.path.isfile(s)):
        if(not inputConfirm(s+" already exists. Overwrite? \n")):
            return "File download was canceled"
    
    return DBdownloadArenas(s)    

def DBdownloadArenas(s):
    f = open(s, 'w+')
    try:
        for doc in settings.arenas.find():
            x1 = doc['x1']
            y1 = doc['y1']
            x2 = doc['x2']
            y2 = doc['y2']
            halign = doc['halign']
            valign = doc['valign']
            arenaImage = doc['arenaImage']
                  
            f.write(str(x1)+'\n')
            f.write(str(y1)+'\n')
            f.write(str(x2)+'\n')
            f.write(str(y2)+'\n')
            f.write(str(halign)+'\n')
            f.write(str(valign)+'\n')
            f.write(str(arenaImage)+'\n')
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    f.close()
    return "File was downloaded"

def validateArenaPack(filename):
    
    try:
        f = open(filename, 'r')
    except FileNotFoundError:
        print("File could not be found")
        return False
    boolReturn = True
    eof = getEndOfFile(filename)
    
    lineCount = 0
    while (f.tell()!=eof and boolReturn):
        #should be able to convert 4 lines to int then 2 to float with no issue 
        for x in range(0, 4):
            lineCount +=1
            try:
                lineOne = int(f.readline()[:-1])
            except:
                boolReturn = False
                print("line "+str(lineCount)+ " could not be read as int")
        for x in range(0, 2):
            lineCount +=1
            try:
                lineOne = float(f.readline()[:-1])
            except:
                boolReturn = False
                print("line "+str(lineCount)+ " could not be read as int")
        #since there must be a string after the previous 6 lines if the eof is reached it is invalid
        if (f.tell() == eof):
            boolReturn = False
            print("End of file reached prematurely. There is an incorrect number of lines. It should be diviisable by 7.")
        #read next line
        lineCount +=1
        f.readline()
    f.close()
    return boolReturn


        
def uploadArenaPack(filename):
    # validate
    if(validateArenaPack(filename) and inputConfirm("You are about to upload the whole pack into your database. Are you sure you want to continue?")):
        return DBuploadArenaPack(filename)
    return "Upload cancelled"

def DBuploadArenaPack(filename):
    eof = getEndOfFile(filename)
    f = open(filename,"r")
    while (f.tell()!=eof):
        DBnewArena(int(f.readline().strip("\n")),int(f.readline().strip("\n")),int(f.readline().strip("\n")),int(f.readline().strip("\n")),float(f.readline().strip("\n")),float(f.readline().strip("\n")),f.readline().strip("\n"))
    f.close()
    return "Upload completed"
    

def getArenaDoc(i):
    return settings.arenas.find_one({'id':i})
def getArenaDocs():
    return settings.arenas.find()
    

def DBnewArena(x1,y1,x2,y2,halign,valign,arenaImage):
    try:
        newID = settings.arenas.count()
        settings.arenas.insert_one({'id':newID,'x1':x1 ,'y1':y1,'x2':x2,'y2':y2,'halign':halign,'valign':valign,'arenaImage':arenaImage})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()

def DBdeleteArena(n):
    try:
        settings.arenas.delete_one({'id':n})
        #update the IDs of arena above
        settings.arenas.update_many({ 'id': { '$gt': n } },{'$inc':{'id':-1}})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
            

    
def DBeditArena (x1,y1,x2,y2,halign,valign,arenaImage,n):
    try:
        settings.arenas.find_and_modify(query={'id':n},update={'id':n,'x1':x1 ,'y1':y1,'x2':x2,'y2':y2,'halign':halign,'valign':valign,'arenaImage':arenaImage})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()





def getMonster(n):
    s = ""
    try:
        doc = settings.monsters.find_one({"monsterID":n})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    
    if(doc == None):
        return "No monster found"
    s = s+"ID: "+ str(doc['monsterID'])+"\n"+"Name:"+doc['name']+"\n"+"Description: "+doc['description']+"\n"+"Rarity:"+ str(doc['rarity'])+"\n"+"Image url:"+doc['monsterImage']+"\n"
    return s
def getMonsterRarity(n):
    s = ""
    try:
        for doc in settings.monsters.find({'rarity':n}):
            s = s+"ID: "+ str(doc['monsterID'])+"\n"+"Name:"+doc['name']+"\n"+"Description: "+doc['description']+"\n"+"Rarity:"+ str(doc['rarity'])+"\n"+"Image url:"+doc['monsterImage']+"\n"
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    if (s == ""):
        return "No monsters found"
    return s
def getMonsters():
    s = ""
    try:
        for doc in settings.monsters.find():
            s = s+"ID: "+ str(doc['monsterID'])+"\n"+"Name:"+doc['name']+"\n"+"Description: "+doc['description']+"\n"+"Rarity:"+ str(doc['rarity'])+"\n"+"Image url:"+doc['monsterImage']+"\n"
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    if (s == ""):
        return "No monsters found"
    return s

def newMonster():
    monsterName = input("Input the monster name\n")
    if (monsterName == "!cancel"):
        return "New monster entry cancelled"
    monsterRarity = getIntInputC("Enter a number for the rarity. ")
    if (not isinstance(monsterRarity, int)):
        return "New monster entry cancelled"
    monsterDesc = input("Input the monster description\n")
    if (monsterDesc == "!cancel"):
        return "New monster entry cancelled"
    monsterImage = input("Input the image url\n")
    if (monsterImage == "!cancel"):
        return "New monster entry cancelled"
    
    print("The following Document will be added")
    print("ID: "+str(settings.monsters.count()+1))
    print("Name: "+monsterName)
    print("Rarity: "+str(monsterRarity))
    print("Description: "+monsterDesc)
    print("Image: "+monsterImage)
    
    if(inputConfirm("Are you sure you want to continue? Y/N\n")):
        DBnewMonster(monsterName, monsterRarity, monsterDesc, monsterImage)
        return"The document was added"
        #Might want to look up a validation method for failed documents.
    return "New monster entry cancelled"

def deleteMonster(n):
    #validate arguement
    if (not isinstance(n, int)):
        return "invalid arguement"
    #check if doc exists
    s = getMonster(n)
    if (s == "No monster with that ID found"):
        return s
    #show the user the doc they are going to delete
    print("This is the monster you are going to delete")
    print(getMonster(n))
    #confirm deletion
    if(inputConfirm("Are you sure you want to continue? Y/N\n")):
        DBdeleteMonster(n)
        return "The document was deleted"
    return "The document was not deleted"

def editMonster(n):
    #validate arguement
    if (not isinstance(n, int)):
        return "invalid arguement"
    #check if doc exists
    s = getMonster(n)
    if (s == "No monster with that ID found"):
        return s
    #show the user the doc they are going to edit
    print("This is the monster you are going to edit")
    print(getMonster(n))
    #ask for input
    print("which attribute do you wish to edit")
    print("name - 1")
    print("rarity - 2")
    print("description - 3")
    print("image - 4")
    monsterDoc = settings.monsters.find_one({"monsterID":n})
    monsterName = monsterDoc['name']
    monsterRarity = monsterDoc['rarity']
    monsterDesc = monsterDoc['description']
    monsterImage = monsterDoc['monsterImage']
    
    while(True):
        selection = input("Enter the number of the attribute you wish to edit or !cancel to cancel\n")
        if (selection == '1'):
            monsterName = input("Input the monster name or !cancel to cancel\n")
            
            if (monsterName == "!cancel"):
                return "Edit monster entry cancelled"
            break
        if (selection == '2'):
            monsterRarity = getIntInputC("Enter a number for the rarity. ")
            
            if (not isinstance(monsterRarity, int)):
               return "Edit monster entry cancelled"
            break
        if (selection == '3'):
            monsterDesc = input("Input the monster description or !cancel to cancel\n")
            
            if (monsterDesc == "!cancel"):
                return "Edit monster entry cancelled"
            break
        if (selection == '4'):
            monsterImage = input("Input the image url or !cancel to cancel\n")
            
            if (monsterImage == "!cancel"):
                return "Edit monster entry cancelled"
            break
        if (selection == '!cancel'):
            return "Edit monster entry cancelled"
        print("invalid input")
        
    
    
    
    #Show user the new document and confirm
    print("The edited document will now look like this")
    print("ID: "+str(n))
    print("Name: "+monsterName)
    print("Rarity: "+str(monsterRarity))
    print("Description: "+monsterDesc)
    print("Image: "+monsterImage)
    
    if(inputConfirm("Are you sure you want to continue? Y/N\n")):
        DBeditMonster(monsterName, monsterRarity, monsterDesc, monsterImage,n)
        return"The document was edited"
        #Might want to look up a validation method for failed documents.
    return "Edit monster entry cancelled"

def downloadMonsters():
    #ask for file name
    s = input("What will the file be called? A .txt extension will be given to it. Type !cancel to cancel\n")
    if(s=="!cancel"):
        return "File download was canceled"
    s = s +".txt"
    
    #check if file exists
    if(os.path.isfile(s)):
        if(not inputConfirm(s+" already exists. Overwrite? \n")):
            return "File download was canceled"
        
    return DBdownloadMonsters(s)

def DBdownloadMonsters(s):
    f = open(s, 'w+')
    
    try: 
        for doc in settings.monsters.find():
            f.write(str(doc['name'])+'\n')
            f.write(str(doc['rarity'])+'\n')
            f.write(str(doc['description'])+'\n')
            f.write(str(doc['monsterImage'])+'\n')
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    
    f.close()
    return "File was downloaded"

def downloadUsers():
    #ask for file name
    s = input("What will the file be called? A .txt extension will be given to it. Type !cancel to cancel\n")
    if(s=="!cancel"):
        return "File download was canceled"
    s = s +".txt"
    
    #check if file exists
    if(os.path.isfile(s)):
        if(not inputConfirm(s+" already exists. Overwrite? \n")):
            return "File download was canceled"
    return DBdownloadUsers(s)

def DBdownloadUsers(s):    
    f = open(s, 'w+')
    
    try: 
        for doc in settings.users.find():
            #print(str(doc))
            f.write(str(doc['userID'])+'\n')
            f.write(str(doc['collection'])+'\n')
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    
    f.close()
    return "File was downloaded"

def validateUserPack(filename):
    
    try:
        f = open(filename, 'r')
    except FileNotFoundError:
        print("File could not be found")
        return False
    boolReturn = True
    eof = getEndOfFile(filename)
    
    lineCount = 0
    while (f.tell()!=eof and boolReturn):
       
        
        #should be able to convert first line to int with no issue then read one more line
        
        try:
            lineCount +=1
            lineOne = (int(f.readline()[:-1]))
        except:
            boolReturn = False
            print("line "+str(lineCount)+ " could not be read as int")
        if (f.tell() == eof):
            boolReturn = False
            print("End of file reached prematurely. There should be a number of lines divisible by 2.")
       
        lineCount +=1
        f.readline()
    f.close()
    return boolReturn

def validateMonsterPack(filename):
    
    try:
        f = open(filename, 'r')
    except FileNotFoundError:
        print("File could not be found")
        return False
    boolReturn = True
    eof = getEndOfFile(filename)
    
    lineCount = 0
    while (f.tell()!=eof and boolReturn):
        #1st line check
        lineCount +=1
        f.readline()
        if (f.tell() == eof):
            boolReturn = False
            print("End of file reached prematurely. There should be a number of lines divisible by 4.")
        
        #should be able to convert first line to int with no issue then read one more line
        
        try:
            lineCount +=1
            lineOne = (int(f.readline()[:-1]))
        except:
            boolReturn = False
            print("line "+str(lineCount)+ " could not be read as int")
        #since there must be an even number of lines if the eof is reached it is invalid
        #3rd line
        lineCount +=1
        f.readline()
        if (f.tell() == eof):
            boolReturn = False
            print("End of file reached prematurely. There should be a number of lines divisible by 4.")
        #4th line
        lineCount +=1
        f.readline()
    f.close()
    return boolReturn


def uploadUserPack(filename):
    # validate
    if(validateUserPack(filename) and inputConfirm("You are about to upload the whole pack into your database. Are you sure you want to continue?")):
        return DBuploadUserPack(filename)
    return "Upload cancelled" 

def DBuploadUserPack(filename):
    eof = getEndOfFile(filename)
    f = open(filename,"r")
    while (f.tell()!=eof):
        settings.users.insert_one({'userID':int(f.readline().strip("\n")),'collection':eval(f.readline().strip("\n"))})
    f.close()
    return "Upload completed"

def uploadMonsterPack(filename):
    # validate
    if(validateMonsterPack(filename) and inputConfirm("You are about to upload the whole pack into your database. Are you sure you want to continue?")):
        return DBuploadMonsterPack(filename)
    return "Upload cancelled" 

def DBuploadMonsterPack(filename):
    eof = getEndOfFile(filename)
    f = open(filename,"r")
    while (f.tell()!=eof):
        DBnewMonster(f.readline().strip("\n"),int(f.readline().strip("\n")),f.readline().strip("\n"),f.readline().strip("\n"))
    f.close()
    return "Upload completed"


def getMonsterDoc(i):
    return settings.monsters.find_one({'monsterID':i})
def getMonsterDocs():
    return settings.monsters.find()


def DBnewMonster(monsterName, monsterRarity, monsterDesc, monsterImage):
    try:
        newID = settings.monsters.count()+1 #+1 because 0 is reserved to be empty
        settings.monsters.insert_one({'monsterID':newID,'name':monsterName ,'rarity':monsterRarity,'description':monsterDesc ,'monsterImage':monsterImage})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()

def DBdeleteMonster(n):
    try:
        settings.monsters.delete_one({'monsterID':n})
        #update the IDs of monsters above
        settings.monsters.update_many({ 'monsterID': { '$gt': n } },{'$inc':{'monsterID':-1}})
        # update the player ownership
        for doc in settings.users.find():
              
              col = doc['collection']
              
              newBools = []
              i = 0
              monsterID = n
              for x in col:
                  if (i != monsterID):
                    newBools.insert(i,x)
                    i+=1
                  else:
                    monsterID = -1
              
              settings.users.find_one_and_update({'userID' : doc['userID']},{'$set':{"collection":newBools } })
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()  
    
def DBeditMonster (monsterName, monsterRarity, monsterDesc, monsterImage,n):
    #validate
    #by default they all com in as strings if using the gui
    mn = isinstance(monsterName, str)
    try:
        monsterRarity = int(monsterRarity)
    except:
        return 'Operation failed at '+ str(n)+ ' monster rarity could not be converted to int'
    mr = isinstance(monsterRarity, int)
    md = isinstance(monsterDesc, str)
    mi = isinstance(monsterImage,str)
    try:
        n = int(n)
    except:
        return 'Operation failed at '+ str(n)+' monster id could not be converted to int'
    try:
        settings.monsters.find_and_modify(query={'monsterID':n},update={'monsterID':n,'name':monsterName ,'rarity':monsterRarity,'description':monsterDesc,'monsterImage':monsterImage})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()

def testArena():
    arenaChoice = getIntInputC('Input an arena to test')
    if (not isinstance(arenaChoice, int)):
        return 'Arena Test Cancelled'
    try:
        arenaDoc = settings.arenas.find_one({'id':arenaChoice})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    if (arenaDoc == None):
        return 'Arena not found'

    
    monsterOne = getIntInputC('Input a monster to test')
    if (not isinstance(monsterOne, int)):
        return 'Arena Test Cancelled'
    
    try:
        monsterOneDoc = settings.monsters.find_one({'monsterID':monsterOne})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    if (monsterOneDoc == None):
        return 'Monster not found'

    
    monsterTwo = getIntInputC('Input a monster to test')
    if (not isinstance(monsterTwo, int)):
        return 'Arena Test Cancelled'
    
    try:
        monsterTwoDoc = settings.monsters.find_one({'monsterID':monsterTwo})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    if (monsterTwoDoc == None):
        return 'Monster not found'




    arenaImageFile = urllib.request.urlopen(arenaDoc["arenaImage"])
    arenaImage = Image.open(arenaImageFile)
        
    monsterImage1 = getMonsterImage(monsterOne)
    monsterImage2 = getMonsterImage(monsterTwo)

    x1 = arenaDoc['x1']
    y1 = arenaDoc['y1']
    x2 = arenaDoc['x2']
    y2 = arenaDoc['y2']

    halign = arenaDoc['halign']
    valign = arenaDoc['valign']
    return compileArena(arenaImage,monsterImage1,monsterImage2,x1,y1,x2,y2,halign,valign)


def getMonsterImage(monsterID):
    print("Getting monster image ID: "+str(monsterID))
    try:
        monster = settings.monsters.find_one({'monsterID': monsterID})
    except pymongo.errors.ServerSelectionTimeoutError:
        return connectionError()
    i = urllib.request.urlopen(monster["monsterImage"])
    image = Image.open(i)
    return image

def compileArena (arena,monsterA,monsterB,xPos1,yPos1,xPos2,yPos2,halign,valign):
    
    print("compiling arena")
    A = monsterA.convert('RGBA')
    B = monsterB.convert('RGBA')
    B = ImageOps.mirror(B)
    arena = arena.convert('RGBA')
    
    #calculate offset coords
    xFinal1 = xPos1+(A.size[0]*halign)
    yFinal1 = yPos1+(A.size[1]*valign)
    xFinal2 = xPos2+(B.size[0]*halign)
    yFinal2 = yPos2+(B.size[1]*valign)
    #if it is too negative don't draw it
    draw1 = True
    draw2 = True
    #crop if the image is in the negatives
    if (xFinal1<0 or yFinal1<0):
        #check if the image is completely out of view 
        if(xFinal1<=-A.size[0]or yFinal1<=-A.size[1]):
            print('image OOB error')
            draw1 = False
        #crop it if it isn't
        else:
            print('cropping image')
            A = A.crop((abs(xFinal1),abs(yFinal1),A.size[0],A.size[1]))
            #set the negatives to 0 so it can draw properly
            if (xFinal1<0):
                print('Set x1 to 0')
                xFinal1 = 0
            if (yFinal1<0):
                print('Set y1 to 0')
                xFinal1 = 0
    #crop if the image is in the negatives
    if (xFinal2<0 or yFinal2<0):
        #check if the image is completely out of view 
        if(xFinal2<=-B.size[0]or yFinal2<=-B.size[1]):
            print('image OOB')
            draw2 = False
        #crop it if it isn't
        else:
            print('cropping image')
            B = B.crop((abs(xFinal2),abs(yFinal2),B.size[0],B.size[1]))
            #set the negatives to 0 so it can draw properly
            if (xFinal2<0):
                print('Set x2 to 0')
                xFinal2 = 0
            if (yFinal2<0):
                print('Set y2 to 0')
                xFinal2 = 0
    #composite = Image.composite(A, B,'RGBA')
    
    arena.alpha_composite(A, (int(xFinal1),int(yFinal1)))
    arena.alpha_composite(B, (int(xFinal2),int(yFinal2)))
    #arena.paste(monsterA,(150,100),composite)
    arena.save("arenaTest.png")
    return "Arena saved under arenaTest.png"

def compileArenaImage (arena,monsterA,monsterB,xPos1,yPos1,xPos2,yPos2,halign,valign):
    
    print("compiling arena")
    A = monsterA.convert('RGBA')
    B = monsterB.convert('RGBA')
    B = ImageOps.mirror(B)
    arena = arena.convert('RGBA')
    
    #calculate offset coords
    xFinal1 = xPos1+(A.size[0]*halign)
    yFinal1 = yPos1+(A.size[1]*valign)
    xFinal2 = xPos2+(B.size[0]*halign)
    yFinal2 = yPos2+(B.size[1]*valign)
    
    #final correction. If it is out of bounds bring it back in

    if xFinal1+A.size[0]>arena.size[0]:
        xFinal1 = arena.size[0]-A.size[0]
    if xFinal1 <0:
        xFinal1 = 0
        
    if yFinal1+A.size[1]>arena.size[1]:
        yFinal1 = arena.size[1]-A.size[1]
    if yFinal1 <0:
        yFinal1 = 0



    if xFinal2+B.size[0]>arena.size[0]:
        xFinal2 = arena.size[0]-B.size[0]
    if xFinal2 <0:
        xFinal2 = 0
        
    if yFinal2+B.size[1]>arena.size[1]:
        yFinal2 = arena.size[1]-B.size[1]
    if yFinal2 <0:
        yFinal2 = 0
    

    print('xFinal1: '+str(xFinal1))
    print('yFinal1: '+str(yFinal1))
    print('xFinal2: '+str(xFinal2))
    print('yFinal2: '+str(yFinal2))
    #composite = Image.composite(A, B,'RGBA')
    
    arena.alpha_composite(A, (int(xFinal1),int(yFinal1)))
    arena.alpha_composite(B, (int(xFinal2),int(yFinal2)))
    #arena.paste(monsterA,(150,100),composite)
    
    return arena

def alignText(left,right):
    print("{:<20s}{:>20s}".format(left,right))
def helpFunction():
    alignText('set all','use this to set the token, mongo login, database name, encounter channel and battle channel')
    return '\n'

def setAll():
    setToken(input('\nUpdate Bot Token \nCurrently: '+ settings.botToken+"\n"))
    setMongo(input('\nUpdate MongoDB login \nCurrently: '+ settings.mongo+"\n"))
    setDatabase(input('\nUpdate database name \nCurrently: '+settings.DBname+"\n"))
    setEChannel(input('\nUpdate Monster Encounter Channel \nCurrently: '+ settings.spawnChannel+"\n"))
    setBChannel(input('\nUpdate Monster Battle Channel \nCurrently: '+ settings.arenaChannel+"\n"))
    updateSettings()

    
def setToken(s):
    settings.botToken = s
    updateSettings()
    return settings.botToken

def setMongo(s):
    settings.mongo = s
    updateSettings()
    return settings.mongo
def setDatabase(s):
    settings.DBname = s
    updateSettings()
    return settings.mongo
def setEChannel(s):
    settings.spawnChannel = s
    updateSettings()
    return settings.spawnChannel

def setBChannel(s):
    settings.arenaChannel = s
    updateSettings()
    return settings.arenaChannel


# opening settings

settings.botToken = file.readline()[:-1]
settings.mongo = file.readline()[:-1]
settings.DBname = file.readline()[:-1]
settings.spawnChannel = file.readline()[:-1]
settings.arenaChannel = file.readline()[:-1]
file.close()
print('Current settings are.../n')
print('\nBot Token: \n'+ settings.botToken)
print('\nMongoDB login: \n'+ settings.mongo)
print('\nDatabase Name : \n'+ settings.DBname)
print('\nMonster Encounter Channel: \n'+ settings.spawnChannel)
print('\nMonster Battle Channel: \n'+ settings.arenaChannel)
if guiCheck:
    try:
        updateDBrefGUI()
    except AttributeError:
        print('internet error')
    except pymongo.errors.ConfigurationError:
        print('config error')
else:
    updateDBref()


print('\n-------\n')


def commandLineInterface():

    while(True):
        command = input('Awaiting command\n')
        command = command.lower()
        #setA;;
        if (command == 'set all'):
            print(setAll())
        #gets
        elif (command == 'get token'):
            print('\nBot Token: \n'+ settings.botToken)
        elif (command == 'get mongo'):
            print('\nMongoDB login: \n'+ settings.mongo)
        elif (command == 'get database'):
            print('\nMongoDB database: \n'+ settings.DBname)
        elif (command == 'get e channel'):
            print('\nMonster Encounter Channel: \n'+ settings.spawnChannel)
        elif (command == 'get b channel'):
            print('\nMonster Battle Channel: \n'+ settings.arenaChannel)
        #flavor commands
        elif (command == 'get flavors'):
            print(getFlavors())
        elif ("get flavor type" in command):
            print(getFlavorType(getIntArgs(command)))
        elif ("get flavor" in command):
            print(getFlavor(getIntArgs(command)))
        #monster commands
        elif (command == 'get monsters'):
            print(getMonsters())
        elif ("get monster rarity" in command):
            print(getMonsterRarity(getIntArgs(command)))
        elif ("get monster" in command):
            print(getMonster(getIntArgs(command)))
        #arena commands
        elif (command == 'get arenas'):
            print(getArenas())
        elif ("get arena" in command):
            print(getArena(getIntArgs(command)))
        #sets
        elif (command == 'set token'):
            setToken(input('\nUpdate Bot Token \nCurrently: '+ settings.botToken+"\n"))
            
        elif (command == 'set mongo'):
            setMongo(input('\nUpdate MongoDB login \nCurrently: '+ settings.mongo+"\n"))
        elif (command == 'set database'):
            setDatabase(input('\nUpdate database name \nCurrently: '+settings.DBname+"\n"))
        elif (command == 'set e channel'):
            setEChannel(input('\nUpdate Monster Encounter Channel \nCurrently: '+ settings.spawnChannel+"\n"))
            
        elif (command == 'set b channel'):
            setBChannel(input('\nUpdate Monster Battle Channel \nCurrently: '+ settings.arenaChannel+"\n"))
        #adds
        elif(command == "add flavor"):
            print(newFlavor())
        elif(command == "add monster"):
            print(newMonster())
        elif(command == "add arena"):
            print(newArena())
        #deletes
        elif("delete flavor" in command):
            print(deleteFlavor(getIntArgs(command)))
        elif("delete monster" in command):
            print(deleteMonster(getIntArgs(command)))
        elif("delete arena" in command):
            print(deleteArena(getIntArgs(command)))
        #edits
        elif("edit flavor" in command):
           print(editFlavor(getIntArgs(command)))
        elif("edit monster" in command):
            print(editMonster(getIntArgs(command)))
        elif("edit arena" in command):
            print(editArena(getIntArgs(command)))
        #download
        elif (command == "download flavors"):
            print(downloadFlavors())
        elif (command == "download monsters"):
            print(downloadMonsters())
        elif (command == "download arenas"):
            print(downloadArenas())
        elif (command == "download users"):
            print(downloadUsers())
        #upload
        elif(command == "upload flavors"):
            print(uploadFlavorPack(input("What is the name of the file you want to upload?(include extension)\n")))
        elif(command == "upload monsters"):
            print(uploadMonsterPack(input("What is the name of the file you want to upload?(include extension)\n")))
        elif(command == "upload arenas"):
            print(uploadArenaPack(input("What is the name of the file you want to upload?(include extension)\n")))
        elif(command == "upload users"):
            print(uploadUserPack(input("What is the name of the file you want to upload?(include extension)\n")))
        #test arena
        elif(command == "test arena"):
            print(testArena())
        #elif(command == 'help'):
         #   print(helpFunction())
        elif(command == 'quit'):
            exit()

def gui():
    app = Application()                       
    app.master.title('Discord Monster Game Manager')
    app.master.minsize(600, 400)
    print('mainloop')
    app.mainloop()
if guiCheck:
    gui()
else:
    commandLineInterface()

