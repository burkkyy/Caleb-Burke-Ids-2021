import tkinter as tk  # Part of Python standard library
import cv2  # pip install opencv-python, face_recognition only compatible with opencv images
import face_recog as face
import network 

TITLE_FONT = ("TkDefaultFont", 15)
LARGE_FONT = ("TkDefaultFont", 12)
SMALL_FONT = ("TkDefaultFont", 10)


class Base(tk.Tk):
    def __init__(self, net, *args, **kwargs):
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
            ShowActiveConnsScreen, HelpScreen):
            frame = f(container, self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(MainScreen)

    def showFrame(self, cont):
        frame = self.frames[cont]
        frame.update()
        frame.tkraise()

    def getConns(self):
        return ["a", "b", "c"]

    def getLedgerIntegrity(self):
        return True

    def getImageFromFile(self):
        filepath = filedialog.askopenfilename(
            initialdir="/",
            title="Select an Image",
            filetypes=(
                ("Custom file", "*.jpeg;*.jpg;*.png*"),
                ("all files", "*.jpeg;*.jpg;*.png*")
            )
        )
        return filepath

class MainScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Initialize the screen buttons and labels
        titleLabel = tk.Label(self, text="Start Page", font=TITLE_FONT)
        openLedgerButton = tk.Button(self, text="Open Ledger", command=lambda: controller.showFrame(OpenLedgerScreen))
        checkLedgerIntegrityButton = tk.Button(self, text="Check Integrity of Ledger", command=lambda: controller.showFrame(ShowLedgerIntegrityScreen))
        createIdentityButton = tk.Button(self, text="Create New Identity", command=lambda: controller.showFrame(CreateIdentityScreen))
        scanImageButton = tk.Button(self, text="Scan image for Identities", command=lambda: controller.showFrame(ScanImageScreen))
        showActiveConnsButton = tk.Button(self, text="Show active connections", command=lambda: controller.showFrame(ShowActiveConnsScreen))
        helpButton = tk.Button(self, text="Help", command=lambda: controller.showFrame(HelpScreen))
        quitButton = tk.Button(self, text="Quit", command=controller.destroy)

        # Add them onto the screen using .grid()
        titleLabel.grid(row=0, column=0, sticky="N")
        openLedgerButton.grid(row=1, column=0, sticky="NESW")
        checkLedgerIntegrityButton.grid(row=2, column=0, sticky="NESW")
        createIdentityButton.grid(row=3, column=0, sticky="NESW")
        scanImageButton.grid(row=4, column=0, sticky="NESW")
        showActiveConnsButton.grid(row=5, column=0, sticky="NESW")
        helpButton.grid(row=6, column=0, sticky="NESW")
        quitButton.grid(row=7, column=0, sticky="NESW")

class OpenLedgerScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        title = tk.Label(self, text="Leader:")
        title.pack(pady=10, padx=10)
        goBackButton = tk.Button(self, text="Go Back", command=lambda: controller.showFrame(MainScreen))
        goBackButton.pack()

    def update(self):
        pass

class ShowLedgerIntegrityScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="Ledger Integrity:")
        title.pack(pady=10, padx=10)
        goBackButton = tk.Button(self, text="Go Back", command=lambda: controller.showFrame(MainScreen))
        goBackButton.pack()

    def update(self):
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
        title = tk.Label(self, text="Create New Identity")
        title.pack(pady=10, padx=10)
        goBackButton = tk.Button(self, text="Go Back", command=lambda: controller.showFrame(MainScreen))
        goBackButton.pack()

    def update(self):
        pass

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
        for slave in self.pack_slaves():
            slave.destroy()

        title = tk.Label(self, text="Active Connections:")
        title.pack(padx=0, pady=0)

        conns = self.controller.getConns()
        for i, conn in enumerate(conns):
            tempLabel = tk.Label(self, text=f"{i}: {conn}")
            tempLabel.pack(padx=0, pady=0)

        goBackButton = tk.Button(self, text="Go Back", command=lambda: self.controller.showFrame(MainScreen))
        goBackButton.pack(padx=0, pady=0)

class HelpScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        title = tk.Label(self, text="Help")
        title.pack(padx=10, pady=10)
        goBackButton = tk.Button(self, text="Go Back", command=lambda: controller.showFrame(MainScreen))
        goBackButton.pack()
    
    def update(self):
        pass

if __name__ == '__main__':
    g = Base(None)
    g.mainloop()
