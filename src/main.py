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


#enabled = True
class SensorsGui:
    def __init__(self, config: Config):
        with open("../config_old.json", "r") as f:
            self.config_old = json.load(f)

        self.remoteDb = RemoteSensorsDatabase.RemoteSensorsDatabase(config.db)

        self.root = tkinter.Tk()
        self.root.wm_title("Embedding in Tk")
        self.root.attributes("-fullscreen", True)

        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)

        self.fullscreen = True

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
        show = True
        if "show_settings" in self.config_old:
            show = self.config_old["show_settings"]

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
        show = True
        if "show_settings" in self.config_old:
            show = self.config_old["show_settings"]

        show = not show
        self.config_old["show_settings"] = show
        self.dumpConfig()

        if show:
            self.list_settings()
        else:
            self.frame2.destroy()

    def checkbutton_changed(self):
        print("check button changed")
        sensors = dict()
        for key in self.enabled.keys():
            sensors[key] = self.enabled[key].get()
        self.config_old["enabled"] = sensors
        self.dumpConfig()

#       self.generate_dummy_data()
        self.fig.canvas.draw_idle()
#       self.fig.canvas.draw()
        return

    def toggle_fullscreen(self, event):
        self.fullscreen = not self.fullscreen  # Just toggling the boolean
        self.root.attributes("-fullscreen", self.fullscreen)
        return "break"

    def end_fullscreen(self, event):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)
        return "break"

    def generate_dummy_data(self):
        print("generate_dummy_data start")
        names = self.remoteDb.getSensorNames()
        print("names", names)
        scales = self.config_old["scale"]
        integrate = self.config_old["integrate"]
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

            if name in integrate:
                if len(sd) > 0:
                    lastTime = td[0]
                    summ = 0.0
                    for i in range(1, len(sd)):
                        summ = summ + sd[i] * (td[i] - lastTime).total_seconds()
                        lastTime = td[i]
                    summ = summ / (60 * 60)
                    print("===", name, summ)
                    self.powerLabelVar.set("{:.2f}".format(summ))

            if name in scales.keys():
                newVals = []
                for val in sd:
                    newVals.append(val * float(scales[name]))
                sd = newVals

            self.timeData[name] = td
            self.sensorData[name] = sd

        print("generate_dummy_data done")

    def dumpConfig(self):
        with open('config_old.json', 'w') as f:
            f.write(json.dumps(self.config_old))

    def getCheckboxState(self, name):
        if not "enabled" in self.config_old:
            self.config_old["enabled"] = dict()

        if name in self.config_old["enabled"]:
            return self.config_old["enabled"][name]

        return 1

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
    return parser.parse_args()


class App:
    def __init__(self, config: Config):
        self.sensorGui = SensorsGui(config)

    def mainloop(self):
        tkinter.mainloop()


def main():
    args = parseArgParams()
    config = loadConfig(args.config_filepath)

    app = App(config)
    app.mainloop()


if __name__ == "__main__":
    main()
