####################################################################################
# Jiten Dhandha, 2023                                                              #
# CFit is a curve fitting tool in python, based on the method of least squares.    #
# It comes equipped with some standard functions and a graphical user interface.   #
####################################################################################

####################################################################################
#                                    LIBRARIES                                     #
####################################################################################

import os
from io import StringIO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plotly import graph_objects as go
from nicegui import ui
from . import dataset, function, fitting

####################################################################################
#                                GLOBAL VARIABLES                                  #
####################################################################################

class GUI():
    
    def __init__(self):
        
        # Initialize non-GUI code variables
        self.data = None
        self.function = None
        self.fit = None
        self._data_and_func = None
        
        # Theme
        self.theme_colors = ['#7f1d1d','#7c2d12','#78350f','#713f12','#365314','#14532d',
                             '#064e3b','#134e4a','#164e63','#0c4a6e','#1e3a8a','#312e81',
                             '#4c1d95','#581c87','#701a75','#831843','#881337']
        self.theme = ui.colors(primary=self.theme_colors[7])
        self.dark_mode = ui.dark_mode(True)
        
        #Run the GUI
        self.run()
        
    def _reset_variables(self):
        self.data = None
        self.function = None
        self.fit = None
        self._data_and_func = None
        
    def __update_data_and_func(self):
        self._data_and_func = self.data is not None and self.function is not None
        
    def _handle_upload(self, e):
        try:
            self.data=None
            self.fit=None
            with StringIO(e.content.read().decode()) as f:
                self.data = dataset.Dataset(f)
            ui.notify(f'Uploaded {e.name} successfully!',type='positive')
            self._update_plot()
            self.__update_data_and_func()
        except ValueError as e:
            ui.notify(f'Could not upload file! {str(e)}',type='negative')
            
    def _show_data(self, e):
        with ui.dialog() as dialog, ui.card():
            dialog.open()
            ui.table.from_pandas(
                self.data._df,pagination={'rowsPerPage': 15},
                ).props('dense')
            ui.button(
                'Close', on_click=dialog.close
                ).classes('w-full justify-center')
                
    def _select_function(self, e):
        if(e.value is None):
            self.function = None
            with self.FN_STR_plot:
                self._fn_str_plot_txt.set_text('')
        else:
            self.function = function.functions_dict[e.value]
            with self.FN_STR_plot:
                self._fn_str_plot_txt.set_text(self.function.string)
            self.__update_data_and_func()
            
    def _perform_fit(self, auto, ini_params=None):
        try:
            self.fit = fitting.Fit(self.data,self.function,auto=auto,ini_params=ini_params)
            with self.FIT_PARAMS_expansion:
                self.FIT_PARAMS_expansion.clear()
                ui.label(f'The best fit parameters for a {self.function} function are as follows:').classes('w-full')
                columns =[{'name': 'Parameter', 'label':'Parameter', 'field': 'Parameter'}, 
                        {'name': 'Best-fit', 'label':'Best-fit', 'field': 'Best-fit'}]
                rows = [
                    {'Parameter': self.function.params[i], 'Best-fit': f'{self.fit.fit_params[i]:.5e} \u00B1 {self.fit.fit_errors[i]:.5e}'}
                    for i in range(self.function.num_params)
                    ]
                ui.table(rows=rows,columns=columns).classes('w-full')
                ui.label(f'The reduced chi-squared of the fit is {self.fit.red_chi2:.5e}.').classes('w-full')
            if(self.fit.red_chi2 > 10):
                ui.notify('Fitting successful but the reduced chi-squared of the fit is greater than 10.',type='warning')
            else:
                ui.notify(f'Fit function successfully!',type='positive')
            self._update_plot()
        except RuntimeError as e:
            ui.notify(f'{str(e)}',type='negative')
        
    def _fit_auto(self):
        self._perform_fit(auto=True)

    def _fit_manual(self, e):
        with ui.dialog() as dialog, ui.card():
            dialog.open()
            ui.label('Enter the initial parameters for the fit below.').classes('w-full')
            ini_params = [1]*self.function.num_params
            def set_param(i,val):
                ini_params[i] = val
                if(np.all([validate_param(i) for i in ini_params])):
                    fit_button.enable()
                else:
                    fit_button.disable()
            def validate_param(val):
                try:
                    float(val)
                    return True
                except ValueError:
                    return False
            for i in range(self.function.num_params):
                ui.input(label=f'{self.function.params[i]} =',
                         on_change=lambda e: set_param(i,e.value),
                         value=1,
                         validation={'Non-numeric input': validate_param},
                         ).classes('w-full')
            fit_button = ui.button('Fit',
                on_click=lambda e: self._perform_fit(auto=False,ini_params=ini_params)
                ).classes('w-full justify-center')
            
    def _update_axis(self):
        fig = self.MAIN_fig
        xstr = self.XLABEL_input.value if self.XLABEL_input.value != '' else None
        ystr = self.YLABEL_input.value if self.YLABEL_input.value != '' else None
        tstr = self.TITLE_input.value if self.TITLE_input.value != '' else None
        fig.update_layout(
            title=dict(text=tstr,font_size=self.TITLE_SIZE_slider.value,x=0.5,y=0.98),
            xaxis=dict(title=dict(text=xstr,font_size=self.XLABEL_SIZE_slider.value)),
            yaxis=dict(title=dict(text=ystr,font_size=self.YLABEL_SIZE_slider.value)),
            )
        self.MAIN_fig.update_xaxes(showgrid=self.GRID_checkbox.value,
                                   zeroline=self.GRID_checkbox.value)
        self.MAIN_fig.update_yaxes(showgrid=self.GRID_checkbox.value,
                                   zeroline=self.GRID_checkbox.value)
        self.MAIN_fig_ui.update()
        
    def _update_plot(self):
        fig = self.MAIN_fig
        fig.data = []
        if(self.data is not None):
            if(self.SCATTER_checkbox.value):
                fig.add_trace(
                    go.Scatter(x=self.data.x,y=self.data.y,
                        error_y=dict(type='data',array=self.data.y_err if self.ERROR_checkbox.value else None),
                        mode='markers',
                        marker=dict(color=self.SCATTER_color.value,size=self.SCATTER_SIZE_slider.value),
                        name='Data')
                    )
        if(self.fit is not None):
            if(self.LINE_checkbox.value):
                x = np.linspace(self.data.x[0],self.data.x[-1],250)
                fig.add_trace(
                    go.Scatter(x=x,y=self.fit.function(x,*self.fit.fit_params),
                        mode='lines',
                        line=dict(color=self.LINE_color.value,width=self.LINE_WIDTH_slider.value),
                        name='Best fit')
                    )
        self.MAIN_fig_ui.update()
            
    def _change_dark(self):
        self.dark_mode.value = not self.dark_mode.value
        with self.FN_STR_plot:
            plt.gcf().set_facecolor('black' if self.dark_mode.value else 'white')
            self._fn_str_plot_txt.set_color('white' if self.dark_mode.value else 'black')
        self.MAIN_fig.layout.template = 'plotly_dark' if self.dark_mode.value else 'plotly_white'
        self.MAIN_fig_ui.update()
            
    def _change_theme(self):
        clr = self.theme_colors
        idx = clr.index(self.theme._props['primary']) 
        self.theme = ui.colors(primary=clr[(idx+1)%len(clr)])
        pass

    def run(self):
        
        self.HEADER = ui.header(
            ).classes('w-full h-[11%] items-center justify-center content-center bg-primary')
        with self.HEADER.classes(''):
            ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ui.image(f'{ROOT_DIR}/CFit.png').classes('w-[4.8%]')
            ui.label('Curve Fitting Tool v2.0'
                ).classes('text-5xl'
                ).style('font-family: Monaco')
            ui.label('by Jiten Dhandha').classes('mr-auto')
            ui.button(icon='dark_mode',
                on_click=self._change_dark
                ).props('round'
                ).tooltip('Toggle dark mode')
            ui.button(icon='palette',
                on_click=self._change_theme
                ).props('round'
                ).tooltip('Change theme')
            ui.button(icon='code',
                on_click=lambda: ui.open('https://github.com/JitenDhandha/CFit', new_tab=True)
                ).props('round'
                ).tooltip('GitHub')
        
        with ui.row().classes('w-full no-wrap'):
            
            #############################################
            #               Data set card               #
            #############################################
            
            with ui.card().classes('w-[25%]'):
                
                ui.label('Data set').classes('text-2xl')
                
                # Upload button
                self.UPLOAD_element = ui.upload(
                    label="Upload your data set (.txt, .csv, .xlsx)",
                    auto_upload=True,max_files=1,on_upload=self._handle_upload,
                        ).props('accept=".txt, .csv, .xlsx"'
                        ).classes('w-full')
                    
                # Show data button
                self.SHOW_DATA_button = ui.button(
                    'Show data', on_click=self._show_data,
                    ).classes('w-full h-[3.1rem]'
                    ).bind_enabled_from(self, 'data')
            
            #############################################
            #            Fitting function card          #
            #############################################
            with ui.card().classes('w-[73.8%]'):
                
                ui.label('Fitting function').classes('text-2xl')
                
                with ui.row().classes('w-full items-center items-stretch'):
                    
                    ui.label(
                        '''
                        The data is fit to a function of your choice through scipy.curve_fit. 
                        This requires an initial guess for the parameters.
                        You can either fit the data automatically, which will use my under-the-hood "magic" 
                        to provide a good first guess, or you can fit the data manually
                        using your own initial guess.
                        '''
                        ).classes('w-full')
        
                    # Fitting function selector
                    self.FN_select = ui.select(
                        list(function.functions_dict.keys()),
                        label='Fitting function',on_change=self._select_function
                        ).classes('w-1/4')
                        
                    # Fitting function string
                    
                    self.FN_STR_plot = ui.pyplot(figsize=(3,0.59),facecolor='black')
                    with self.FN_STR_plot:
                        plt.axis('off')
                        self._fn_str_plot_txt = plt.text(0.5, 0.5,'',
                                                         fontsize=12.4,weight='bold',
                                                         ha='center',va='center',
                                                         color='white')
                    # Auto fit button
                    self.AUTO_FIT_button = ui.button(
                        'Fit automatically', on_click=self._fit_auto
                        ).classes('w-1/5'
                        ).bind_enabled_from(self,'_data_and_func')
                    
                    # Manual fit button
                    self.MAN_FIT_button = ui.button(
                        'Fit manually', on_click=self._fit_manual
                        ).classes('w-1/5'
                        ).bind_enabled_from(self,'_data_and_func')
                        
                    self.FIT_PARAMS_expansion =  ui.expansion(
                        'Best fit', icon='fitness_center'
                        ).classes(f'w-full bg-primary text-white'
                        ).bind_enabled_from(self,'fit')
                    
        with ui.row().classes('w-full no-wrap'):
            
            #############################################
            #             Plot options card             #
            #############################################
            with ui.card().classes('w-[50%]'):
                
                ui.label('Plotting options').classes('text-2xl')
                
                with ui.row().classes('w-full items-center'):
                    
                    self.TITLE_input = ui.input(label='Plot title',
                        ).classes('w-[31%]')
                    with self.TITLE_input:
                        ui.button(on_click=self._update_axis, icon='send'
                                  ).classes('w-1/6'
                                  ).props('flat dense')
                    self.XLABEL_input = ui.input(label='X-axis label',
                        ).classes('w-[31%]')
                    with self.XLABEL_input:
                        ui.button(on_click=self._update_axis, icon='send'
                                  ).classes('w-1/6'
                                  ).props('flat dense')
                    self.YLABEL_input = ui.input(label='Y-axis label',
                        ).classes('w-[31%]')
                    with self.YLABEL_input:
                        ui.button(on_click=self._update_axis, icon='send'
                                  ).classes('w-1/6'
                                  ).props('flat dense')
                    with ui.column().classes('w-[31%]'):
                        ui.label('Title size').classes('w-full')
                        self.TITLE_SIZE_slider = ui.slider(min=5, max=25,value=15,
                            on_change=self._update_axis
                            ).classes('w-full')
                    with ui.column().classes('w-[31%]'):
                        ui.label('X-Label size').classes('w-full')
                        self.XLABEL_SIZE_slider = ui.slider(min=5, max=25,value=15,
                            on_change=self._update_axis
                            ).classes('w-full')
                    with ui.column().classes('w-[31%]'):
                        ui.label('Y-Label size').classes('w-full')
                        self.YLABEL_SIZE_slider = ui.slider(min=5, max=25,value=15,
                            on_change=self._update_axis
                            ).classes('w-full')
                    with ui.column().classes('w-[31%]'):
                        self.SCATTER_checkbox = ui.checkbox('Show scatter',value=True,
                            on_change=self._update_plot
                            ).bind_enabled_from(self,'data')
                        self.ERROR_checkbox = ui.checkbox('Show error bars',value=True,
                            on_change=self._update_plot
                            ).bind_enabled_from(self,'data')
                    with ui.column().classes('w-[31%]'):
                        ui.label('Scatter size').classes('w-full')
                        self.SCATTER_SIZE_slider = ui.slider(min=1, max=10,value=1,
                            on_change=self._update_plot
                            ).classes('w-full'
                            ).bind_enabled_from(self,'data')
                    self.SCATTER_color = ui.color_input(label='Scatter color',value='#ffffff',
                        on_change=self._update_plot
                        ).classes('w-[31%]'
                        ).bind_enabled_from(self,'data')
                    self.LINE_checkbox = ui.checkbox('Show best fit',value=True,
                        on_change=self._update_plot
                        ).classes('w-[31%]'
                        ).bind_enabled_from(self,'fit')
                    with ui.column().classes('w-[31%]'):
                        ui.label('Line width').classes('w-full')
                        self.LINE_WIDTH_slider = ui.slider(min=1, max=10,value=1,
                            on_change=self._update_plot
                            ).classes('w-full'
                            ).bind_enabled_from(self,'fit')
                    self.LINE_color = ui.color_input(label='Line color',value='#ff0000',
                        on_change=self._update_plot
                        ).classes('w-[31%]'
                        ).bind_enabled_from(self,'fit')
                    self.GRID_checkbox = ui.checkbox('Show grid',value=True,
                        on_change=self._update_axis
                        ).classes('w-[31%]')
            
            #############################################
            #                Main plot card             #
            #############################################
            with ui.card().classes('w-[49.8%]'):
                with ui.column().classes('w-full items-center'):
                    self.MAIN_fig = go.Figure()
                    self.MAIN_fig.layout.template = 'plotly_dark'
                    self.MAIN_fig.update_layout(
                        margin=dict(l=2,r=2,b=2,t=2),
                        width=650,
                        height=435,
                        showlegend=False
                        )
                    self.MAIN_fig_ui = ui.plotly(self.MAIN_fig)
        
        ui.button('Clear all', on_click=self.clear_all).classes('w-full')
        
    def clear_all(self):
        self._reset_variables()
        self.UPLOAD_element.reset()
        self.FN_select.set_value(None)
        self.FIT_PARAMS_expansion.clear()
        self.TITLE_input.set_value('')
        self.XLABEL_input.set_value('')
        self.YLABEL_input.set_value('')
        self.SCATTER_checkbox.set_value(True)
        self.ERROR_checkbox.set_value(True)
        self.SCATTER_SIZE_slider.set_value(1)
        self.SCATTER_color.set_value('#000000')
        self.LINE_checkbox.set_value(True)
        self.LINE_WIDTH_slider.set_value(1)
        self.LINE_color.set_value('#ff0000')
        self.GRID_checkbox.set_value(True)
        self._update_plot()
        self._update_axis()