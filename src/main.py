#!/usr/bin/env python3

import argparse
import copy
from datetime import datetime
import json
from random import randint
import tkinter

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from Config import Config, loadConfig
import RemoteSensorsDatabase
import SensorNames
from Settings import Sensor, Settings, SettingsManager


#enabled = True
class SensorsGui:
    def __init__(self, config: Config, settings: Settings):
        self.settings = settings
        self.remoteDb = RemoteSensorsDatabase.RemoteSensorsDatabase(config.db)

        self.root = tkinter.Tk()
        self.root.wm_title("Embedding in Tk")
        self.root.attributes("-fullscreen", self.settings.fullscreen)

        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)

        frame = tkinter.Frame(master=self.root)
        frame.grid(column=0, row=0, sticky="ns")

        button = tkinter.Button(master=frame, text="Settings", command=self.on_show_settings)
        button.pack(expand=True, fill='both')
        button = tkinter.Button(master=frame, text="Reset", command=self.remoteDb.resetStartTimer)
        button.pack(expand=True, fill='both')
        button = tkinter.Button(master=frame, text="60 min", command=self.remoteDb.setInterval60min)
        button.pack(expand=True, fill='both')
        button = tkinter.Button(master=frame, text="6 hours", command=self.remoteDb.setInterval6hours)
        button.pack(expand=True, fill='both')
        button = tkinter.Button(master=frame, text="Day", command=self.remoteDb.setIntervalDay)
        button.pack(expand=True, fill='both')
        button = tkinter.Button(master=frame, text="Week", command=self.remoteDb.setIntervalWeek)
        button.pack(expand=True, fill='both')
        self.powerLabelVar = tkinter.StringVar()
        self.powerLabelVar.set("0")
        self.powerLabel = tkinter.Label(master=frame, textvariable=self.powerLabelVar)
        self.powerLabel.pack(expand=True, fill='both')

        self.list_settings()

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(column=2,row=0,sticky="nsew")

        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.timeData = {}
        self.sensorData = {}

        self.remoteDb.connect()

        self.ani = animation.FuncAnimation(self.fig,
                              self.animate,
                              interval=10*1000)

        #plt.style.use('dark_background')
        #plt.style.use('seaborn-dark')

    def list_settings(self):
        show = not self.settings.hide_settings

        if show:
            self.frame2 = tkinter.Frame(master=self.root)
            self.frame2.grid(column=1, row=0, sticky="ns")
            button = tkinter.Button(master=self.frame2, text="Quit", command=self.root.quit)
            button.pack(expand=True, fill='both')

        names = self.remoteDb.getSensorNames()
        self.enabled = dict()
        self.checkboxes = dict()

        for name in names:
            var = tkinter.IntVar()
            var.set(self.getCheckboxState(name))
            self.enabled[name] = var
            if name not in self.settings.sensors:
                self.settings.sensors[name] = Sensor(disabled=False)

            #self.checkboxes[name] = tkinter.Checkbutton(master=frame2, text=name, command=self.lambdas[name], variable=var)
            if show:
                self.checkboxes[name] = tkinter.Checkbutton(master=self.frame2, text=name, command=self.checkbutton_changed, variable=var)

#               print(self.enabled[name])
#               print(self.enabled)

#           sensor_checkbutton = tkinter.Checkbutton(master=frame2, text=name, variable=self.enabled[name], command=self.checkbutton_changed)
            #global enabled
            #sensor_checkbutton = tkinter.Checkbutton(master=frame2, text=name, variable=enabled, command=self.checkbutton_changed)
            
                self.checkboxes[name].pack(expand=True, fill='both')


    def on_show_settings(self):
        show = self.settings.hide_settings
        self.settings.hide_settings = not show

        if show:
            self.list_settings()
        else:
            self.frame2.destroy()

    def checkbutton_changed(self):
        print("check button changed")
        sensors = dict()
        for key in self.enabled.keys():
            self.settings.sensors[key].disabled = not self.enabled[key].get()

#       self.generate_dummy_data()
        self.fig.canvas.draw_idle()
#       self.fig.canvas.draw()
        return

    def toggle_fullscreen(self, event):
        self.settings.fullscreen = not self.settings.fullscreen
        self.root.attributes("-fullscreen", self.settings.fullscreen)
        return

    def end_fullscreen(self, event):
        self.settings.fullscreen = False
        self.root.attributes("-fullscreen", False)
        return

    def generate_dummy_data(self):
        print("generate_dummy_data start")
        names = self.remoteDb.getSensorNames()
        print("names", names)
        for name in names:
            t_utc, sd = self.remoteDb.getData(name)
            print("sensor data size: ", len(t_utc), len(sd))
            td = []
            for t in t_utc:
                td += [t.astimezone(None)]

            if len(td) == 0:
                print("no data")
            else:
                print(td[0])

            self.timeData[name] = td
            self.sensorData[name] = sd

        print("generate_dummy_data done")

    def getCheckboxState(self, name):
        return not self.settings.sensors[name].disabled

    def animate(self, i):
        self.generate_dummy_data()

        self.ax.clear()

        #plt.title('Adafruit DHT11 Sensor')
        #plt.xlabel('Time')
        #plt.ylabel('values')

        names = self.remoteDb.getSensorNames()
        for name in names:
            print ("plot", name, len(self.timeData[name]))
            if self.enabled[name].get():
                self.ax.plot(self.timeData[name], self.sensorData[name], label=name)

        plt.legend()

        self.fig.autofmt_xdate()


def parseArgParams():
    parser = argparse.ArgumentParser("PyGUI")
    parser.add_argument(
            "-c", "--config",
            action="store", dest='config_filepath',
            default='config.json',
            help="Config filename (default: config.json)"
    )
    parser.add_argument(
            "-s", "--settings",
            action="store", dest='settings_filepath',
            default='settings.json',
            help="Settings filename (default: settings.json)"
    )
    return parser.parse_args()


class App:
    def __init__(self, config: Config, settings: Settings):
        self.sensorGui = SensorsGui(config, settings)

    def mainloop(self):
        tkinter.mainloop()


def main():
    args = parseArgParams()
    config = loadConfig(args.config_filepath)

    with SettingsManager(args.settings_filepath) as settings:
        app = App(config, settings)
        app.mainloop()


if __name__ == "__main__":
    main()
