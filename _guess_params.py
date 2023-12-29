import warnings
import numpy as np
import scipy.optimize as opt
import scipy.linalg as linalg

def guess_params(dataset, function):
    
    #Data and function variables
    x = dataset.x
    y = dataset.y
    y_err = dataset.y_err if dataset.y_err is not None else np.ones(dataset.num_points)
    num_points = dataset.num_points
    num_params = function.num_params
    
    #Useful quantities for parameter estimation
    xmin = min(x)
    xmax = max(x)
    ymin = min(y)
    ymax = max(y)
    
    #Empty array to store "initial guess"
    ini_params = []
    
    def _wrap_chi2(params):
        return function.chi2(params,dataset)

    #All the parameter estimation happens here

    if(str(function) in ['Constant','Linear','Quadratic','Cubic','Quartic','Quintic']):

        order = num_params - 1
        ini_params = np.polyfit(x,y,deg=order,w=1/y_err)

    elif(str(function)=='Sine wave'):

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

        omega_bound = (0.5*(2*np.pi)*guess_f,2*(2*np.pi)*guess_f)

        BOUNDS = [y0_bound, A_bound, omega_bound, phi_bound]
        BOUNDS = [np.sort(bound) for bound in BOUNDS]

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            ini_params = opt.differential_evolution(_wrap_chi2,bounds=BOUNDS,seed=0).x

    elif(str(function)=='Square wave'):

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

        omega_bound = (0.5*(2*np.pi)*guess_f,2*(2*np.pi)*guess_f)

        BOUNDS = [y0_bound, A_bound, omega_bound, phi_bound]
        BOUNDS = [np.sort(bound) for bound in BOUNDS]

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            ini_params = opt.differential_evolution(_wrap_chi2,bounds=BOUNDS,seed=0).x

    elif(str(function)=='Gaussian'):

        x_range = xmax - xmin
        y_range = ymax - ymin

        mu_bound = (xmin-x_range,xmax+x_range)
        omega_bound = (0,x_range)

        A_bound1 = (abs(y_range)/3,2*abs(y_range)*2.5*x_range)
        y0_bound1 = (ymin-y_range,ymin+y_range/2)
        BOUNDS1 = [y0_bound1, A_bound1, mu_bound, omega_bound]
        BOUNDS1 = [np.sort(bound) for bound in BOUNDS1]

        A_bound2 = (-abs(y_range)/3,-2*abs(y_range)*2.5*x_range)
        y0_bound2 = (ymax-y_range/2,ymax+y_range)
        BOUNDS2 = [y0_bound2, A_bound2, mu_bound, omega_bound]
        BOUNDS2 = [np.sort(bound) for bound in BOUNDS2]

        BOUNDS_LIST = [BOUNDS1,BOUNDS2]

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            bestChiSquared = np.inf
            for BOUNDS in BOUNDS_LIST:
                tempParameters = opt.differential_evolution(_wrap_chi2,bounds=BOUNDS,seed=0).x
                tempChiSquared = _wrap_chi2(tempParameters)
                if(tempChiSquared < bestChiSquared):
                    bestChiSquared = tempChiSquared
                    ini_params = tempParameters
        
    elif(str(function)=='Poisson'):

        x_range = xmax - xmin
        y_range = ymax - ymin

        lamda_bound = (max(0,xmin-x_range),xmax+x_range)

        A_bound1 = (0,2*abs(y_range))
        y0_bound1 = (ymin-y_range,ymin+y_range/2)        
        BOUNDS1 = [y0_bound1, A_bound1, lamda_bound]
        BOUNDS1 = [np.sort(bound) for bound in BOUNDS1]

        A_bound2 = (0,-2*abs(y_range))
        y0_bound2 = (ymax-y_range/2,ymax+y_range)
        BOUNDS2 = [y0_bound1, A_bound1, lamda_bound]  
        BOUNDS2 = [np.sort(bound) for bound in BOUNDS2]

        BOUNDS_LIST = [BOUNDS1,BOUNDS2]

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            bestChiSquared = np.inf
            for BOUNDS in BOUNDS_LIST:
                tempParameters = opt.differential_evolution(_wrap_chi2,bounds=BOUNDS,seed=0).x
                tempChiSquared = _wrap_chi2(tempParameters)
                if(tempChiSquared < bestChiSquared):
                    bestChiSquared = tempChiSquared
                    ini_params = tempParameters

    elif(str(function)=='Laplacian'):
        
        x_range = xmax - xmin
        y_range = ymax - ymin

        mu_bound = (xmin-x_range,xmax+x_range)
        b_bound = (0,x_range)

        A_bound1 = (abs(y_range)/3,2*abs(y_range)*2*x_range)
        y0_bound1 = (ymin-y_range,ymin+y_range/2)
        BOUNDS1 = [y0_bound1, A_bound1, mu_bound, b_bound]
        BOUNDS1 = [np.sort(bound) for bound in BOUNDS1]

        A_bound2 = (-abs(y_range)/3,-2*abs(y_range)*2*x_range)
        y0_bound2 = (ymax-y_range/2,ymax+y_range)
        BOUNDS2 = [y0_bound2, A_bound2, mu_bound, b_bound]
        BOUNDS2 = [np.sort(bound) for bound in BOUNDS2]

        BOUNDS_LIST = [BOUNDS1,BOUNDS2]

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            bestChiSquared = np.inf
            for BOUNDS in BOUNDS_LIST:
                tempParameters = opt.differential_evolution(_wrap_chi2,bounds=BOUNDS,seed=0).x
                tempChiSquared = _wrap_chi2(tempParameters)
                if(tempChiSquared < bestChiSquared):
                    bestChiSquared = tempChiSquared
                    ini_params = tempParameters

    elif(str(function)=='Lorentzian'):

        x_range = xmax - xmin
        y_range = ymax - ymin

        x0_bound = (xmin-x_range,xmax+x_range)
        omega_bound = (0,x_range)

        A_bound1 = (abs(y_range)/3,2*abs(y_range)*np.pi/2*x_range)
        y0_bound1 = (ymin-y_range,ymin+y_range/2)
        BOUNDS1 = [y0_bound1, A_bound1, x0_bound, omega_bound]
        BOUNDS1 = [np.sort(bound) for bound in BOUNDS1]

        A_bound2 = (-abs(y_range)/3,-2*abs(y_range)*np.pi/2*x_range)
        y0_bound2 = (ymax-y_range/2,ymax+y_range)
        BOUNDS2 = [y0_bound2, A_bound2, x0_bound, omega_bound]
        BOUNDS2 = [np.sort(bound) for bound in BOUNDS2]

        BOUNDS_LIST = [BOUNDS1,BOUNDS2]

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            bestChiSquared = np.inf
            for BOUNDS in BOUNDS_LIST:
                tempParameters = opt.differential_evolution(_wrap_chi2,bounds=BOUNDS,seed=0).x
                tempChiSquared = _wrap_chi2(tempParameters)
                if(tempChiSquared < bestChiSquared):
                    bestChiSquared = tempChiSquared
                    ini_params = tempParameters

    elif(str(function)=='Power'):

        lX = np.log(abs(x), where=x>0)
        lY = np.log(abs(y), where=x>0)

        with np.errstate(invalid='ignore'):
            b_est, logA_est = np.polyfit(lX,lY,w=np.exp(lX),deg=1)
        A_est = np.exp(logA_est)

        A_bound = (-A_est,A_est)
        b_bound = (b_est-0.5*abs(b_est),b_est+0.5*abs(b_est))

        BOUNDS = [A_bound,b_bound]
        BOUNDS = [np.sort(bound) for bound in BOUNDS]

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            ini_params = opt.differential_evolution(_wrap_chi2,bounds=BOUNDS,seed=0).x

    elif(str(function)=='Exponential'):
        
        if(np.any(x<=0)):
            raise ValueError('Exponential function cannot be fit to negative or zero x values.')

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

        ini_params = [y0,A,b]

    elif(str(function)=='Logarithm'):
         
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

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            y0 = -A*np.log(t2)
            
        ini_params = [y0,A,x0]

    #Sending the "best guess" parameters
    return ini_params