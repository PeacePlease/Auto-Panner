from scipy.io import wavfile as wav
from scipy.fftpack import fft, ifft
import numpy as np
from bokeh.plotting import figure, show

plot_graphs = False
rate = 0

def ramp(freqs, highest, lowest):

    print "\n\n==========================\n Generating ramp function \n==========================\n"
    
    increment = float(highest - lowest)/freqs
    ramp_l = [0]*freqs
    ramp_r = [0]*freqs
    for i in range(0,freqs):
        magn = increment * i
        ramp_l[i] = lowest  + magn
        ramp_r[i] = highest - magn
        
    print ("Lowest: " + str(lowest) + ", highest: " + str(highest) + ", increment: " + str(increment))

    x = range(0, freqs)
    plot(x, ramp_l, 'Ramp (L)', 'frequency', 'power', True)
        
    return ramp_l, ramp_r


def plot(x, y, title, x_label, y_label, force=False):
    global plot_graphs
    if plot_graphs or force:
        p = figure(title=title, x_axis_label=x_label, y_axis_label=y_label)
        p.line(x, y, legend=title, line_width=1)
        show(p)


def getFFT(wav_path):

    print "\n==========================\n Getting FFT of audio \n==========================\n"

    global rate
    rate, data = wav.read(wav_path)
    
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
    
    x = range(0, len(data))
    plot(x, data, 'Original audio signal', 'time', 'signal')
        
    fft_out = fft(data)
    
    x = range(0, len(fft_out))
    plot(x, np.abs(fft_out), 'Original FFT', 'frequency', 'power')
        
    return fft_out

def pan(fft_out):

    print "\n==========================\n Applying pan effect \n==========================\n"

    #Find peak power
    peak = np.real(np.amax(fft_out))
    print("Max value: " + str(peak))
    
    #Get number of frequency samples
    freqs = len(fft_out)
    print("Frequency samples: " + str(freqs))
    
    #Get ramp functions
    ramp_l, ramp_r = ramp(freqs, peak, 0)
    
    #Apply ramps                        <<<<---------------
    #process_out_l = ramp_l * fft_out
    #process_out_r = ramp_r * fft_out
    
    process_out_l = fft_out
    process_out_r = fft_out
    
    x = range(0, len(process_out_l))
    plot(x, np.abs(process_out_l), 'Final signal (L)', 'frequency', 'power')
        
    x = range(0, len(process_out_r))
    plot(x, np.abs(process_out_r), 'Final signal (R)', 'frequency', 'power')
        
    return process_out_l, process_out_r


def write_wav(left, right, path):
    print "\n==========================\n Run IFFT and write audio out \n==========================\n"
    final_out = np.vstack(( np.real(ifft(left)).astype('int16'), np.real(ifft(right)).astype('int16') )).transpose()
    print ("Shape of data: " + str(final_out.shape) + ", data type: " + str(final_out.dtype))
    wav.write(path, rate, final_out)
    
####################################################################################################

def main():

#Get FFT
    fft_out = getFFT('../InputSamples/16-bit/68_C_HugePad_01_539.wav')

#Apply pan effect (mono in, stereo out)
    process_out_l, process_out_r = pan(fft_out)

#IFFT and write result
    write_wav(process_out_l, process_out_r, '../OutputSamples/68_C_HugePad_01_539.wav')

if __name__ == "__main__":
    main()
