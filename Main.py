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
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox
from inspect import signature

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
        self.fitTypes = ['Polynomial','Constant','Linear','Quadratic', 'Cubic','Quartic',
            'Quintic','Other functions','Sine wave','Square wave','Gaussian','Poisson','Laplacian',
            'Lorentzian','Power','Exponential growth','Exponential decay','Logarithm']       
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
        self.frame5.grid_columnconfigure(2, weight=1)
        self.frame5.grid_columnconfigure(3, weight=8)
        self.frame5.grid_rowconfigure(0, weight=1)

        self.clearButton = tk.Button(self.frame5, text="Clear", width=10, command=self.clear)
        self.clearButton.grid(row=0, rowspan=1, column=0, columnspan=1, sticky='NES', padx=5, pady=5)    
        
        self.exitButton = tk.Button(self.frame5, text="Exit", width=8, command=self.destroy)
        self.exitButton.grid(row=0, rowspan=1, column=1, columnspan=1, sticky='NEWS', padx=5, pady=5)

        self.helpButton = tk.Button(self.frame5, text="Help", width=8, command=self.help)
        self.helpButton.grid(row=0, rowspan=1, column=2, columnspan=1, sticky='NEWS', padx=5, pady=5)

        self.aboutButton = tk.Button(self.frame5, text="About", width=10, command=self.about)
        self.aboutButton.grid(row=0, rowspan=1, column=3, columnspan=1, sticky='NWS', padx=5, pady=5)

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
        
        #Setting preview of the form of the function
        if(self.fitType.get()=='Constant'):
            self.fitTypeStr.set('y = a')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'a=1')

        elif(self.fitType.get()=='Linear'):
            self.fitTypeStr.set('y = ax+b')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'a=1, b=1')

        elif(self.fitType.get()=='Quadratic'):
            self.fitTypeStr.set('y = ax\u00B2+bx+c')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'a=1, b=1, c=1')

        elif(self.fitType.get()=='Cubic'):
            self.fitTypeStr.set('y = ax\u00B3+bx\u00B2+cx+d')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'a=1, b=1, c=1, d=1')

        elif(self.fitType.get()=='Quartic'):
            self.fitTypeStr.set('y = ax\u2074+bx\u00B3+cx\u00B2+dx+e')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'a=1, b=1, c=1, d=1, e=1')

        elif(self.fitType.get()=='Quintic'):
            self.fitTypeStr.set('y = ax\u2075+bx\u2074+cx\u00B3+dx\u00B2+ex+f')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'a=1, b=1, c=1, d=1, e=1, f=1')

        elif(self.fitType.get()=='Sine wave'):
            self.fitTypeStr.set('y = y\u2080 + A sin(\u03C9x+\u03D5)')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'y\u2080=1, A=1, \u03C9=1, \u03D5=1')

        elif(self.fitType.get()=='Square wave'):
            self.fitTypeStr.set('y = y\u2080 + A signum[sin(\u03C9x+\u03D5)]')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'y\u2080=1, A=1, \u03C9=1, \u03D5=1')

        elif(self.fitType.get()=='Gaussian'):
            self.fitTypeStr.set('y = y\u2080 + A/[\u03C3 \u221A(2\u03C0)] \u00D7 e^[(x-\u03BC)\u00B2/(2\u03C3\u00B2)]')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'y\u2080=1, A=1, \u03BC=1, \u03C3=1')

        elif(self.fitType.get()=='Poisson'):
            self.fitTypeStr.set('y = y\u2080 + A [(e^\u03BB)(\u03BB^x)]/x!')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'y\u2080=1, A=1, \u03BB=1')

        elif(self.fitType.get()=='Laplacian'):
            self.fitTypeStr.set('y = y\u2080 + A/(2b) \u00D7 e^(-|(x-\u03BC)|/2b)')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'y\u2080=1, A=1, \u03BC=1, b=1')

        elif(self.fitType.get()=='Lorentzian'):
            self.fitTypeStr.set('y = y\u2080 + (2A/\u03C0) \u00D7 (\u03C9/[4(x-x\u2080)\u00B2+\u03C9\u00B2])')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'y\u2080=1, A=1, x\u2080=1, \u03C9=1')

        elif(self.fitType.get()=='Power'):
            self.fitTypeStr.set('y = A x\u1D47')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'A=1, b=1')

        elif(self.fitType.get()=='Exponential growth'):
            self.fitTypeStr.set('y = y\u2080 + A e^(x/t)')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'y\u2080=1, A=1, t=1')

        elif(self.fitType.get()=='Exponential decay'):
            self.fitTypeStr.set('y = y\u2080 + A e^(-x/t)')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'y\u2080=1, A=1, t=1')

        elif(self.fitType.get()=='Logarithm'):
            self.fitTypeStr.set('y = A log(x-x\u2080)')
            self.fitDataManEntry.delete(0,'end')
            self.fitDataManEntry.insert(0, 'y\u2080=1, A=1, x\u2080=1')

        #Setting type of function
        fit.function = self.fitType.get()
        #Setting number of parameters
        fit.numberOfParameters = len(signature(fit.functions[fit.function]).parameters)-1            
            
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

        self.infoText = 'The curve fitting tool provides the user the ability to browse a .txt or .csv file containing the data set. '\
        'The file must have 2 columns (no errors along y-axis) or 3 columns (with errors along y-axis), separated by commas or spaces. '\
        'The user can then choose to plot the raw data or choose a function to fit the data to. The tool has the option for fitting polynomials '\
        'of degree 0 upto 5 along with some other standard functions. These functions can either be fit automatically or manually by '\
        'providing an initial guess for the parameters. The user can add plot annotations, grid lines or view the fit parameters and residuals '\
        'as they wish!'\
        '\n\nNOTE ON ERRORS:\n'\
        'In case no errors are provided along the y-axis, the error on the parameters and the chi-squared value are calculated based on an error '\
        'of 1.00 (arbitrary unit) on each data point. Due to this, the errors on the fitting parameters dont have much meaning; however the '\
        'best fit can still be useful!'\
        '\n\nHave fun plotting!'\

        messagebox.showinfo('Help', self.infoText)

    '''
    This function opens up an 'about' message box showing author and copyright status. 
    '''
    def about(self):

        self.aboutText = 'CFit (Curve fitting Tool)\n\u00A9 2020 Jiten Dhandha\nSchool Of Physics and Astronomy\nThe University of Manchester'
        messagebox.showinfo('About', self.aboutText)

    '''
    This function exits the GUI.
    '''
    def destroy(self):
        self.master.quit()
        self.master.destroy()

####################################################################################
#                                  MAIN FUNCTION                                   #
####################################################################################
def main():
    root = tk.Tk()
    GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
