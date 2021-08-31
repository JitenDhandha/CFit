# CFit
CFit is a curve fitting tool in Python, based on the method of least squares. It comes equipped with some standard functions and a graphical user interface.

<img src="https://github.com/JitenDhandha/CFit/blob/master/CFit.png" width="31.4%" height="31.4%">

## Installation
- Click the drop down menu titled 'Code' at the top right of the window and select 'Download zip'.
- Save this zip file wherever you want the curve fitting tool to be.
- Unzip the contents of the zip file and run the file titled 'Main.py' on a Python IDE of your choice! Make sure you have numpy, scipy, matplotlib and tkinter packages installed on your version of Python.

**Note**: The files 'Fitting.py' and 'Main.py' need to be in the same folder for it to work!

## Interface

<img src="https://user-images.githubusercontent.com/68048517/92326951-a0960600-f05e-11ea-98f1-9a3fc009a36c.PNG" width="50%" height="50%">

## How to use it

- Browse a .txt or .csv file with your data set. The file must have 2 columns (no errors along y-axis) or 3 columns (with errors along y-axis), separated by commas or spaces. 
- You can then choose to plot the raw data or choose a function to fit the data to. The tool has the option for fitting polynomials of degree 0 upto 5 along with some other standard functions.
- Click 'Fit data automatically' if you want the tool to attempt a fit by itself. Or click 'Fit data using my guess' after providing an initial guess for the fitting parameters if you want to attempt a fit manually.
- You should see the best fit line if the routine runs successfully. You can add plot annotations, grid lines or view the fit parameters and residuals plot as you wish!

**Note on errors**: In case no errors are provided along the y-axis, the error on the parameters and the chi-squared value are calculated based on an error of 1.00 (arbitrary unit) on each data point. Due to this, the errors on the fitting parameters dont have much meaning; however the best fit can still be useful!

## Bugs and suggestions

If you find any bugs, run into errors or have suggestions on functions you would like to see added, feel free to open a GitHub issue or email me directly at jitendhandha@gmail.com. I will be more than happy to take a look at it!

### Have fun plotting!
