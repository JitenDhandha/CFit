from fastapi import FastAPI
from nicegui import app, ui
from cfit import gui

@ui.page("/", title="CFit v2.0", favicon="./CFit.png")
def init():
    gui.GUI()
    
fastapi_app = FastAPI()
ui.run_with(fastapi_app,storage_secret='secret')

if __name__ == '__main__':
    print('Please start with "uvicorn main:fastapi_app --reload"')