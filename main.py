# from backEnd import 
from frontEnd import app
import backEnd as backEnd

# running the program
if __name__ == "__main__":
    app = app(backEnd)  # creating the instance of app
    app.mainloop()  # actually running it 