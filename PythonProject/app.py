from tkinter import *   # syntax for importing all classes from tkinter
from mydb import Database
from tkinter import messagebox

class NLPApp:

    def __init__(self):

        # creating database object
        self.dbo = Database()

        # loading login gui

        self.root = Tk()    # Tk is the main class inside tkinter so here we are making an object of this class
        self.root.title("NLPApp")   # changing the title of the app
        self.root.iconbitmap("resources/favicon.ico")   # changing the icon in the title bar of the app
        self.root.geometry("350x600")   # adjusting the size of gui app
        self.root.configure(bg = "red")    # adjusting the background color of the app

        self.login_gui()

        self.root.mainloop()   # the role of this method is to hold the gui on the screen


    def login_gui(self):
        """login functionality and gui operations"""

        self.clear()    # clear the existing gui first

        heading = Label(self.root, text = "NLP Application GUI", bg = "red", fg = "white")    # display heading on the app using Label class; it takes two arguements: gui object and text to display
        heading.pack(pady = (30, 30))    # to display heading ui component on the app, we need to explicitly tell the tkinter to put that in gui; to do this we use geometry managers; there are two geometry managers in tkinter: `pack` and `grid`, we will use pack in this case; `pady` is used to do padding in y direction by 30 pixels in both upward and downward side
        heading.configure(font = ("verdana", 18, "italic"))     # changing the writing style of the font in heading

        # creating text for email entry
        label1 = Label(self.root, text = "Enter your email")
        label1.pack(pady = (10,10))
        self.email_input = Entry(self.root, width = 30)     # creating entry box for email; width is the width of entry box
        self.email_input.pack(pady = (5,10), ipady = 3)     # `ipady` is the internal padding and it means height of the entry box

        # creating text for password entry
        label2 = Label(self.root, text="Enter your password")
        label2.pack(pady=(10, 10))
        self.password_input = Entry(self.root, width=30, show = "*")    # `show` is for showing the typed password in ******.. from
        self.password_input.pack(pady=(5, 10), ipady=3)


        # creating login button
        login_btn = Button(self.root, text = "LOGIN", width = 20, height = 2, command = self.perform_login)
        login_btn.pack(pady = (10,10))

        #creating text and button for registration of new users
        label3 = Label(self.root, text="Not a Member?")
        label3.pack(pady=(20, 10))

        redirect_btn = Button(self.root, text="Register Now", command = self.register_gui)      # command is for detecting if somebody has clicked on the button and what to do if the button has been clicked
        redirect_btn.pack(pady=(10, 10))


    def register_gui(self):
        """register functionality and gui operations"""

        self.clear()    # clear the existing gui first


        # registration flow similar to login
        heading = Label(self.root, text="NLP Application GUI", bg="red", fg="white")
        heading.pack(pady=(30, 30))
        heading.configure(font=("verdana", 18, "italic"))

        label0 = Label(self.root, text="Enter your name")
        label0.pack(pady=(10, 10))
        self.name_input = Entry(self.root, width=30)
        self.name_input.pack(pady=(5, 10), ipady=3)


        # creating text for email entry
        label1 = Label(self.root, text="Enter your email")
        label1.pack(pady=(10, 10))
        self.email_input = Entry(self.root, width=30)
        self.email_input.pack(pady=(5, 10), ipady=3)

        # creating text for password entry
        label2 = Label(self.root, text="Enter your password")
        label2.pack(pady=(10, 10))
        self.password_input = Entry(self.root, width=30, show="*")  # `show` is for showing the typed password in ******.. from
        self.password_input.pack(pady=(5, 10), ipady=3)

        # creating login button
        register_btn = Button(self.root, text="REGISTER", width=20, height=2, command = self.perform_registration)
        register_btn.pack(pady=(10, 10))

        # creating text and button for registration of new users
        label3 = Label(self.root, text="Already a Member?")
        label3.pack(pady=(20, 10))

        redirect_btn = Button(self.root, text="Login Now", command=self.login_gui)
        redirect_btn.pack(pady=(10, 10))


    def clear(self):
        """clear the existing gui"""

        for i in self.root.pack_slaves():
            i.destroy()


    def perform_registration(self):

        # fetch data from gui
        name = self.name_input.get()
        email = self.email_input.get()
        password = self.password_input.get()

        response = self.dbo.add_data(name, email, password)
        if response:
            messagebox.showinfo("Success", "Registration successful. You can login now.")
        else:
            messagebox.showerror("Error", "Email already exists.")


    def perform_login(self):

        # fetch data from gui
        email = self.email_input.get()
        password = self.password_input.get()

        response = self.dbo.search(email, password)
        if response:
            messagebox.showinfo("Success", "Login successful.")
            self.home_gui()
        else:
            messagebox.showerror("Error", "Incorrect email or password.")


    def home_gui(self):

        self.clear()

        heading = Label(self.root, text="NLP Application GUI", bg="red", fg="white")
        heading.pack(pady=(30, 30))
        heading.configure(font=("verdana", 18, "italic"))

        sentiment_btn = Button(self.root, text="Sentiment Analysis", width=25, height=3, command=self.sentiment_gui)
        sentiment_btn.pack(pady=(10, 10))

        ner_btn = Button(self.root, text="Named Entity Recognition", width=25, height=3, command=self.perform_registration)
        ner_btn.pack(pady=(10, 10))

        emotion_btn = Button(self.root, text="Emotion Detection", width=25, height=3, command=self.perform_registration)
        emotion_btn.pack(pady=(10, 10))

        logout_btn = Button(self.root, text="Logout", command=self.login_gui)
        logout_btn.pack(pady=(10, 10))


    def sentiment_gui(self):

        self.clear()

        heading = Label(self.root, text="NLP Application GUI", bg="red", fg="white")
        heading.pack(pady=(30, 30))
        heading.configure(font=("verdana", 18, "italic"))

        heading2 = Label(self.root, text="Sentiment Analysis", bg="red", fg="white")
        heading2.pack(pady=(10, 20))
        heading2.configure(font=("verdana", 14))

        label1 = Label(self.root, text="Enter the text")
        label1.pack(pady=(20, 10))
        self.sentiment_input = Entry(self.root, width=30)
        self.sentiment_input.pack(pady=(5, 10), ipady=3)

        sentiment_btn = Button(self.root, text="Analyze Sentiment", command = self.do_sentiment_analysis)
        sentiment_btn.pack(pady=(10, 10))

        self.sentiment_result = Label(self.root, text="", bg = "red", fg = "white")
        self.sentiment_result.pack(pady=(20, 10))
        self.sentiment_result.configure(font=("verdana", 12))

        goback_btn = Button(self.root, text="Go Back", command = self.home_gui)
        goback_btn.pack(pady=(10, 10))


    def do_sentiment_analysis(self):


nlp = NLPApp()