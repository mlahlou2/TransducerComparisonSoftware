from hyd_calibration import hyd_calibration, hyd_calibration_multiple_freq
import matplotlib.pyplot as plt
import numpy as np
import datetime
from tkinter import *
import tkinter.messagebox
import tkinter.filedialog as filedialog
import tkinter.simpledialog as simpledialog
import tkinter
import fpdf
from fpdf import FPDF
import os

class Hydrophone:
    def __init__(self, amplifier='', matchingnetwork='', hydro='', headerversion='', depth=np.array([0.0]), voltage=[0.0], pulselength=10, pulserep=1e-6, amplify=0, tx_bursts=8, cfreq=np.array([2.4]), angle= np.array([0.0]), samplingfreq=125e6, hydoutput = np.matrix([0.0]), bursts = 8, txdr= ''):
        '''Initializing hydrophone class objects'''
        self.amplifier = amplifier  # amplifier make and serial number, string
        self.matchingnetwork = matchingnetwork  # matching network description, string ,10uH inductor
        self.hydro = hydro  # hydrophone make and serial number, string
        self.headerversion = headerversion  # current version of the header in use, string
        self.depth = depth  # depth of acquisition, float
        self.samplingfreq = samplingfreq  # red pitaya sampling frequency (125e6), float
        self.voltage = voltage   # transducer excitation voltage, float/Array (during voltsweep)
        self.pulselength = pulselength  # excitation pulse length in cycles, int
        self.pulserep = pulserep   # pulse repitition period (seconds), float
        self.cfreq = cfreq  # transducer excitation frequency, float/ array (during freq sweep)
        self.angle = angle  # transducer angel of aquisition, float/ array (during beam profile)
        self.bursts = bursts  # number of times to average each measurement
        self.hydoutput = hydoutput  # data output of the hydrophone
        self.txdr = txdr  # transducer number/name/label
        self.amplify = amplify  # amplification of the input voltages in dB (default = 0)
        self.tx_bursts = tx_bursts  # number of times to average each measurement
        self.collectiondate = '' #COLLECTION DATE TIME
        self.operator = '' #Who collected the measurement

    def save(self):
        '''Saves voltsweep, freqsweep or beamprofile object as a .npz file.
         Each piece of info saved as an array on a separate line of the .npz file.
         Must be read using the load function.
         User is prompted for the save name and location.'''
        currentDT = datetime.datetime.now()
        initialFileTag = 'filename' + currentDT.strftime("%Y-%m-%d_%H%M") + ".txt"
        savefile = tkinter.filedialog.asksaveasfilename(initialfile=initialFileTag, defaultextension='.npz')
        np.savez(savefile, amplifier= self.amplifier,amplify=self.amplify, matchingnetwork = self.matchingnetwork, hydro = self.hydro, headerversion= self.headerversion, depth = self.depth,
                 samplingfreq = self.samplingfreq, voltage=self.voltage, pulselength=self.pulselength, pulserep = self.pulserep,
                 cfreq= self.cfreq, angle = self.angle, bursts = self.bursts,
                 hydoutput=self.hydoutput,txdr= self.txdr, operator = self.operator)
    def load(self,filename = ''):
        """Loads saved objects from .npz format. If no filename is provided, user will be prompted to select file from
        directory.
        INPUTS:
         filename: path to file to be loaded, sting
            """
        if filename == '':
            filename = filedialog.askopenfilename()
        data = np.load(filename)

        try:
            self.amplifier = data['amplifier'].item()

        except:
            pass

        self.matchingnetwork = data['matchingnetwork'].item()
        self.hydro = data['hydro'].item()
        self.headerversion = data['headerversion'].item()
        self.depth = data['depth']
        self.samplingfreq = data['samplingfreq'].item()
        self.voltage = data['voltage']
        self.pulselength = data['pulselength'].item()
        self.pulserep = data['pulserep'].item()
        self.cfreq = data['cfreq']
        self.angle = data['angle']
        self.bursts = data['bursts'].item()
        self.hydoutput = data['hydoutput']
        self.txdr = data['txdr'].item()
        try:
            self.amplify = data['amplify'].item()
        except:
            print("Amplify variable not available")
        try:
            self.operator = data['operator'].item()
        except:
            print("Operator variable not available")

class VoltSweep(Hydrophone):
    def __init__(self):
        super().__init__(self)

    def plot(self,displayplt = True,saveplt = False,savepath=''):
        '''Plots input voltage vs. peak negative pressure and MI '''
        def pnp2mi(pnp):
            return pnp / np.sqrt(self.cfreq)
        def mi2pnp(pnp):
            return pnp * np.sqrt(self.cfreq)
        sensitivity = hyd_calibration(self.cfreq)
        pnp = -1e-6 * np.min(self.hydoutput, axis=1) / sensitivity
        x=self.voltage * np.power(10.0, (self.amplify / 20.0))
        figure1,ax1 = plt.subplots()
        figure1 = ax1.plot(x, pnp,'x')
        plt.xlabel('Input Voltage (V)')
        plt.ylabel('Peak Negative Pressure (MPa)')
        plt.title(self.txdr)
        ax2 = ax1.secondary_yaxis(location='right', functions=(pnp2mi,mi2pnp))
        ax2.set_ylabel('MI')
        ax2.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
        if displayplt:
            plt.show()
        if saveplt:
            if savepath=='':
                #prompt for a save path using a default filename
                defaultfn = self.txdr+'_'+self.collectiondate+'_'+self.collectiontime+'_voltsweep.png'
                savepath = tkinter.filedialog.asksaveasfilename(initialfile=defaultfn, defaultextension='.png')
            plt.savefig(savepath)
        return figure1,savepath

    # def plot(self,displayplt = True,saveplt = False,savepath=''):
    #     self.plot_vs(displayplt, saveplt, savepath)

    def legacy_load(self,filepath = '', amplifier = 'Amplifier'):
        """Loads data from .txt file formats into a VoltSweep object that can be saved into the new .npz file format
        INPUTS:
            filepath: filepath for old file to be loaded, string
                        if no filepath is provided useer will be prompted to select file from directory
                       amplifier: amplifier make and serial number, string"""

        if filepath == '':
            filepath = filedialog.askopenfilename()

        file1 = open(filepath)
        ctxt = file1.readline().rstrip()

        header = ''
        rowskip = 0
        while ctxt[0] == '#':
            header = header + ctxt[1:]
            ctxt = file1.readline().rstrip()
            rowskip += 1

        voltstr = header[2:-1]

        if voltstr.find(',') > 0:
            volts = np.fromstring(voltstr, sep=',')
        else:
            volts = np.fromstring(voltstr, sep='\t')

        file1.close()
        data1 = np.loadtxt(filepath, skiprows=rowskip)
        self.hydoutput = data1
        self.voltage = volts
        self.amplifier = amplifier

    def load(self,filename='',amplifier='A150'):
        if filename == '':
            filename = filedialog.askopenfilename()

        #if the you have a hydrophone class data file, use the hydrophone class load functon
        if(os.path.splitext(filename)[1]=='.npz'):
            super().load(filename)
        else:
            self.legacy_load(filename,amplifier=amplifier)

class BeamProfile(Hydrophone):
    def __init__(self):
        super().__init__(self)
        self.pnp = np.array([])

    def load(self,filename='',amplifier='A150'):
        if filename == '':
            filename = filedialog.askopenfilename()

        #if the you have a hydrophone class data file, use the hydrophone class load functon
        if(os.path.splitext(filename)[1]=='.npz'):
            super().load(filename)
        else:
            self.legacy_load(filename,amplifier=amplifier)

        self.pnp = self.calc_pnp()

    def legacy_load(self,filepath= '', amplifier = 'Amplifier'):
        """Loads data from .txt file formats into a BeamProfile object that can be saved into the new .npz file format
                INPUTS:
                    filepath: filepath for old file to be loaded, string
                                if no filepath is provided useer will be prompted to select file from directory
                               amplifier: amplifier make and serial number, string"""
        if filepath == '':
            filepath = filedialog.askopenfilename()

        file1 = open(filepath)
        ctxt = file1.readline().rstrip()

        header = ''
        rowskip = 0
        while ctxt[0] == '#':
            header = header + ctxt[1:]
            ctxt = file1.readline().rstrip()
            rowskip += 1
        voltstr = header[2:-1]
        file1.close()
        data1 = np.loadtxt(filepath, skiprows=rowskip)
        angles1 = data1[0, :]
        volts1 = data1[1, :]
        self.angle = angles1
        self.hydoutput= volts1
        self.amplifier = amplifier

    def plot(self,displayplt = True,saveplt = False,savepath='',polarplt=True, dbdown = False):
        """Plots a polar plot of the beam profile data"""
        plt.figure()

        #legacy beamprofile data is a 1-D array of the peak negative pressure
        pnp = self.pnp

        if dbdown:
            pnp = 20.0*np.log10(pnp/np.max(pnp))
        else:
            pnp = pnp*1e-6

        if polarplt:
            figure1 = plt.polar(self.angle * np.pi / 180.0, pnp)
        else:
            figure1 = plt.plot(self.angle, pnp)
        #the latest beamprofile data should be a 2-D array of the hydrophone output
        plt.xlabel('Angle (degrees)')
        if dbdown:
            plt.ylabel('Peak Negative Pressure (dB Max)')
        else:
            plt.ylabel('Peak Negative Pressure (MPa)')
        plt.title(self.txdr)
        if displayplt:
            plt.show()
        if saveplt:
            if savepath=='':
                #prompt for a save path using a default filename
                defaultfn = self.txdr+'_'+self.collectiondate+'_'+self.collectiontime+'_beamprofile.png'
                savepath = tkinter.filedialog.asksaveasfilename(initialfile=defaultfn, defaultextension='.png')
            plt.savefig(savepath)
        return figure1, savepath

    # def plot(self,displayplt = True,saveplt = False,savepath='',polarplt=True, dbdown = False):
    #     self.plot_fs(displayplt,saveplt,savepath,polarplt,dbdown)
    def plotpulses(self,subsample = 1):

        if len(self.hydoutput.shape) < 2:
            print("Legacy data. Individual pulses not available\n")
        else:
            plt.figure()
            plt.plot(self.hydoutput[0::subsample].transpose())
            plt.title('Beamprofile pulses')

    def beamarea(self):
        pnparea = np.trapz(self.pnp, self.angle)
        return pnparea

    def calc_pnp(self):
        '''
        Return the peak negative pressure for each angle
        :return:
        '''
        if len(self.hydoutput.shape)<2:
            pnp = self.hydoutput
        else:
            sensitivity = hyd_calibration(self.cfreq)
            pnp = -1*np.min(self.hydoutput,1)/sensitivity
        return pnp


    def beamwidth(self,dbdown = -6):
        pnp = self.pnp

        outdb = 20.0 * np.log10(pnp / np.max(pnp))
        #find peak
        peakind = np.argmax(outdb)
        outdb = np.roll(outdb,len(outdb)//2 - peakind)
        #angt = np.roll(self.angle,len(outdb)//2 - peakind)
        peakind = len(outdb)//2 - peakind
        lowvals = np.where(outdb[0:peakind]<dbdown)
        highvals = np.where(outdb[peakind:]<dbdown)
        bwlow_ind = lowvals[0][-1]
        bwhigh_ind = highvals[0][0]+peakind
        bw = self.angle[bwhigh_ind]-self.angle[bwlow_ind]
        return bw

class FreqSweep(Hydrophone):
    def __init__(self):
        super().__init__(self)


    def plot(self,displayplt = True,saveplt = False,savepath=''):
        """Plots freq sweep data. Frequency vs. PNP and Frequency vs. MI"""
        figure1 = plt.figure()
        axa = figure1.add_subplot(2, 1, 1)
        sensitivity =hyd_calibration_multiple_freq(self.cfreq)
        pnp = -1e-6 * np.min(self.hydoutput, axis=1) / sensitivity
        figure2 = axa.plot(self.cfreq, pnp, 'x')
        axa.set_title('Frequency Sweep')
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Peak Negative Pressure (MPa)')
        axb = figure1.add_subplot(2, 1, 2)
        mi_fs = pnp / np.sqrt(self.cfreq)
        figure4 = axb.plot(self.cfreq, mi_fs, 'x')
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('MI')
        if displayplt:
            plt.show()
        if saveplt:
            if savepath == '':
                # prompt for a save path using a default filename
                defaultfn = self.txdr + '_' + self.collectiondate + '_' + self.collectiontime + '_freqsweep.png'
                savepath = tkinter.filedialog.asksaveasfilename(initialfile=defaultfn, defaultextension='.png')
            plt.savefig(savepath)
        return figure1, savepath

    # def plot(self,displayplt = True,saveplt=False,savepath=''):
    #     self.plot_fs(displayplt,saveplt,savepath)

    def load(self,filename='',amplifier='A150'):
        if filename == '':
            filename = filedialog.askopenfilename()

        #if the you have a hydrophone class data file, use the hydrophone class load functon
        if(os.path.splitext(filename)[1]=='.npz'):
            super().load(filename)
        else:
            self.legacy_load(filename,amplifier=amplifier)

    def legacy_load(self,filepath = '', amplifier = 'Amplifier'):
        """Loads data from .txt file formats into a BeamProfile object that can be saved into the new .npz file format
                 INPUTS:
                     filepath: filepath for old file to be loaded, string
                                 if no filepath is provided useer will be prompted to select file from directory
                                amplifier: amplifier make and serial number, string"""
        if filepath == '':
            filepath = filedialog.askopenfilename()
        file1 = open(filepath)
        ctxt = file1.readline().rstrip()

        header = ''
        rowskip = 0
        while ctxt[0] == '#':
            header = header + ctxt[1:]
            ctxt = file1.readline().rstrip()
            rowskip += 1

        voltstr = header[2:-1]

        if voltstr.find(',') > 0:
            volts = np.fromstring(voltstr, sep=',')
        else:
            volts = np.fromstring(voltstr, sep='\t')

        file1.close()
        data1 = np.loadtxt(filepath, skiprows=rowskip)
        self.hydoutput = data1
        self.cfreq = volts
        self.amplifier = amplifier

class DepthProfile(Hydrophone):
    def __init__(self):
        super().__init__(self)

    def load(self,filename='',amplifier='A150'):
        if filename == '':
            filename = filedialog.askopenfilename()

        #if the you have a hydrophone class data file, use the hydrophone class load functon
        if(os.path.splitext(filename)[1]=='.npz'):
            super().load(filename)
        else:
            self.legacy_load(filename,amplifier=amplifier)


    def plot(self,displayplt = True,saveplt = False,savepath='',polarplt=True, dbdown = False):
        """Plots a  plot of the depth profile data"""
        plt.figure()

        #legacy beamprofile data is a 1-D array of the peak negative pressure
        if len(self.hydoutput.shape)<2:
            pnp = self.hydoutput
        else:
            sensitivity = hyd_calibration(self.cfreq)
            pnp = -1*np.min(self.hydoutput,1)/sensitivity

        if dbdown:
            pnp = 20.0*np.log10(pnp/np.max(pnp))
        else:
            pnp = pnp*1e-6

        figure1 = plt.plot(self.depth, pnp)
        #the latest beamprofile data should be a 2-D array of the hydrophone output
        plt.xlabel('Depth (mm)')
        if dbdown:
            plt.ylabel('Peak Negative Pressure (dB Max)')
        else:
            plt.ylabel('Peak Negative Pressure (MPa)')
        plt.title(self.txdr)
        if displayplt:
            plt.show()
        if saveplt:
            if savepath=='':
                #prompt for a save path using a default filename
                defaultfn = self.txdr+'_'+self.collectiondate+'_'+self.collectiontime+'_depthprofile.png'
                savepath = tkinter.filedialog.asksaveasfilename(initialfile=defaultfn, defaultextension='.png')
            plt.savefig(savepath)
        return figure1, savepath


class InfoDialog(simpledialog.Dialog):
    def body(self,parent):
        frame = Frame(parent)
        frame.pack()

        Label(frame, text="Transducer:").grid(row=0)
        Label(frame, text="Measured by:").grid(row=1)
        Label(frame, text="Amplifier:").grid(row=2)
        Label(frame, text="Amplification (dB):").grid(row=3)
        Label(frame, text="Matching Network:").grid(row=4)

        self.e1 = Entry(frame)
        self.e1.insert(0, "TC3-0D")
        self.e1.grid(row=0,column=1)
        self.e5 = Entry(frame)
        self.e5.insert(0, "")
        self.e5.grid(row=1, column=1)
        self.e2 = Entry(frame)
        self.e2.insert(0, "325LA")
        self.e2.grid(row=2, column=1)
        self.e3 = Entry(frame)
        self.e3.insert(0, "50.0")
        self.e3.grid(row=3, column=1)
        self.e4 = Entry(frame)
        self.e4.insert(0, "10 uH series")
        self.e4.grid(row=4, column=1)

    def apply(self):
        txdr = self.e1.get()
        amplifier = self.e2.get()
        amplify = self.e3.get()
        matchnet = self.e4.get()
        operator = self.e5.get()
        print(txdr)
        self.result = txdr,amplifier,amplify,matchnet,operator









