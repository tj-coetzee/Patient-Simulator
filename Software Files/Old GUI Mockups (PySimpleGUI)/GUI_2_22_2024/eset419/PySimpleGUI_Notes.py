# commands
# imports module
import PySimpleGUI as sg

# layout: 
layout = [[sg.Text("Hello from PySimpleGUI")], [sg.Button("OK")]]

# window: This is the actual whole window. "Demo" is what app will be called.
window = sg.Window("Demo", layout)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break

window.close()