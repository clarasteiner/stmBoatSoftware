# Author    -   Luis Gerloni    |   MIND-Codes
# Author    -   Clara Steiner   |   MIND-Codes
# Email:    -   gerloni-luis@outlook.com
# Github:   -   https://github.com/MIND-Codes

# Imports
import sys
from pasco import PASCOBLEDevice
from datetime import datetime
import csv
import pytz
from FTPUpload import saveValue
from time import sleep


# Class for colored outputs
class c:
    INCIDENTAL = '\33[90m'
    ERROR = '\33[31m'
    SUCCESS = '\33[32m'
    WARNING = '\33[33m'
    HIGHLIGHT = '\33[34m'
    ENDC = '\033[0m'


time = []
germanTZ = pytz.timezone("Europe/Berlin")
germanTime = datetime.now(germanTZ)

# Time format: Year-Month-Day.Hour-Minute-Second
date = germanTime.strftime(("%Y-%m-%d.%H-%M-%S")[:-3])

global v, s, l, name

sensor_list = []


# Function to connect to all sensors
def connect(sensors):
    l = len(sensors)
    name = [sensors[i][0] for i in range(l)]
    id = [sensors[i][1] for i in range(l)]
    s = [PASCOBLEDevice() for i in range(l)]
    v = [[] for i in range(l)]

    print(l, name, id, s, v)
    for i in range(l):
        try:
            s[i].connect_by_id(id[i])
            print(f"{c.INCIDENTAL} {name} connected")

        except Exception as error:
            print(f'{c.ERROR}Error occurred with some of the Sensors: ', type(error).__name__)
            proceed = input(f"{c.WARNING}Proceed with connected Sensors? Yes -> '1'  || No -> '0': ")
            proceed.lower()
            if proceed == 'yes' or proceed == '1':
                print(f'{c.INCIDENTAL}Proceeding...')
            else:
                for i in range(l):
                    s[i].disconnect()
                sys.exit()


def measure():
    try:
        for n in range(10):
            print(f"{c.INCIDENTAL}Measurement round {n}")
            for i in range(l):
                v[i].append(f'{s[i].read_data(name)}')
            time.append(germanTime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            sleep(0.2)

        with open(f'Values {date}.csv', 'w', newline='') as new_file:
            csv_writer = csv.writer(new_file)
            csv_writer.writerow(name)

            for n in range(10):
                li = [time[n]].append([v[i][n] for i in range(l)])
                print(li)
                csv_writer.writerow(li)
        print(f'{c.SUCCESS}File saved as "{date}"')

    except Exception as error:
        print(f'{c.ERROR}Error occured: ', type(error).__name__)
        print(f'{c.WARNING}Please check, if all sensors are connected correctly!')


# Function to call the upload in FTPUpload
def upload():
    fileName = input(f'{c.WARNING}Enter date of file like this: "Year-Month-Day.Hour-Minute" ')
    saveValue(fileName)


# Function to exit the programm
def exit():
    for i in range(l):
        s[i].disconnect()
