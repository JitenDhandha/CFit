# CFit

**CFit** is a curve fitting tool written in Python, based on the method of least squares. It comes equipped with some standard functions used in physics, and a graphical user interface built using Streamlit. Some of the functions provided are: _polynomials_ from linear upto quintic; _periodic_ functions like sine and square waves; _peaked_ functions such as Gaussian, Lorentzian, Poisson, Laplacian; and _monotonic_ functions like exponential, power law, and logarithmic.

Under the hood, the code calls `scipy.optimize.curve_fit`, but the real strength of this tool lies in the fact that by looking at the range, scale and behaviour of the data, the code automatically provides a initial guess for the parameters for `curve_fit` to work with. Of course, if the user decides, they can also provide their own initial guess, which can be useful in cases where the code fails to work.

<img src="https://github.com/JitenDhandha/CFit/blob/master/CFit.png" width="31.4%" height="31.4%">

## Usage
The easiest way to use the code is the web app: [CFit v3.0](https://cfit-v3.streamlit.app/). However, it can also be used in code without the GUI. A minimal working example is:
```
import numpy as np
import matplotlib.pyplot as plt
from cfit import dataset, function, fitting

# Load and fit the data
data = dataset.Dataset('path/to/data.csv')
function = function.functions_dict["Gaussian"]
fit = fitting.Fit(data, function)

# Plot data
plt.plot(data.x, data.y, 'o', label='data')
plt.plot(data.x, fit.function(data.x, *fit.fit_params), label='fit')
```
  
## Acknowledgements, bugs, etc.

This initially started as a passion project during the COVID-19 lockdown in 2020, partly inspired by a similar, much more basic tool used at the University of Manchester called `LSFR.py` (by Abie Marshall, 2016). The code was written in a few days, but the GUI took a couple weeks to get right (with a v2.0 built in 2023, and a v3.0 built in 2026).

If you find any bugs, run into errors or have suggestions on functions you would like to see added, feel free to open a GitHub issue or email me directly at jitendhandha[a]gmail[dot]com. I will be more than happy to take a look at it! 

The code is released under CC0 1.0 Universal, so you are free to use it for any purpose, including commercial applications, without asking for permission.

## Have fun plotting!