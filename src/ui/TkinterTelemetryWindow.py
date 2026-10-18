from datetime import timedelta
import tkinter

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from core.TelemetryRepository import TelemetryRepository

from Config import Config
from Settings import Settings
from ui.TelemetryView import TelemetryView
from ui.TelemetryPresenter import TelemetryPresenter

class TkinterTelemetryWindow(TelemetryView):
    def __init__(self, presenter:TelemetryPresenter):
        self.presenter = presenter

        self.root: tkinter.Tk | None = None
        self.settings_frame: tkinter.Frame | None = None
        self.buttons_frame: tkinter.Frame | None = None
        self.checkbuttons = {}
        self.checkbuttons_vars = {}

    def destroy(self) -> None:
        self.root.quit()

    def setupView(self) -> None:
        self.root = tkinter.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)

        self.root.bind("<F11>", lambda event: self.presenter.onF11Key())
        self.root.bind("<Escape>", lambda event: self.presenter.onEscapeKey())

        self.setupButtonsPanel()
        self.setupSettingsPanel()
        self.setupPlotCanvas()

        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)

    def setupButtonsPanel(self) -> None:
        self.buttons_frame = tkinter.Frame(master=self.root)
        self.buttons_frame.grid(column=0, row=0, sticky="ns")

        button = tkinter.Button(master=self.buttons_frame,
                text="Settings", command=self.presenter.onSettingsButton)
        button.pack(expand=True, fill='both')

        button = tkinter.Button(master=self.buttons_frame, text="60 min",
                command = lambda: self.presenter.setInterval(timedelta(hours=1)))
        button.pack(expand=True, fill='both')

        self.addIntervalButton("6 hours", timedelta(hours=6))
        self.addIntervalButton("Day", timedelta(hours=24))
        self.addIntervalButton("Week", timedelta(hours=24*7))

    def addIntervalButton(self, title:str, interval: timedelta) -> None:
        button = tkinter.Button(master=self.buttons_frame, text=title,
                command = lambda: self.presenter.setInterval(interval))
        button.pack(expand=True, fill='both')

    def setupSettingsPanel(self) -> None:
        self.settings_frame = tkinter.Frame(master=self.root)
        self.settings_frame.grid(column=1, row=0, sticky="ns")
        button = tkinter.Button(master=self.settings_frame, text="Quit",
                command=self.root.quit)
        button.pack(expand=True, fill='both')

        button = tkinter.Button(master=self.settings_frame, text="Full screen",
                command=self.presenter.onFullscreenButton)
        button.pack(expand=True, fill='both')

    def setupPlotCanvas(self) -> None:
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(column=2,row=0,sticky="nsew")

        UPDATE_VIEW_TIME_INTERVAL=10*1000 # 10 seconds
        self.ani = animation.FuncAnimation(self.fig,
                lambda event: self.presenter.onAnimate(),
                interval=UPDATE_VIEW_TIME_INTERVAL, cache_frame_data=False)

    def setTitle(self, title:str) -> None:
        self.root.wm_title("Telemetry")

    def setFullscreen(self, fullscreen:bool) -> None:
        self.root.attributes("-fullscreen", fullscreen)

    def setPlotData(self, plot_data:dict) -> None:
        self.ax.clear()
        for sensor_name, sensor_data in plot_data.items():
            self.ax.plot(sensor_data.time_data, sensor_data.value_data, label=sensor_name)
        plt.legend()
        self.fig.autofmt_xdate()
        self.fig.canvas.draw_idle()

    def destroyView(self) -> None:
        self.root.quit()

    def showSettingsPanel(self, enabled_sensors:dict[str, bool]) -> None:
        self.settings_frame.grid()
        for checkbutton in self.checkbuttons.values():
            checkbutton.destroy()
        self.checkbuttons = {}
        self.checkbuttons_vars = {}
        for name, enabled in enabled_sensors.items():
            self.addCheckbutton(name, enabled)

    def addCheckbutton(self, name:str, enabled:bool) -> None:
        var = tkinter.BooleanVar()
        var.set(enabled)
        self.checkbuttons_vars[name] = var
        checkbutton = tkinter.Checkbutton(
                master=self.settings_frame, text=name, variable=var,
                command=lambda: self.presenter.onSensorCheckbutton(name))

        checkbutton.pack(expand=True, fill='both')
        self.checkbuttons[name] = checkbutton

    def hideSettingsPanel(self) -> None:
        self.settings_frame.grid_remove()
