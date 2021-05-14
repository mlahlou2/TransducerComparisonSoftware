# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import tkinter as tk
from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import tkinter.filedialog as filedialog
import tkinter.simpledialog as sdialog
import tkinter.messagebox as msgbox
import pandas as pd
import TransducerComparison

# from C:\Users\SoundPipe\PycharmProjects\hydrophone\pytic\redpitaya_scpi import redpitaya_scpi as rp
import redpitaya_scpi as rp
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import hyd_calibration
import hyd_calibration
# from hyd_calibration import hyd_calibration, hyd_calibration_multiple_freq
import calibrationsheet
import hydrophone as hyd
import numpy as np

import os.path
import datetime
import fpdf


def main():
    """ Main function. Runs the program."""
    # def closeWindowHandler():
    #     root.destroy()
    #     print("exit protocol executed")
    def voltsweepwindow():
        top = Toplevel(root)
        #b2 = Button(top, text='testme')
        #b2.pack()
        VoltSweep(top)
    #Prompt user to collect data or process data
    root = Tk()
    defaultbg = root.cget('bg')
    root.title("Compare Transducers")
    # root.protocol("WM_DELETE_WINDOW", closeWindowHandler())


    TransducerComparison.VoltSweepGUI(root)

    # plt.ion()
    root.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
