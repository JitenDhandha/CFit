####################################################################################
#                                    LIBRARIES                                     #
####################################################################################


from io import BytesIO, StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from . import dataset, fitting, function


####################################################################################
#                                 GLOBALS/STYLING                                  #
####################################################################################


_STATE_DEFAULTS = {
    'data': None,
    'fit': None,
    'function_name': '',
    'manual_fit_open': False,
    'title': '',
    'xlabel': '',
    'ylabel': '',
    'title_size': 15,
    'xlabel_size': 15,
    'ylabel_size': 15,
    'scatter_visible': True,
    'error_visible': True,
    'scatter_size': 1,
    'scatter_color': '#ffffff',
    'line_visible': True,
    'line_width': 1,
    'line_color': '#ff0000',
    'show_grid': True,
    'x_log': False,
    'y_log': False,
    '_clear_all_pending': False,
}

def _apply_css():

    background = '#08111f'
    text = '#e5eefb'
    muted = '#a8b3c7'
    primary = '#134e4a'

    def _rgba(hex_color, alpha):
        return 'rgba({}, {}, {}, {})'.format(*[int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)], alpha)

    st.markdown(
        f'''
        <style>
        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"] {{
            display: none;
        }}
        .stApp {{
            background:
                radial-gradient(circle at top left, {_rgba(primary, 0.24)}, transparent 34%),
                radial-gradient(circle at top right, {_rgba(primary, 0.14)}, transparent 22%),
                linear-gradient(180deg, {background} 0%, {background} 100%);
            color: {text};
        }}
        .block-container {{
            padding-top: 2.5rem;
            padding-bottom: 1.5rem;
            max-width: 1480px;
        }}
        .cfit-hero {{
            padding: 0.15rem 0 0.5rem 0;
        }}
        .cfit-section-title {{
            font-size: 1.45rem;
            font-weight: 700;
            margin: 0.1rem 0 0.65rem 0;
            color: {text};
        }}
        .cfit-subtitle {{
            color: {muted};
            line-height: 1.55;
        }}
        div[data-testid="stDataFrame"] {{
            border-radius: 18px;
            overflow: hidden;
        }}
        </style>
        ''',
        unsafe_allow_html=True,
    )


####################################################################################
#                                    HEADER                                        #
####################################################################################


def _render_header():
    left, middle, right = st.columns([0.14, 0.78, 0.08])
    root_dir = Path(__file__).resolve().parents[1]

    with left:
        st.image(str(root_dir / 'CFit.png'), width='stretch')

    with middle:
        st.markdown(
            '''
            <div class="cfit-hero" style="width: 100%;">
                <div style="font-size: 3rem; font-weight: 800; line-height: 1.05;">Curve Fitting Tool v3.0</div>
                <div style="font-size: 1rem; opacity: 0.88; margin-top: 0.35rem;">by Jiten Dhandha</div>
                <div style="margin-top: 0.75rem; font-size: 0.96rem; line-height: 1.55; opacity: 0.82;">
                    CFit is a curve fitting tool in Python, based on the method of least squares. It is equipped with some standard functions commonly used in physics and can be used out-of-the-box for simple datasets through its "smart" parameter guesses. The code began as a lockdown project in 2020. It was written in a few days, but the GUI took a couple weeks to get right (with a v2.0 built in 2023, and v3.0 built in 2026).
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )


####################################################################################
#                                LOADING DATASET                                   #
####################################################################################


def _load_dataset(uploaded_file):
    if uploaded_file is None:
        st.session_state.data = None
        st.session_state.fit = None
        return

    try:
        suffix = Path(uploaded_file.name).suffix.lower()
        if suffix == '.xlsx':
            frame = pd.read_excel(BytesIO(uploaded_file.getvalue()))
            csv_buffer = StringIO()
            frame.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            st.session_state.data = dataset.Dataset(csv_buffer)
        else:
            st.session_state.data = dataset.Dataset(StringIO(uploaded_file.getvalue().decode('utf-8')))
        st.session_state.fit = None
        st.toast(f'Uploaded {uploaded_file.name} successfully.', icon='✅')
    except Exception as exc:
        st.session_state.data = None
        st.session_state.fit = None
        st.toast(f'Could not upload file: {exc}', icon='⚠️')


def _render_dataset_card():
    st.markdown('<div class="cfit-section-title">1. Upload data set</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        'Upload your data set (.txt, .csv, .xlsx)',
        type=['txt', 'csv', 'xlsx'],
        key='uploaded_file',
        label_visibility='collapsed',
        on_change=lambda: _load_dataset(st.session_state.uploaded_file),
    )


####################################################################################
#                                FITTING DATASET                                   #
####################################################################################


def _fit_data(selected_function, auto=True, ini_params=None):
    try:
        fit = fitting.Fit(st.session_state.data, selected_function, auto=auto, ini_params=ini_params)
    except Exception as exc:
        st.session_state.fit = None
        st.toast(str(exc), icon='⚠️')
        return

    st.session_state.fit = fit
    if fit.red_chi2 > 10:
        st.toast('Fitting successful but the reduced chi-squared is greater than 10.', icon='⚠️')
    else:
        st.toast('Fitting successful.', icon='✅')


@st.dialog('Manual fit')
def _manual_fit_dialog(selected_function):
    st.caption('Enter the initial parameter guesses.')
    manual_params = [
        st.number_input(param_name, value=1.0, key=f'manual_{selected_function.name}_{idx}')
        for idx, param_name in enumerate(selected_function.params)
    ]

    action_columns = st.columns(2)
    if action_columns[0].button('Run manual fit', width='stretch'):
        _fit_data(selected_function, auto=False, ini_params=manual_params)
        st.session_state.manual_fit_open = False
        st.rerun()

    if action_columns[1].button('Cancel', width='stretch'):
        st.session_state.manual_fit_open = False
        st.rerun()

def _render_function_card():
    def _on_function_change():
        selected = function.functions_dict.get(st.session_state.function_name)
        fit = st.session_state.fit
        if fit is not None and selected is not None and fit.function is not selected:
            st.session_state.fit = None
            st.session_state.manual_fit_open = False

    st.markdown('<div class="cfit-section-title">2. Pick a fitting function </div>', unsafe_allow_html=True)

    options = [''] + list(function.functions_dict.keys())
    st.selectbox(
        'Fitting function',
        options,
        key='function_name',
        on_change=_on_function_change,
        label_visibility='collapsed',
    )
    selected_function = function.functions_dict.get(st.session_state.function_name)

    if selected_function is not None:
        st.latex(selected_function.string.strip('$'))

    button_row = st.columns(2)
    can_fit = st.session_state.data is not None and selected_function is not None
    if button_row[0].button('Fit automatically', disabled=not can_fit, width='stretch'):
        st.session_state.manual_fit_open = False
        _fit_data(selected_function, auto=True)
    if button_row[1].button('Fit manually', disabled=not can_fit, width='stretch'):
        st.session_state.manual_fit_open = True

    if st.session_state.manual_fit_open and selected_function is not None:
        _manual_fit_dialog(selected_function)


####################################################################################
#                                PLOTTING DATASET                                  #
####################################################################################


def _build_figure():
    fig = go.Figure()

    if st.session_state.data is not None and st.session_state.scatter_visible:
        fig.add_trace(
            go.Scatter(
                x=st.session_state.data.x,
                y=st.session_state.data.y,
                error_y=dict(
                    type='data',
                    array=st.session_state.data.y_err if st.session_state.error_visible else None,
                    visible=st.session_state.error_visible and st.session_state.data.y_err is not None,
                ),
                mode='markers',
                marker=dict(color=st.session_state.scatter_color, size=st.session_state.scatter_size * 4),
                name='Data',
            )
        )

    if st.session_state.fit is not None and st.session_state.line_visible:
        x_values = np.linspace(st.session_state.data.x[0], st.session_state.data.x[-1], 250)
        fit = st.session_state.fit
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=fit.function(x_values, *fit.fit_params),
                mode='lines',
                line=dict(color=st.session_state.line_color, width=st.session_state.line_width * 2),
                name=f'Best fit (χ² = {fit.red_chi2:.3e})',
            )
        )
        for idx, param_name in enumerate(fit.function.params):
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode='markers',
                    marker=dict(size=0.1, color='rgba(0,0,0,0)'),
                    name=f'{param_name} = {fit.fit_params[idx]:.3e} ± {fit.fit_errors[idx]:.3e}',
                    showlegend=True,
                    hoverinfo='skip',
                    visible='legendonly',
                )
            )

    title = st.session_state.title.strip() or None
    xlabel = st.session_state.xlabel.strip() or None
    ylabel = st.session_state.ylabel.strip() or None

    fig.update_layout(
        title=dict(text=title, font_size=st.session_state.title_size, x=0.5, y=0.98) if title else {},
        xaxis=dict(title=dict(text=xlabel, font_size=st.session_state.xlabel_size)),
        yaxis=dict(title=dict(text=ylabel, font_size=st.session_state.ylabel_size)),
        margin=dict(l=4, r=4, b=4, t=40),
        showlegend=st.session_state.data is not None,
        template='plotly_dark',
        height=405,
    )
    fig.update_xaxes(
        exponentformat='E',
        showgrid=st.session_state.show_grid,
        zeroline=st.session_state.show_grid,
        type='log' if st.session_state.x_log else 'linear',
    )
    fig.update_yaxes(
        exponentformat='E',
        showgrid=st.session_state.show_grid,
        zeroline=st.session_state.show_grid,
        type='log' if st.session_state.y_log else 'linear',
    )
    return fig

def _render_plotting_card():
    st.markdown('<div class="cfit-section-title">3. Style your plot</div>', unsafe_allow_html=True)

    row1 = st.columns(3)
    row1[0].text_input('Title', key='title')
    row1[1].text_input('X-axis label', key='xlabel')
    row1[2].text_input('Y-axis label', key='ylabel')

    row2 = st.columns(3)
    row2[0].slider('Title size', 5, 25, key='title_size')
    row2[1].slider('X-axis label size', 5, 25, key='xlabel_size')
    row2[2].slider('Y-axis label size', 5, 25, key='ylabel_size')

    checkbox_columns = st.columns(3)
    with checkbox_columns[0]:
        st.checkbox('Show scatter', key='scatter_visible', disabled=st.session_state.data is None)
        st.checkbox('Show best fit', key='line_visible', disabled=st.session_state.fit is None)
    with checkbox_columns[1]:
        st.checkbox('Show errors', key='error_visible', disabled=st.session_state.data is None)
        st.checkbox('Show grid', key='show_grid')
    with checkbox_columns[2]:
        st.checkbox('Log x-axis', key='x_log')
        st.checkbox('Log y-axis', key='y_log')

    control_columns = st.columns(2)
    with control_columns[0]:
        st.color_picker('Scatter color', key='scatter_color', disabled=st.session_state.data is None)
        st.slider('Scatter size', 1, 10, key='scatter_size', disabled=st.session_state.data is None)
    with control_columns[1]:
        st.color_picker('Line color', key='line_color', disabled=st.session_state.fit is None)
        st.slider('Line size', 1, 10, key='line_width', disabled=st.session_state.fit is None)


####################################################################################
#                                      MAIN                                        #
####################################################################################


def render_app():
    st.set_page_config(page_title='CFit v3.0', page_icon='📈', layout='wide')

    for key, value in _STATE_DEFAULTS.items():
        st.session_state.setdefault(key, value)

    if st.session_state._clear_all_pending:
        for key, value in _STATE_DEFAULTS.items():
            st.session_state[key] = value
        st.rerun()

    _apply_css()

    _render_header()

    upper_left, upper_right = st.columns([1.0, 2.0], gap='small')
    with upper_left:
        with st.container(border=True):
            _render_dataset_card()
    with upper_right:
        with st.container(border=True):
            _render_function_card()

    lower_left, lower_right = st.columns([1.0, 2.0], gap='small')
    with lower_left:
        with st.container(border=True):
            _render_plotting_card()
    with lower_right:
        with st.container(border=True):
            st.markdown('<div class="cfit-section-title">4. Visualize your dataset and fit</div>', unsafe_allow_html=True)
            st.plotly_chart(_build_figure(), width='stretch')

    st.button('Clear all', width='stretch', on_click=lambda: st.session_state.update({'_clear_all_pending': True}))