####################################################################################
#                                    LIBRARIES                                     #
####################################################################################

import inspect
import numpy as np
import scipy.special as sp

####################################################################################
#                                  CLASS: Function                                 #
####################################################################################

class Function():
    
    def __init__(self, name, func, string):
        self.name = name
        self.func = func
        self.string = string
        self.params = list(inspect.signature(self.func).parameters.keys())[1:]
        self.num_params = len(self.params)

    def __call__(self, x, *args):
        return self.func(x, *args)
    
    def __str__(self):
        return self.name
    
    # Calculate the chi2 value for a given set of parameters and dataset
    def chi2(self, params, dataset):
        if(len(params) != self.num_params):
            raise ValueError('Number of parameters does not match the number of function parameters.')
        x = dataset.x
        y = dataset.y
        y_err = dataset.y_err if dataset.y_err is not None else 1
        y_fit = self.func(x,*params)
        chi2 = np.sum( ((y-y_fit)/y_err)**2 )
        return chi2

####################################################################################
#                Dictionary to hold all the pre-defined functions                  #
####################################################################################

functions_dict = {
        'Constant': 
         Function(name='Constant',
              func=lambda x,a: np.polyval([a],x),
              string=r"$y = a$",
              ),

        'Linear': 
        Function(name='Linear',
             func=lambda x,a,b: np.polyval([a,b],x),
             string=r"$y = ax + b$",
             ),

        'Quadratic': 
        Function(name='Quadratic',
             func=lambda x,a,b,c: np.polyval([a,b,c],x),
             string=r"$y = ax^2 + bx + c$",
             ),

        'Cubic': 
        Function(name='Cubic',
             func=lambda x,a,b,c,d: np.polyval([a,b,c,d],x),
             string=r"$y = ax^3 + bx^2 + cx + d$",
             ),

        'Quartic': 
        Function(name='Quadratic',
             func=lambda x,a,b,c,d,e: np.polyval([a,b,c,d,e],x),
             string=r"$y = ax^4 + bx^3 + cx^2 + dx + e$",
             ),

        'Quintic': 
        Function(name='Quintic',
             func=lambda x,a,b,c,d,e,f: np.polyval([a,b,c,d,e,f],x),
             string=r"$y = ax^5 + bx^4 + cx^3 + dx^2 + ex + f$",
             ),

        'Sine wave': 
        Function(name='Sine wave',
             func=lambda x,y0,A,omega,phi: y0 + A*np.sin(omega*x+phi),
             string=r"$y = y_0 + A\sin(\omega x + \phi)$",
             ),

        'Square wave': 
        Function(name='Square wave',
             func=lambda x,y0,A,omega,phi: y0 + A*np.sign(np.sin(omega*x+phi)),
             string=r"$y = y_0 + A~\mathrm{sgn}[\sin(\omega x + \phi)]$",
             ),

        'Gaussian': 
        Function(name='Gaussian',
             func=lambda x,y0,A,mu,sigma: y0 + (A/(sigma*np.sqrt(2*np.pi)))*np.exp((-1/2)*((x-mu)/sigma)**2),
             string=r"$y = y_0 + \frac{A}{\sigma \sqrt{2\pi}}\exp\left[\frac{-(x-\mu)^2}{2\sigma^2}\right]$",
             ),

        'Poisson': 
        Function(name='Poisson',
             func=lambda x,y0,A,lamda: y0 + A*(np.exp(-lamda))*(lamda**x)/sp.gamma(x),
             string=r"$y = y_0 + A\/\frac{e^{-\lambda}\lambda^x}{x!}$",
            ),

        'Laplacian':        
        Function(name='Laplacian',
             func=lambda x,y0,A,mu,b: y0 + (A/(2*b))*np.exp(-np.abs(x-mu)/b),
             string=r"$y = y_0 + \frac{A}{2b}\exp\left[\frac{-|x-\mu|}{b}\right]$",
            ),

        'Lorentzian':       
        Function(name='Lorentzian',
             func=lambda x,y0,A,x0,omega: y0 + (2*A/np.pi)*(omega/(4*(x-x0)**2+omega**2)),
             string=r"$y = y_0 + \frac{2A}{\pi}\frac{\omega}{4(x-x_0)^2+\omega^2}$",
            ),

        'Power':        
        Function(name='Power',
             func=lambda x,A,b: A*(x)**b,
             string=r"$y = Ax^b$",
            ),

        'Exponential':    
        Function(name='Exponential',
             func=lambda x,y0,A,b: y0 + A*np.exp(b*x),
             string=r"$y = y_0 + A\/e^{bx}$",
            ),
        
        'Logarithm':        
        Function(name='Logarithm',
             func=lambda x,y0,A,x0: y0 + A*np.log(x-x0),
             string=r"$y = y_0 + A\log(x-x_0)$",
            ),
        }