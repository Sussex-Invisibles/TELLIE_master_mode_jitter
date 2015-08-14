#####################################
# Script to run jitter analysis on
# saved traces.
#
#####################################
import optparse
import time
import os
import numpy as np
import calc_utils as cu
import matplotlib.pyplot as plt
import ROOT as r

def threshold_crossings(filename, can, thresh=0.4):
    #for i in range(len(y[:,1])):
    dt, count = np.zeros(1e4), 0
    #for file in os.listdir(filename):
            #print options.file+str(file)
    #x,y = cu.readPickleChannel(options.file+str(file), 1)
    x,y = cu.readPickleChannel(filename, 1)
    peak = min(y[0,:])
    threshold = thresh*peak
    index = np.where( y[0,:] < threshold )[0]
    for j, idx in enumerate(index):
        if j < len(index)-1:
            tmp = x[index[j+1]] - x[index[j]]
            if tmp > 1e-7: # make sure we didn't miss a pulse
                dt[count] = tmp
                count = count + 1
    dt = np.trim_zeros(dt, 'fb') #Get rid of unused 'zero' points
    scale = 1e6
    mean, std = np.mean(dt), np.std(dt)
    nBins, mi, ma = 20, -2e-9, +2e9
    dt_hist = r.TH1F('dt','Transient time spead on PMT response transients', nBins, mi, ma)
    for d in dt:
        dt_hist.Fill(d-mean)
    dt_hist.GetYaxis().SetTitle("Counts / %1.1f ns" % ((ma-mi)/nBins) )
    dt_hist.GetXaxis().SetTitle('Pulse separation - mean(Pulse separation) [s]')
    dt_hist.Draw()
    can.Update()
    #dt_hist.SaveAs("./PulseSeparation.pdf")    
    can.SaveAs("./PulseSeparation.png")

    #plt.figure(1)
    #n, bins, patches = plt.hist(dt, facecolor='green', histtype='stepfilled', alpha=0.75)

    #plt.figure(2)
    #plt.plot(x[0:5000], y[0,0:5000])

    #plt.figure(3)
    #plt.plot(index)
    #for i in range(10):
    #    plt.plot(x[index[i]-10:index[i]+10], y[0,index[i]-10:index[i]+10],'.-')
    #plt.show()

def calc_jitter(x, y):
    a = 1

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-f",dest="file",help="Name of file to be read")
    (options,args) = parser.parse_args()

    # Make canvas
    can = r.TCanvas("c1","c1") 

    #Time
    total_time = time.time()

    #Read files
    threshold_crossings(options.file, can)
