from customtkinter import *  # using this because the UI is just infinitely better like it doesn't
import backEnd as backEnd
from datetime import datetime

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
        self.accountBtn = CTkButton(self.header, text="Account", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"),
                                       command=lambda: self.show_frame("account_frame"))
        self.homeBtn = CTkButton(self.header, text="Home", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"),
                                 command=lambda: self.show_frame("home_frame"))
        self.refresh_header()

        # frame is like <div> in HTML for organising layout
        container = CTkFrame(self)  # making a frame to hold all UI stuff
        container.pack(fill="both", expand=True)  # any widgets added to our frame will be stacked vertically

        self.frames = {}  # creating a dictionary to store each screen's frames
        for f in (home_frame, login_frame, register_frame, account_frame, betting_frame):  # with eaach iteration, f is one of the frame classes (defined later)
            frame = f(container, self)  # creating an instance of the class
            self.frames[f.__name__] = frame  # storing the frame in the dictionary
            frame.grid(row=0, column=0, sticky="nsew")  # putting the frame inside the container at row0,col0 whenever we show it (aka just on the screen)
        container.grid_rowconfigure(0, weight=1)  # making the container stretch to the full window size
        container.grid_columnconfigure(0, weight=1)

        # structurally, we have the container inside the app window, and then all the frames are stored inside the container, but only one is visible at a time
        self.show_frame("home_frame")  # when the app starts, we show the homeframe (duh)

    def show_frame(self, name):  # defining the show_frame function (so we can switch between frames)
        frame = self.frames[name]  # we find the active frame in the dictionary with its name as the ke
        if name == "account_frame":
            frame.balance_refresh()  # making sure wallet balance is always good
    
        if hasattr(frame, "on_show"):  # if we have stuff to clear, we clear it (;
            frame.on_show()

        if self.current_user:  # if we're logged in 
            if name == "account_frame":  # AND wer're on the account frame
                self.accountBtn.configure(text="Log out", command=self.logout)  # we change the button to a logout
            else:  # on any other page it's the account one
                self.accountBtn.configure(text="Account", command=lambda: self.show_frame("account_frame"))

        frame.tkraise()  # this is a tk builtin function that brings the frame to the front (so its displayed/visible)

    def refresh_header(self):
        self.accountBtn.pack_forget()  # forget all of these, we then reput them on as per login in the correct order
        self.loginBtn.pack_forget()
        self.homeBtn.pack_forget()
        if not self.current_user:  # if we're not logged in we show the account button 
            self.loginBtn.pack(side="right", pady=5, padx=10)
            self.homeBtn.pack(side="right", pady=5, padx=10)  # the pack is just to actually place it on the screen (and has a vertical padding of 5)
        else:
            self.accountBtn.pack(side="right", pady=5, padx=10)
            self.homeBtn.pack(side="right", pady=5, padx=10)

    def logout(self):
        self.current_user = None  # logging out user
        self.refresh_header()
        self.show_frame("login_frame")


# individual screens (frames) classes
class home_frame(CTkFrame):  # inheriting from the tk class Frame
    def __init__(self, parent, controller):  # parent is the container in which the frame is "stored in" and controller is the main app (so buttons clicked on the app then trigger show_frame() etc)
        super().__init__(parent)  # taking all the functionalities we defined for the container it'll be stored in (so in this case it'll always be the container defined in app)

        self.controller = controller
        
        # ad banners
        self.ads_left = CTkFrame(self, corner_radius=0)
        self.ads_left.pack(side="left", fill="y") 

        self.ads_right = CTkFrame(self, corner_radius=0)
        self.ads_right.pack(side="right", fill="y") 

        # live sports section 
        # the live events won't actually update, we'll just choose a date for the app to be kinda of "stuck in time" on

        self.events_scroll = CTkScrollableFrame(self, fg_color="transparent")
        self.events_scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.refresh_events()
        
    def refresh_events(self):
        # Clear existing event frames
        for widget in self.events_scroll.winfo_children():
            widget.destroy()
        
        # Define cutoff datetime for live category
        cutoff_live_start = datetime(2025, 1, 1, 0, 0, 1)  # Feb 3rd 1:00 AM
        cutoff_live_end = datetime(2025, 2, 3, 2, 59, 59)  # Feb 3rd 2:59 AM

        #self.controller.backend.update_event_status_by_cutoff(cutoff_live_start, cutoff_live_end)
        
        # Fetch events from backend
        events = self.controller.backend.get_sports_events()
        
        open_events = []
        closed_events = []
        settled_events = []

        for event in events:
            
            event_date_str = str(event['event_date'])
            
            event_dt = datetime.strptime(event_date_str, "%Y-%m-%d %H:%M:%S")
                
            if cutoff_live_start <= event_dt <= cutoff_live_end:
                event['temp_status'] = 'LIVE'
                open_events.append(event)
            elif event_dt > cutoff_live_end:
                event['temp_status'] = 'OPEN'
                open_events.append(event)
            else:
                event['temp_status'] = 'CLOSED'
                closed_events.append(event)

        settled_events = [e for e in events if e.get('bet_status') == 'SETTLED']
        
        def populate_section(title, event_list):
            section_frame = CTkFrame(self.events_scroll, fg_color="transparent")
            CTkLabel(section_frame, text=title, font=("Open Sans", 18, "bold"), text_color="#ff7a00").pack(anchor="w", padx=10, pady=10)
            section_frame.pack(fill="x", pady=10)

            for event in event_list:
                sports_preview = sports_frame(section_frame, self.controller, event)
                sports_preview.pack(fill="x", pady=5)

        populate_section("Live Events", open_events)
        populate_section("Upcoming Events", closed_events)
        populate_section("Past Events", settled_events)
        
class login_frame(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        CTkLabel(self, text="Login", font=("Open Sans", 20, "bold"), text_color="#ff7a00").pack(pady=10)
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
            self.controller.frames["account_frame"].balance_refresh()
            self.controller.show_frame("home_frame")

    def on_show(self):  # for clearing all our fields etc
        self.error_message.configure(text="")
        self.login_username_entry.delete(0, END)
        self.login_password_entry.delete(0, END)


class register_frame(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller  # making the controller (app) exist here

        CTkLabel(self, text="Register", font=("Open Sans", 20, "bold"), text_color="#ff7a00").pack(pady=10)

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
            self.controller.frames["account_frame"].balance_refresh()
            self.controller.show_frame("home_frame")
    
    def on_show(self):  # clearing it out
        self.reset_form()


class account_frame(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        CTkLabel(self, text="Wallet", font=("Open Sans", 20, "bold"), text_color="#ff7a00").pack(pady=10)

        self.balanceFrame = CTkFrame(self)
        self.balanceFrame.pack(padx=50, pady=50, ipadx=100, ipady=50, fill="x") 
        CTkLabel(self.balanceFrame, text="Balance", font=("Open Sans", 16, "bold")).pack(pady=(20, 10))
        self.balanceTxt = CTkLabel(self.balanceFrame, text="$0.00", font=("Open Sans", 20, "bold"))  # initialised with a $0.00 (although this is never seen if not logged in)
        self.balance_refresh()
        self.balanceTxt.pack()

        CTkLabel(self.balanceFrame, text="Amount", font=("Open Sans", 16, "bold")).pack(pady=(40, 10))
        self.tx_amount = CTkEntry(self.balanceFrame)  
        self.tx_amount.pack()  

        self.error_message = CTkLabel(self.balanceFrame, text="")  # space for error message we can adjust
        self.error_message.pack()

        CTkButton(self.balanceFrame, text="Withdraw", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"), 
                   command=self.withdraw_click
                   ).pack(side="left", pady=10, padx=(180, 10))
        CTkButton(self.balanceFrame, text="Deposit", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", font=("Open Sans", 12, "bold"), 
                   command=self.deposit_click
        ).pack(side="right", pady=10, padx=(10, 180))

        CTkLabel(self, text="Transaction History", font=("Open Sans", 20, "bold"), text_color="#ff7a00").pack(pady=10)

        self.history_scroll = CTkScrollableFrame(self, fg_color="transparent")
        self.history_scroll.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        self.refresh_history()


    
    def balance_refresh(self):
        if self.controller.current_user:
            self.balance = self.controller.current_user["balance"]
        else:
            self.balance = 0
        self.balanceTxt.configure(text=f"${self.balance:.2f}")

    def deposit_click(self):
        if not self.controller.current_user:  # if no one is logged in
            return
        user_id = self.controller.current_user["user_id"]
        amount = float(self.tx_amount.get().strip())

        if amount <= 0:
            self.error_message.configure(text="Amount must be greater than 0.")
            print("Amount must be greater than 0.")
            return
        
        new_balance = backEnd.deposit(user_id, amount)
        self.controller.current_user["balance"] = new_balance  # updating the controller
        self.tx_amount.delete(0, END)  # clearing the input field
        self.error_message.configure(text=f"Deposited ${amount:.2f} ")  # confirmation message
        self.balance_refresh()  # making sure the value updates
        self.refresh_history()  

    def withdraw_click(self):
        if not self.controller.current_user:  # if no one is logged in
            return
        user_id = self.controller.current_user["user_id"]
        
        amount = float(self.tx_amount.get().strip())

        if amount <= 0:
            self.error_message.configure(text="Amount must be greater than 0.")
            print("Amount must be greater than 0.")
            return
        
        if amount > float(self.controller.current_user["balance"]):
            self.error_message.configure(text="Insufficient balance.")
            print("Insufficient balance.")
            return

        new_balance = backEnd.withdraw(user_id, amount)
        self.controller.current_user["balance"] = new_balance
        self.tx_amount.delete(0, END)
        self.error_message.configure(text=f"Withdrew ${amount:.2f} ")
        self.balance_refresh()
        self.refresh_history()  

    def on_show(self):
        self.error_message.configure(text="")
        self.tx_amount.delete(0, END)
        self.balance_refresh()
        self.refresh_history()  

    def refresh_history(self):
        # clear previous history widgets
        for w in self.history_scroll.winfo_children():
            w.destroy()

        if not self.controller.current_user:  # if we're not logged in (tbh this is just so the thing loads anyway but we don't see it)
            return

        user_id = self.controller.current_user["user_id"]
        tx_list = backEnd.get_wallet_transactions(user_id)

        if not tx_list:  # if theres no transactions yet
            CTkLabel(
                self.history_scroll,
                text="No transactions yet.",
                font=("Open Sans", 12),
                text_color="gray"
            ).pack(pady=10)
            return

        for tx in tx_list:
            row = CTkFrame(self.history_scroll, fg_color="#2b2b2b", corner_radius=8)
            row.pack(fill="x", pady=4, padx=2)

            # left: type + date
            left = CTkFrame(row, fg_color="transparent")
            left.pack(side="left", padx=10, pady=8, fill="x", expand=True)

            tx_type = tx["tx_type"]       # 'DEPOSIT', 'WITHDRAW', 'BET', 'WIN'
            created = tx["created_at"]    # datetime or string depending on connector

            CTkLabel(
                left,
                text=tx_type.title(),
                font=("Open Sans", 12, "bold"),
                text_color="#ff7a00" if tx_type in ("DEPOSIT", "WIN") else "white"
            ).pack(anchor="w")

            CTkLabel(
                left,
                text=str(created),
                font=("Open Sans", 10),
                text_color="gray"
            ).pack(anchor="w")

            # right: amount
            amount = float(tx["amount"])
            sign_color = "green" if amount > 0 else "red"

            CTkLabel(
                row,
                text=f"${amount:.2f}",
                font=("Open Sans", 12, "bold"),
                text_color=sign_color
            ).pack(side="right", padx=10)


# these are the little previews we see of each sports event, an instant of this class will be created for each sports event we want displayed on the home screen
class sports_frame(CTkFrame):
    def __init__(self, parent, controller, event_data):
        super().__init__(parent, fg_color="#2b2b2b", corner_radius=10)  # Dark card style
        self.controller = controller
        self.event = event_data
        
        # Event title (Team1 vs Team2)
        CTkLabel(self, text=f"{self.event.get('team1', 'Team A')} vs {self.event.get('team2', 'Team B')}", 
                font=("Open Sans", 16, "bold"), text_color="white").pack(pady=10, padx=15)
        
        # Sport type and status
        status_frame = CTkFrame(self, fg_color="transparent")
        status_frame.pack(fill="x", padx=15)
        CTkLabel(status_frame, text=self.event.get('sport_type', 'Unknown'), 
                font=("Open Sans", 12), text_color="#ff7a00").pack(side="left")
        
        # Show status badge
        status = self.event.get('bet_status', 'OPEN')
        status_color = {"OPEN": "green", "CLOSED": "red", "SETTLED": "orange"}
        CTkLabel(status_frame, text=status, font=("Open Sans", 10, "bold"), 
                text_color=status_color.get(status, "white"), 
                fg_color="transparent").pack(side="right")
        
        # Details row (date)
        details_frame = CTkFrame(self, fg_color="transparent")
        details_frame.pack(fill="x", padx=15, pady=(0, 10))
        CTkLabel(details_frame, text=str(self.event.get('event_date', 'No date')), 
                font=("Open Sans", 10), text_color="gray").pack()
        
        # CONDITIONAL BET BUTTON - Only show for OPEN events AND logged in users
        if status == "OPEN":
            def on_bet_click(event_data):
                if not controller.current_user:
            # Store pending event and redirect to login
                    controller.frames["betting_frame"].pending_event = event_data
                    controller.show_frame("login_frame")
                    return
        # User is logged in, proceed to betting
                controller.frames["betting_frame"].set_event(event_data)
                controller.show_frame("betting_frame")
    
            CTkButton(self, text="Place Bet", fg_color="#ff7a00", hover_color="#cc6100", text_color="white", 
              command=lambda e=self.event: on_bet_click(e)).pack(pady=10, padx=15)

        else:
            # Show status message for closed/settled events
            status_label = CTkLabel(self, text=f"{status} - No bets available", 
                                  font=("Open Sans", 12), text_color="gray")
            status_label.pack(pady=10)

# this is the screen that will appear whenever you click into a sports event to actually bet on it 
class betting_frame(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.current_event = None  # Will store the event data when accessed from sports_frame
        
        self.build_ui()
    
    def build_ui(self):
        # Title
        CTkLabel(self, text="Place Your Bet", font=("Open Sans", 24, "bold"), text_color="#ff7a00").pack(pady=20)
        
        # Event details card
        self.event_card = CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        self.event_card.pack(fill="x", padx=40, pady=10)

        self.event_title = CTkLabel(self.event_card, text="Select an event", 
                                   font=("Open Sans", 18, "bold"), text_color="white")
        self.event_title.pack(pady=20)
        
        self.event_details = CTkLabel(self.event_card, text="", 
                                    font=("Open Sans", 12), text_color="gray")
        self.event_details.pack(pady=(0, 20))
        
        # Bet selection section
        bet_section = CTkFrame(self, fg_color="transparent")
        bet_section.pack(fill="x", padx=40, pady=10)
        
        CTkLabel(bet_section, text="Select Outcome", 
                font=("Open Sans", 16, "bold")).pack(anchor="w", pady=(20, 10))
        
        # Radio buttons for win/draw/loss (import tkinter at top of file)
        self.outcome_var = StringVar(value="HOME_WIN")
        self.home_radio = CTkRadioButton(bet_section, text="Home Win", 
                                       variable=self.outcome_var, value="HOME_WIN",
                                       font=("Open Sans", 14), radiobutton_width=30, fg_color="#ff7a00", hover_color="#cc6100",
                                       command=self.update_potential_winnings)
        self.home_radio.pack(anchor="w", pady=5)
        
        self.draw_radio = CTkRadioButton(bet_section, text="Draw", 
                                       variable=self.outcome_var, value="DRAW",
                                       font=("Open Sans", 14), radiobutton_width=30, fg_color="#ff7a00", hover_color="#cc6100", 
                                       command=self.update_potential_winnings)
        self.draw_radio.pack(anchor="w", pady=5)
        
        self.away_radio = CTkRadioButton(bet_section, text="Away Win", 
                                       variable=self.outcome_var, value="AWAY_WIN",
                                       font=("Open Sans", 14), radiobutton_width=30, fg_color="#ff7a00", hover_color="#cc6100",
                                       command=self.update_potential_winnings)
        self.away_radio.pack(anchor="w", pady=5)
        
        # Amount input
        amount_frame = CTkFrame(self, fg_color="transparent")
        amount_frame.pack(fill="x", padx=40, pady=20)
        
        CTkLabel(amount_frame, text="Bet Amount ($)", font=("Open Sans", 16, "bold")).pack(anchor="w")
        self.amount_entry = CTkEntry(amount_frame, placeholder_text="Enter amount", 
                                   font=("Open Sans", 14), width=200)
        self.amount_entry.pack(pady=5)
        self.amount_entry.bind("<KeyRelease>", self.on_amount_change)
        
        # Balance warning
        self.balance_warning = CTkLabel(amount_frame, text="", text_color="orange")
        self.balance_warning.pack(anchor="w", pady=2)
        
        # Odds and potential winnings
        self.odds_frame = CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        self.odds_frame.pack(fill="x", padx=40, pady=10)
        
        self.odds_label = CTkLabel(self.odds_frame, text="Odds: -", 
                                 font=("Open Sans", 14, "bold"))
        self.odds_label.pack(pady=10)
        
        self.winnings_label = CTkLabel(self.odds_frame, text="Potential Winnings: $0.00", 
                                     font=("Open Sans", 16, "bold"), text_color="#ff7a00")
        self.winnings_label.pack(pady=10)
        
        # Action buttons
        buttons_frame = CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=40, pady=30)
        
        self.place_bet_btn = CTkButton(buttons_frame, text="Place Bet", text_color="white",
                                     fg_color="#ff7a00", hover_color="#cc6100",
                                     font=("Open Sans", 16, "bold"), height=40,
                                     command=self.place_bet)
        self.place_bet_btn.pack(side="right", padx=10)
        
        CTkButton(buttons_frame, text="Back", fg_color="gray", 
                 hover_color="#666", font=("Open Sans", 14), height=40,
                 command=lambda: self.controller.show_frame("home_frame")).pack(side="right")
    
    def set_event(self, event_data):
        """Called from sports_frame when Place Bet is clicked"""
        self.current_event = event_data
        self.event_title.configure(text=f"{event_data.get('team1', 'Team A')} vs {event_data.get('team2', 'Team B')}")
        self.event_details.configure(text=f"{event_data.get('sport_type', 'Sport')} • {event_data.get('event_date', 'Date')}")
        self.update_potential_winnings()
    
    def on_amount_change(self, event=None):
        amount_text = self.amount_entry.get().strip()
        if amount_text and not amount_text.replace('.', '').isdigit():
            self.amount_entry.delete(0, "end")
            return
        self.update_potential_winnings()
    
    def update_potential_winnings(self):
        if not self.current_event or not self.controller.current_user:
            self.winnings_label.configure(text="Potential Winnings: $0.00")
            self.odds_label.configure(text="Odds: -")
            self.balance_warning.configure(text="")
            self.place_bet_btn.configure(state="disabled")
            return
        
        try:
            amount_text = self.amount_entry.get().strip()
            amount = float(amount_text) if amount_text else 0
            if amount <= 0:
                self.winnings_label.configure(text="Potential Winnings: $0.00")
                self.odds_label.configure(text="Odds: -")
                self.balance_warning.configure(text="")
                self.place_bet_btn.configure(state="disabled")
                return
            
            # Get odds from your sports_events table (single odds column)
            odds = self.current_event.get('odds', 2.0)
            
            # Calculate potential winnings
            potential = amount * odds
            
            # Update UI labels
            self.winnings_label.configure(text=f"Potential Winnings: ${potential:.2f}")
            self.odds_label.configure(text=f"Odds: {self.outcome_var.get()} ({odds:.2f}x)")
            
            # Check user balance
            balance = self.controller.current_user.get("balance", 0)
            if amount > balance:
                self.balance_warning.configure(text="Insufficient balance!", text_color="red")
                self.place_bet_btn.configure(state="disabled")
            else:
                self.balance_warning.configure(text=f"Balance: ${balance:.2f}", text_color="green")
                self.place_bet_btn.configure(state="normal")
            
            # Amount input validation (only numbers/decimals)
            if amount_text and not amount_text.replace('.', '').replace('-', '').isdigit():
                self.amount_entry.delete(0, "end")
                self.amount_entry.insert(0, amount_text[:-1])  # Remove invalid char
                
        except Exception as e:
            print(f"Update winnings error: {e}")
            self.winnings_label.configure(text="Potential Winnings: $0.00")
    
    def place_bet(self):
        if not self.current_event or not self.controller.current_user:
            return
    
        try:
            amount = float(self.amount_entry.get() or 0)
            if amount <= 0:
                return
            
            user_id = self.controller.current_user['user_id']
            event_id = self.current_event['event_id']
            outcome = self.outcome_var.get()
            
            # INSERT THIS LINE HERE - gets odds from your sports_events table
            odds = self.current_event.get('odds', 2.0)
            
            # Map frontend to backend outcomes
            outcome_map = {"HOME_WIN": "TEAM1", "AWAY_WIN": "TEAM2", "DRAW": "DRAW"}
            db_outcome = outcome_map[outcome]
            
            # Call backend
            result = self.controller.backend.place_bet(user_id, event_id, db_outcome, amount, odds)
            if result:
                print(f"Bet placed successfully: {result}")
                self.controller.current_user = self.controller.backend.get_user(
                    self.controller.current_user['username'])  # Refresh user balance
                self.controller.refresh_header()
                self.controller.frames["account_frame"].balance_refresh()
                self.controller.show_frame("home_frame")
            else:
                print("Bet failed - check balance/event status")
                
        except ValueError:
            print("Invalid amount")
        except KeyError:
            print("Invalid outcome selected")

    def on_show(self):
        self.balance_warning.configure(text="")
        self.amount_entry.delete(0, END)
        self.place_bet_btn.configure(state="disabled")

        if self.current_event:
            self.update_potential_winnings()
        else:
            self.event_title.configure(text="Select an event")
            self.event_details.configure(text="")
            self.winnings_label.configure(text="Potential Winnings: $0.00")
            self.odds_label.configure(text="Odds: -")


    

# running the program
if __name__ == "__main__":
    app = app(backEnd)  # creating the instance of app
    app.mainloop()  # actually running it 

