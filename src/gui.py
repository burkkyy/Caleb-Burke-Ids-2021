from tkinter import simpledialog, messagebox, filedialog
import network, threading, cv2
from PIL import Image, ImageTk
import face_recog as face
import tkinter as tk

TITLE_FONT = ("TkDefaultFont", 15)
LARGE_FONT = ("TkDefaultFont", 12)
SMALL_FONT = ("TkDefaultFont", 10)
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Even with no webcam this raises no error

class Base(tk.Tk):  # inherent from tk.Tk class
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)  # initialize the tk.Tk class so we can use it's functions
        tk.Tk.iconbitmap(self, default="myIcon.ico")  # to add a logo on each window
        tk.Tk.wm_title(self, "Caleb's Blockchain Network Client")  # title of each window
        tk.Tk.geometry(self, "400x300+300+300")  # size of the current window, width x height + x + y

        # initialize 'root' frame
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=0)
        container.grid_columnconfigure(0, weight=0)

        self.frames = {}  # to hold and manage each screen in the app
        for f in (MainScreen, OpenLedgerScreen, CreateIdentityScreen, ScanImageScreen, WebcamScreen, ImageScreen):
            frame = f(container, self)  # init each screen and set parent each each screen to container
            self.frames[f] = frame  # add the screen to the frames dict 
            frame.grid(row=0, column=0, sticky="nsew")
        self.showFrame(MainScreen)

        # Start the blockchain network
        self.net = network.BlockchainNetwork()
        self.net.start()

    def showFrame(self, cont):
        '''
        To display a frame, we simply find the frame in the dict
        self.frames in what ever index given from cont and call 
        .tkraise() on it so tkinter knows to display it on screen
        '''
        frame = self.frames[cont]
        frame.update()
        frame.tkraise()

    def changeWindowSize(self, width, height):
        tk.Tk.geometry(self, f"{width}x{height}")

    def getConns(self):
        return self.net.get_sockets()[0]

    def getLedgerIntegrity(self):
        return self.net.ledger.check_integrity()

    def getImageFromFile(self):
        # use filedialog class from tkinter to handle file selecting
        filepath = filedialog.askopenfilename(
            initialdir="/",
            title="Select an Image",
            filetypes=(
                ("Custom file", "*.jpeg;*.jpg;*.png*"),  # only allow pictures
                ("all files", "*.jpeg;*.jpg;*.png*")  # only allow pictures
            )
        )
        return filepath

    def quit(self):
        '''
        When we exit the program, we want to release the webcam to avoid weird opencv errors
        then we destory all frames and close the network and destory all opencv windows
        for safe measure
        '''
        cam.release()
        self.destroy()
        self.net.close()
        cv2.destroyAllWindows()

class MainScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def update(self):
        '''
        Before we display the frame, we need to clean up the
        frame by deleting everything (.destroy()) and changing 
        the window size to look nicer
        '''
        self.controller.changeWindowSize(200, 250)
        for slave in self.pack_slaves():
            slave.destroy()
        for slave in self.grid_slaves():
            slave.destroy()
        
        # Initialize the screen buttons and labels
        titleLabel = tk.Label(self, text="Start Page", font=TITLE_FONT, padx=5, pady=5)
        openLedgerButton = tk.Button(self, text="Open Ledger", command=lambda: self.controller.showFrame(OpenLedgerScreen))
        checkLedgerIntegrityButton = tk.Button(self, text="Check Integrity of Ledger", command=self.ledgerIntegrityBox)
        createIdentityButton = tk.Button(self, text="Create New Identity", command=lambda: self.controller.showFrame(CreateIdentityScreen))
        scanImageButton = tk.Button(self, text="Scan image for Identities", command=lambda: self.controller.showFrame(ScanImageScreen))
        showActiveConnsButton = tk.Button(self, text="Show active connections", command=self.showConnsBox)
        helpButton = tk.Button(self, text="Help", command=self.helpBox)
        quitButton = tk.Button(self, text="Quit", command=self.controller.quit)

        # Add them onto the screen using .grid()
        titleLabel.grid(row=0, column=0, sticky="N")
        openLedgerButton.grid(row=1, column=0, sticky="NESW")
        checkLedgerIntegrityButton.grid(row=2, column=0, sticky="NESW")
        createIdentityButton.grid(row=3, column=0, sticky="NESW")
        scanImageButton.grid(row=4, column=0, sticky="NESW")
        showActiveConnsButton.grid(row=5, column=0, sticky="NESW")
        helpButton.grid(row=6, column=0, sticky="NESW")
        quitButton.grid(row=7, column=0, sticky="NESW")

    def ledgerIntegrityBox(self):
        integrity = self.controller.getLedgerIntegrity()
        messagebox.showinfo("Ledger Integrity", f"Integrity of ledger: {integrity}")

    def showConnsBox(self):
        conns = self.controller.getConns()
        if conns:
            lines = []
            for i, conn in enumerate(conns):
                lines.append(f"Connection #{i + 1}: {conn}")
            txt = '\n'.join(lines)
            messagebox.showinfo("Connections", txt)
        else:
            messagebox.showinfo("Connections", "no active connections")
    
    def helpBox(self):
        with open("data/help.txt", "r") as r:
            lines = r.readlines()
        txt = ''.join(lines)
        messagebox.showinfo("Help Box", txt)

class OpenLedgerScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def update(self):
        self.controller.changeWindowSize(300, 200)
        for slave in self.pack_slaves():
            slave.destroy()
        for slave in self.grid_slaves():
            slave.destroy()
        
        title = tk.Label(self, text="Ledger UI", font=TITLE_FONT)
        title.pack(pady=10, padx=10)

        goBackButton = tk.Button(self, text="Go Back", command=lambda: self.controller.showFrame(MainScreen))
        goBackButton.pack()

class CreateIdentityScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def update(self):
        self.controller.changeWindowSize(200, 150)
        for slave in self.pack_slaves():
            slave.destroy()
        for slave in self.grid_slaves():
            slave.destroy()

        title = tk.Label(self, text="Create New Identity")
        CreateFromWebcam = tk.Button(self, text="Create Identity from Webcam", command=lambda: self.controller.showFrame(WebcamScreen))
        CreateFromImage = tk.Button(self, text="Create Identity from Image", command=lambda: self.controller.showFrame(ImageScreen))
        goBackButton = tk.Button(self, text="Go Back", command=lambda: self.controller.showFrame(MainScreen))

        title.grid(column=0, row=0, pady=0, padx=0)
        CreateFromWebcam.grid(column=0, row=1, pady=0, padx=0)
        CreateFromImage.grid(column=0, row=2, pady=0, padx=0)
        goBackButton.grid(column=0, row=3, pady=0, padx=0)

class ScanImageScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def update(self):
        self.controller.changeWindowSize(400, 300)
        for slave in self.pack_slaves():
            slave.destroy()
        for slave in self.grid_slaves():
            slave.destroy()

        title = tk.Label(self, text="Scan Image for Identities")
        goBackButton = tk.Button(self, text="Go Back", command=lambda: self.controller.showFrame(MainScreen))
        
        title.pack(pady=10, padx=10)
        goBackButton.pack()

class WebcamScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.current_image = None
        self.current_frame = None
        self.running = False
    
    def getCamFrame(self):
        if cam.isOpened():  # check if cam is useable
            ret, frame = cam.read()
            if ret:  # if read was successful
                return True, frame  # cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return False, None
    
    def showCamFrame(self):
        while self.running:
            check, frame = self.getCamFrame()
            if check:  # if cam read was successful
                if self.canvas.winfo_exists() == 1:
                    self.canvas.create_image(0, 0, image=self.current_frame, anchor='nw')
                self.current_image = frame
                frame = face.draw_rect_on_people(frame)  # face detection
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert image to rgb
                frame = ImageTk.PhotoImage(image=Image.fromarray(frame))  # convert to PIL image
                self.current_frame = frame
                if self.canvas.winfo_exists() == 1:
                    self.canvas.create_image(0, 0, image=self.current_frame, anchor='nw')  # display image on canvas
            else:
                if self.canvas.winfo_exists() == 1:
                    self.canvas.create_text(0, 0, text="WEBCAM ERROR", anchor='center')

    def capture(self):
        self.running = False  # stop showCamFrame and getCamFrame
        createIdenBtn = tk.Button(self, text="Create Identity using Image", command=self.create_identity, padx=0, pady=0, anchor='center')
        restartBtn = tk.Button(self, text="Restart", command=self.close, padx=0, pady=0, anchor='center')
        
        createIdenBtn.grid(column=0, row=4, sticky='NW')
        restartBtn.grid(column=0, row=4, sticky='NE')
    
    def create_identity(self):
        name = simpledialog.askstring(title="Dialog Box", prompt="Enter name for your Identity below")
        if name:  # check if name was inputted, if not display another dialog box until they enter a name
            encoding = face.create_encoding(self.current_image)
            qk, pk = self.controller.net.createIdentity(name, encoding)
            self.close()
            messagebox.showinfo("Identity Successfully Created", f"Keys:\n\nprivate key: {qk}\n\npublic key: {pk}\n\nKeys can also be viewed in src/data/keys.txt")
        else:
            self.create_identity()
    
    def update(self):
        self.controller.changeWindowSize(int(cam.get(cv2.CAP_PROP_FRAME_WIDTH)+300), int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)+150))
        for slave in self.pack_slaves():
            slave.destroy()
        for slave in self.grid_slaves():
            slave.destroy()
        
        title = tk.Label(self, text="Create Identity From Webcam", font=TITLE_FONT, padx=0, pady=0, anchor='nw')
        description = tk.Label(self, text="Identity is created for the face with the red box")
        self.captureBtn = tk.Button(self, text="Capture", command=self.capture, padx=0, pady=0, anchor='nw')
        goBackButton = tk.Button(self, text="Go Back", command=self.close, padx=0, pady=0, anchor='nw')
        self.canvas = tk.Canvas(self, width=cam.get(cv2.CAP_PROP_FRAME_WIDTH), height=cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        title.grid(column=0, row=0, padx=5, pady=5)
        description.grid(column=0, row=1, padx=3, pady=3)
        self.captureBtn.grid(column=0, row=2, padx=3, pady=3)
        goBackButton.grid(column=0, row=3, padx=3, pady=3)
        self.canvas.grid(column=1, row=4, padx=5, pady=5)

        self.running = True
        thread = threading.Thread(target=self.showCamFrame)
        thread.start()

    def close(self):
        self.running = False
        self.canvas.destroy()
        self.controller.showFrame(CreateIdentityScreen)

class ImageScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def createIdentityFromImage(self):
        name = simpledialog.askstring(title="Dialog Box", prompt="Enter name for your Identity below")
        if name:
            encoding = face.create_encoding(self.imageCv)
            qk, pk = self.controller.net.createIdentity(name, encoding)
            self.close()
            messagebox.showinfo("Identity Successfully Created", f"Keys:\n\nprivate key: {qk}\n\npublic key: {pk}\n\nKeys can also be viewed in src/data/keys.txt")
        else:
            self.create_identity()

    def update(self):
        # disgusting image converting because tkinter only works with PIL images
        self.image = self.controller.getImageFromFile()
        self.imageCv = cv2.imread(self.image)
        self.image = face.draw_rect_on_people(self.imageCv)
        self.image = cv2.resize(self.image, (200, 300))
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.image = ImageTk.PhotoImage(image=Image.fromarray(self.image))

        self.controller.changeWindowSize(500, 500)
        for slave in self.pack_slaves():
            slave.destroy()
        for slave in self.grid_slaves():
            slave.destroy()

        title = tk.Label(self, text="Create Identity From Image", font=TITLE_FONT)
        confirmBtn = tk.Button(self, text="Create Identity From this Image", command=self.createIdentityFromImage, padx=0, pady=0, anchor='nw')
        goBackBtn = tk.Button(self, text="Go Back", command=self.close, padx=0, pady=0, anchor='nw')
        self.canvas = tk.Canvas(self, width=self.image.width(), height=self.image.height())
        self.canvas.create_image(0, 0, image=self.image, anchor='nw')

        title.grid(column=0, row=0, padx=5, pady=5)
        confirmBtn.grid(column=0, row=1, padx=5, pady=5)
        goBackBtn.grid(column=0, row=2, padx=5, pady=5)
        self.canvas.grid(column=1, row=6, padx=5, pady=5)

    def close(self):
        self.canvas.destroy()
        self.controller.showFrame(CreateIdentityScreen)

if __name__ == '__main__':
    g = Base()
    g.mainloop()
