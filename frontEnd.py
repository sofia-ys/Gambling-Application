from customtkinter import *  # using this because the UI is just infinitely better like it doesn't
import backEnd as backEnd

# main application class
class app(CTk):  # extending upon the tk.Tk class, this one defines the main GUI window
    def __init__(self, backend):  # this class automatically runs everytime, it initialises the object
        super().__init__()  # we run the parent class initialisation too (so inherit all methods from tk.Tk)
        self.backend = backend  # storing the backend so frames can use it
        self.title("BE-THE-ONE")  # setting text in the window title bar (.title is a method from tk.Tk)
        self.geometry("800x600")  # setting window size
        set_appearance_mode("dark")  # always dark mode (:


        self.current_user = None  # to store the logged-in user later

        # contents for the header 
        self.header = CTkFrame(self, corner_radius=0)
        self.header.pack(side="top", fill="x")  # a frame placed at the top, filling the full x-axis span

        CTkLabel(self.header, text="BE-T", font=("Open Sans", 24, "italic"), text_color="#ff7a00").pack(side="left", pady=20, padx=(20, 0))  # this just uses the tk method .Label for the title at the top of the page 
        CTkLabel(self.header, text="HE-ONE", font=("Open Sans", 24, "italic"), text_color="white").pack(side="left", pady=20, padx=(0, 20))  

        
        self.loginBtn = CTkButton(self.header, text="Login", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"), # text is what the button shows
                                      command=lambda: self.show_frame("login_frame"))  # we use lambda to avoid the function being called immediately, this is only executed if clicked (it shows the frame)
        self.walletBtn = CTkButton(self.header, text="Wallet", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"),
                                       command=lambda: self.show_frame("wallet_frame"))
        self.homeBtn = CTkButton(self.header, text="Home", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"),
                                 command=lambda: self.show_frame("home_frame"))
        self.refresh_header()

        # frame is like <div> in HTML for organising layout
        container = CTkFrame(self)  # making a frame to hold all UI stuff
        container.pack(fill="both", expand=True)  # any widgets added to our frame will be stacked vertically

        self.frames = {}  # creating a dictionary to store each screen's frames
        for f in (home_frame, login_frame, register_frame, wallet_frame):  # with eaach iteration, f is one of the frame classes (defined later)
            frame = f(container, self)  # creating an instance of the class
            self.frames[f.__name__] = frame  # storing the frame in the dictionary
            frame.grid(row=0, column=0, sticky="nsew")  # putting the frame inside the container at row0,col0 whenever we show it (aka just on the screen)
        container.grid_rowconfigure(0, weight=1)  # making the container stretch to the full window size
        container.grid_columnconfigure(0, weight=1)

        # structurally, we have the container inside the app window, and then all the frames are stored inside the container, but only one is visible at a time
        self.show_frame("home_frame")  # when the app starts, we show the homeframe (duh)

    def show_frame(self, name):  # defining the show_frame function (so we can switch between frames)
        frame = self.frames[name]  # we find the active frame in the dictionary with its name as the key
        frame.tkraise()  # this is a tk builtin function that brings the frame to the front (so its displayed/visible)

    def refresh_header(self):
        self.walletBtn.pack_forget()  # forget all of these, we then reput them on as per login in the correct order
        self.loginBtn.pack_forget()
        self.homeBtn.pack_forget()
        if not self.current_user:  # if we're not logged in we show the account button 
            self.loginBtn.pack(side="right", pady=5, padx=10)
            self.homeBtn.pack(side="right", pady=5, padx=10)  # the pack is just to actually place it on the screen (and has a vertical padding of 5)
        else:
            self.walletBtn.pack(side="right", pady=5, padx=10)
            self.homeBtn.pack(side="right", pady=5, padx=10)


# individual screens (frames) classes
class home_frame(CTkFrame):  # inheriting from the tk class Frame
    def __init__(self, parent, controller):  # parent is the container in which the frame is "stored in" and controller is the main app (so buttons clicked on the app then trigger show_frame() etc)
        super().__init__(parent)  # taking all the functionalities we defined for the container it'll be stored in (so in this case it'll always be the container defined in app)

        # ad banners
        self.ads_left = CTkFrame(self, corner_radius=0)
        self.ads_left.pack(side="left", fill="y") 

        self.ads_right = CTkFrame(self, corner_radius=0)
        self.ads_right.pack(side="right", fill="y") 

        # live sports section
        self.live = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.live.pack(side="top", fill="x")  # a frame placed at the top, filling the full x-axis span    

        CTkLabel(self.live, text="Live", font=("Open Sans", 20), text_color="white").pack(side="left", pady=20, padx=20)


        
class login_frame(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        CTkLabel(self, text="Login", font=("Open Sans", 20, "bold")).pack(pady=10)
        CTkLabel(self, text="Username").pack()
        self.login_username_entry = CTkEntry(self)  # .Entry is a method that stores the input so we can use it later
        self.login_username_entry.pack()  # making sure to pack it so that the element is displayed

        CTkLabel(self, text="Password").pack()
        self.login_password_entry = CTkEntry(self, show="*")  # show="*" so that the password is hidden (;
        self.login_password_entry.pack()

        self.error_message = CTkLabel(self, text="")  # space for error message we can adjust
        self.error_message.pack()

        CTkButton(self, text="Login", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"),
                   command=self.login).pack(pady=10)
        
        CTkLabel(self, text="Not a member yet?").pack()
        CTkButton(self, text="Register", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"),
                   command=lambda: controller.show_frame("register_frame")).pack(pady=10)
        
    def login(self):
        username = self.login_username_entry.get().strip()
        plain_password = self.login_password_entry.get()

        # first check if we have inputs
        if not username or not plain_password:  # if we're missing any of these
            print("All fields are required.")
            self.error_message.configure(text="All fields are required.")
            return
        
        user = self.controller.backend.verify_login(username, plain_password)  # now we check if the inputs are valid

        if not user:  # if the info doesn't match, aka function returns none --> so if not(none) = if true
            print("Invalid username and/or password.")
            self.error_message.configure(text="Invalid username and/or password.")
            return
        else:
            self.controller.current_user = user  # storing the logged in user
            self.login_username_entry.delete(0, END)  # clearing fields
            self.login_password_entry.delete(0, END)
            self.controller.refresh_header()
            self.controller.frames["wallet_frame"].balance_refresh()
            self.controller.show_frame("home_frame")



class register_frame(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller  # making the controller (app) exist here

        CTkLabel(self, text="Register", font=("Open Sans", 20, "bold")).pack(pady=10)

        # still have to add name, surname, email, password, confirm password entries (wtv we want when registering user)
        CTkLabel(self, text="Email").pack()
        self.register_email_entry = CTkEntry(self)  
        self.register_email_entry.pack()  

        CTkLabel(self, text="Username").pack()
        self.register_username_entry = CTkEntry(self)  
        self.register_username_entry.pack()  

        CTkLabel(self, text="Password").pack()
        self.register_password_entry = CTkEntry(self, show="*") 
        self.register_password_entry.pack()

        CTkLabel(self, text="Confirm password").pack()
        self.confirm_password_entry = CTkEntry(self, show="*") 
        self.confirm_password_entry.pack()

        self.error_message = CTkLabel(self, text="")  # space for error message we can adjust
        self.error_message.pack()

        CTkButton(self, text="Create account", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"), 
                  command=self.registration).pack(pady=10)  # button to create the account

        CTkButton(self, text="Back", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"),
                   command=lambda: controller.show_frame("login_frame")).pack(pady=10)
        
    def reset_form(self):
        self.register_email_entry.delete(0, END)
        self.register_username_entry.delete(0, END)
        self.register_password_entry.delete(0, END)
        self.confirm_password_entry.delete(0, END)
        self.error_message.configure(text="")
    
    def registration(self):
        # getting all the values entered by the user
        email = self.register_email_entry.get().strip()
        username = self.register_username_entry.get().strip()
        password = self.register_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not email or not username or not password or not confirm_password:  # if any of these fields are an empty string
            print("All fields are required.")
            self.error_message.configure(text="All fields are required.")  # error message popup
            return  # truncate registration process
        elif password != confirm_password:
            print("Passwords do not match.")
            self.error_message.configure(text="Passwords do not match.")  # error message popup
            return
        else:
            user = self.controller.backend.create_user(username, email, password)  # creating the user with the backend function we made
            self.controller.current_user = user
            self.controller.refresh_header()
            self.controller.frames["wallet_frame"].balance_refresh()
            self.controller.show_frame("home_frame")


class wallet_frame(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        CTkLabel(self, text="Wallet", font=("Open Sans", 20, "bold")).pack(pady=10)
        # need to decide what we want on the page

        self.balanceFrame = CTkFrame(self)
        self.balanceFrame.pack(padx=50, pady=50, ipadx=100, ipady=50, fill="x") 
        CTkLabel(self.balanceFrame, text="Balance", font=("Open Sans", 16, "bold")).pack()
        self.balanceTxt = CTkLabel(self.balanceFrame, text="$0.00", font=("Open Sans", 20, "bold"))  # initialised with a $0.00 (although this is never seen if not logged in)
        self.balance_refresh()
        self.balanceTxt.pack()

        CTkButton(self, text="Withdraw", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"), 
                   # something
                   ).pack(side="left", pady=20, padx=(240, 10))
        CTkButton(self, text="Deposit", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"), 
                   # something
        ).pack(side="right", pady=20, padx=(10, 240))
    
    def balance_refresh(self):
        if self.controller.current_user:
            self.balance = self.controller.current_user["balance"]
        else:
            self.balance = 0
        self.balanceTxt.configure(text=f"${self.balance:.2f}")
    

# running the program
if __name__ == "__main__":
    app = app(backEnd)  # creating the instance of app
    app.mainloop()  # actually running it 

