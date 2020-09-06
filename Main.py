####################################################################################
# Jiten Dhandha, 2020                                                              #
# CFit is a curve fitting tool in python, based on the method of least squares.    #
# It comes equipped with some standard functions and a graphical user interface.   #
#                                                                                  #
# Inspired by: LSFR.py, Abie Marshall, The University of Manchester, 2016          #
####################################################################################



####################################################################################
#                                    LIBRARIES                                     #
####################################################################################

import Fitting as fit
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk

####################################################################################
#                                  USER INTERFACE                                  #
####################################################################################

class GUI:
    
    def __init__(self,master=None):
        
        ############################################################################
        #                            INTERFACE SETTINGS                            #
        ############################################################################

        self.master = master
        master.title('CFit (Curve fitting Tool)')
        master.geometry('1000x700')     #Size of the window
        master.resizable(0,0)           #Making window un-resizeable
        master.configure(background='white')
        
        #Relative sizes of each row and column containing frames
        master.grid_rowconfigure(0, weight=5)
        master.grid_rowconfigure(1, weight=4)
        master.grid_rowconfigure(2, weight=6)
        master.grid_rowconfigure(3, weight=2)
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        
        ############################################################################
        #                                  FRAMES                                  #
        ############################################################################
         
        self.frame1 = tk.LabelFrame(master, text=' Data Options ', background='white')
        self.frame1.grid(row=0, rowspan=1, column=0, columnspan=1, sticky='NEWS', padx=2,pady=2)

        self.frame2 = tk.LabelFrame(master, text=' File preview ', background='white')
        self.frame2.grid(row=0, rowspan=1, column=1, columnspan=1, sticky='NEWS', padx=2,pady=2)
        
        self.frame3 = tk.LabelFrame(master, text=' Plot Options ', background='white')
        self.frame3.grid(row=1, rowspan=1, column=0, columnspan=2, sticky='NEWS', padx=2,pady=2)
        
        self.frame4 = tk.LabelFrame(master, text=' Fit Options ', background='white')
        self.frame4.grid(row=2, rowspan=1, column=0, columnspan=2, sticky='NEWS', padx=2,pady=2)

        self.frame5 = tk.Frame(master, background='white')
        self.frame5.grid(row=3, rowspan=1, column=0, columnspan=2, sticky='NEWS', padx=2,pady=2)
        
        ############################################################################
        #                                 VARIABLES                                #
        ############################################################################
        
        self.fileLocation = str    #String holding location of file   
        self.fileCheck = int       #Integer denoting whether the file was successfully read

        self.fileStatus = tk.StringVar()    #String holding status of the file
 
        #Types of fits
        functionsList = list(fit.functions.keys())
        self.fitTypes = ['Polynomial'] + functionsList[0:6] + ['Other functions'] + functionsList[6:]   
        self.fitType = tk.StringVar()       #String holding the current type of fit chosen

        self.viewGrid = tk.IntVar()         #Boolean holding whether the user wants to see gridlines in plot
        self.viewParameters = tk.IntVar()   #Boolean holding whether the user wants to see fitting parameters in plot
        self.viewResiduals = tk.IntVar()   #Boolean holding whether the user wants to see a residuals plot

        self.fitTypeStr = tk.StringVar()    #String holding the the display of function form

        self.fitCheck = int          #Integer denoting whether the fit was successful
        self.fitStatus = tk.StringVar()     #String holding status of the fit

        ############################################################################
        #                                 FRAMES 1                                 #
        ############################################################################ 
        
        #Fixing the size of the each row and column
        self.frame1.grid_propagate(False)
        #Relative sizes of each row and column
        for i in range(0,2):
            self.frame1.grid_columnconfigure(i, weight=1)
        for i in range(0,3):
            self.frame1.grid_rowconfigure(i, weight=1)       

        self.fileLocationLabel = tk.Label(self.frame1, text ='File directory: ', background='white')
        self.fileLocationLabel.grid(row=0, rowspan=1, column=0, columnspan=1, sticky='NEWS', padx=5, pady=5)
        
        self.fileLocationEntry = tk.Entry(self.frame1, justify='center', foreground='blue')
        self.fileLocationEntry.insert(0, string='(no directory selected)')
        self.fileLocationEntry.configure(state='readonly')
        self.fileLocationEntry.grid(row=0, rowspan=1, column=1, columnspan=1, sticky='NEWS', padx=5, pady=5)  

        self.browseFileButton = tk.Button(self.frame1, text="Load data", command=self.browseFileFunc)
        self.browseFileButton.grid(row=1, rowspan=1, column=0, columnspan=2, sticky='NEWS', padx=5, pady=5) 
        
        self.fileStatusLabel = tk.Label(self.frame1, justify='center', textvariable=self.fileStatus)
        self.fileStatusLabel.grid(row=2, rowspan=1, column=0, columnspan=2, sticky='NEWS', padx=5, pady=5) 

        ############################################################################
        #                                 FRAMES 2                                 #
        ############################################################################ 

        #Fixing the size of the each row and column
        self.frame2.grid_propagate(False)
        #Relative sizes of each row and column
        self.frame2.grid_columnconfigure(0, weight=1)
        self.frame2.grid_rowconfigure(0, weight=1)

        self.filePreviewListBox = tk.Listbox(self.frame2, borderwidth=0, height=5)
        self.filePreviewListBox.configure(state='disable')
        self.filePreviewListBox.grid(row=0, rowspan=1, column=0, columnspan=1, sticky='NEWS', padx=5, pady=5)

        ############################################################################
        #                                 FRAMES 3                                 #
        ############################################################################  
        
        #Fixing the size of the each row and column
        self.frame3.grid_propagate(False)
        #Relative sizes of each row and column
        for i in range(0,3):
            self.frame3.grid_columnconfigure(i, weight=1)
        for i in range(0,3):
            self.frame3.grid_rowconfigure(i, weight=1)

        self.plotTitleLabel = tk.Label(self.frame3, text = 'Plot title: ', background='white')
        self.plotTitleLabel.grid(row=0, rowspan=1, column=0, columnspan=1, sticky='NEWS', padx=5, pady=2)

        self.plotTitleEntry = tk.Entry(self.frame3, foreground='blue', bd='2', relief='ridge')
        self.plotTitleEntry.grid(row=0, rowspan=1, column=1, columnspan=1, sticky='NEWS', padx=5, pady=2)

        self.xAxisTitleLabel = tk.Label(self.frame3, text = 'X axis label: ', background='white')
        self.xAxisTitleLabel.grid(row=1, rowspan=1, column=0, columnspan=1, sticky='NEWS', padx=5, pady=2)

        self.xAxisTitleEntry = tk.Entry(self.frame3, foreground='blue', bd='2', relief='ridge')
        self.xAxisTitleEntry.grid(row=1, rowspan=1, column=1, columnspan=1, sticky='NEWS', padx=5, pady=2)

        self.yAxisTitleLabel = tk.Label(self.frame3, text = 'Y axis label: ', background='white')
        self.yAxisTitleLabel.grid(row=2, rowspan=1, column=0, columnspan=1, sticky='NEWS', padx=5, pady=2)

        self.yAxisTitleEntry = tk.Entry(self.frame3, foreground='blue', bd='2', relief='ridge')
        self.yAxisTitleEntry.grid(row=2, rowspan=1, column=1, columnspan=1, sticky='NEWS', padx=5, pady=2)

        self.viewGridCheckButton = tk.Checkbutton(self.frame3, text="Grid lines", variable=self.viewGrid)
        self.viewGridCheckButton.grid(row=0, rowspan=1, column=2, columnspan=1, sticky='NEWS', padx=5, pady=2)

        self.viewParametersCheckButton = tk.Checkbutton(self.frame3, text="View parameters", variable=self.viewParameters)
        self.viewParametersCheckButton.grid(row=1, rowspan=1, column=2, columnspan=1, sticky='NEWS', padx=5, pady=2)

        self.viewResidualsCheckButton = tk.Checkbutton(self.frame3, text="View residuals", variable=self.viewResiduals)
        self.viewResidualsCheckButton.grid(row=2, rowspan=1, column=2, columnspan=1, sticky='NEWS', padx=5, pady=2)

        ############################################################################
        #                                 FRAMES 4                                 #
        ############################################################################     

        #Fixing the size of the each row and column
        self.frame4.grid_propagate(False)
        #Relative sizes of each row and column
        self.frame4.grid_columnconfigure(0, weight=1)
        self.frame4.grid_columnconfigure(1, weight=2)
        self.frame4.grid_columnconfigure(2, weight=4)
        for i in range(4):
            self.frame4.grid_rowconfigure(i, weight=1)

        self.fitTypeLabel = tk.Label(self.frame4, text = 'Fit type: ', background='white')
        self.fitTypeLabel.grid(row=0, rowspan=1, column=0, columnspan=1, sticky='NEWS', padx=5, pady=5)

        self.fitTypeOptionMenu = ttk.OptionMenu(self.frame4, self.fitType, 'None', *self.fitTypes, command=self.fitTypeOptionMenuFunc)
        self.fitTypeOptionMenu.configure(width=25)
        self.fitTypeOptionMenu['menu'].entryconfigure(0, state = "disabled")
        self.fitTypeOptionMenu['menu'].entryconfigure(7, state = "disabled")
        self.fitTypeOptionMenu.grid(row=0, rowspan=1, column=1, columnspan=1, sticky='NEWS', padx=5, pady=5)
       
        self.fitTypeStrLabel = tk.Label(self.frame4,textvariable=self.fitTypeStr,width=25,foreground='blue')
        self.fitTypeStrLabel.grid(row=0, rowspan=1, column=2, columnspan=1, sticky='NEWS', padx=5, pady=5)
        
        self.plotRawDataButton = tk.Button(self.frame4, text="Plot raw data", command=self.plotRawDataButtonFunc)
        self.plotRawDataButton.grid(row=1, rowspan=2, column=0, columnspan=1, sticky='NEWS', padx=5, pady=5)
        
        self.fitDataAutoButton = tk.Button(self.frame4, text="Fit data automatically", command=self.fitDataAutoButtonFunc) 
        
        self.fitDataManButton = tk.Button(self.frame4, text="Fit data using my guess:", command=self.fitDataManButtonFunc)

        self.fitDataManEntry = tk.Entry(self.frame4, justify='center')

        self.fitStatusLabel = tk.Label(self.frame4, justify='center', textvariable=self.fitStatus)
        self.fitStatusLabel.grid(row=3, rowspan=1, column=0, columnspan=3, sticky='NEWS', padx=5, pady=5)
        
        ############################################################################
        #                                 FRAMES 5                                 #
        ############################################################################  
        
        #Fixing the size of the each row and column
        self.frame5.grid_propagate(False)
        #Relative sizes of each row and column
        self.frame5.grid_columnconfigure(0, weight=8)
        self.frame5.grid_columnconfigure(1, weight=1)
        self.frame5.grid_columnconfigure(2, weight=8)
        self.frame5.grid_rowconfigure(0, weight=1)

        self.clearButton = tk.Button(self.frame5, text="Clear", width=10, command=self.clear)
        self.clearButton.grid(row=0, rowspan=1, column=0, columnspan=1, sticky='NES', padx=5, pady=5)    
        
        self.helpButton = tk.Button(self.frame5, text="Help", width=8, command=self.help)
        self.helpButton.grid(row=0, rowspan=1, column=1, columnspan=1, sticky='NEWS', padx=5, pady=5)

        self.aboutButton = tk.Button(self.frame5, text="About", width=10, command=self.about)
        self.aboutButton.grid(row=0, rowspan=1, column=2, columnspan=1, sticky='NWS', padx=5, pady=5)

    ############################################################################
    #                                FUNCTIONS                                 #
    ############################################################################ 
    '''
    This function adds a preview of the file in the file preview box.
    '''
    def setFilePreview(self):

        #Clearing the preview
        self.filePreviewListBox.configure(state='normal')
        self.filePreviewListBox.delete(0, 'end')

        #Opening the file and adding it to the preview box
        lineNum = 0
        with open(self.fileLocation, 'r') as file:
            for line in file:
                self.filePreviewListBox.insert(lineNum, line)
                lineNum += 1

    '''
    This function lets the user browse the file, calls the readFile() function in
    Fitting.py, sets file preview sets file status for user to see.
    '''
    def browseFileFunc(self):

        #Clearing everything in the GUI first
        self.clear()

        #Letting user browse the file and calling readFile() in Fitting.py
        self.fileLocation = filedialog.askopenfilename(title='Choose a file')
        self.fileCheck = fit.readFile(self.fileLocation)

        #Showing the directory of the file
        self.fileLocationEntry.configure(state='normal')
        self.fileLocationEntry.delete(0,'end')
        if(self.fileLocation==''):
            self.fileLocationEntry.insert(0, string='(no directory selected)')
        else:
            self.fileLocationEntry.insert(0, string=self.fileLocation)
        self.fileLocationEntry.configure(state='readonly')

        #Setting file status
        if(self.fileCheck==0):
            self.fileStatus.set("File opened successfully!")
        elif(self.fileCheck==1):
            self.fileStatus.set("")
        elif(self.fileCheck==2):
            self.fileStatus.set("Not a .txt or .csv file!")
        elif(self.fileCheck==3):
            self.fileStatus.set("Couldn't parse file properly.")
        elif(self.fileCheck==4):
            self.fileStatus.set("File must contain 2 or 3 columns!")
        elif(self.fileCheck==5):
            self.fileStatus.set("File contains NaNs or Infs.")
        elif(self.fileCheck==6):
            self.fileStatus.set("Y-errors need to be a positive number!")

        #Checking if file can be previewed or not
        if(self.fileCheck!=1 and self.fileCheck!=2):
            self.setFilePreview()
    
    '''
    This function is called when the user selects a function from the drop down.
    It sets the preview of the form of the function and also some variables in the 
    Fitting.py file.
    '''
    def fitTypeOptionMenuFunc(self, event):
        
        #Setting the function and its preview
        fit.function = self.fitType.get()
        fit.numberOfParameters = fit.functions[fit.function].numberOfParameters
        self.fitTypeStr.set(fit.functions[fit.function].unicodeFuncStr)
        self.fitDataManEntry.delete(0,'end')
        string = ''
        for param in fit.functions[fit.function].unicodeParametersStr:
            string += param + '=1, '
        string = string[:-2]
        self.fitDataManEntry.insert(0,string)
            
        #Placing the fitting buttons and setting fit status
        self.fitDataAutoButton.grid(row=1, rowspan=1, column=1, columnspan=1, sticky='NEWS', padx=5, pady=5)   
        self.fitDataManButton.grid(row=2, rowspan=1, column=1, columnspan=1, sticky='NEWS', padx=5, pady=5)
        self.fitDataManEntry.grid(row=2, rowspan=1, column=2, columnspan=1, sticky='NEWS', padx=5, pady=5)
        self.fitStatus.set("")

    '''
    This function calls the relevant function in Fitting.py to plot the raw data.
    '''
    def plotRawDataButtonFunc(self):
        if(self.fileCheck==0):
            fit.plotRawData(self.plotTitleEntry.get(),self.xAxisTitleEntry.get(),self.yAxisTitleEntry.get(),self.viewGrid.get())

    '''
    This function calls the relevant functions in Fitting.py to fit a polynomial
    or a custom function automatically. It also sets the fit status and plots the 
    raw data with the best fit in case it is successful.
    '''
    def fitDataAutoButtonFunc(self):

        #Checking if the data file was successfully opened
        if(self.fileCheck==0):

            #Calling the relevant function in Fitting.py to handle the rest
            self.fitCheck = fit.guessParameters()
            
            #Checking if the fit was successful and showing the plot.
            if(self.fitCheck==0):
                self.fitStatus.set("Fit attempt successful!")
                fit.plotFitData(self.plotTitleEntry.get(),self.xAxisTitleEntry.get(),self.yAxisTitleEntry.get(),self.viewGrid.get(),self.viewParameters.get(),self.viewResiduals.get())
            elif(self.fitCheck==1):
                self.fitStatus.set("Max iterations performed but couldn't find a fit!")
            elif(self.fitCheck==2):
                self.fitStatus.set("Number of data points is less than number of fitting parameters!")

    '''
    This function calls the relevant functions in Fitting.py to fit a function manually 
    from the guess parameters input by the user.
    '''
    def fitDataManButtonFunc(self):

        #Checking if the data file was successfully opened
        if(self.fileCheck==0):

            #Calling the relevant function in Fitting.py to handle the rest
            self.fitCheck = fit.manualParameters(self.fitDataManEntry.get())
            
            #Checking if the fit was successful and showing the plot.
            if(self.fitCheck==0):
                self.fitStatus.set("Fit attempt successful!")
                fit.plotFitData(self.plotTitleEntry.get(),self.xAxisTitleEntry.get(),self.yAxisTitleEntry.get(),self.viewGrid.get(),self.viewParameters.get(),self.viewResiduals.get())
            elif(self.fitCheck==1):
                self.fitStatus.set("Max iterations performed but couldn't find a fit!")
            elif(self.fitCheck==2):
                self.fitStatus.set("Number of data points is less than number of fitting parameters!")
            elif(self.fitCheck==3):
                self.fitStatus.set("Invalid parameters!")

    '''
    This function resets everything in the GUI. 
    '''
    def clear(self):

        #RESETTING THINGS IN FITTING FILE
        #Data related variables
        fit.data = []
        fit.x = []
        fit.y = []
        fit.y_err = []
        fit.numberOfDataPoints = int
        fit.ERR = bool
        #Fit function related variables
        fit.function = ''
        fit.numberOfParameters = int
        #Fitting variables
        fit.fitStructure = []
        fit.fitParameters = []
        fit.fitErrors = []
        fit.chiSquared = float
        fit.redChiSquared = float
        fit.redChiSquaredLimits = []

        #RESETTING THINGS IN INTERFACE
        #Frame 1
        self.fileLocation = str
        self.fileLocationEntry.configure(state='normal')
        self.fileLocationEntry.delete(0,'end')
        self.fileLocationEntry.insert(0, string='(no directory selected)')
        self.fileLocationEntry.configure(state='readonly')
        self.fileCheck = int
        self.fileStatus.set("")
        #Frame 2
        self.filePreviewListBox.delete(0, 'end')
        self.filePreviewListBox.configure(state='disable')  
        #Frame 3
        self.plotTitleEntry.delete(0, 'end')
        self.xAxisTitleEntry.delete(0, 'end')
        self.yAxisTitleEntry.delete(0, 'end')
        self.viewGrid.set(0) 
        self.viewParameters.set(0)
        self.viewResiduals.set(0)
        #Frame 4
        self.fitType.set("None")
        self.fitTypeStr.set("")
        self.fitCheck = bool
        self.fitStatus.set("")
        self.fitDataAutoButton.grid_forget()
        self.fitDataManButton.grid_forget()
        self.fitDataManEntry.grid_forget()

    '''
    This function opens up a 'help' message box. 
    '''
    def help(self):

        self.infoText = 'How to use it:'\
        '\n\u2022 Browse a .txt or .csv file with your data set. The file must have 2 columns (no errors along y-axis) or 3 columns (with errors along y-axis), separated by commas or spaces.'\
        '\n\u2022 You can then choose to plot the raw data or choose a function to fit the data to. The tool has the option for fitting polynomials of degree 0 upto 5 along with some other standard functions.'\
        '\n\u2022 Click \'Fit data automatically\' if you want the tool to attempt a fit by itself. Or click \'Fit data using my guess\' after providing an initial guess for the fitting parameters if you want to attempt a fit manually.'\
        '\n\u2022 You should see the best fit line if the routine runs successfully. You can add plot annotations, grid lines or view the fit parameters and residuals plot as you wish!'\
        '\n\nNote on errors:'\
        '\nIn case no errors are provided along the y-axis, the error on the parameters and the chi-squared value are calculated based on an error of 1.00 (arbitrary unit) on each data point. Due to this, the errors on the fitting parameters dont have much meaning; however the best fit can still be useful!'\
        '\n\nHave fun plotting!'

        tk.messagebox.showinfo('Help', self.infoText)

    '''
    This function opens up an 'about' message box showing author and copyright status. 
    '''
    def about(self):

        self.aboutText = 'CFit (Curve fitting Tool)\n\u24EA 2020 Jiten Dhandha\nSchool of Physics and Astronomy\nThe University of Manchester'
        tk.messagebox.showinfo('About', self.aboutText)

####################################################################################
#                                  MAIN FUNCTION                                   #
####################################################################################
def main():
    root = tk.Tk()
    GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
