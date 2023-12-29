# CFit
CFit is a curve fitting tool in Python, based on the method of least squares. It is equipped with some standard functions, and can be used out-of-the-box for simple datasets through its "smart" parameter guesses.

<img src="https://github.com/JitenDhandha/CFit/blob/master/CFit.png" width="31.4%" height="31.4%">

## Example
```
import numpy as np
import matplotlib.pyplot as plt
import dataset, function, fitting

# Load data
data = dataset.Dataset('path/to/data.csv')
function = function.functions_dict["Gaussian"]
fit = fitting.Fit(data, function)

# Plot data
plt.plot(data.x, data.y, 'o', label='data')
plt.plot(data.x, fit.function(data.x, *fit.fit_params), label='fit')
```
  
## Bugs and suggestions

If you find any bugs, run into errors or have suggestions on functions you would like to see added, feel free to open a GitHub issue or email me directly at jitendhandha[a]gmail[dot]com. I will be more than happy to take a look at it!

### Have fun plotting!