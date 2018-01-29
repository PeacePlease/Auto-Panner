from scipy.io import wavfile as wav
from scipy.fftpack import fft, ifft, fftfreq
import numpy as np
from bokeh.plotting import figure, show

plot_graphs = False
rate = 0

def ramp(freqs, startf, endf):

    print "\n\n==========================\n Generating ramp function \n==========================\n"
    
    ramp_l = np.zeros(len(freqs))
    ramp_r = np.zeros(len(freqs))

    for i in range(0, len(freqs)):
        if   abs(freqs[i]) < startf:
            ramp_l[i] = 1
        elif abs(freqs[i]) > endf:
            ramp_r[i] = 1
        else:
            ramp_r[i] = float(abs(freqs[i])-startf)/(endf-startf)
            ramp_l[i] = 1-ramp_r[i]
    
    plot(freqs, ramp_l, 'Ramp (L)', 'frequency', 'power')
    plot(freqs, ramp_r, 'Ramp (R)', 'frequency', 'power')
        
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

    if len(data) > 10000000:
        print("WARNING: Cutting short for now")
        data = data[:10000000]
    
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
    freqs = fftfreq(data.size, float(1)/rate)
    
    plot(freqs, np.abs(fft_out), 'Original FFT', 'frequency', 'power')
        
    return freqs, fft_out

def pan(freqs, fft_out):

    print "\n==========================\n Applying pan effect \n==========================\n"

    #Find peak power
    peak = np.real(np.amax(fft_out))
    print("Max value: " + str(peak))
    
    #Get number of frequency samples
    print("Frequency samples: " + str(len(fft_out)))
    print("Frequency range:   " + str(min(freqs)/1000) + "-" + str(max(freqs)/1000) + " kHz")
    
    #Get ramp functions
    ramp_l, ramp_r = ramp(freqs, 50, 1000)
    
    process_out_l = fft_out * ramp_l
    process_out_r = fft_out * ramp_r
    
    plot(freqs, process_out_l, 'Final signal (L)', 'frequency', 'power')
    plot(freqs, process_out_r, 'Final signal (R)', 'frequency', 'power')
        
    return process_out_l, process_out_r


def write_wav(left, right, path):
    print "\n==========================\n Run IFFT and write audio out \n==========================\n"
    final_out = np.vstack(( np.real(ifft(left)).astype('int16'), np.real(ifft(right)).astype('int16') )).transpose()
    print ("Shape of data: " + str(final_out.shape) + ", data type: " + str(final_out.dtype))
    wav.write(path, rate, final_out)
    
####################################################################################################

def main():

#Get FFT
    freqs, fft_out = getFFT('../InputSamples/16-bit/LeOnde.wav')

#Apply pan effect (mono in, stereo out)
    process_out_l, process_out_r = pan(freqs, fft_out)

#IFFT and write result
    write_wav(process_out_l, process_out_r, '../OutputSamples/LeOnde.wav')

if __name__ == "__main__":
    main()
