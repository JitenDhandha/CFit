####################################################################################
#                                    LIBRARIES                                     #
####################################################################################

import warnings
import numpy as np
import scipy.optimize as opt
import scipy.stats as stats

from _guess_params import *

####################################################################################
#                                    CLASS: Fit                                    #
####################################################################################

class Fit():
    
    def __init__(self, dataset, function, auto=True, ini_params=None):
        
        #Store the dataset and function
        self.dataset = dataset
        self.function = function
        
        #If no initial parameters are given, use the auto_ini_params function
        if(auto):
            try:
                self.ini_params = guess_params(dataset,function)
            except ValueError as e:
                raise ValueError(f'Could not guess initial parameters. {e}')
        else:
            if(ini_params is None):
                raise ValueError('No initial parameters were given.')
            elif(len(ini_params) != function.num_params):
                raise ValueError('Number of initial parameters does not match the number of function parameters.')
            else:
                try:
                    self.ini_params = [float(i) for i in ini_params]
                except ValueError:
                    raise ValueError('Initial parameters must be numeric.')
            self.ini_params = ini_params
            
        #Perform the fit. Note that sigma=None is equivalent to sigma=1
        #absolute_sigma=True forces the errors to not be used in a relative manner (often what is needed?)
        sig_flag = False if dataset.y_err is None else True
        try:
            fit_struct = opt.curve_fit(function, 
                        dataset.x, dataset.y, sigma=dataset.y_err,
                        p0=self.ini_params,
                        absolute_sigma=sig_flag,
                        )
        except RuntimeError as e:
            if str(e).startswith('Optimal parameters not found'):
                raise RuntimeError('Could not find optimal parameters. Try changing the initial parameters.')

        #Unwrapping the fit parameters and covariance matrix
        self.fit_params = fit_struct[0]
        self.fit_errors = np.sqrt(np.diag(fit_struct[1]))
        
        #Calculate the goodness of fit
        dof = dataset.num_points - function.num_params
        self.red_chi2 = function.chi2(self.fit_params,dataset)/dof
        p_values = [0.95,0.05] # 95% and 5% confidence levels
        self.red_chi2_limits = stats.chi2.isf(p_values,dof)/dof