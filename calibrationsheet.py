import hydrophone as hyd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import hyd_calibration
import numpy as np
import tkinter.filedialog as filedialog
import tkinter.simpledialog as sdialog
import tkinter.messagebox as msgbox
import tkinter as tk
import os.path
import datetime
import fpdf
import pandas as pd

def BasicExcelSpreadsheet(spreadsheet,data, row):
    try:
        print(len(data))
        print(row)
        for i in range(len(data)):
            spreadsheet.write(row, i, data[i])
    except:
        print("error")
    return

def BasicPandasDataFrameTable(PandasDataFrame,data, collabels):
    try:
        # print(data)
        print("put data into pandas")
        print(len(data))
        print(len(collabels))

        # DataFrameTable = pd.DataFrame(data, columns=collabels)

        print("append to main data frame")
        print(PandasDataFrame)
        PandasDataFrame.append(data)

    except:
        print("error")

    return


def BasicFPDFTable(pdf1,data,labels=[]):
    th = pdf1.font_size
    epw = pdf1.w - 2*pdf1.l_margin
    print(epw)
    try:
        print(data.shape[1])
        colwid = epw / data.shape[1]
        for i in labels:
            pdf1.cell(colwid, th, i, border=1),
        pdf1.ln(th)
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                pdf1.cell(colwid, th, str(data[i, j]), border=1)
            pdf1.ln(th)
    except:
        print(data.shape[0])
        colwid = epw/data.shape[0]
        for i in labels:
            pdf1.cell(colwid,th,i,border = 1),
        pdf1.ln(th)
        for i in range(data.shape[0]):
            pdf1.cell(colwid,th,str(data[i]), border = 1)
        pdf1.ln(th)

def gen_report( vs_file='', fs_file='',bp_file='', pdfname= '',freq_data= True, beam_data=True):
    '''Generates a pdf report from voltsweep, freqsweep and beam profile data
    INPUTS:
        vs_file: voltsweep data file path, string (if no path is provided user will be prompted to select file from directory)
        fs_file: freqsweep data file path, string (if no path is provided user will be prompted to select file from directory)
        bp_file: beamprofile data file path  string (if no path is provided user will be prompted to select file from directory)
        pdfname: path of pdf to be saved, string (if no path is provided user will be prompted to select save location and name)
        freq_data: boolean, if True, the user has freq sweep data to be included in the report, if False no freq sweep
                   data will be included in the report
        beam_data: boolean, if True, the user has beam profile data to be included in the report, if False no beam profile
                   data will be included in the report
    OUTPUT:
        pdf document saved as directed by user
        '''
    # creating objects
    vs = hyd.VoltSweep()
    fs = hyd.FreqSweep()
    bp = hyd.BeamProfile()
    if vs_file == '':
        vs_file = filedialog.askopenfilename(title='Select Volt Sweep File')
        vs.load(vs_file)
    if freq_data == True:
        if fs_file == '':
            fs_file = filedialog.askopenfilename(title='Select Frequency Sweep File')
        if fs_file == '':
            freq_data=False
        else:
            fs.load(fs_file)
    if beam_data == True:
        if bp_file == '':
            bp_file = filedialog.askopenfilename(title='Select Beam Profile File')
        bp.load(bp_file)

    if vs.amplify == 0:
        vs.amplify = float(sdialog.askstring('Amplification', 'Amplification is set to 0 dB. Please enter amplification in dB'))

    # initialize a multi page pdf (make pdf object)
    if pdfname == '':
        pdfname = vs_file
        pdfname = pdfname.replace("voltsweep",str(vs.txdr) + "_calibrationsheet_")
        pdfname = pdfname.replace("txt.npz", "pdf")
        pdfname = pdfname.replace("npz", "pdf")
        print(pdfname)
        # pdfname = filedialog.asksaveasfilename(title='Save Pdf as:',initialfile = os.path.splitext(os.path.split(vs_file)[1])[0]+'.pdf',defaultextension = 'pdf')
    #pp = PdfPages(pdfname)
    print('next')
    fig = plt.figure()
    plt.clf()
    ax = fig.add_subplot(1, 1, 1)
    #getting the date the volt sweep file was created
    created = os.path.getctime(vs_file)
    date = datetime.datetime.fromtimestamp(created)
    date2 = date.date()
    try:
        beamwidth = bp.beamwidth()
    except:
        beamwidth=0
    #creating table of settings/info about the transducer, add rows and columns to include more information.
    table_data = [
        ["Txdr #", vs.txdr],
        ["Matching Network:", vs.matchingnetwork],
        ["Amplifier", vs.amplifier],
        ["Frequency", vs.cfreq.item()],
        ["-6 dB Beamwidth", beamwidth],
        ["Date", date2]
     ]

    table = ax.table(cellText=table_data, loc='center')
    table.set_fontsize(14)
    table.scale(1, 4)
    ax.axis('off')
    #saves the figure to one page of the pdf document
    #pp.savefig()

    #adding subplots for volt sweep, freq sweep, beam profile and the PNP/MI table
    fig = plt.figure()

    #these functions are necessary to make the secondary MI axis for the voltsweep plot
    def pnp2mi(pnp):
        return pnp / np.sqrt(vs.cfreq)

    def mi2pnp(pnp):
        return pnp * np.sqrt(vs.cfreq)
    #plotting volt sweep data
    [vs_figure1,vs_figpath] = vs.plot(displayplt=False,saveplt=True,savepath=os.path.splitext(vs_file)[0]+'.png')
    #axa = fig.add_subplot(2, 2, 1)
    #sensitivity = hyd_calibration.hyd_calibration(vs.cfreq)
    #pnp = -1e-6 * np.min(vs.hydoutput, axis=1) / sensitivity
    x = vs.voltage * np.power(10.0, (vs.amplify / 20.0))
    #figure3 = axa.plot(x, pnp, 'x')
    #axa.set_xlabel('Input Voltage (v)')
    #axa.set_ylabel('Peak Negative Pressure (MPa)')
    #axa.set_title('Voltage Sweep')
    #ax2 = axa.secondary_yaxis(location='right', functions=(pnp2mi, mi2pnp))
    #ax2.set_ylabel('MI')
    #ax2.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    #plotting freq sweep data
    if freq_data == True:
    #    axb = fig.add_subplot(2, 2, 2)
    #    sensitivity = hyd_calibration.hyd_calibration_multiple_freq(fs.cfreq)
    #    pnp = -1e-6 * np.min(fs.hydoutput, axis=1) / sensitivity
    #    figure2 = axb.plot(fs.cfreq, pnp, 'x')
    #    axb.set_title('Frequency Sweep')
    #    plt.xlabel('Frequency (MHz)')
    #    plt.ylabel('Peak Negative Pressure (MPa)')
    #    axe = fig.add_subplot(2,2,4)
    #    mi_fs = pnp/np.sqrt(fs.cfreq)
    #    figure4 = axe.plot(fs.cfreq, mi_fs, 'x')
    #    axe.set_title('Frequency Sweep')
    #    plt.xlabel('Frequency (MHz)')
    #    plt.ylabel('MI')
        [fs_figure,fs_figpath] = fs.plot(displayplt=False,saveplt=True,savepath=os.path.splitext(fs_file)[0]+'.png')
    #plotting beam profile data
    if beam_data == True:
        [bp_figure, bp_figpath] = bp.plot(displayplt=False, saveplt=True,
                                             savepath=os.path.splitext(bp_file)[0] + '.png')
        #axc = fig.add_subplot(223, projection='polar')
        #axc.set_title('Beam Profile, PNP (MPa)', pad=15)
        #axc.plot(bp.angle * np.pi / 180.0, bp.hydoutput * 1e-6) #TODO  - correct to pressure

    # expanding the subplot window so that the plots are more spread out and bigger on the pdf
    manager = plt.get_current_fig_manager()
    manager.resize(*manager.window.maxsize())
    plt.tight_layout()
    #plt.show()
    #pp.savefig(fig)

#TODO check this for accuracy
    # Creating information table and putting it on a separate pdf page
    fig2 = plt.figure()
    axd = fig2.add_subplot(1,1,1)
    vnoamp = vs.voltage*2e3
    vnoamp_round = np.round(vnoamp, decimals=3)
    vamp = vs.voltage * 2 * (10 ** (vs.amplify / 20))
    vamp_round = np.round(vamp, decimals=3)
    #input of hyd_calibration should be in MHz
    sensitivity = hyd_calibration.hyd_calibration(vs.cfreq)
    #calculating pnp
    pnp = -1e-6 * np.min(vs.hydoutput, axis=1) / sensitivity
    pnp_round = np.round(pnp, decimals=3)
    #calculating MI based off of the volt sweep data
    mi = pnp / np.sqrt(vs.cfreq)
    for i in range(len(mi)):
        mi[i] = np.format_float_scientific(mi[i], precision=3)
    table_data2 = [vnoamp_round, vamp_round, pnp_round, mi]
    table_data2 = np.transpose(table_data2)
    collabels = ['Vnoamp (mVpp)', 'Vamp (Vpp)','PNP (MPa)', 'MI']
    #table = axd.table(cellText=table_data2, colLabels=collabels, loc='center', bbox=[0.05, 0.05, 0.8, 0.6])
    #table.set_fontsize(8)
    #table.scale(1, 4)
    #axd.axis('off')
    #plt.show()
    #pp.savefig()
    #pp.close() #call this after all of the figures are saved

    # cal325LA = msgbox.askquestion('Calibrated with 325LA?', 'Calibrated with 325LA?') == 'yes'
    cal325LA = True
    if cal325LA:
        voltscale = 1.77
    else:
        voltscale = 1.0

    #interpolated data for key pressures
    # couplerbool = msgbox.askquestion('Calibrated with couplers?', 'Calibrated with couplers?')=='yes'
    couplerbool = False
    keypressures = np.array([0.3, 0.5, 1.5])  # in MPa
    kp_noamp = np.interp(keypressures, pnp, vnoamp/voltscale)
    #kp_amp = np.interp(keypressures, pnp, vamp/voltscale)
    couplvalue = -0.5375 #in db for pair of directional couplers from minicircuits
    if couplerbool:
        kp_noamp_coupl = kp_noamp
        kp_noamp = kp_noamp*(10**(couplvalue/20)) #account for attenuation
    else:
        kp_noamp_coupl = kp_noamp/(10**(couplvalue/20)) #account for attenuation

    table_data_kp = [keypressures, np.round(keypressures/np.sqrt(vs.cfreq),decimals=3),np.round(kp_noamp,decimals=1),np.round(kp_noamp_coupl,decimals=1)]
    table_data_kp = np.transpose(table_data_kp)
    #table_data_kp.append(['', '', '', ''])
    collabels_kp = ['PNP (MPa)', 'MI','Vnoamp w/o couplers (mVpp)', 'Vnoamp w/ couplers (Vpp)']

    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font('Arial','',12)
    if(vs.txdr==''):
        vs.txdr = sdialog.askstring('Transducer Name','Please enter transducer name')
    pdf.cell(0, 6, 'Transducer: '+vs.txdr, ln=1)
    pdf.cell(0, 6, 'Amplifier: '+vs.amplifier, ln=1)
    pdf.cell(0, 6, 'Matching Network: ' + vs.matchingnetwork, ln=1)
    pdf.cell(0, 6, 'Frequency: ' + str(vs.cfreq.item()), ln=1)
    pdf.cell(0, 6, "-6 dB Beamwidth: "+str(beamwidth), ln=1)
   # pdf.cell(0, 10, 'Distance from Hydrophone: ' + str(vs.depth.item()), ln=1)
   # pdf.cell(0, 10, 'Collection Date: ' + vs.collectiondate , ln=1)

    curline = pdf.get_y()
    pdf.image(vs_figpath,w=100)
    pdf.image(fs_figpath,w=100,y=curline,x=110)
    pdf.image(bp_figpath,w=100,x=55)
    BasicFPDFTable(pdf, table_data_kp, collabels_kp)
    BasicFPDFTable(pdf, table_data2,collabels)

    pdf.output(pdfname)
    pdf.close()
    plt.close('all')

def main():
    #making a GUI to generate a pdf
    window = tk.Tk()
    frame = tk.Frame()
    frame.pack()
    b = tk.Button(frame, text="Generate PDF", command=lambda: gen_report())
    b.pack()
    window.mainloop()

if __name__ == '__main__':
    #parentpath = '/Users/joe/Dropbox/Sarah Zagorin Share/TransducerData/D061_ExampleData/'
    #gen_report(vs_file=parentpath+'voltsweepdata_A150_2400khz_2020-04-30_1241.npz',
    #    fs_file=parentpath+'freqsweepdata_A150_40mvpp_2020-04-30_1235_v2.npz',
    #    bp_file=parentpath+'BeamProfileA150_2400khz_2020-04-30_1239_v2.npz', pdfname=parentpath+'output2.pdf')

    gen_report()
    #    #main()
