import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# main application class
class app(tk.Tk):  # extending upon the tk.Tk class, this one defines the main GUI window
    def __init__(self, backend):  # this class automatically runs everytime, it initialises the object
        super().__init__()  # we run the parent class initialisation too (so inherit all methods from tk.Tk)
        self.backend = backend  # storing the backend so frames can use it
        self.title("Cheeky Thou on Green")  # setting text in the window title bar (.title is a method from tk.Tk)
        self.geometry("800x600")  # setting window size
        # frame is like <div> in HTML for organising layout
        container = ttk.Frame(self)  # making a frame to hold all UI stuff
        container.pack(fill="both", expand=True)  # any widgets added to our frame will be stacked vertically

        self.frames = {}  # creating a dictionary to store each screen's frames
        for f in (home_frame, login_frame, register_frame, sports_frame, wallet_frame):  # with eaach iteration, f is one of the frame classes (defined later)
            frame = f(container, self)  # creating an instance of the class
            self.frames[f.__name__] = frame  # storing the frame in the dictionary
            frame.grid(row=0, column=0, sticky="nsew")  # putting the frame inside the container at row0,col0 whenever we show it (aka just on the screen)
        container.grid_rowconfigure(0, weight=1)  # making the container stretch to the full window size
        container.grid_columnconfigure(0, weight=1)

        self.current_user = None  # to store the logged-in user later

        # structurally, we have the container inside the app window, and then all the frames are stored inside the container, but only one is visible at a time
        self.show_frame("home_frame")  # when the app starts, we show the homeframe (duh)

    def show_frame(self, name):  # defining the show_frame function (so we can switch between frames)
        frame = self.frames[name]  # we find the active frame in the dictionary with its name as the key
        frame.tkraise()  # this is a tk builtin function that brings the frame to the front (so its displayed/visible)

# individual screens (frames) classes
class home_frame(ttk.Frame):  # inheriting from the tk class Frame
    def __init__(self, parent, controller):  # parent is the container in which the frame is "stored in" and controller is the main app (so buttons clicked on the app then trigger show_frame() etc)
        super().__init__(parent)  # taking all the functionalities we defined for the container it'll be stored in (so in this case it'll always be the container defined in app)

        ttk.Label(self, text="Cheeky Thou on Green", font=("Arial", 24)).pack(side="top", anchor="center", pady=20)  # this just uses the tk method .Label for the title at the top of the page (will format later)
        # here we add all the buttons we want to be able to click with the built in tk method
        ttk.Button(self, text="Login",  # text is what the button shows
                   command=lambda: controller.show_frame("login_frame")).pack(pady=5)  # we use lambda to avoid the function being called immediately, this is only executed if clicked (it shows the frame)
        ttk.Button(self, text="Sports",
                   command=lambda: controller.show_frame("sports_frame")).pack(pady=5)  # the pack is just to actually place it on the screen (and has a vertical padding of 5)
        ttk.Button(self, text="Wallet",
                   command=lambda: controller.show_frame("wallet_frame")).pack(pady=5)

class login_frame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Login").pack(pady=10)
        ttk.Label(self, text="Username").pack()
        self.login_username_entry = ttk.Entry(self)  # .Entry is a method that stores the input so we can use it later
        self.login_username_entry.pack()  # making sure to pack it so that the element is displayed

        ttk.Label(self, text="Password").pack()
        self.login_password_entry = ttk.Entry(self, show="*")  # show="*" so that the password is hidden (;
        self.login_password_entry.pack()
        
        ttk.Label(self, text="Not a member yet?").pack()
        ttk.Button(self, text="Register",
                   command=lambda: controller.show_frame("register_frame")).pack(pady=10)

        ttk.Button(self, text="Back",
                   command=lambda: controller.show_frame("home_frame")).pack(pady=10)

class register_frame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ttk.Label(self, text="Register").pack(pady=10)

        # still have to add name, surname, email, password, confirm password entries (wtv we want when registering user)
        ttk.Label(self, text="Email").pack()
        self.register_email_entry = ttk.Entry(self)  
        self.register_email_entry.pack()  

        ttk.Label(self, text="Username").pack()
        self.register_username_entry = ttk.Entry(self)  
        self.register_username_entry.pack()  

        ttk.Label(self, text="Password").pack()
        self.register_password_entry = ttk.Entry(self, show="*") 
        self.register_password_entry.pack()

        ttk.Label(self, text="Confirm password").pack()
        self.confirm_password_entry = ttk.Entry(self, show="*") 
        self.confirm_password_entry.pack()

        ttk.Button(self, text="Create account", command=self.registration).pack(pady=10)  # button to create the account

        ttk.Button(self, text="Back",
                   command=lambda: controller.show_frame("home_frame")).pack(pady=10)
    
    def registration(self):
        # getting all the values entered by the user
        email = self.register_email_entry.get().strip()
        username = self.register_username_entry.get().strip()
        password = self.register_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not email or not username or not password or not confirm_password:  # if any of these fields are an empty string
            print("All fields are required.")
            messagebox.showerror("Error", "All fields are required.")  # error message popup
        elif password != confirm_password:
            print("Passwords do not match.")
            messagebox.showerror("Error", "Passwords do not match.")  # error message popup
        else:
            user_id = self.controller.backend.create_user(username, email, password)  # creating the user with the backend function we made

class sports_frame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ttk.Label(self, text="Sports").pack(pady=10)
        # have to decide what we want this page to show then add it in

        ttk.Button(self, text="Back",
                   command=lambda: controller.show_frame("home_frame")).pack(pady=10)

class wallet_frame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ttk.Label(self, text="Wallet").pack(pady=10)
        # need to decide what we want on the page
        ttk.Label(self, text="Balance").pack()

        # ttk.Button(self, text="Withdraw",
        #            # something
        #            )
        # ttk.Button(self, text="Deposit",
        #            # something
        # )

        ttk.Button(self, text="Back",
                   command=lambda: controller.show_frame("home_frame")).pack(pady=10)
