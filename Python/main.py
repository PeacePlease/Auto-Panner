from scipy.io import wavfile as wav
from scipy.fftpack import fft, ifft
import numpy as np
from bokeh.plotting import figure, show

def ramp(freqs, highest, lowest):
    increment = float(highest - lowest)/freqs
    for i in range(0,freqs):
        magn = increment * i
        ramp_l = lowest  + magn
        ramp_r = highest - magn

    global plot_graphs
    if plot_graphs:
        x = range(0, freqs)
        p = figure(title="Ramp function (L)", x_axis_label='frequency', y_axis_label='amplitude')
        p.line(x, ramp_l, legend="Ramp (L)", line_width=1)
        show(p)
    
    return ramp_l, ramp_r


plot_graphs = True

####################
###  OBTAIN FFT  ###
####################

rate, data = wav.read('../InputSamples/16-bit/68_C_HugePad_01_539.wav')

#For comparison with final product
print ("Shape of data: " + str(data.shape))
print ("Data type: " + str(data.dtype))

#Check if Mono, discard right side if not
if   len(data.shape) >  2:
    print "Error, more than 2 channels"
elif len(data.shape) == 2:
    print "WARNING: sample is stero - using left side only..."
    data = data[:, 0]
elif len(data.shape) == 1:
    print "Sample is mono, continuing"
else:
    print "ERROR: Something's gone horribly wrong - stereo check"

#Plot graph
if plot_graphs:
    x = range(0, len(data))
    p = figure(title="Original audio", x_axis_label='time (samples)', y_axis_label='signal')
    p.line(x, data, legend="Original signal", line_width=1)
    show(p)

#FFT

fft_out = fft(data)

if plot_graphs:
    x = range(0, len(fft_out))
    p = figure(title="Original FFT", x_axis_label='frequency', y_axis_label='power')
    p.line(x, np.abs(fft_out), legend="Original signal", line_width=1)
    show(p)

####################
###  PROCESSING  ###
####################

#Find peak power
peak = np.real(np.amax(fft_out))
print("Max value: " + str(peak))

#Get number of frequency samples
freqs = len(fft_out)
print("Frequeny samples: " + str(freqs))

#Get ramp functions
ramp_l, ramp_r = ramp(freqs, peak, 0)

#Apply ramps
#process_out_l = ramp_l * fft_out
#process_out_r = ramp_r * fft_out

process_out_l = fft_out
process_out_r = fft_out

if plot_graphs:
    x = range(0, len(process_out_l))
    p = figure(title="Final leftside FFT", x_axis_label='frequency', y_axis_label='power')
    p.line(x, np.abs(process_out_l), legend="Final signal (L)", line_width=1)
    show(p)

    x = range(0, len(process_out_r))
    p = figure(title="Final rightside FFT", x_axis_label='frequency', y_axis_label='power')
    p.line(x, np.abs(process_out_r), legend="Final signal (R)", line_width=1)
    show(p)


######################################
###  INVERSE FT AND WRITE TO FILE  ###
######################################

final_out = np.vstack(( np.real(ifft(process_out_l)).astype('int16'), np.real(ifft(process_out_r)).astype('int16') )).transpose()

print ("Shape of data: " + str(final_out.shape))
print ("Data type: " + str(final_out.dtype))

wav.write('../OutputSamples/68_C_HugePad_01_539.wav', rate, final_out)
