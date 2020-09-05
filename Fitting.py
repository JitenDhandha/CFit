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
import matplotlib
matplotlib.use('Qt5Agg')    #This requires PyQt5 to be installed.
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import scipy.optimize as opt
import scipy.special as sp
import scipy.stats as stats
import scipy.linalg as linalg
import warnings

####################################################################################
#                                 LIST OF FUNCTIONS                                #
####################################################################################

#Class to hold all relevant function information
class Function():
    def __init__(self,name,func,numberOfParameters,rawFuncStr,unicodeFuncStr,rawParametersStr,unicodeParametersStr):
        self.name = name
        self.func = func
        self.numberOfParameters = numberOfParameters
        self.rawFuncStr = rawFuncStr
        self.unicodeFuncStr = unicodeFuncStr
        self.rawParametersStr = rawParametersStr
        self.unicodeParametersStr = unicodeParametersStr

'''
Current supported functions are as follows:
Polynomial: constant, linear, quadratic, cubic, quartic, quintic
Periodic functions: sine wave, square wave
Peak shape functions: gaussian, poisson, laplace, lorentz
Polynomial-based functions: power law
Exponentials and logarithms: exponential growth, exponential decay, logarithm
'''

#Dictonary to hold the functions
functions = {
            'Constant': 
             Function(name='Constant',
                      func=lambda x,a: np.polyval([a],x),
                      numberOfParameters=1,
                      rawFuncStr=r"$y = a$",
                      unicodeFuncStr="y = a",
                      rawParametersStr=[r'$a$'],
                      unicodeParametersStr=['a']),

            'Linear': 
            Function(name='Linear',
                     func=lambda x,a,b: np.polyval([a,b],x),
                     numberOfParameters=2,
                     rawFuncStr=r"$y = ax+b$",
                     unicodeFuncStr="y = ax+b",
                     rawParametersStr=[r'$a$',r'$b$'],
                     unicodeParametersStr=['a','b']),

            'Quadratic': 
            Function(name='Quadratic',
                     func=lambda x,a,b,c: np.polyval([a,b,c],x),
                     numberOfParameters=3,
                     rawFuncStr=r"$y = ax^2+bx+c$",
                     unicodeFuncStr="y = ax\u00B2+bx+c",
                     rawParametersStr=[r'$a$',r'$b$',r'$c$'],
                     unicodeParametersStr=['a','b','c']),

            'Cubic': 
            Function(name='Cubic',
                     func=lambda x,a,b,c,d: np.polyval([a,b,c,d],x),
                     numberOfParameters=4,
                     rawFuncStr=r"$y = ax^3+bx^2+cx+d$",
                     unicodeFuncStr="y = ax\u00B3+bx\u00B2+cx+d",
                     rawParametersStr=[r'$a$',r'$b$',r'$c$',r'$d$'],
                     unicodeParametersStr=['a','b','c','d']),

            'Quartic': 
            Function(name='Quadratic',
                     func=lambda x,a,b,c,d,e: np.polyval([a,b,c,d,e],x),
                     numberOfParameters=5,
                     rawFuncStr=r"$y = ax^4+bx^3+cx^2+dx+e$",
                     unicodeFuncStr="y = ax\u2074+bx\u00B3+cx\u00B2+dx+e",
                     rawParametersStr=[r'$a$',r'$b$',r'$c$',r'$d$',r'$e$'],
                     unicodeParametersStr=['a','b','c','d','e']),

            'Quintic': 
            Function(name='Quintic',
                     func=lambda x,a,b,c,d,e,f: np.polyval([a,b,c,d,e,f],x),
                     numberOfParameters=6,
                     rawFuncStr=r"$y = ax^5+bx^4+cx^3+dx^2+ex+f$",
                     unicodeFuncStr="y = ax\u2075+bx\u2074+cx\u00B3+dx\u00B2+ex+f",
                     rawParametersStr=[r'$a$',r'$b$',r'$c$',r'$d$',r'$e$',r'$f$'],
                     unicodeParametersStr=['a','b','c','d','e','f']),

            'Sine wave': 
            Function(name='Sine wave',
                     func=lambda x,y0,A,omg,phi: y0 + A*np.sin(omg*x+phi),
                     numberOfParameters=4,
                     rawFuncStr=r"$y = y_0 + A[\sin(\omega x+\phi)]$",
                     unicodeFuncStr="y = y\u2080 + A sin(\u03C9x+\u03D5)",
                     rawParametersStr=[r'$y_0$',r'$A$',r'$\omega$',r'$\phi$'],
                     unicodeParametersStr=['y\u2080','A','\u03C9','\u03D5']),

            'Square wave': 
            Function(name='Square wave',
                     func=lambda x,y0,A,omg,phi: y0 + A*np.sign(np.sin(omg*x+phi)),
                     numberOfParameters=4,
                     rawFuncStr=r"$y = y_0 + A\/signum[\sin(\omega x+\phi)]$",
                     unicodeFuncStr="y = y\u2080 + A signum[sin(\u03C9x+\u03D5)]",
                     rawParametersStr=[r'$y_0$',r'$A$',r'$\omega$',r'$\phi$'],
                     unicodeParametersStr=['y\u2080','A','\u03C9','\u03D5']),

            'Gaussian': 
            Function(name='Gaussian',
                     func=lambda x,y0,A,mu,sig: y0 + (A/(sig*np.sqrt(2*np.pi)))*np.exp((-1/2)*((x-mu)/sig)**2),
                     numberOfParameters=4,
                     rawFuncStr=r"$y = y_0 + \frac{A}{\sigma \sqrt{2\pi}}e^{-\frac{(x-\mu)^2}{2\sigma^2}}$",
                     unicodeFuncStr="y = y\u2080 + A/[\u03C3 \u221A(2\u03C0)] \u00D7 e^[-(x-\u03BC)\u00B2/(2\u03C3\u00B2)]",
                     rawParametersStr=[r'$y_0$',r'$A$',r'$\mu$',r'$\sigma$'],
                     unicodeParametersStr=['y\u2080','A','\u03BC','\u03C3']),

            'Poisson': 
            Function(name='Poisson',
                     func=lambda x,y0,A,lmd: y0 + A*(np.exp(-lmd))*(lmd**x)/sp.gamma(x),
                     numberOfParameters=3,
                     rawFuncStr=r"$y = y_0 + A\/\frac{e^{-\lambda}\lambda^x}{x!}$",
                     unicodeFuncStr="y = y\u2080 + A [(e^\u03BB)(\u03BB^x)]/x!",
                     rawParametersStr=[r'$y_0$',r'$A$',r'$\lambda$'],
                     unicodeParametersStr=['y\u2080','A','\u03BB']),

            'Laplacian':            
            Function(name='Laplacian',
                     func=lambda x,y0,A,mu,b: y0 + (A/(2*b))*np.exp(-np.abs(x-mu)/b),
                     numberOfParameters=4,
                     rawFuncStr=r"$y = y_0 + \frac{A}{2b}e^{-\frac{|x-\mu|}{b}}$",
                     unicodeFuncStr="y = y\u2080 + A/(2b) \u00D7 e^(-|(x-\u03BC)|/b)",
                     rawParametersStr=[r'$y_0$',r'$A$',r'$\mu$',r'$b$'],
                     unicodeParametersStr=['y\u2080','A','\u03BC','b']),

            'Lorentzian':           
            Function(name='Lorentzian',
                     func=lambda x,y0,A,x0,omg: y0 + (2*A/np.pi)*(omg/(4*(x-x0)**2+omg**2)),
                     numberOfParameters=4,
                     rawFuncStr=r"$y = y_0 + \frac{2A}{\pi}\frac{\omega}{4(x-x_0)^2+\omega^2}$",
                     unicodeFuncStr="y = y\u2080 + (2A/\u03C0) \u00D7 (\u03C9/[4(x-x\u2080)\u00B2+\u03C9\u00B2])",
                     rawParametersStr=[r'$y_0$',r'$A$',r'$x_0$',r'$\omega$'],
                     unicodeParametersStr=['y\u2080','A','x\u2080','\u03C9']),

            'Power':                
            Function(name='Power',
                     func=lambda x,A,b: A*(x)**b,
                     numberOfParameters=2,
                     rawFuncStr=r"$y = Ax^b$",
                     unicodeFuncStr="y = A x\u1D47",
                     rawParametersStr=[r'$A$',r'$b$'],
                     unicodeParametersStr=['A','b']),

            'Exponential':    
            Function(name='Exponential',
                     func=lambda x,y0,A,b: y0 + A*np.exp(b*x),
                     numberOfParameters=3,
                     rawFuncStr=r"$y = y_0 + A\/e^{bx}$",
                     unicodeFuncStr="y = y\u2080 + A e^(bx)",
                     rawParametersStr=[r'$y_0$',r'$A$',r'$b$'],
                     unicodeParametersStr=['y\u2080','A','b']),

            'Logarithm':            
            Function(name='Logarithm',
                     func=lambda x,y0,A,x0: y0 + A*np.log(x-x0),
                     numberOfParameters=3,
                     rawFuncStr=r"$y = y_0 + A\/log(x-x_0)$",
                     unicodeFuncStr="y = y\u2080 + A log(x-x\u2080)",
                     rawParametersStr=[r'$y_0$',r'$A$',r'$x_0$'],
                     unicodeParametersStr=['y\u2080','A','x\u2080'])
            }

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
            clean_lines = [' '.join(line.split()) for line in file]
            for delims in [(' ,',','),(', ',','),(' ',',')]:
                clean_lines = [line.replace(*delims) for line in clean_lines]
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
    return np.sum( ((y-functions[function].func(x,*params))/y_err)**2 )

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
The initial guess is based on a two step procedure. It involves looking at the data:
1) and figuring out a single-valued "guess"
2) or figuring out bounds on the parameters and obtaining a guess from that by
global minimization of chi-squared using the scipy differential evolution algorithm.
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

    #Useful quantities for parameter estimation
    xmin = min(x)
    xmax = max(x)
    ymin = min(y)
    ymax = max(y)
    
    #Empty array to store "initial guess"
    iniParameters = []

    #All the parameter estimation happens here

    if(function in ['Constant','Linear','Quadratic','Cubic','Quartic','Quintic']):

        order = numberOfParameters - 1
        iniParameters = np.polyfit(x,y,deg=order,w=1/y_err)

    elif(function=='Sine wave'):

        x_range = xmax - xmin
        y_range = ymax - ymin

        y0_bound = (ymin+2/5*abs(y_range),ymax-2/5*abs(y_range))
        A_bound = (abs(y_range)/3,2*abs(y_range)/3)
        phi_bound = (0,2*np.pi)

        y_avg = np.average(y)
        y_std = np.std(y)
        yscaled = []
        for i in y:
            if(i>y_avg+y_std):
                yscaled.append(1)
            elif(i<y_avg-y_std):
                yscaled.append(-1)
            else:
                yscaled.append(0)
        flag = yscaled[0]
        crossings = 0
        for i in yscaled:
            if(i==0):
                continue
            if(flag==0):
                flag=i
            elif(i==-flag):
                flag = -flag
                crossings+=1
        crossings = crossings/2
        guess_f = crossings/x_range

        omg_bound = (0.5*(2*np.pi)*guess_f,2*(2*np.pi)*guess_f)

        BOUNDS = [y0_bound, A_bound, omg_bound, phi_bound]

        with np.errstate(invalid='ignore'):
            iniParameters = opt.differential_evolution(calcChiSquared,bounds=BOUNDS,seed=0).x

    elif(function=='Square wave'):

        x_range = xmax - xmin
        y_range = ymax - ymin

        y0_bound = (ymin+2/5*abs(y_range),ymax-2/5*abs(y_range))
        A_bound = (abs(y_range)/3,2*abs(y_range)/3)
        phi_bound = (0,2*np.pi)

        y_avg = np.average(y)
        y_std = np.std(y)
        yscaled = []
        for i in y:
            if(i>y_avg+y_std):
                yscaled.append(1)
            elif(i<y_avg-y_std):
                yscaled.append(-1)
            else:
                yscaled.append(0)
        flag = yscaled[0]
        crossings = 0
        for i in yscaled:
            if(i==0):
                continue
            if(flag==0):
                flag=i
            elif(i==-flag):
                flag = -flag
                crossings+=1
        crossings = crossings/2
        guess_f = crossings/x_range

        omg_bound = (0.5*(2*np.pi)*guess_f,2*(2*np.pi)*guess_f)

        BOUNDS = [y0_bound, A_bound, omg_bound, phi_bound]

        with np.errstate(invalid='ignore'):
            iniParameters = opt.differential_evolution(calcChiSquared,bounds=BOUNDS,seed=0).x

    elif(function=='Gaussian'):

        x_range = xmax - xmin
        y_range = ymax - ymin

        mu_bound = (xmin-x_range,xmax+x_range)
        omg_bound = (0,x_range)

        A_bound1 = (abs(y_range)/3,2*abs(y_range)*2.5*x_range)
        y0_bound1 = (ymin-y_range,ymin+y_range/2)
        BOUNDS1 = [y0_bound1, A_bound1, mu_bound, omg_bound]

        A_bound2 = (-abs(y_range)/3,-2*abs(y_range)*2.5*x_range)
        y0_bound2 = (ymax-y_range/2,ymax+y_range)
        BOUNDS2 = [y0_bound2, A_bound2, mu_bound, omg_bound]

        BOUNDS_LIST = [BOUNDS1,BOUNDS2]

        with np.errstate(invalid='ignore'):
            bestChiSquared = np.inf
            for BOUNDS in BOUNDS_LIST:
                #Fixed seed for repeatability of fit
                tempParameters = opt.differential_evolution(calcChiSquared,bounds=BOUNDS,seed=0).x
                tempChiSquared = calcChiSquared(tempParameters)
                if(tempChiSquared < bestChiSquared):
                    bestChiSquared = tempChiSquared
                    iniParameters = tempParameters
        
    elif(function=='Poisson'):

        x_range = xmax - xmin
        y_range = ymax - ymin

        lmd_bound = (max(0,xmin-x_range),xmax+x_range)

        A_bound1 = (0,2*abs(y_range))
        y0_bound1 = (ymin-y_range,ymin+y_range/2)        
        BOUNDS1 = [y0_bound1, A_bound1, lmd_bound]

        A_bound2 = (0,-2*abs(y_range))
        y0_bound2 = (ymax-y_range/2,ymax+y_range)
        BOUNDS2 = [y0_bound1, A_bound1, lmd_bound]        

        BOUNDS_LIST = [BOUNDS1,BOUNDS2]

        with np.errstate(invalid='ignore'):
            bestChiSquared = np.inf
            for BOUNDS in BOUNDS_LIST:
                #Fixed seed for repeatability of fit
                tempParameters = opt.differential_evolution(calcChiSquared,bounds=BOUNDS,seed=0).x
                tempChiSquared = calcChiSquared(tempParameters)
                if(tempChiSquared < bestChiSquared):
                    bestChiSquared = tempChiSquared
                    iniParameters = tempParameters

    elif(function=='Laplacian'):
        
        x_range = xmax - xmin
        y_range = ymax - ymin

        mu_bound = (xmin-x_range,xmax+x_range)
        b_bound = (0,x_range)

        A_bound1 = (abs(y_range)/3,2*abs(y_range)*2*x_range)
        y0_bound1 = (ymin-y_range,ymin+y_range/2)
        BOUNDS1 = [y0_bound1, A_bound1, mu_bound, b_bound]

        A_bound2 = (-abs(y_range)/3,-2*abs(y_range)*2*x_range)
        y0_bound2 = (ymax-y_range/2,ymax+y_range)
        BOUNDS2 = [y0_bound2, A_bound2, mu_bound, b_bound]

        BOUNDS_LIST = [BOUNDS1,BOUNDS2]

        with np.errstate(invalid='ignore'):
            bestChiSquared = np.inf
            for BOUNDS in BOUNDS_LIST:
                #Fixed seed for repeatability of fit
                tempParameters = opt.differential_evolution(calcChiSquared,bounds=BOUNDS,seed=0).x
                tempChiSquared = calcChiSquared(tempParameters)
                if(tempChiSquared < bestChiSquared):
                    bestChiSquared = tempChiSquared
                    iniParameters = tempParameters

    elif(function=='Lorentzian'):

        x_range = xmax - xmin
        y_range = ymax - ymin

        x0_bound = (xmin-x_range,xmax+x_range)
        omg_bound = (0,x_range)

        A_bound1 = (abs(y_range)/3,2*abs(y_range)*np.pi/2*x_range)
        y0_bound1 = (ymin-y_range,ymin+y_range/2)
        BOUNDS1 = [y0_bound1, A_bound1, x0_bound, omg_bound]

        A_bound2 = (-abs(y_range)/3,-2*abs(y_range)*np.pi/2*x_range)
        y0_bound2 = (ymax-y_range/2,ymax+y_range)
        BOUNDS2 = [y0_bound2, A_bound2, x0_bound, omg_bound]

        BOUNDS_LIST = [BOUNDS1,BOUNDS2]

        with np.errstate(invalid='ignore'):
            bestChiSquared = np.inf
            for BOUNDS in BOUNDS_LIST:
                #Fixed seed for repeatability of fit
                tempParameters = opt.differential_evolution(calcChiSquared,bounds=BOUNDS,seed=0).x
                tempChiSquared = calcChiSquared(tempParameters)
                if(tempChiSquared < bestChiSquared):
                    bestChiSquared = tempChiSquared
                    iniParameters = tempParameters

    elif(function=='Power'):

        lX = np.log(abs(x), where=x>0)
        lY = np.log(abs(y), where=x>0)

        with np.errstate(invalid='ignore'):
            b_est, logA_est = np.polyfit(lX,lY,w=np.exp(lX),deg=1)
        A_est = np.exp(logA_est)

        A_bound = (-A_est,A_est)
        b_bound = (b_est-0.5*abs(b_est),b_est+0.5*abs(b_est))

        BOUNDS = [A_bound,b_bound]

        with np.errstate(invalid='ignore'):
            iniParameters = opt.differential_evolution(calcChiSquared,bounds=BOUNDS,seed=0).x

    elif(function=='Exponential'):

        #Inspired by https://github.com/scipy/scipy/pull/9158

        s = np.empty_like(y)
        s[0] = 0
        s[1:] = np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(x))

        xn = np.array(x - x[0])
        yn = np.array(y - y[0])
    
        sx2 = np.sum(xn**2)
        sxs = np.sum(xn*s)
        sys = np.sum(yn*s)
        ss2 = np.sum(s**2)
        sxy = np.sum(xn*yn)
    
        _, [b] = linalg.inv([[sx2, sxs], [sxs, ss2]]).dot([[sxy], [sys]])
    
        ex = np.exp(b * x)
    
        se1 = np.sum(ex)
        se2 = np.sum(ex**2)
        sy0 = np.sum(y)
        sye = np.sum((y * ex))
    
        [y0], [A] = linalg.inv([[x.size, se1], [se1, se2]]).dot([[sy0], [sye]])

        iniParameters = [y0,A,b]

    elif(function=='Logarithm'):
         
        #Inspired by https://github.com/scipy/scipy/pull/9158

        s = np.empty_like(x)
        s[0] = 0
        s[1:] = np.cumsum(0.5 * (x[1:] + x[:-1]) * np.diff(y))

        xn = np.array(x - x[0])
        yn = np.array(y - y[0])
    
        sy2 = np.sum(yn**2)
        sys = np.sum(yn*s)
        sxs = np.sum(xn*s)
        ss2 = np.sum(s**2)
        syx = np.sum(xn*yn)
    
        _, [t1] = linalg.inv([[sy2, sys], [sys, ss2]]).dot([[syx], [sxs]])
    
        A = 1/t1

        ey = np.exp(t1 * y)
    
        se1 = np.sum(ey)
        se2 = np.sum(ey**2)
        sx0 = np.sum(x)
        sxe = np.sum((x * ey))
    
        [x0], [t2] = linalg.inv([[x.size, se1], [se1, se2]]).dot([[sx0], [sxe]])

        with np.errstate(invalid='ignore'):
            y0 = -A*np.log(t2)
            
        iniParameters = [y0,A,x0]

    #If there is no initial guess
    if(iniParameters==[]):
        return 1

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
        with np.errstate(invalid='ignore'):
            #Main optimization happens here
            #Note: curve_fit populates sigma with 1's as a default.
            #absolute_sigma = True is the flag that forces errors to not be used in a relative manner
            fitStructure = opt.curve_fit(functions[function].func,x,y,absolute_sigma=True,p0=iniParameters,sigma=y_err)

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
    if(ERR):
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
    global function
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
    if(ERR):
        axes2.errorbar(x,y,y_err, fmt='.', color='midnightblue', ecolor='royalblue', capsize=2, zorder=1, label='Data')
    else:
        axes2.scatter(x,y,color='midnightblue', label='Data')
    
    #Plotting the best fit
    xx = np.linspace(min(x),max(x),1000)
    yy = functions[function].func(xx,*fitParameters)
    axes2.plot(xx,yy,color='darkorange', zorder=2, label='Fit function')

    #Plotting the residuals
    if(viewResiduals):
        residuals = functions[function].func(x,*fitParameters) - y
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
        parametersStr.append(functions[function].name)
        parametersStr.append(functions[function].rawFuncStr)

        #Adding fit parameters to the parameters box
        parametersStr.append("")
        parametersStr.append(r"$\bf{Fitting\/parameters:}$")
        for i in range(numberOfParameters):
            parametersStr.append(functions[function].rawParametersStr[i]+r' = {0:.5e} $\pm$ {1:.5e}'.format(fitParameters[i],fitErrors[i]))

        #Adding some additional fitting details to the parameters box
        parametersStr.append("")
        parametersStr.append(r"$\bf{Other\/fitting\/data:}$")
        parametersStr.append(r'Number of data points = {0}'.format(numberOfDataPoints))
        parametersStr.append(r'Number of parameters  = {0}'.format(numberOfParameters))
        parametersStr.append(r'$\chi^2$ = {0:.5e}'.format(chiSquared))
        parametersStr.append(r'$\chi_r^2$ = {0:.5e}'.format(redChiSquared))
        parametersStr.append(r'Acceptable range of $\chi_r^2$ = ({0:.2f},{1:.2f})'.format(redChiSquaredLimits[0],redChiSquaredLimits[1]))

        #Adding an important note
        if(not ERR):
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
