import numpy as np
import decimal

import os

this_dir, this_filename = os.path.split(__file__)

def hyd_calibration(freq):
    """ Find the calibration factor for a given frequency in the hydrophone calibration file
    INPUTS:
        freq: The desired frequency in MHz
    OUTPUTS:
        cval: Hydrophone calibration value in Pa/V

    """
    h = open(os.path.join(this_dir,'calibration_hydrophone.txt'))
    f = np.loadtxt(h)
    a = np.where(f == freq)
    cval =  f[a[0]][0][1]
    print(cval)
    return cval

def hyd_calibration_multiple_freq(freq_array):
    """ Find the calibration factor for a given frequency in the hydrophone calibration file
    INPUTS:
        freq: The desired frequency in MHz
    OUTPUTS:
        cval: Hydrophone calibration value in Pa/V

    """
    h = open('calibration_hydrophone.txt')
    f = np.loadtxt(h)
    sensitivity_array =[]
    for freq in freq_array:
        print(freq)
        a = np.where(f == freq)
        cval =  f[a[0]][0][1]
        sensitivity_array.append(cval)
    return sensitivity_array