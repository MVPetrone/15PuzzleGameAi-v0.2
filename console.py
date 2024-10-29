from tkinter import *
from tkinter.font import Font
import inspect


class Console:

    Description = """type '-info commands' for all command options"""
    BuiltInCommands = [["-info", "self.update()"]]
    Width, Height = 450, 300

    def __init__(self, app=None, commands=None, _class_=None):
        if commands is None:
            commands = []
        if app is None:
            root = Tk()
            show = True
        else:
            root = app.root
            show = False
        if _class_ is None:
            _class_ = None
        self.app = app
        self.root = root
        self.commands = commands
        for command in Console.BuiltInCommands:
            self.commands.append(command)
        self._class_ = _class_

        self.fonts = {"times": Font(family="Times", size="10"),
                      "times big": Font(family="Times", size="15", weight="bold"),
                      "lucida console": Font(family="Lucida Console", size=11)}

        self.geo = [Console.Width, Console.Height]
        self.pos = [20, 20]

        self.root.bind("<Key-`>", self.toggle_hideshow)
        self.root.bind("<Key-Return>", self.execute)
        self.root.bind("<a>", self.get_functions())
        self.root.bind("<Escape>", self.escape_pressed)

        self.showing = False

        if show:
            self.root.geometry(f"{Console.Width}x{Console.Height}")
            self.show()
            self.root.mainloop()

    def execute(self, event=None):
        # Will ignore request if not visible
        if not self.showing:
            return

        # Will ignore request if not a valid command
        entry = self.get_entry()

        # Collect command keys
        command_keys = self.getCommandKeys()

        # Filter input to validate command
        if entry not in command_keys:
            print("invalid command", entry)
            return

        # Execute command
        i = command_keys.index(entry)
        #try:
        eval(str(self.commands[i][1]))
        #except:
        #    print(f"Command Execution Error for {self.commands[i][1]}")

        self.clear_entry()

    def escape_pressed(self, e=None):
        if self.showing:
            if len(self.entry.get()) > 0:
                self.entry.delete(0, 999)
            else:
                self.hide()

    def show(self):
        self.showing = True
        self.canvas = Canvas(self.root, bg="grey45", width=self.geo[0], height=self.geo[1])
        self.canvas.place(x=self.pos[0], y=self.pos[1])

        self.title = Label(self.canvas, text="CONSOLE", font=self.fonts["times big"], bg="grey45")
        self.title.place(x=5, y=5)

        self.info = Label(self.canvas, text="Type '-info' for list of commands", font=self.fonts["times"], bg="grey45")
        self.info.place(x=5, y=30)

        self.entry = Entry(self.canvas, bd=2, width=40, relief=FLAT, fg="white", bg="grey40", font=self.fonts["lucida console"])
        self.entry.place(x=20, y=Console.Height - 20 - 20)
        self.entry.focus()

        self.commandListbox = Listbox(self.canvas, width=50, height=10)
        self.commandListbox.place(x=20, y=Console.Height - 20 - 20 - 200)

    def hide(self):
        self.showing = False
        self.canvas.destroy()

    def toggle_hideshow(self, event=None):
        if self.showing:
            self.hide()
        else:
            self.show()

    def set_entry(self, value):
        if self.showing:
            self.entry.config(text=value)

    def get_entry(self):
        return self.entry.get()

    def clear_entry(self):
        self.entry.delete(0, 999)

    def getCommandKeys(self):
        command_keys = []
        for command in self.commands:
            command_keys.append(command[0])
        return command_keys

    def get_classes(self):
        classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        return classes

    def get_functions(self):
        methods = inspect.getmembers(self._class_, predicate=inspect.ismethod)
        return methods

    def add_command(self, name, command):
        """Command: [name, command]"""

        self.commands.append([str(name), str(command)])

    def update(self):
        self.commandListbox.delete(0, 9999)
        for i in range(1, len(self.commands)):
            self.commandListbox.insert(i, self.getCommandKeys()[i])


if __name__ == '__main__':
    con = Console()
