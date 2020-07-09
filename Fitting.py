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

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import scipy.optimize as opt
import scipy.special as sp
import scipy.stats as stats
import warnings

####################################################################################
#                                 LIST OF FUNCTIONS                                #
####################################################################################

#POLYNOMIALS
constant = lambda x,a: np.polyval([a],x)
linear = lambda x,a,b: np.polyval([a,b],x)
quadratic = lambda x,a,b,c: np.polyval([a,b,c],x)
cubic = lambda x,a,b,c,d: np.polyval([a,b,c,d],x)
quartic = lambda x,a,b,c,d,e: np.polyval([a,b,c,d,e],x)
quintic = lambda x,a,b,c,d,e,f: np.polyval([a,b,c,d,e,f],x)
#PERIODIC FUNCTIONS
sine_wave = lambda x,y0,A,omg,phi: y0 + A*np.sin(omg*x+phi)
square_wave = lambda x,y0,A,omg,phi: y0 + A*np.sign(np.sin(omg*x+phi))
#PEAK-BASED FUNCTIONS
gaussian = lambda x,y0,A,mu,sig: y0 + (A/(sig*np.sqrt(2*np.pi)))*np.exp((-1/2)*((x-mu)/sig)**2)
poisson = lambda x,y0,A,lmd: y0 + A*(np.exp(-lmd))*(lmd**x)/sp.gamma(x)
laplace = lambda x,y0,A,mu,b: y0 + (A/(2*b))*np.exp(-np.abs(x-mu)/b)
lorentz = lambda x,y0,A,x0,omg: y0 + (2*A/np.pi)*(omg/(4*(x-x0)**2+omg**2))
#POLYNOMIAL-BASED FUNCTIONS
power = lambda x,A,b: A*(x)**b
#EXPONENTIALS AND LOGARITHMS
exp_growth = lambda x,y0,A,t: y0 + A*np.exp(x/t)
exp_decay = lambda x,y0,A,t: y0 + A*np.exp(-x/t)
logarithm = lambda x,y0,A,x0: y0 + A*np.log(x-x0)
#Dictonary to hold the functions
functions = {'Constant':constant,
             'Linear':linear,
             'Quadratic':quadratic,
             'Cubic':cubic,
             'Quartic':quartic,
             'Quintic':quintic,
             'Sine wave':sine_wave, 
             'Square wave':square_wave, 
             'Gaussian':gaussian, 
             'Poisson':poisson,
             'Laplacian':laplace,
             'Lorentzian':lorentz,
             'Power':power,
             'Exponential growth':exp_growth,
             'Exponential decay':exp_decay,
             'Logarithm':logarithm}

####################################################################################
#                                  GLOBAL VARIABLES                                #
####################################################################################

#DATA RELATED VARIABLES
data = []           #holds the data from data file
x = []              #holds the x values from the data file
y = []              #holds the y values from the data file
y_err = []          #holds the y errors, either from user file or generated
ERR = bool          #boolean to check if data file contains errors
numberOfDataPoints = int    #holds the number of points in the data file
#FIT FUNCTION RELATED VARIABLES
function = ''       #string holding the function to fit to
numberOfParameters = int    #holds the number of parameters of the fitting function
#FITTING VARIABLES
fitStructure = []       #holds the fitting information from curve_fit/polyfit
fitParameters = []      #holds the fitting parameters
fitErrors = []          #holds the errors on the fitting parameters
chiSquared = float      #holds the final chi-squared value of the fit
redChiSquared = float   #holds the final reduced chi-squared value of the fit
redChiSquaredLimits = []    #holds the "acceptable range" of reduced chi-squared

####################################################################################
#                                 READING USER FILE                                #
####################################################################################
'''
This function tries to read the file held at fileLocation and sets the global
variables that hold all the information about the data set. 
@Arguments:
fileLocation - string containing the location of the file chosen by user.
@Return value:
Returns an integer that specifies success (0) or failure (non 0) of the function.
'''
def readFile(fileLocation):
    
    #Access to global variables
    global data
    global x
    global y
    global y_err
    global ERR
    global numberOfDataPoints

    #Checking if the file string is empty
    if(fileLocation == ''):
        return 1
    
    #Checking if the file is a .txt or .csv file
    if(not fileLocation.endswith('.txt') and not fileLocation.endswith('.csv') ):
        return 2
        
    #Trying to populate the data array from the file (allows both spaces and commas)
    try:
        with open(fileLocation, 'r') as file:
            clean_lines = (' '.join(line.split()) for line in file)
            clean_lines = (line.replace(' ',',') for line in clean_lines)
            data = np.genfromtxt(clean_lines, delimiter=',',dtype='float_')
    except (TypeError, ValueError, AttributeError):
        return 3
    
    #Checking if the data array has 2 or 3 columns
    try:
        if(not len(data[0])==2 and not len(data[0])==3):
            return 4
    except TypeError:
        return 4

    #Checking if there are any NaN's or Inf's in the data
    if(np.any(np.isnan(data)) or np.any(np.isinf(data))):
        return 5

    #Checking if the errors are all positive number
    if(len(data[0])==3 and np.any(data[:,2]<=0)):
        return 6

    #Setting global variables
    numberOfDataPoints = len(data)
    data = data[data[:,0].argsort()]    #Sorting the array in ascending order along x column
    x = data[:,0]
    y = data[:,1]
    
    #Checking if error along y axis has been provided
    if(len(data[0])==2):
        y_err = np.array([1 for i in data])   #Constant error to aid in best chi-squared estimate
        ERR = False
    elif(len(data[0])==3):
        y_err = data[:,2]
        ERR = True     
    
    #All ran correctly!
    return 0
        
####################################################################################
#                             FIT - RELATED FUNCTIONS                              #
####################################################################################
'''
This function calculates the chi-squared against the data set given specific 
values of fitting function parameters.  
@Arguments:
params - array containing parameters of the fitting function to calculate chi-squared
against
@Return value:
Returns chi-squared as a float.
'''
def calcChiSquared(params):

    #Access to global variables
    global function
    global x
    global y
    global y_err

    #Returning chi-squared value for the given fitting function parameters
    return np.sum( ((y-functions[function](x,*params))/y_err)**2 )

'''
This function calculates the final chi-squared as well as reduced chi-squared
of the fit. It also calculates the acceptable range of reduced chi-squared based on
the chi-squared statistic.
@Arguments:
--
@Return value:
--
'''
def calcGoodnessOfFit():

    #Access to global variables
    global numberOfDataPoints
    global numberOfParameters
    global fitParameters
    global chiSquared
    global redChiSquared
    global redChiSquaredLimits

    #Calculating degrees of freedom
    degreesOfFreedom = numberOfDataPoints - numberOfParameters
    #Calculating chi-squared and reduced chi-squared
    chiSquared = calcChiSquared(fitParameters)
    redChiSquared = chiSquared/degreesOfFreedom
    
    #Calculating the "acceptable" range of reduced chi-squared
    pValues = [0.95,0.05]
    redChiSquaredLimits = stats.chi2.isf(pValues,degreesOfFreedom)/degreesOfFreedom

'''
This function provides an initial guess for the final fitting to take place in 
fitFunction(). It comes into play when the user wants to fit the data automatically.
The initial guess is based on a two step procedure:
1) Looking at data and figuring out bounds on the guess
2) Getting a single-valued guess by global minimization of chi-squared using the 
differential evolution algorithm in scipy
(NOTE: In case of polynomial, a straightforward np.polyfit is used instead)
@Arguments:
--
@Return value:
Returns an integer denoting success (0) or failure (non 0) of the function.
'''
def guessParameters():

    #Access to global variables
    global function
    global x
    global y
    global numberOfDataPoints

    #Useful quantities for guess estimation
    xmin = min(x)
    xmax = max(x)
    ymin = min(y)
    ymax = max(y)
    
    #All the parameter bound estimation happens here

    if(function in ['Constant','Linear','Quadratic','Cubic','Quartic','Quintic']):

        order = numberOfParameters - 1
        iniParameters = np.polyfit(x,y,deg=order,w=1/y_err)
        return fitFunction(iniParameters)


    elif(function=='Sine wave'):

        y0_bound = (ymin+2/5*abs(ymax-ymin),ymax-2/5*abs(ymax-ymin))
        A_bound = (abs(2*(ymax-ymin))/3,abs(ymax-ymin)/3)
        omg_bound = (2*0.5*np.pi/(xmax-xmin),2*100*np.pi/abs(xmax-xmin))
        phi_bound = (0,2*np.pi)

        BOUNDS = [y0_bound, A_bound, omg_bound, phi_bound]

    elif(function=='Square wave'):

        y0_bound = (ymin+2/5*abs(ymax-ymin),ymax-2/5*abs(ymax-ymin))
        A_bound = (abs(2*(ymax-ymin))/3,abs(ymax-ymin)/3)
        omg_bound = (2*1*np.pi/(xmax-xmin),2*100*np.pi/abs(xmax-xmin))
        phi_bound = (0,2*np.pi)

        BOUNDS = [y0_bound, A_bound, omg_bound, phi_bound]

    elif(function=='Gaussian'):

        concavity = True if sum(np.array([(y[-1]-i)<0 for i in y]))>int(len(y)/2) else False

        if(concavity):
            mean = x[np.argmax(y)]
            std = abs(x[np.argmax(y)]-x[np.argmin(y)])

            y0_bound = (ymin+abs(ymin),ymin-9*abs(ymin))
            A_bound = (0,5*abs(ymax-ymin)*3*std)
            mu_bound = (mean-abs(mean),mean+abs(mean))
            omg_bound = (0,3*std)

        else:
            mean = x[np.argmin(y)]
            std = abs(x[np.argmax(y)]-x[np.argmin(y)])

            y0_bound = (ymax+abs(ymax),ymax+9*abs(ymax))
            A_bound = (0,-5*abs(ymax-ymin)*3*std)
            mu_bound = (mean-abs(mean),mean+abs(mean))
            omg_bound = (0,3*std)           

        BOUNDS = [y0_bound, A_bound, mu_bound, omg_bound]
        
    elif(function=='Poisson'):

        mean = x[np.argmax(y)]

        y0_bound = (ymin+abs(ymin),ymin-9*abs(ymin))
        A_bound = (0,5*abs(ymax-ymin))
        lmd_bound = (mean-abs(mean),mean+abs(mean))

        BOUNDS = [y0_bound, A_bound, lmd_bound]       

    elif(function=='Laplacian'):

        mean = x[np.argmax(y)]

        b_arr = []
        for i in range(numberOfDataPoints-1):
            if(y[i+1]==y[i]):
                continue
            else:
                if(x[i]<mean):
                    temp = (y[i]-ymin)*(x[i+1]-x[i])/(y[i+1]-y[i])
                else:
                    temp = (y[i]-ymin)*(x[i+1]-x[i])/(y[i+1]-y[i])
                b_arr.append(temp)
        hist, edges = np.histogram(b_arr, bins=int(len(b_arr)/5))
        b_est = (edges[np.argmax(hist)] + edges[np.argmax(hist)+1])/2

        y0_bound = (ymin+abs(ymin),ymin-9*abs(ymin))
        A_bound = (0,5*2*b_est*abs(ymax-ymin))
        mu_bound = (mean-abs(mean),mean+abs(mean)) 
        b_bound = (b_est-abs(b_est),b_est+abs(b_est))

        BOUNDS = [y0_bound, A_bound, mu_bound, b_bound]
        print(BOUNDS)
        
    elif(function=='Lorentzian'):

        mean = x[np.argmax(y)]
        std = abs(x[np.argmax(y)]-x[np.argmin(y)]) 

        y0_bound = (ymin+abs(ymin),ymin-9*abs(ymin))
        A_bound = (0,10*abs(ymax-ymin))
        x0_bound = (mean-abs(mean),mean+abs(mean))
        omg_bound = (0,3*std)

        BOUNDS = [y0_bound, A_bound, x0_bound, omg_bound]

    elif(function=='Power'):

        lX = np.log(abs(x), where=x>0)
        lY = np.log(abs(y), where=x>0)

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            b_est, logA_est = np.polyfit(lX,lY,deg=1)
            
        A_est = np.exp(logA_est)

        A_bound = (-A_est,A_est)
        b_bound = (b_est-0.5*abs(b_est),b_est+0.5*abs(b_est))
        
        BOUNDS = [A_bound,b_bound]

    elif(function=='Exponential growth'):

        monotonicity = True if np.average(np.diff(y))>=0 else False

        if(monotonicity):

            t_arr = []
            for i in range(numberOfDataPoints-1):
                if(y[i+1]==y[i]):
                    continue
                else:
                    temp = (y[i]-ymin)*(x[i+1]-x[i])/(y[i+1]-y[i])
                    t_arr.append(temp)
            hist, edges = np.histogram(t_arr, bins=int(len(t_arr)/5))
            t_est = (edges[np.argmax(hist)] + edges[np.argmax(hist)+1])/2

            y0_bound = (ymin+abs(ymin),ymin-9*abs(ymin))
            A_bound = (0,10*abs(ymin))
            t_bound = (t_est-10*abs(t_est),t_est+10*abs(t_est))
      
        else:

            t_arr = []
            for i in range(numberOfDataPoints-1):
                if(y[i+1]==y[i]):
                    continue
                else:
                    temp = (y[i]-ymax)*(x[i+1]-x[i])/(y[i+1]-y[i])
                    t_arr.append(temp)
            hist, edges = np.histogram(t_arr, bins=int(len(t_arr)/5))
            t_est = (edges[np.argmax(hist)] + edges[np.argmax(hist)+1])/2

            y0_bound = (ymax-abs(ymax),ymin+9*abs(ymax))
            A_bound = (0,-10*abs(ymin))
            t_bound = (t_est-10*abs(t_est),t_est+10*abs(t_est))

        BOUNDS = [y0_bound, A_bound, t_bound]
        
    elif(function=='Exponential decay'):

        monotonicity = True if np.average(np.diff(y))>=0 else False

        if(monotonicity):

            A_est = y[0] + (-x[0])*(y[1]-y[0])/(x[1]-x[0]) - ymax

            t_arr = []
            for i in range(numberOfDataPoints-1):
                if(y[i+1]==y[i]):
                    continue
                else:
                    temp = -(y[i]-ymax)*(x[i+1]-x[i])/(y[i+1]-y[i])
                    t_arr.append(temp)
            hist, edges = np.histogram(t_arr, bins=int(len(t_arr)/5))
            t_est = (edges[np.argmax(hist)] + edges[np.argmax(hist)+1])/2
            
            y0_bound = (ymax-abs(ymax),ymax+9*abs(ymax))
            A_bound = (0,100*A_est)
            t_bound = (t_est-10*abs(t_est),t_est+10*abs(t_est))
      
        else:
            
            A_est = y[0] + (-x[0])*(y[1]-y[0])/(x[1]-x[0]) - ymin

            t_arr = []
            for i in range(numberOfDataPoints-1):
                if(y[i+1]==y[i]):
                    continue
                else:
                    temp = -(y[i]-ymin)*(x[i+1]-x[i])/(y[i+1]-y[i])
                    t_arr.append(temp)
            hist, edges = np.histogram(t_arr, bins=int(len(t_arr)/5))
            t_est = (edges[np.argmax(hist)] + edges[np.argmax(hist)+1])/2
            
            y0_bound = (ymin+abs(ymin),ymin-9*abs(ymin))
            A_bound = (0,100*A_est)
            t_bound = (t_est-10*abs(t_est),t_est+10*abs(t_est))

        BOUNDS = [y0_bound, A_bound, t_bound]

    elif(function=='Logarithm'):
         
        A_arr = []
        for i in range(numberOfDataPoints-1):
            if(x[i+1]==x[i]):
                continue
            else:
                temp = (y[i+1]-y[i])*(x[i]-xmin)/(x[i+1]-x[i])
                A_arr.append(temp)
        hist, edges = np.histogram(A_arr, bins=int(len(A_arr)/5))
        A_est = (edges[np.argmax(hist)] + edges[np.argmax(hist)+1])/2

        y0_est = y[np.argmin(np.diff(y)/np.diff(x) - A_est)]   

        y0_bound = (y0_est-5*abs(y0_est),y0_est+5*abs(y0_est))
        A_bound = (A_est-2*abs(A_est),A_est+2*abs(A_est))
        x0_bound = (xmin - 10*abs(xmin),xmin)

        BOUNDS = [y0_bound, A_bound, x0_bound]

    #Ignoring runtime warnings (in case the optimization passes through invalid values)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        #Using differential evolution algorithm for minimizing chi-squared within the bounds
        iniParameters = opt.differential_evolution(calcChiSquared,bounds=BOUNDS,polish=True).x

    #Sending the "best guess" parameters to the final fitting algorithm
    return fitFunction(iniParameters)

'''
This function converts a string containing the guess parameters for fitting
provided by the user into an array of floats for the fitFunction() to use.
It comes into play when the user wants to fit the data manually.
@Arguments:
iniParametersString - string containing initial parameters
@Return value:
Returns an integer denoting success (0) or failure (non 0) of the function.
'''
def manualParameters(iniParametersString):

    #Access to global variables
    global numberOfParameters

    #Splitting string delimited by commas
    splitString = iniParametersString.split(',')

    #Trying to populate the iniParameters array
    iniParameters = []
    try:
        for i in splitString:
            #Further splitting each sub-string into "right and left" of the "=" sign
            temp1 = i.split('=')
            #Taking the value on the right side and converting to float
            temp2 = float(temp1[1])
            #Adding it to the iniParameters array
            iniParameters.append(temp2)
    except (ValueError,IndexError):
        return 3

    #Checking if the number of parameters expected and received match
    if(len(iniParameters)!=numberOfParameters):
        return 3

    #Sending the "manually input" parameters to the final fitting algorithm   
    return fitFunction(iniParameters)  

'''
This function does the final fitting of the data. It takes an inital guess on the 
parameters and optimizes from there.
@Arguments:
iniParameters - array containing initial guess
@Return value:
Returns an integer denoting success (0) or failure (non 0) of the function.
'''    
def fitFunction(iniParameters):
    
    #Access to global variables
    global function
    global x
    global y
    global y_err
    global numberOfDataPoints
    global numberOfParameters
    global fitStructure
    global fitParameters
    global fitErrors
        
    if(numberOfDataPoints<numberOfParameters):
        return 2

    #Doing the final fitting of the data
    try:
        #Ignoring runtime warnings (in case the optimization passes through invalid values) 
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            #Main optimization happens here
            #Note: curve_fit populates sigma wtih 1's as a default.
            #absolute_sigma = True is the flag that forces errors to not be used in a relative manner
            fitStructure = opt.curve_fit(functions[function],x,y,absolute_sigma=True,p0=iniParameters,sigma=y_err)

    #Catching errors
    except RuntimeError as e:
        #Optimization failed
        if (str(e).startswith('Optimal parameters not found: Number of calls to function has reached maxfev')):
            return 1
        #Something else went wrong
        else:
            raise

    #Filling in the fit parameters and errors on them (from the covariance matrix)
    fitParameters = fitStructure[0]
    fitErrors = np.sqrt(np.diag(fitStructure[1]))

    #Quantizing the goodness of fit
    calcGoodnessOfFit()

    #All ran correctly!   
    return 0

####################################################################################
#                                PLOTTING FUNCTIONS                                #
####################################################################################
'''
This function plots the raw data (without the fit).
@Arguments:
plotTitle - string holding the title of the plot
xTitle - string holding the label for the x axis
yTitle - string holding the label for the y axis
viewGrid - boolean denoting whether the user wants the plot to have gridlines
@Return value:
--
'''     
def plotRawData(plotTitle,xTitle,yTitle,viewGrid):

    #Access to global variables
    global x
    global y
    global y_err
    global ERR

    #Creating figure and adding subplot
    figure1 = plt.figure()
    axes1 = figure1.add_subplot(111)

    #Setting x and y axis labels
    axes1.set_title(plotTitle, fontsize='x-large')
    axes1.set_xlabel(xTitle, fontsize='large')
    axes1.set_ylabel(yTitle, fontsize='large')

    #Checking if user wants to add grid to plot and adding them
    if(viewGrid):
        axes1.minorticks_on()
        axes1.set_axisbelow(True)
        axes1.grid(b=True, which='major', alpha=0.5)
        axes1.grid(b=True, which='minor', alpha=0.2)

    #Plotting the raw data
    if(ERR==True):
        axes1.errorbar(x,y,y_err,fmt='.',color='midnightblue',ecolor='royalblue',capsize=2)
    else:
        axes1.scatter(x,y,color='midnightblue', label='Data')
        
    #Displaying the beauty
    figure1.show()

'''
This function plots the raw data along with the fitting function and shows the 
fitting parameters if the user wants to see it.
@Arguments:
plotTitle - string holding the title of the plot
xTitle - string holding the label for the x axis
yTitle - string holding the label for the y axis
viewGrid - boolean holding whether the user wants the plot to have gridlines
viewParameters - boolean holding whether the user wants to see the fitting
parameters
viewResiduals - boolean holding whether the user wants to see the residuals
plot
@Return value:
--
'''    
def plotFitData(plotTitle,xTitle,yTitle,viewGrid,viewParameters,viewResiduals):

    #Access to global variables
    global x
    global y
    global y_err
    global ERR
    global numberOfDataPoints
    global func
    global numberOfParameters
    global fitParameters
    global fitErrors
    global chiSquared
    global redChiSquared
    global redChiSquaredLimits

    #Creating figure and adding subplots
    figure2 = plt.figure()
    if(viewResiduals and viewParameters):
        gs = gridspec.GridSpec(2, 2, height_ratios=[3, 1], width_ratios=[4,1]) 
        axes2 = figure2.add_subplot(gs[0,0])
        axes3 = figure2.add_subplot(gs[1,0])
        axes4 = figure2.add_subplot(gs[0,1])
    elif(viewResiduals and not viewParameters):
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1]) 
        axes2 = figure2.add_subplot(gs[0])
        axes3 = figure2.add_subplot(gs[1])
    elif(not viewResiduals and viewParameters):
        gs = gridspec.GridSpec(1, 2, width_ratios=[4, 1])
        axes2 = figure2.add_subplot(gs[0])
        axes4 = figure2.add_subplot(gs[1])    
    else:
        axes2 = figure2.add_subplot(111)

    #Setting axes titles
    axes2.set_title(plotTitle, fontsize='x-large')
    axes2.set_xlabel(xTitle, fontsize='large')
    axes2.set_ylabel(yTitle, fontsize='large')

    #Checking if user wants to add grid to plot and adding them
    if(viewGrid):
        axes2.minorticks_on()
        axes2.set_axisbelow(True)
        axes2.grid(b=True, which='major', alpha=0.5)
        axes2.grid(b=True, which='minor', alpha=0.2)
        if(viewResiduals):
            axes3.minorticks_on()
            axes3.set_axisbelow(True)
            axes3.grid(b=True, which='major', alpha=0.5)
            axes3.grid(b=True, which='minor', alpha=0.2)

    #Plotting the raw data
    if(ERR==True):
        axes2.errorbar(x,y,y_err, fmt='.', color='midnightblue', ecolor='royalblue', capsize=2, zorder=1, label='Data')
    else:
        axes2.scatter(x,y,color='midnightblue', label='Data')
    
    #Plotting the best fit
    xx = np.linspace(min(x),max(x),1000)
    yy = functions[function](xx,*fitParameters)
    axes2.plot(xx,yy,color='darkorange', zorder=2, label='Fit function')

    #Plotting the residuals
    if(viewResiduals):
        residuals = functions[function](x,*fitParameters) - y
        axes3.axhline(0,color='darkorange', zorder=2)
        if(ERR==True):
            axes3.errorbar(x,residuals,y_err,fmt='.', color='midnightblue', ecolor='royalblue', capsize=2, zorder=1)
        else:
            axes3.scatter(x,residuals,color='midnightblue')

    #Adding legend to the plot
    axes2.legend(markerscale=2, fontsize='large')

    #Displaying fit parameters if the user wants
    if(viewParameters):

        #Removing x and y axis
        axes4.set_axis_off()

        #Declaring the string array that holds everything displayed in the parameters box
        parametersStr = []

        #Adding function type to parameters box
        parametersStr.append(r"$\bf{Function:}$")

        if(function=='Constant'):

            parametersStr.append(r"$y = a$")
            listOfParams = [r'$a$']

        elif(function=='Linear'):

            parametersStr.append(r"$y = ax+b$")
            listOfParams = [r'$a$',r'$b$']

        elif(function=='Quadratic'):

            parametersStr.append(r"$y = ax^2+bx+c$")
            listOfParams = [r'$a$',r'$b$',r'$c$']

        elif(function=='Cubic'):

            parametersStr.append(r"$y = ax^3+bx^2+cx+d$")
            listOfParams = [r'$a$',r'$b$',r'$c$',r'$d$']

        elif(function=='Quartic'):

            parametersStr.append(r"$y = ax^4+bx^3+cx^2+dx+e$")
            listOfParams = [r'$a$',r'$b$',r'$c$',r'$d$',r'$e$']

        elif(function=='Quintic'):

            parametersStr.append(r"$y = ax^5+bx^4+cx^3+dx^2+ex+f$")
            listOfParams = [r'$a$',r'$b$',r'$c$',r'$d$',r'$e$',r'$f$']

        elif(function=='Sine wave'):

            parametersStr.append(r'$y = y_0 + A[\sin(\omega x+\phi)]$')
            listOfParams = [r'$y_0$',r'$A$',r'$\omega$',r'$\phi$']

        elif(function=='Square wave'):

            parametersStr.append(r'$y = y_0 + A\/sgn[\sin(\omega x+\phi)]$')
            listOfParams = [r'$y_0$',r'$A$',r'$\omega$',r'$\phi$']

        elif(function=='Gaussian'):

            parametersStr.append(r'$y = y_0 + \frac{A}{\sigma \sqrt{2\pi}}e^{-\frac{(x-\mu)^2}{2\sigma^2}}$')
            listOfParams = [r'$y_0$',r'$A$',r'$\mu$',r'$\sigma$']

        elif(function=='Poisson'):

            parametersStr.append(r'$y = y_0 + A\/\frac{e^{-\lambda}\lambda^x}{x!}$')
            listOfParams = [r'$y_0$',r'$A$',r'$\lambda$']

        elif(function=='Laplacian'):

            parametersStr.append(r'$y = y_0 + \frac{A}{2b}e^{-\frac{|x-\mu|}{b}}$')
            listOfParams = [r'$y_0$',r'$A$',r'$\mu$',r'$b$']

        elif(function=='Lorentzian'):

            parametersStr.append(r'$y = y_0 + \frac{2A}{\pi}\frac{\omega}{4(x-x_0)^2+\omega^2}$')
            listOfParams = [r'$y_0$',r'$A$',r'$x_0$',r'$\omega$']
            
        elif(function=='Power'):

            parametersStr.append(r'$y = Ax^b$')
            listOfParams = [r'$A$',r'$b$']

        elif(function=='Exponential growth'):

            parametersStr.append(r'$y = y_0 + A\/e^{x/t}$')
            listOfParams = [r'$y_0$',r'$A$',r'$t$']

        elif(function=='Exponential decay'):

            parametersStr.append(r'$y = y_0 + A\/e^{-x/t}$')
            listOfParams = [r'$y_0$',r'$A$',r'$t$']

        elif(function=='Logarithm'):

            parametersStr.append(r'$y = y_0 + A\/log(x-x_0)$')
            listOfParams = [r'$y_0$',r'$A$',r'$x_0$']

        #Adding fit parameters to the parameters box
        parametersStr.append("")
        parametersStr.append(r"$\bf{Fitting\/parameters:}$")
        for i in range(numberOfParameters):
            parametersStr.append(listOfParams[i]+r' = {0:.5e} $\pm$ {1:.5e}'.format(fitParameters[i],fitErrors[i]))

        #Adding some additional fitting details to the parameters box
        parametersStr.append("")
        parametersStr.append(r"$\bf{Other\/fitting\/data:}$")
        parametersStr.append(r'Number of data points = {0}'.format(numberOfDataPoints))
        parametersStr.append(r'Number of parameters  = {0}'.format(numberOfParameters))
        parametersStr.append(r'$\chi^2$ = {0:.5e}'.format(chiSquared))
        parametersStr.append(r'$\chi_r^2$ = {0:.5e}'.format(redChiSquared))
        parametersStr.append(r'Acceptable range of $\chi_r^2$ = ({0:.2f},{1:.2f})'.format(redChiSquaredLimits[0],redChiSquaredLimits[1]))

        #Adding an important note
        if(ERR == False):
            parametersStr.append("")
            parametersStr.append(r'$\bf{Note}$: Errors and chi-squared estimates')
            parametersStr.append(r'here dont mean much since no errors')
            parametersStr.append(r'along y-axis are present!')            

        #Joining all elements of the string array into a single string separated by \n's 
        parametersStr = '\n'.join(parametersStr)

        #Placing the parameters box in the plot
        axes4.text(-0.35,1.0,parametersStr, bbox=dict(boxstyle="square", fc="lemonchiffon", ec="darkorange", pad=0.5),
            va='top', ha='left', fontsize='large', linespacing=1.3)

    #Displaying the beauty
    figure2.show()

'''
APPENDIX:
Check efficiency of differential evolution against other global minimization techniques:
iniParameters = opt.brute(calcChiSquared,ranges=[],finish=opt.fmin)
iniParameters = opt.basinhopping(calcChiSquared,x0=[])
'''
