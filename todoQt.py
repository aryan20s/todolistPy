from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont

from functools import partial
import os

#some constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 350

DIALOG_WIDTH = 300
DIALOG_HEIGHT = 100

#this is our window class
class TodoAppWindow(QMainWindow):
    #when we create the window, this function is called, and we can use it to initialize the window
    def __init__(self):
        super().__init__()
        
        #this sets our window title, size, and layout
        self.setWindowTitle("To-Do List")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.generalLayout = QVBoxLayout()
        
        #this creates two fonts, one default, one strikethrough
        self.defaultFont = QFont("Arial")
        self.strikeOutFont = QFont("Arial")
        self.strikeOutFont.setStrikeOut(True)
        
        #this defines a central widget which defines the layout etc, then we set it to the window, and create the ui elements.
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self._createUI()
        
        #finally, we apply a style to our app
        _style = """
        QListWidget {
            color: #FFFFFF;
            background-color: #D0D0E0;
        }

        QListWidget::item {
            height: 50px;
        }

        QCheckBox {
            color: #222222;
            font-size: 18px;
        }

        QListWidget::item:selected {
            background-color: #9999DD;
        }

        QLabel {
            background-color: #FFFFFF;
            qproperty-alignment: AlignCenter;
        }

        QPushButton {
            background-color: #D0D0E0;
            padding: 20px;
            font-size: 20px;
        }"""
        self.setStyleSheet(_style)
    
    #this gets run whenever the task list is updated, for example if you add or remove a task, or check or uncheck a task
    #its function is to save everything to disk
    def taskListUpdated(self):
        #this basically appends the name of the task, then a \x06 character for splitting, then the boolean which tells whether the task is done or not on every line, like so:
        #task 1\x06False
        #task 2\x06True
        
        datFile = ""
        for checkBox in self.taskCheckBoxes:
            datFile += checkBox.text() + "\x06" + str(checkBox.isChecked())
            #this is to make sure that no \n is added at the end, otherwise there would be one empty line at the end
            if checkBox != self.taskCheckBoxes[-1]:
                datFile += "\n"
        
        #after we have added all the tasks to the list, we save it to a file called "tasks.dat"
        with open("tasks.dat", "w") as tasksFile:
            tasksFile.write(datFile)
    
    #this gets run whenever a checkbox is checked or unchecked, and is used to apply the strikthrough effect
    def checkBoxStateChanged(self):
        #we check every checkbox to see if its checkedd
        for checkBox in self.taskCheckBoxes:
            if checkBox.isChecked():
                checkBox.setFont(self.strikeOutFont) #apply strikethrough if its checked
            else:
                checkBox.setFont(self.defaultFont) #otherwise use the default font
        
        self.taskListUpdated()
    
    #this gets run whenever the "Add Task" button is pressed, and displays the dialog
    def _addTaskDialog(self):
        #this creates the dialog and sets it's size and title
        addDialog = QDialog()
        addDialog.setFixedSize(DIALOG_WIDTH, DIALOG_HEIGHT)
        addDialog.setWindowTitle("Add Task")
        addDialog.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint) #this line is just there to disable a feature we don't need
        
        #this adds the text box, sets it's empty text, size, and position
        taskNameBox = QLineEdit(addDialog)
        taskNameBox.setPlaceholderText("Task Name")
        taskNameBox.resize(DIALOG_WIDTH - 30, DIALOG_HEIGHT - 60)
        taskNameBox.move(15, 10)
        
        #this adds the "Add Task" button, sets it's text, size, and position
        okButton = QPushButton(addDialog)
        okButton.setText("Add Task")
        okButton.resize((DIALOG_WIDTH - 40) // 2, 30)
        okButton.move(15, DIALOG_HEIGHT - 40)
        
        #this adds the "Cancel" button, sets it's text, size, and position
        cancelButton = QPushButton(addDialog)
        cancelButton.setText("Cancel")
        cancelButton.resize((DIALOG_WIDTH - 40) // 2, 30)
        cancelButton.move(25 + (DIALOG_WIDTH - 40) // 2, DIALOG_HEIGHT - 40)
        
        #this is the function that gets run when the "Add Task" button is pressed, which adds the task and closes the dialog
        def okButtonPressed():
            self._addTask({"name": taskNameBox.text() if taskNameBox.text() != "" else "Task Name", "done": False})
        
            #this saves the task list to disk
            self.taskListUpdated()
            addDialog.accept()
        
        #this links the buttons to their respective functions
        okButton.clicked.connect(okButtonPressed)
        cancelButton.clicked.connect(lambda: addDialog.accept()) #this just closes the dialog
        
        #this executes the add task dialog
        addDialog.exec_()
    
    #this is an internal function that is used to add a task
    def _addTask(self, task):
        #first we create a checkbox, then if the task is already done, we check it and set the font to strikethrough, otherwise the default font
        taskCheckBoxWidget = QCheckBox(task["name"])
        if task["done"]:
            taskCheckBoxWidget.setChecked(True)
            taskCheckBoxWidget.setFont(self.strikeOutFont)
        else:
            taskCheckBoxWidget.setFont(self.defaultFont)
        
        #we link the check box to the function that gets run when a checkbox is checked or unchecked
        taskCheckBoxWidget.stateChanged.connect(self.checkBoxStateChanged)
        #now we add it to a list of checkboxes which we store internally
        self.taskCheckBoxes.append(taskCheckBoxWidget)
        
        #we now create a QListWidgetItem, and add it to the list of tasks
        taskWidget = QListWidgetItem()
        self.tasks.append(taskWidget) #we also add this to a list of QListWidgetItems which we store internally
        self.tasksLayout.addItem(taskWidget)
        self.tasksLayout.scrollToItem(taskWidget) #now we scroll to the item to make sure its visible
        
        #now we connect this QListWidgetItem to the checkbox we created
        #the reason for doing this is that we cannot insert a checkbox into a list, so we insert a QListWidgetItem and link the checkbox to it
        self.tasksLayout.setItemWidget(taskWidget, taskCheckBoxWidget)
        
        #this just makes it so that the item gets selected
        self.listItemClicked(taskWidget)
    
    def _removeTask(self):
        #this is to ensure no out of bounds operations occur
        if self.currentItemIdx < 0 or self.currentItemIdx >= len(self.tasks):
            return
        
        #this removes the item from the list view
        self.tasksLayout.takeItem(self.currentItemIdx)
        #this deletes the checkbox
        del self.taskCheckBoxes[self.currentItemIdx]
        #this deletes the QListWidgetItem that the checkbox was linked to
        del self.tasks[self.currentItemIdx]
        
        #we deselect all tasks, and set the current selected task to -1 so that no issues with the "Delete Task" button occur
        for task in self.tasks:
            task.setSelected(False)
            self.currentItemIdx = -1
        
        #this saves the task list to disk
        self.taskListUpdated()
    
    #this is run when a list item (task) is clicked, and simply selects the item visually, and sets the current selected task to that index
    def listItemClicked(self, item):
        self.currentItemIdx = self.tasksLayout.indexFromItem(item).row()
        item.setSelected(True)
    
    #this function creates the ui elements
    def _createUI(self):
        #we initialize some variables
        self.tasks = []
        self.taskCheckBoxes = []
        self.tasksLayout = QListWidget()
        self.currentItemIdx = -1
        
        #we link the task list to the function that gets run when any list element is clicked
        self.tasksLayout.itemClicked.connect(self.listItemClicked)
        #we add our tasks list layout to the main layout of the app
        self.generalLayout.addWidget(self.tasksLayout)
        #we resize the tasks list layout to be the same width as the window, but 50 pixels shorter
        self.tasksLayout.resize(WINDOW_WIDTH, WINDOW_HEIGHT - 50)
        
        #we add each task after loading them using the function
        for task in self._loadTasks():
            self._addTask(task)
        
        #we use a grid layout for the buttons
        self.buttonsLayout = QGridLayout()
        #we set the size of the first 2 columns here, the third one is automatically set
        self.buttonsLayout.setColumnMinimumWidth(0, 250)
        self.buttonsLayout.setColumnMinimumWidth(1, 250)
        self.generalLayout.addLayout(self.buttonsLayout) #we add our buttons layout to the main layout of the app
        
        #we create an "Add Task" button, link it to its function, and add it to the buttons layout
        self.addTaskButton = QPushButton("Add Task")
        self.addTaskButton.clicked.connect(self._addTaskDialog)
        self.buttonsLayout.addWidget(self.addTaskButton, 0, 0)
        
        #we create a "Delete Task" button, link it to its function, and add it to the buttons layout
        self.deleteTaskButton = QPushButton("Delete Selected Task")
        self.deleteTaskButton.clicked.connect(self._removeTask)
        self.buttonsLayout.addWidget(self.deleteTaskButton, 0, 1)
        
        #this function is run when the info button is pressed
        def infoMessage():
            #this creates the dialog and sets it's size and title
            infoMsgBox = QDialog()
            infoMsgBox.setFixedSize(DIALOG_WIDTH - 100, DIALOG_HEIGHT)
            infoMsgBox.setWindowTitle("Info")
            infoMsgBox.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint) #this line is just there to disable a feature we don't need
            
            #this adds a label with the credits text, and moves it to the correct position
            infoText = QLabel(infoMsgBox)
            infoText.setText("placeholder")
            infoText.move(10, 2)
            
            #now we execute the info dialog
            infoMsgBox.exec_()
        
        #we create an "Info" button, link it to its function, and add it to the buttons layout
        self.infoButton = QPushButton("Info")
        self.infoButton.clicked.connect(infoMessage)
        self.buttonsLayout.addWidget(self.infoButton, 0, 2)
    
    #this function loads the tasks from the "tasks.dat" file when the program first starts
    def _loadTasks(self):
        tasks = []
        #this checks if the file exists
        if os.path.exists("tasks.dat"):
            #if yes, we open it and read it line by line
            with open("tasks.dat", "r") as tasksFile:
                for line in tasksFile.readlines():
                    #we now split the line using the \x06 character from before
                    splitLine = line.split("\x06")
                    #the first splitted element is the name, and the second is whether the task was done
                    tasks.append({"name": splitLine[0], "done": splitLine[1] == "True\n"})
        
        return tasks

#this creates a new qt application, and a window
#then we show the window, and execute the application
todoApp = QApplication([])
todoAppWindow = TodoAppWindow() #this runs the __init__ function of our app window and creates it
todoAppWindow.show()
todoApp.exec()