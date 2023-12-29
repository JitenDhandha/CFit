####################################################################################
#                                    LIBRARIES                                     #
####################################################################################

import numpy as np
import pandas as pd

####################################################################################
#                                  CLASS: Dataset                                  #
####################################################################################

class Dataset():
    
    def __init__(self, file_path):
        
        # Read data from file
        df = pd.read_table(file_path, # file path
                  delimiter=',|\s+|\t+', # delimiter can be ',' or spaces or tabs
                  engine='python') # engine='python' is needed for the delimiter to work

        # CHECK #1: data has 2 or 3 columns
        ncols = len(df.columns)
        if (ncols == 2):
            df.columns = ['x', 'y']
            self.y_err = None
        elif (ncols == 3):
            df.columns = ['x', 'y', 'y_err']
            self.y_err = df['y_err'].values
        else:
            raise ValueError('Data must have 2 or 3 columns.')

        # CHECK #2: data is all numeric and doesn't contain NaN or Infs
        # (Note: to_numeric converts non-numeric values to NaN)
        df = df.apply(lambda s: pd.to_numeric(s, errors='coerce'))
        is_finite = ~df.isin([np.nan, np.inf, -np.inf]).any().any()
        if(not is_finite):
            raise ValueError('Data must be all numeric and cannot contain NaN or Inf.')

        # CHECK #3: Y-axis errors are positive
        if (self.y_err is not None):
            is_yerr_positive = df['y_err'].gt(0).all()
            if(not is_yerr_positive):
                raise ValueError('Data must have positive \'y_err\'.')
            
        # Sort data by x values
        df.sort_values(by=['x'], inplace=True)
    
        # Set class variables
        self._df = df
        self.x = df['x'].values
        self.y = df['y'].values
        #self.y_err is set above
        self.num_points = len(self.x)