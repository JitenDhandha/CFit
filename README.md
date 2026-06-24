# CFit
CFit (named after optimization algorithm `scipy.curve_fit`) is a curve fitting tool in Python, based on the method of least squares. It is equipped with some standard functions commonly used in physics, and plotting functionality, with a graphical user interface built using Streamlit. It can be used out-of-the-box for simple datasets through its "smart" parameter guesses. The code began as a lockdown project in 2020, partly inspired by a similar, much more basic tool used at the University of Manchester called `LSFR.py` (by Abie Marshall, 2016). It was written in a few days, but the GUI took a couple weeks to get right (with a v2.0 built in 2023, and v3.0 built in 2026). Try it for yourself at [CFit v2.0](https://cfit.onrender.com/)!

<img src="https://github.com/JitenDhandha/CFit/blob/master/CFit.png" width="31.4%" height="31.4%">

## Usage
The easiest way to use the code is the web app linked above. However, it can also be used in code without the GUI. A minimal working example is:
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
  
## Bugs and suggestions
If you find any bugs, run into errors or have suggestions on functions you would like to see added, feel free to open a GitHub issue or email me directly at jitendhandha[a]gmail[dot]com. I will be more than happy to take a look at it! The code is released under CC0 1.0 Universal, so you are free to use it for any purpose, including commercial applications, without asking for permission.

### Have fun plotting!