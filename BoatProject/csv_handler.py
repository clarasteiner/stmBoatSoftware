import pandas as pd
import csv
import numpy as np
from list import table, oxygen_list


def get_data(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        data = []
        for row in reader:
            data.append(row)

    parameters = data[0][1:-2]
    location = data[1][-2:]
    time = data[1][0]
    l = len(parameters)
    values = []

    print(1, parameters, location, time)

    for i in range(1, l + 1):
        s = 0
        for row in data[1:-1]:
            s += float(row[i])

        values.append(s / (len(data) - 2))

    quality, ci, text = get_quality(parameters, values)

    return time, location, parameters, values, quality, ci, text


def get_quality(parameters, values):
    global indices
    indices = {"Temperatur": 0, "Sauerstoff": 1, "pH": 2, "Nitrat": 3, "Ammonium": 4, "Leitfaehigkeit": 5,
               "Phosphat": 6,
               "BSB5": 7}

    quality = []
    for i, p in enumerate(parameters):
        if p == "Sauerstoff":
            quality.append(oxygen(values[0], values[i]))
        elif p in indices:
            quality.append(transform(table[indices[p]], values[i]))
    ci, text = get_ci(parameters, quality)
    return quality, ci, text


def get_ci(parameters, index):
    quality_class = ["I: unbelastet", "I-II: gering belastet", "II: mäßig belastet", "II-III: kritisch belastet",
                     "III: stark verschmutzt", "III-IV: sehr stark verschmutz", "IV: verödet"]
    weight = [0.08, 0.20, 0.10, 0.10, 0.15, 0.07, 0.10, 0.20]
    list = [83, 74, 56, 45, 27, 18, 0]

    ci = 1
    for i in range(len(index)):
        ci *= index[i] ** weight[i]

    for i in range(7):
        if ci >= list[i]:
            return round(ci, 2), quality_class[i]


def oxygen(temperature, oxygen):
    concentration = transform(oxygen_list, temperature)
    return (oxygen * 100) / concentration


def transform(parameter, value):
    x = parameter[0]
    y = parameter[1]
    coefficients = []
    for i in range(len(x) - 1):
        coefficients.append(np.polyfit([x[i], x[i + 1]], [y[i], y[i + 1]], 1))

    if value <= x[0]:
        index = y[0]
    elif value >= x[-1]:
        index = y[-1]
    else:
        for i in range(len(x)):
            if value <= x[i]:
                n = coefficients[i - 1]
                break
        index = n[0] * value + n[1]

    return round(index, 2)
