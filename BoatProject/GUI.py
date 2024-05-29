import paramiko
from tkinter.ttk import Progressbar
from tkinter import *
import tkinter as tk
import FTPDownload
from PIL import Image, ImageTk
import os
import pandas as pd
import time
from functools import partial
import FTPUpload
from csv_handler import get_data
import json
import customtkinter as ctk
from tkintermapview import TkinterMapView
import paramiko

connected = True
measured = False


def home():
    global master, sensors, frms, fav_btn, frm_sensors

    master = ctk.CTk()
    master.title("Gewässeranalyse Software")

    frm = ctk.CTkFrame(master, fg_color='#242424')
    frm.pack(side=TOP, expand=True, anchor=N)
    frm1 = ctk.CTkFrame(frm, fg_color='#242424')
    frm1.pack(side=LEFT, expand=True, anchor=N)
    frm2 = ctk.CTkFrame(frm, fg_color='#242424')
    frm2.pack(side=LEFT, expand=True, anchor=N)
    frm3 = ctk.CTkFrame(frm, fg_color='#242424')
    frm3.pack(side=LEFT, expand=True, anchor=N)
    frm4 = ctk.CTkFrame(master, fg_color='#2b2b2b')
    frm4.pack(side=BOTTOM, expand=True, anchor=CENTER, pady=10)

    ctk.CTkLabel(frm2, text="Dein Boot", font=("Arial", 25)).pack(side=TOP, pady=10)

    boat_img = ctk.CTkImage(Image.open("images/boot.png"), size=(320, 260))
    ctk.CTkLabel(frm2, text="", image=boat_img).pack(side=TOP, pady=30, padx=20)

    # Boot Konfigurationen
    settings_img = ctk.CTkImage(Image.open("images/settings.png"), size=(26, 26))

    # Cloud
    frm_cloud = ctk.CTkFrame(frm1, fg_color="#2b2b2b")
    frm_cloud.pack(pady=30, padx=10, side=TOP)
    cloud_img = ctk.CTkImage(Image.open("images/cloud.png"), size=(50, 40))
    ctk.CTkLabel(frm_cloud, text="", image=cloud_img).pack(side=TOP)
    var_cloud = ctk.StringVar(value="on")
    switch_cloud = ctk.CTkSwitch(frm_cloud, text="Cloud", variable=var_cloud, onvalue="on", offvalue="off")
    switch_cloud.pack(side=LEFT, padx=(10, 0))
    settings_cloud = ctk.CTkButton(master=frm_cloud, text="", image=settings_img, fg_color="#2b2b2b", width=10,
                                   hover_color="#2b2b2b", command=configureCloud)
    settings_cloud.pack(side=LEFT)

    # RaspberryPi
    frm_raspi = ctk.CTkFrame(frm1, fg_color="#242424")
    frm_raspi.pack(pady=10, padx=10, side=TOP)
    ctk.CTkLabel(frm_raspi, text="RaspberryPi").pack(side=LEFT)
    settings_raspi = ctk.CTkButton(master=frm_raspi, text="", image=settings_img, fg_color="#242424", width=10,
                                   hover_color="#242424", command=configureRaspi)
    settings_raspi.pack(side=LEFT)

    # Pumpen
    frm_pumps = ctk.CTkFrame(frm1, fg_color="#242424")
    frm_pumps.pack(pady=10, padx=10, side=TOP)
    var_pumps = ctk.StringVar(value="on")
    switch_pumps = ctk.CTkSwitch(frm_pumps, text="Pumpen", variable=var_pumps, onvalue="on", offvalue="off")
    switch_pumps.pack(side=LEFT)
    settings_pumps = ctk.CTkButton(master=frm_pumps, text="", image=settings_img, fg_color="#242424", width=10,
                                   hover_color="#242424", command=configurePumps)
    settings_pumps.pack(side=LEFT)

    # GPS
    frm_gps = ctk.CTkFrame(frm1, fg_color="#242424")
    frm_gps.pack(pady=10, padx=10, side=TOP)
    var_gps = ctk.StringVar(value="on")
    switch_gps = ctk.CTkSwitch(frm_gps, text="GPS-Gerät", variable=var_gps, onvalue="on", offvalue="off")
    switch_gps.pack(side=LEFT)
    settings_gps = ctk.CTkButton(master=frm_gps, text="", image=settings_img, fg_color="#242424", width=10,
                                 hover_color="#242424", command=configureGPS)
    settings_gps.pack(side=LEFT)

    # Kamera
    frm_cam = ctk.CTkFrame(frm1, fg_color="#242424")
    frm_cam.pack(pady=10, padx=10, side=TOP)
    var_cam = ctk.StringVar(value="on")
    switch_cam = ctk.CTkSwitch(frm_cam, text="Kamera", variable=var_cam, onvalue="on", offvalue="off")
    switch_cam.pack(side=LEFT)
    settings_cam = ctk.CTkButton(master=frm_cam, text="", image=settings_img, fg_color="#242424", width=10,
                                 hover_color="#242424", command=configureCam)
    settings_cam.pack(side=LEFT)

    # Sensoren
    frm_sensors = ctk.CTkFrame(frm3, fg_color="#242424")
    frm_sensors.pack(pady=10, padx=10, side=LEFT)

    add_btn = ctk.CTkButton(frm_sensors, text="+", command=partial(newSensor, master), width=30)
    add_btn.pack(padx=(0, 5), pady=10, side=RIGHT, anchor=N)

    fav_btn = ctk.CTkButton(frm_sensors, text="★", command=saveFav, width=30)
    fav_btn.pack(side=RIGHT, pady=10, anchor=N, padx=(0, 5))

    ctk.CTkLabel(frm_sensors, text="Sensoren", font=("Arial", 20)).pack(side=TOP, pady=10)

    with open("fav_sensors.txt", "r") as myfile:
        sensors = myfile.read().splitlines()
        sensors = [sensor.split(",") for sensor in sensors]

    sensor_btn(sensors, master)

    # Optionen
    btn_archive = ctk.CTkButton(frm4, text="Manuelle Fahrt", height=70, command=manual_drive)
    btn_archive.pack(side=LEFT, pady=20, padx=20)
    btn_archive = ctk.CTkButton(frm4, text="Messung auswerten", height=70, command=evaluation)
    btn_archive.pack(side=LEFT, pady=20, padx=20)

    master.protocol("WM_DELETE_WINDOW", on_closing)
    master.mainloop()


def saveFav():
    fav_btn.configure(text="★")
    os.system('copy sensor_data.txt fav_sensors.txt')


def sensor_btn(sensors, win):
    global frms, lbls, btns

    l = len(sensors)
    frms = [ctk.CTkFrame(frm_sensors, fg_color="#242424") for _ in range(l)]
    btns = [ctk.CTkButton(frms[i], text=":", width=2, command=partial(configureSensor, i, win), fg_color="#2b2b2b") for
            i
            in range(l)]
    lbls = [ctk.CTkLabel(frms[i], text=sensors[i][0]) for i in range(l)]

    for i in range(l):
        frms[i].pack(anchor=W, pady=2)
        btns[i].pack(side=LEFT, padx=5)
        lbls[i].pack(side=RIGHT)


def newSensor(win):
    global parameter, id, btn_a, sensor_window, availableSensors, frm, frm3, frm5, combobox2, parameter2, calibration

    sensor_window = ctk.CTkToplevel(win)
    sensor_window.title("Sensor hinzufügen")

    frm = ctk.CTkFrame(sensor_window, fg_color='#242424')
    frm.pack(anchor='center')
    frm1 = ctk.CTkFrame(frm, fg_color='#242424')
    frm1.pack(fill='x')
    frm2 = ctk.CTkFrame(frm, fg_color='#242424')
    frm2.pack(fill='x')
    frm3 = ctk.CTkFrame(frm, fg_color='#242424')
    frm3.pack(fill='x')
    frm4 = ctk.CTkFrame(frm, fg_color='#242424')
    frm4.pack(fill='x')
    frm5 = ctk.CTkFrame(frm, fg_color='#242424')
    frm5.pack(fill='x')

    with open("AvailableSensors.json", "r") as myfile:
        availableSensors = json.load(myfile)
    options = list(availableSensors.keys())
    parameter = ctk.StringVar(value="")

    ctk.CTkLabel(frm1, text="Sensor").pack(side=LEFT, padx=5, anchor='center')
    combobox1 = ctk.CTkOptionMenu(master=frm1, values=options, command=select, variable=parameter)
    combobox1.pack(padx=5, pady=1, side=RIGHT)

    ctk.CTkLabel(frm2, text="Code").pack(side=LEFT, padx=5, anchor='center')
    id = ctk.CTkEntry(frm2, width=100)
    id.pack(padx=5, pady=1, side=RIGHT)

    ctk.CTkLabel(frm3, text="Messparameter").pack(side=LEFT, padx=5, anchor='center')
    options2 = []
    parameter2 = ctk.StringVar(value="Wähle zuerst ein Sensor aus")
    combobox2 = ctk.CTkOptionMenu(master=frm3, values=options2, command=select2, variable=parameter2)
    combobox2.pack(padx=5, pady=1, side=RIGHT)

    ctk.CTkLabel(frm4, text="Kalibrierungskurve").pack(side=LEFT, padx=5, anchor='center')
    calibration = ctk.CTkEntry(frm4, width=100)
    calibration.insert(END, "x")
    calibration.pack(padx=5, pady=1, side=RIGHT)

    ctk.CTkButton(frm5, text="Abbrechen", command=sensor_window.destroy, width=20).pack(side=LEFT, padx=5, pady=5)


def select(selection):
    global parameter2, calibration, frm5, options2

    options2 = availableSensors[selection]
    parameter2.set("")
    combobox2.configure(values=options2)


def select2(selection2):
    ctk.CTkButton(frm5, text="Hinzufügen", command=partial(addSensor, sensor_window)).pack(side=LEFT, padx=5, pady=5)


def configureSensor(sensor, win):
    global parameter2, id, calibration, btn_a, sensor_window, availableSensors, sensor_name

    name, code, calibration, sensor_name = sensors[sensor]

    sensor_window = ctk.CTkToplevel(win)
    sensor_window.title("Sensor bearbeiten")

    frm = ctk.CTkFrame(sensor_window, fg_color='#242424')
    frm.pack(anchor='center')
    frm1 = ctk.CTkFrame(frm, fg_color='#242424')
    frm1.pack(fill='x')
    frm2 = ctk.CTkFrame(frm, fg_color='#242424')
    frm2.pack(fill='x')
    frm3 = ctk.CTkFrame(frm, fg_color='#242424')
    frm3.pack(fill='x')
    frm4 = ctk.CTkFrame(frm, fg_color='#242424')
    frm4.pack(fill='x')
    frm5 = ctk.CTkFrame(frm, fg_color='#242424')
    frm5.pack(fill='x')

    with open("AvailableSensors.json", "r") as myfile:
        availableSensors = json.load(myfile)

    ctk.CTkLabel(frm1, text="Sensor").pack(side=LEFT, padx=5, anchor='center')
    ctk.CTkLabel(frm1, text=sensor_name).pack(padx=5, pady=1, side=RIGHT)

    ctk.CTkLabel(frm2, text="Code").pack(side=LEFT, padx=5, anchor='center')
    id = ctk.CTkEntry(frm2, width=100)
    id.insert(END, code)
    id.pack(padx=5, pady=1, side=RIGHT)

    ctk.CTkLabel(frm3, text="Messparameter").pack(side=LEFT, padx=5, anchor='center')
    options2 = availableSensors[sensor_name]
    parameter2 = ctk.StringVar(value=name)
    combobox = ctk.CTkOptionMenu(master=frm3,
                                 values=options2,
                                 variable=parameter2)
    combobox.pack(padx=5, pady=1, side=RIGHT)

    ctk.CTkLabel(frm4, text="Kalibrierungskurve").pack(side=LEFT, padx=5, anchor='center')
    calibration = ctk.CTkEntry(frm4, width=100)
    calibration.insert(END, "x")
    calibration.pack(padx=5, pady=1, side=RIGHT)

    ctk.CTkButton(frm5, text="Abbrechen", command=sensor_window.destroy, width=20).pack(side=LEFT, padx=5, pady=5)
    ctk.CTkButton(frm5, text="Löschen",
                  command=partial(deleteSensor, sensor, sensor_window, win), width=20).pack(side=LEFT, padx=5, pady=5)
    ctk.CTkButton(frm5, text="Speichern", command=partial(saveSensor, sensor, sensor_window), width=20).pack(side=LEFT,
                                                                                                             padx=5,
                                                                                                             pady=5)


def deleteSensor(i, win, win2):
    global lbls, sensors, frms, btns

    fav_btn.configure(text="☆")
    sensors.pop(i)

    with open("sensor_data.txt", 'w') as myfile:
        for number, line in enumerate(sensors):
            if number != i:
                myfile.write(f"{line[0]},{line[1]},{line[2]},{line[3]}\n")

    for frm in frms:
        frm.pack_forget()

    sensor_btn(sensors, win2)
    win.destroy()


def addSensor(win):
    global sensors, btns, frms, lbls

    fav_btn.configure(text="☆")

    sensors.append([parameter2.get(), id.get(), calibration.get(), parameter.get()])

    frms.append(ctk.CTkFrame(frm_sensors, fg_color="#242424"))
    btns.append(
        ctk.CTkButton(frms[-1], text=":", width=2, command=partial(configureSensor, len(sensors) - 1, win),
                      fg_color="#2b2b2b"))
    lbls.append(ctk.CTkLabel(frms[-1], text=sensors[-1][0]))

    frms[-1].pack(anchor=W, pady=2)
    btns[-1].pack(side=LEFT, padx=5)
    lbls[-1].pack(side=RIGHT)

    file1 = open("sensor_data.txt", "a")
    file1.write(f"{parameter2.get()},{id.get()},{calibration.get()},{parameter.get()}\n")
    file1.close()

    win.destroy()


def saveSensor(sensor, win):
    global sensors

    fav_btn.configure(text="☆")

    with open("sensor_data.txt", 'w') as myfile:
        for number, line in enumerate(sensors):
            if number != sensor:
                myfile.write(f"{line[0]},{line[1]},{line[2]},{line[3]}\n")
            else:
                myfile.write(f"{parameter2.get()},{id.get()},{calibration.get()},{sensor_name}\n")

    lbls[sensor].pack_forget()
    lbls[sensor] = ctk.CTkLabel(frms[sensor], text=parameter2.get())
    lbls[sensor].pack(side=RIGHT)
    sensors[sensor] = [parameter2.get(), id.get(), calibration.get(), sensor_name]

    win.destroy()


def configureRaspi():
    global e11, e21, e31
    ip, username, password = raspi_data.split(",")

    raspi_window = ctk.CTkToplevel(master)
    raspi_window.title("RaspberryPi Einstellungen")

    frm = ctk.CTkFrame(raspi_window, fg_color='#242424')
    frm.pack(anchor='center')
    frm1 = ctk.CTkFrame(frm, fg_color='#242424')
    frm1.pack(fill='x')
    frm2 = ctk.CTkFrame(frm, fg_color='#242424')
    frm2.pack(fill='x')
    frm3 = ctk.CTkFrame(frm, fg_color='#242424')
    frm3.pack(fill='x')
    frm4 = ctk.CTkFrame(frm, fg_color='#242424')
    frm4.pack(fill='x')

    ctk.CTkLabel(frm1, text="IP-Adresse").pack(side=LEFT, padx=5, anchor='center')
    e11 = ctk.CTkEntry(frm1, width=100)
    e11.insert(END, ip)
    e11.pack(padx=5, pady=1, side=RIGHT)
    ctk.CTkLabel(frm2, text="Nutzername").pack(side=LEFT, padx=5, anchor='center')
    e21 = ctk.CTkEntry(frm2, width=100)
    e21.insert(END, username)
    e21.pack(padx=5, pady=1, side=RIGHT)
    ctk.CTkLabel(frm3, text="Passwort").pack(side=LEFT, padx=5, anchor='center')
    e31 = ctk.CTkEntry(frm3, width=100)
    e31.insert(END, password)
    e31.pack(padx=5, pady=1, side=RIGHT)
    ctk.CTkButton(frm4, text="Abbrechen", command=raspi_window.destroy, width=10).pack(side=LEFT, padx=10)
    ctk.CTkButton(frm4, text="Speichern", command=partial(save, 0, raspi_window), width=10).pack(side=RIGHT, padx=10)


def configurePumps():
    global e14
    pins = pump_data

    pump_window = ctk.CTkToplevel(master)
    pump_window.title("Pumpen Einstellungen")

    frm = ctk.CTkFrame(pump_window, fg_color='#242424')
    frm.pack(anchor='center')
    frm1 = ctk.CTkFrame(frm, fg_color='#242424')
    frm1.pack(fill='x')
    frm2 = ctk.CTkFrame(frm, fg_color='#242424')
    frm2.pack(fill='x')

    ctk.CTkLabel(frm1, text="Pins").pack(side=LEFT, padx=5, anchor=E)
    e14 = ctk.CTkEntry(frm1, width=100)
    e14.insert(END, pins)
    e14.pack(padx=5, pady=1, side=RIGHT)

    ctk.CTkButton(frm2, text="Abbrechen", command=pump_window.destroy, width=10).pack(side=LEFT, padx=10)
    ctk.CTkButton(frm2, text="Speichern", command=partial(save, 3, pump_window), width=10).pack(side=RIGHT, padx=10)


def configureGPS():
    global e13, e23
    host, port = gps_data.split(",")

    gps_window = ctk.CTkToplevel(master)
    gps_window.title("GPS Einstellungen")

    frm = ctk.CTkFrame(gps_window, fg_color='#242424')
    frm.pack(anchor='center')
    frm1 = ctk.CTkFrame(frm, fg_color='#242424')
    frm1.pack(fill='x')
    frm2 = ctk.CTkFrame(frm, fg_color='#242424')
    frm2.pack(fill='x')
    frm3 = ctk.CTkFrame(frm, fg_color='#242424')
    frm3.pack(fill='x')

    ctk.CTkLabel(frm1, text="Host").pack(side=LEFT, padx=5, anchor=E)
    e13 = ctk.CTkEntry(frm1, width=100)
    e13.insert(END, host)
    e13.pack(padx=5, pady=1, side=RIGHT)
    ctk.CTkLabel(frm2, text="Port").pack(side=LEFT, padx=5, anchor=E)
    e23 = ctk.CTkEntry(frm2, width=100)
    e23.insert(END, port)
    e23.pack(padx=5, pady=1, side=RIGHT)
    ctk.CTkButton(frm3, text="Abbrechen", command=gps_window.destroy, width=10).pack(side=LEFT, padx=10)
    ctk.CTkButton(frm3, text="Speichern", command=partial(save, 2, gps_window), width=10).pack(side=RIGHT, padx=10)


def configureCloud():
    global e12, e22, e32
    ip, username, password = cloud_data.split(",")

    cloud_window = ctk.CTkToplevel(master)
    cloud_window.title("Cloud Einstellungen")

    frm = ctk.CTkFrame(cloud_window, fg_color='#242424')
    frm.pack(anchor='center')
    frm1 = ctk.CTkFrame(frm, fg_color='#242424')
    frm1.pack(fill='x')
    frm2 = ctk.CTkFrame(frm, fg_color='#242424')
    frm2.pack(fill='x')
    frm3 = ctk.CTkFrame(frm, fg_color='#242424')
    frm3.pack(fill='x')
    frm4 = ctk.CTkFrame(frm, fg_color='#242424')
    frm4.pack(fill='x')

    ctk.CTkLabel(frm1, text="IP-Adresse").pack(side=LEFT, padx=5, anchor=E)
    e12 = ctk.CTkEntry(frm1, width=100)
    e12.insert(END, ip)
    e12.pack(padx=5, pady=1, side=RIGHT)
    ctk.CTkLabel(frm2, text="Nutzername").pack(side=LEFT, padx=5, anchor=E)
    e22 = ctk.CTkEntry(frm2, width=100)
    e22.insert(END, username)
    e22.pack(padx=5, pady=1, side=RIGHT)
    ctk.CTkLabel(frm3, text="Passwort").pack(side=LEFT, padx=5, anchor=E)
    e32 = ctk.CTkEntry(frm3, width=100)
    e32.insert(END, password)
    e32.pack(padx=5, pady=1, side=RIGHT)

    ctk.CTkButton(frm4, text="Abbrechen", command=cloud_window.destroy, width=10).pack(side=LEFT, padx=10)
    ctk.CTkButton(frm4, text="Speichern", command=partial(save, 1, cloud_window), width=10).pack(side=RIGHT, padx=10)


def configureCam():
    global e15, e25, e35
    ip, username, password = cloud_data.split(",")

    cloud_window = ctk.CTkToplevel(master)
    cloud_window.title("Cloud Einstellungen")

    frm = ctk.CTkFrame(cloud_window, fg_color='#242424')
    frm.pack(anchor='center')
    frm1 = ctk.CTkFrame(frm, fg_color='#242424')
    frm1.pack(fill='x')
    frm2 = ctk.CTkFrame(frm, fg_color='#242424')
    frm2.pack(fill='x')
    frm3 = ctk.CTkFrame(frm, fg_color='#242424')
    frm3.pack(fill='x')
    frm4 = ctk.CTkFrame(frm, fg_color='#242424')
    frm4.pack(fill='x')

    ctk.CTkLabel(frm1, text="IP-Adresse").pack(side=LEFT, padx=5, anchor=E)
    e15 = ctk.CTkEntry(frm1, width=100)
    e15.insert(END, ip)
    e15.pack(padx=5, pady=1, side=RIGHT)
    ctk.CTkLabel(frm2, text="Nutzername").pack(side=LEFT, padx=5, anchor=E)
    e25 = ctk.CTkEntry(frm2, width=100)
    e25.insert(END, username)
    e25.pack(padx=5, pady=1, side=RIGHT)
    ctk.CTkLabel(frm3, text="Passwort").pack(side=LEFT, padx=5, anchor=E)
    e35 = ctk.CTkEntry(frm3, width=100)
    e35.insert(END, password)
    e35.pack(padx=5, pady=1, side=RIGHT)

    ctk.CTkButton(frm4, text="Abbrechen", command=cloud_window.destroy, width=10).pack(side=LEFT, padx=10)
    ctk.CTkButton(frm4, text="Speichern", command=partial(save, 4, cloud_window), width=10).pack(side=RIGHT, padx=10)


def on_closing():
    exit()
    frm_sensors.destroy()
    master.destroy()


def save(var, win):
    global data, raspi_data, cloud_data, gps_data, pump_data, cam_data

    if var == 0:
        values = f"{e11.get()},{e21.get()},{e31.get()}"
    elif var == 1:
        values = f"{e12.get()},{e22.get()},{e32.get()}"
    elif var == 2:
        values = f"{e13.get()},{e23.get()}"
    elif var == 3:
        values = e14.get()
    elif var == 4:
        values = f"{e13.get()},{e23.get()}"

    win.destroy()

    data[var] = values
    raspi_data, cloud_data, gps_data, pump_data, cam_data = data


def connectSensors():
    global progress, btn_m, roun

    roun = 1

    stdin.write('0\n')
    stdin.flush()
    print(0)

    btn_v.pack_forget()

    btn_m = ctk.CTkButton(frm1, text=f"Messung 1/{l_pumps}", command=bar)
    btn_m.pack(pady=10)

    progress = Progressbar(frm1, orient=HORIZONTAL, length=150, mode='determinate')


def manual_drive():
    global r_window, stdin, sensors, l, fav_btn, frms, btns, frm_sensors, frm1, l_pumps, btn_v

    frm_sensors.destroy()
    master.destroy()
    r_window = ctk.CTk()
    r_window.title("Fahrt starten")

    ip, username, password = raspi_data.split(",")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    com = "python /home/pi/Desktop/MeasureWrapper.py"
    client.connect("10.3.6.86", username='pi', password='123')
    output = ""
    stdin, stdout, stderr = client.exec_command(com)

    print("Connected succesfully")

    pumps = pump_data.split(",")
    l = len(sensors)
    l_pumps = len(pumps)

    frm1 = ctk.CTkFrame(r_window, fg_color="#242424")
    frm1.pack(fill='x', side=LEFT, anchor='n')
    frm2 = ctk.CTkFrame(r_window, fg_color='#242424')
    frm2.pack(fill='x', side=LEFT)

    frm_sensors = ctk.CTkFrame(frm1, fg_color="#242424")
    frm_sensors.pack(pady=10, padx=10, side=TOP)

    add_btn = ctk.CTkButton(frm_sensors, text="+", command=partial(newSensor, r_window), width=30)
    add_btn.pack(padx=(0, 5), pady=10, side=RIGHT, anchor=N)

    fav_btn = ctk.CTkButton(frm_sensors, text="★", command=saveFav, width=30)
    fav_btn.pack(side=RIGHT, pady=10, anchor=N, padx=(0, 5))

    ctk.CTkLabel(frm_sensors, text="Sensoren", font=("Arial", 20)).pack(side=TOP, pady=10)

    sensor_btn(sensors, r_window)

    if connected:
        btn_v = ctk.CTkButton(frm1, text="Verbinden", command=connectSensors)
        btn_v.pack()

    else:
        frm_sensors = ctk.CTkFrame(frm1, fg_color="red")
        frm_sensors.pack(pady=10, padx=10, side=TOP)
        ctk.CTkLabel(frm_sensors, text="Es konnte keine Verbindung zum \nRaspberryPi hergestellt werden").pack(side=TOP,
                                                                                                               pady=5,
                                                                                                               padx=5)

    map_widget = TkinterMapView(frm2, width=400, height=400, corner_radius=0)
    map_widget.pack()

    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    map_widget.set_position(50.771143, 8.756525)

    ctk.CTkButton(frm2, text="Zurück", command=partial(back, r_window)).pack(side=RIGHT, padx=10, pady=10)

    r_window.mainloop()


def bar():
    global roun, measured

    roun += 1
    progress.pack(side=BOTTOM)

    stdin.write('3\n')
    stdin.flush()
    stdin.write('1\n')
    stdin.flush()

    for i in range(10):
        progress['value'] = 10 * (i + 1)
        r_window.update_idletasks()
        time.sleep(1)

    progress.pack_forget()

    if roun <= l_pumps:
        btn_m.configure(text=f"Messung {roun}/{l_pumps}")
    else:
        ctk.CTkFrame(frm1, text="Messung abgeschlossen", fg_color="red").pack(pady=10, padx=10, side=TOP)
        btn_m.pack_forget()

    if not measured:
        btn_u = ctk.CTkButton(frm1, text="Datei auswählen", command=upload)
        btn_u.pack(pady=(0, 10))

    measured = True


def upload():
    filename = tk.filedialog.askopenfilename()
    stdin.write('2\n')
    stdin.flush()
    stdin.write(f"{filename}\n")
    stdin.flush()
    return filename


def back(win):
    win.destroy()
    home()


def evaluation():
    master.destroy()

    e_window = ctk.CTk()
    e_window.title("Messung auswerten")

    filename = upload()
    time, location, parameters, values, quality, ci, text = get_data(filename)

    l = len(parameters)
    print(parameters, values, quality)

    frm1 = ctk.CTkFrame(e_window, fg_color="#242424", width=1000)
    frm1.pack(fill='x', side=LEFT, anchor='n')
    frm2 = ctk.CTkFrame(e_window, fg_color='#242424', width=1000)
    frm2.pack(fill='x', side=LEFT)
    frm7 = ctk.CTkFrame(frm1, fg_color='#242424', width=1000)
    frm7.pack(fill='x', side=TOP)
    frm6 = ctk.CTkFrame(frm1, fg_color='#242424', width=1000)
    frm6.pack(fill='x', side=BOTTOM)
    frm3 = ctk.CTkFrame(frm1, fg_color="#242424", width=1000)
    frm3.pack(fill='y', side=LEFT, anchor='n')
    frm4 = ctk.CTkFrame(frm1, fg_color='#242424', width=1000)
    frm4.pack(fill='y', side=LEFT)
    frm5 = ctk.CTkFrame(frm1, fg_color='#242424', width=1000)
    frm5.pack(fill='y', side=LEFT)

    ctk.CTkButton(frm7, text="Andere Datei wählen", command=upload).pack(side=TOP, pady=10)

    for i in range(l):
        ctk.CTkLabel(frm3, text=parameters[i]).pack(padx=(5, 5), anchor=W)
        ctk.CTkLabel(frm4, text=str("⬛" * (int(quality[i]) // 10) + "⬜" * (10 - (int(quality[i]) // 10)))).pack(
            anchor=W)
        ctk.CTkLabel(frm5, text=round(values[i], 3)).pack(padx=(5, 5), anchor=W)

    ctk.CTkLabel(frm6, font=("Arial", 25), text=ci).pack(side=LEFT, anchor='center', padx=(5, 5))
    ctk.CTkLabel(frm6, font=("Arial", 25), text=text).pack(side=LEFT, anchor='center', padx=(5, 5))

    map_widget = TkinterMapView(frm2, width=400, height=400, corner_radius=0)
    map_widget.pack(padx=(50, 10), pady=(10, 10))

    map_widget.set_position(50.771143, 8.756525)

    current_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    plane_circle_2_image = ImageTk.PhotoImage(
        Image.open(os.path.join(current_path, "images/76.png")).resize((35, 35)))

    plane_circle_1_image = ImageTk.PhotoImage(
        Image.open(os.path.join(current_path, "images/89.png")).resize((35, 35)))

    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    # "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga"

    map_widget.set_marker(50.7716991, 8.7569005, icon=plane_circle_2_image)
    map_widget.set_marker(50.7708105, 8.7559242, icon=plane_circle_1_image)

    e_window.mainloop()


def setup():
    global cloud_data, raspi_data, data, gps_data, pump_data, cam_data, sensors

    with open("data.txt", "r") as myfile:
        data = myfile.read().splitlines()
    raspi_data, cloud_data, gps_data, pump_data, cam_data = data

    with open("fav_sensors.txt", "r") as myfile:
        sensors = myfile.read().splitlines()
        sensors = [sensor.split(",") for sensor in sensors]


def exit():
    f = open('data.txt', 'w')
    for line in data:
        f.write(line + "\n")
    f.close()


if __name__ == '__main__':
    os.system('copy fav_sensors.txt sensor_data.txt')
    cwd = os.getcwd()
    setup()
    home()
