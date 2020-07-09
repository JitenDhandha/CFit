# CFit
CFit is a curve fitting tool in python, based on the method of least squares. It comes equipped with some standard functions and a graphical user interface.

<img src="https://github.com/JitenDhandha/CFit/blob/master/CFit.png" width="31.4%" height="31.4%">

## Installation
- Click the drop down menu titled 'Code' at the top right of the window and select 'Download zip'.
- Save this zip file wherever you want the curve fitting tool to be.
- Unzip the contents of the zip file and run the file titled 'Main.py' on a python IDE of your choice!

**Note**: The files 'Fitting.py' and 'Main.py' need to be in the same folder for it to work!

## Interface

<img src="https://user-images.githubusercontent.com/68048517/87061686-f63b6700-c203-11ea-995b-e4e5adf8e580.PNG" width="50%" height="50%">

## How to use it

- Browse a .txt or .csv file with your data set. The file must have 2 columns (no errors along y-axis) or 3 columns (with errors along y-axis), separated by commas or spaces. 
- You can then choose to plot the raw data or choose a function to fit the data to. The tool has the option for fitting polynomials of degree 0 upto 5 along with some other standard functions.
- Click 'Fit data automatically' if you want the tool to attempt a fit by itself. Or click 'Fit data using my guess' after providing an initial guess for the fitting parameters if you want to attempt a fit manually.
- You should see the best fit line if the routine runs successfully. You can add plot annotations, grid lines or view the fit parameters and residuals plot as you wish!

**Note on errors**: In case no errors are provided along the y-axis, the error on the parameters and the chi-squared value are calculated based on an error of 1.00 (arbitrary unit) on each data point. Due to this, the errors on the fitting parameters dont have much meaning; however the best fit can still be useful!

### Have fun plotting!
