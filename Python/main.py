from scipy.io import wavfile as wav
from scipy.fftpack import fft, ifft
import numpy as np
from bokeh.plotting import figure, show

plot_graphs = False
rate = 0

def ramp(freqs, highest, lowest):

    print "\n\n==========================\n Generating ramp function \n==========================\n"
    
    increment = float(highest - lowest)/freqs
    for i in range(0,freqs):
        magn = increment * i
        ramp_l = lowest  + magn
        ramp_r = highest - magn

    print ("Lowest: " + str(lowest) + ", highest: " + str(highest) + ", increment: " + str(increment))

    x = range(0, freqs)
    plot(x, ramp_l, 'Ramp (L)', 'frequency', 'power')
        
    return ramp_l, ramp_r


def plot(x, y, title, x_label, y_label):
    global plot_graphs
    if plot_graphs:
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
    print("Frequeny samples: " + str(freqs))
    
    #Get ramp functions
    ramp_l, ramp_r = ramp(freqs, peak, 0)
    
    #Apply ramps                        <--------------------------------- TODO
    #process_out_l = ramp_l * fft_out
    #process_out_r = ramp_r * fft_out
    
    process_out_l = fft_out
    process_out_r = fft_out
    
    x = range(0, len(process_out_l))
    plot(x, np.abs(process_out_l), 'Final signal (L)', 'frequency', 'power')
        
    x = range(0, len(process_out_r))
    plot(x, np.abs(process_out_r), 'Final signal (R)', 'frequency', 'power')
        
    final_out = np.vstack(( np.real(ifft(process_out_l)).astype('int16'), np.real(ifft(process_out_r)).astype('int16') )).transpose()
    
    print ("Shape of data: " + str(final_out.shape))
    print ("Data type: " + str(final_out.dtype))

    return final_out


def main():    
    fft_out = getFFT('../InputSamples/16-bit/68_C_HugePad_01_539.wav')
    final_out = pan(fft_out)
    wav.write('../OutputSamples/68_C_HugePad_01_539.wav', rate, final_out)

if __name__ == "__main__":
    main()
