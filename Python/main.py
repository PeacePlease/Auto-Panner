from scipy.io import wavfile as wav
from scipy.fftpack import fft, ifft, fftfreq

import numpy as np
from bokeh.plotting import figure, show
from math import log10

import time
from inspect import currentframe, getframeinfo
from re import split as rsplit
#import sys

####################################################################################################

plot_graphs = False
rate = 0

def main():

    global start_time
    start_time = time.time()
    
    log('Starting', currentframe())
    
#Parameters
    inpath     = '../InputSamples/16-bit/'
    outpath    = '../OutputSamples/'
    infile     = 'LeOnde.wav'
    outfile    = infile
    #startrampf = 50
    #endrampf   = 1000
    devia      = 0.95
    severity   = 1 #TODO
    
#Get FFT
    freqs, fft_out, ave_f = getFFT(inpath + infile)

#Get ramp params
    startrampf = (1-devia)*ave_f
    endrampf   = (1+devia)*ave_f

#Apply pan effect (mono in, stereo out)
    process_out_l, process_out_r = pan(freqs, fft_out, startrampf, endrampf)

#IFFT and write result
    write_wav(process_out_l, process_out_r, outpath + outfile)

####################################################################################################



def log(text, currframe, level='INFO'):
    global start_time
    frameinfo = getframeinfo(currframe)
    print(str.format('{0:.10f}', time.time() - start_time) + "\t| " + rsplit('[\\\/]', frameinfo.filename)[-1] + "\t| " +  str(frameinfo.lineno) + "\t| " + level + "\t| " + text)

def wall(text, currframe, level='INFO'):
    log('', currframe)
    log('==============================', currframe, level)
    log(text, currframe, level)
    log('==============================', currframe, level)

def plot(x, y, title, x_label, y_label, force=False):
    global plot_graphs
    if plot_graphs or force:
        p = figure(title=title, x_axis_label=x_label, y_axis_label=y_label)
        p.line(x, y, legend=title, line_width=1)
        show(p)

def logiter(x):
    return log10(abs(x)+1)
def oneminus(x):
    return 1-x

####################################################################################################


def getFFT(wav_path):

    wall('Getting FFT of audio', currentframe())

    global rate
    rate, data = wav.read(wav_path)

    if len(data) > 10000000:
        log('Cutting short for now', currentframe(), 'WARN')
        data = data[:10000000]
    
    #For comparison with final product
    log("Shape of data: " + str(data.shape), currentframe())
    log("Data type: " + str(data.dtype), currentframe())
    
    #Check if Mono, discard right side if not
    if   len(data.shape) >  2:
        log('More than 2 channels', currentframe(), 'ERROR')
    elif len(data.shape) == 2:
        log('Sample is stero - using left side only...', currentframe(), 'WARN')
        data = data[:, 0]
    elif len(data.shape) == 1:
        log("Sample is mono, continuing", currentframe())
    else:
        log("Something's gone horribly wrong - stereo check", currentframe(), 'CRIT')
        sys.exit(1)
    
    x = range(0, len(data))
    plot(x, data, 'Original audio signal', 'time', 'signal')
        
    fft_out = fft(data)
    freqs = fftfreq(data.size, float(1)/rate)
    
    plot(freqs, np.abs(fft_out), 'Original FFT', 'frequency', 'power')

    ave_f = np.average(np.absolute(freqs), None, np.absolute(fft_out))
    log("Average freqency: " + str(round(ave_f, 3)), currentframe())
    
    return freqs, fft_out, ave_f

def write_wav(left, right, path):
    #wall('Run IFFT and write audio out', currentframe())
    #log("Running IFT...", currentframe())
    print ("Hi Sam 1")
    print(left)
    print(ifft(left))
    iftl = ifft(left)
    print ("Hi Sam 2")
    #log("Left side half done...", currentframe())
    iftl = np.real(iftl).astype('int16')
    #log("Left side done...", currentframe())
    iftr = np.real(ifft(right)).astype('int16')
    #log("Right side done...", currentframe())
    
    final_out = np.vstack(( iftl, iftr )).transpose()


    
    #log("Shape of data: " + str(final_out.shape) + ", data type: " + str(final_out.dtype), currentframe())
    wav.write(path, rate, final_out)
    #log("Written " + path + ". Enjoy!", currentframe())


def ramp(freqs, startf, endf):

    wall('Generating ramp function', currentframe())
    log("Start freq: " + str(round(startf, 4)/1000) + "kHz, end freq: " + str(round(endf, 4)/1000) + "kHz", currentframe())
    
    ramp_l = np.zeros(len(freqs))
    ramp_r = np.zeros(len(freqs))

    for i in range(0, len(freqs)):
        if i == len(freqs)/2 and 0 == len(freqs)%2:
            log('Halfway there...', currentframe())
        
        if   abs(freqs[i]) < startf:
            ramp_l[i] = 1
        elif abs(freqs[i]) > endf:
            ramp_r[i] = 1
        else:
            ramp_r[i] = float(abs(freqs[i])-startf)/(endf-startf)
            ramp_l[i] = 1-ramp_r[i]

    log("There!", currentframe())
    
    plot(freqs, ramp_l, 'Ramp (L)', 'frequency', 'power')
    plot(freqs, ramp_r, 'Ramp (R)', 'frequency', 'power')
        
    return ramp_l, ramp_r


def logfunc(freqs, stretch):
    logl = map(logiter, freqs)
    logr = map(oneminus, logl)
    log(str(freqs), currentframe())
    log(str(logl), currentframe())
    plot(freqs, logl, 'Log (L)', 'frequency', 'power')
    return logl, logr

def pan(freqs, fft_out, startrampf, endrampf):

    wall('Applying pan effect', currentframe())

    #Find peak power
    peaki = np.argmax(fft_out)
    
    
    log("Peak is at " + str(round(freqs[peaki]/1000, 4)) + " kHz", currentframe())
    
    #Get number of frequency samples
    log("Frequency samples: " + str(len(fft_out)), currentframe())
    log("Frequency range:   " + str(round(max(freqs)/1000, 4)) + " kHz", currentframe())
    
    #Get ramp functions
    ramp_l, ramp_r = ramp(freqs, startrampf, endrampf)
    #log_l, log_r   = logfunc(freqs, 1)
    
    process_out_l = fft_out * ramp_l
    process_out_r = fft_out * ramp_r
    
    plot(freqs, process_out_l, 'Final signal (L)', 'frequency', 'power')
    plot(freqs, process_out_r, 'Final signal (R)', 'frequency', 'power')

    ave_f_l = round(np.average(np.absolute(freqs), None, np.absolute(process_out_l)), 4)
    ave_f_r = round(np.average(np.absolute(freqs), None, np.absolute(process_out_r)), 4)
    log("Leftside average freqency: " + str(ave_f_l) + "Hz, rightside: " + str(ave_f_r) + "Hz", currentframe())
    log("Average frequency (assuming same power): " + str(round((ave_f_l + ave_f_r)/2, 3)) + "Hz", currentframe())
            
    return process_out_l, process_out_r

    
####################################################################################################

if __name__ == "__main__":
    main()
