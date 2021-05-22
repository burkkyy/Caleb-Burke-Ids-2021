from tkinter.constants import ANCHOR  # Part of Python standard library
import network, threading, time, cv2
from PIL import Image, ImageTk
import face_recog as face
import tkinter as tk

TITLE_FONT = ("TkDefaultFont", 15)
LARGE_FONT = ("TkDefaultFont", 12)
SMALL_FONT = ("TkDefaultFont", 10)
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

class Base(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="myIcon.ico")
        tk.Tk.wm_title(self, "Caleb's Blockchain Network Client")
        tk.Tk.geometry(self, "400x300+300+300")  # width x height + x + y

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=0)
        container.grid_columnconfigure(0, weight=0)

        self.frames = {}
        for f in (
            MainScreen, 
            OpenLedgerScreen, 
            ShowLedgerIntegrityScreen, 
            CreateIdentityScreen, 
            ScanImageScreen, 
            ShowActiveConnsScreen, 
            HelpScreen,
            WebcamScreen,
            ):
            frame = f(container, self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(MainScreen)

        self.net = network.BlockchainNetwork()
        self.net.start()

    def showFrame(self, cont):
        frame = self.frames[cont]
        frame.update()
        frame.tkraise()

    def changeWindowSize(self, width, height):
        # width x height + x + y
        tk.Tk.geometry(self, f"{width}x{height}+300+300")
        pass

    def getConns(self):
        return self.net.get_conns()

    def getLedgerIntegrity(self):
        return True

    def getImageFromFile(self):
        filepath = tk.filedialog.askopenfilename(
            initialdir="/",
            title="Select an Image",
            filetypes=(
                ("Custom file", "*.jpeg;*.jpg;*.png*"),
                ("all files", "*.jpeg;*.jpg;*.png*")
            )
        )
        return filepath

    def quit(self):
        cam.release()
        self.destroy()
        self.net.close()
        cv2.destroyAllWindows()


class MainScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # Initialize the screen buttons and labels
        titleLabel = tk.Label(self, text="Start Page", font=TITLE_FONT)
        openLedgerButton = tk.Button(self, text="Open Ledger", command=lambda: controller.showFrame(OpenLedgerScreen))
        checkLedgerIntegrityButton = tk.Button(self, text="Check Integrity of Ledger", command=lambda: controller.showFrame(ShowLedgerIntegrityScreen))
        createIdentityButton = tk.Button(self, text="Create New Identity", command=lambda: controller.showFrame(CreateIdentityScreen))
        scanImageButton = tk.Button(self, text="Scan image for Identities", command=lambda: controller.showFrame(ScanImageScreen))
        showActiveConnsButton = tk.Button(self, text="Show active connections", command=lambda: controller.showFrame(ShowActiveConnsScreen))
        helpButton = tk.Button(self, text="Help", command=lambda: controller.showFrame(HelpScreen))
        quitButton = tk.Button(self, text="Quit", command=controller.quit)

        # Add them onto the screen using .grid()
        titleLabel.grid(row=0, column=0, sticky="N")
        openLedgerButton.grid(row=1, column=0, sticky="NESW")
        checkLedgerIntegrityButton.grid(row=2, column=0, sticky="NESW")
        createIdentityButton.grid(row=3, column=0, sticky="NESW")
        scanImageButton.grid(row=4, column=0, sticky="NESW")
        showActiveConnsButton.grid(row=5, column=0, sticky="NESW")
        helpButton.grid(row=6, column=0, sticky="NESW")
        quitButton.grid(row=7, column=0, sticky="NESW")

    def update(self):
        self.controller.changeWindowSize(200, 250)

class OpenLedgerScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="Leader:")
        title.pack(pady=10, padx=10)
        goBackButton = tk.Button(self, text="Go Back", command=lambda: controller.showFrame(MainScreen))
        goBackButton.pack()

    def update(self):
        self.controller.changeWindowSize(300, 200)

class ShowLedgerIntegrityScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="Ledger Integrity:")
        title.pack(pady=10, padx=10)
        goBackButton = tk.Button(self, text="Go Back", command=lambda: controller.showFrame(MainScreen))
        goBackButton.pack()

    def update(self):
        self.controller.changeWindowSize(400, 300)
        for slave in self.pack_slaves():
            slave.destroy()
        integrity = self.controller.getLedgerIntegrity()
        tempLabel = tk.Label(self, text=f"Integrity of ledger: {integrity}")
        tempLabel.pack(padx=0, pady=0)
        goBackButton = tk.Button(self, text="Go Back", command=lambda: self.controller.showFrame(MainScreen))
        goBackButton.pack(padx=0, pady=0)

class CreateIdentityScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def update(self):
        self.controller.changeWindowSize(200, 150)
        for slave in self.pack_slaves():
            slave.destroy()
        title = tk.Label(self, text="Create New Identity")
        title.grid(column=0, row=0, pady=0, padx=0)
        CreateFromWebcam = tk.Button(self, text="Create Identity from Webcam", command=lambda: self.controller.showFrame(WebcamScreen))
        CreateFromWebcam.grid(column=0, row=1, pady=0, padx=0)
        CreateFromImage = tk.Button(self, text="Create Identity from Image", command=lambda: self.controller.showFrame(MainScreen))
        CreateFromImage.grid(column=0, row=2, pady=0, padx=0)
        goBackButton = tk.Button(self, text="Go Back", command=lambda: self.controller.showFrame(MainScreen))
        goBackButton.grid(column=0, row=3, pady=0, padx=0)

class ScanImageScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        title = tk.Label(self, text="Scan Image for Identities")
        title.pack(pady=10, padx=10)
        goBackButton = tk.Button(self, text="Go Back", command=lambda: controller.showFrame(MainScreen))
        goBackButton.pack()

    def update(self):
        pass

class ShowActiveConnsScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="Active Connections:")
        title.pack(padx=10, pady=10)
        goBackButton = tk.Button(self, text="Go Back", command=lambda: controller.showFrame(MainScreen))
        goBackButton.pack()

    def update(self):
        self.controller.changeWindowSize(400, 300)
        for slave in self.pack_slaves():
            slave.destroy()

        title = tk.Label(self, text="Active Connections:")
        title.pack(padx=0, pady=0)

        conns = self.controller.getConns()
        if conns:
            for i, conn in enumerate(conns):
                tempLabel = tk.Label(self, text=f"{i}: {conn}")
                tempLabel.pack(padx=0, pady=0)
        else:
            tempLabel = tk.Label(self, text="no connections")
            tempLabel.pack(padx=0, pady=0)
        
        goBackButton = tk.Button(self, text="Go Back", command=lambda: self.controller.showFrame(MainScreen))
        goBackButton.pack(padx=0, pady=0)

class HelpScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="Help")
        title.pack(padx=10, pady=10)
        goBackButton = tk.Button(self, text="Go Back", command=lambda: controller.showFrame(MainScreen))
        goBackButton.pack()
    
    def update(self):
        self.controller.changeWindowSize(400, 300)

class WebcamScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.current_image = None
        self.running = False
    
    def getCamFrame(self):
        if cam.isOpened():
            ret, frame = cam.read()
            if ret:
                return True, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return False, None
    
    def showCamFrame(self):
        while self.running:
            check, frame = self.getCamFrame()
            if check:
                self.current_image = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.current_image, anchor='nw')
            else:
                self.canvas.create_text(0, 0, text="WEBCAM ERROR", anchor='nw')

    def capture(self):
        pass

    def update(self):
        self.controller.changeWindowSize(int(cam.get(cv2.CAP_PROP_FRAME_WIDTH)+50), int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)+100))
        title = tk.Label(self, text="Create Identity From Webcam", padx=0, pady=0, anchor='nw')
        title.grid(column=0, row=0, padx=0, pady=0)

        self.captureBtn = tk.Button(self, text="Capture", command=self.capture, padx=0, pady=0, anchor='nw')
        self.captureBtn.grid(column=0, row=1, padx=0, pady=0)

        goBackButton = tk.Button(self, text="Go Back", command=self.close, padx=0, pady=0, anchor='nw')
        goBackButton.grid(column=0, row=2, padx=0, pady=0)

        self.canvas = tk.Canvas(self, width=cam.get(cv2.CAP_PROP_FRAME_WIDTH), height=cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.grid(column=1, row=0, padx=5, pady=5)

        self.running = True
        thread = threading.Thread(target=self.showCamFrame)
        thread.start()

    def close(self):
        self.running = False
        self.controller.showFrame(CreateIdentityScreen)
        for slave in self.pack_slaves():
            slave.destroy()

if __name__ == '__main__':
    g = Base()
    g.mainloop()
