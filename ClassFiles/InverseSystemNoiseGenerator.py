import numpy as np
from scipy.io import wavfile
import control as ctrl
import os

class InverseSystemNoiseGenerator:
    def __init__(self, A, B, C, D, fs=44100, duration=60):
        """
        Initializes the system parameters.
        :param A: State matrix
        :param B: Input matrix
        :param C: Output matrix
        :param D: Direct transmission matrix
        :param fs: Sampling frequency (default is 44100 Hz)
        :param duration: Signal duration in seconds (default is 1 second)
        :param outlier_threshold: Z-score threshold for outlier removal (default is 3.0)
        """
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.fs = fs
        self.Ts = 1 / fs
        self.duration = duration
        self.n_points = fs * duration
    
    def compute_inverse_frequency_response(self):
        """
        Computes the inverse frequency response of the system.
        
        Returns:
            Tuple: (inverted magnitude, inverted phase, frequencies)
        """
        # Create a state-space representation of the digital system
        digital_system = ctrl.ss(self.A, self.B, self.C, self.D, self.Ts)

        # Compute the Bode plot
        magnitude, phase, omega = ctrl.bode(digital_system, plot=False)
        # print('magnitude: ', magnitude)
        frequencies = omega / (2 * np.pi)

        # Normalize the 'magnitude' array by dividing each element by 0.03
        magnitude_normalize = magnitude / (3e-2)

        # Invert the magnitude by taking the reciprocal
        magnitude_inverse = 1 / magnitude_normalize

        # Invert the phase by negating it
        phase_inverse = -phase

        return magnitude_inverse, phase_inverse, frequencies
    
    def generate_modified_swept_sine_signal(self, magnitude_inverse, phase_inverse, frequencies, start_freq=20, end_freq=20e3):
        """
        Generates an exponential swept-sine signal modified by the inverse frequency response.
        
        Parameters:
            magnitude_inverse (np.ndarray): Inverted magnitude response.
            phase_inverse (np.ndarray): Inverted phase response.
            frequencies (np.ndarray): Frequencies corresponding to the inverse response.
            start_freq (float): Starting frequency of the swept-sine signal in Hz.
            end_freq (float): Ending frequency of the swept-sine signal in Hz.

        Returns:
            Tuple: (time array, swept-sine signal affected by inverse frequency response)
        """
        # Calculate the sweep rate constant K
        sweep_rate_constant = self.duration / np.log(end_freq / start_freq)

        # Create a time array for the signal duration
        time_array = np.linspace(0, self.duration, self.n_points)

        # Initialize the modified exponential swept-sine signal
        modified_swept_sine_signal = np.zeros_like(time_array)

        # Generate the original exponential swept-sine signal
        original_swept_sine_signal = np.sin(2 * np.pi * start_freq * sweep_rate_constant * (np.exp(time_array / sweep_rate_constant) - 1))

        for i, t in enumerate(time_array):
            current_freq = start_freq * np.exp(t / sweep_rate_constant)

            # Find the index of the frequency in `frequencies` that is closest to `current_freq`
            closest_freq_index = np.argmin(np.abs(frequencies - current_freq))

            # Retrieve the corresponding inverse magnitude and inverse phase
            magnitude_inv = magnitude_inverse[closest_freq_index]
            phase_inv = phase_inverse[closest_freq_index]

            # Generate the modified swept-sine signal
            modified_swept_sine_signal[i] = magnitude_inv * np.sin(2 * np.pi * start_freq * sweep_rate_constant * (np.exp(t / sweep_rate_constant) - 1) + phase_inv)
        
        return time_array, original_swept_sine_signal, modified_swept_sine_signal
    
    def save_as_wav(self, original_filename='original_swept_sine.wav', modified_filename='modified_swept_sine.wav'):
        """
        Saves both the original and modified swept-sine signals as .wav files.
        :param original_filename: Filename for the original swept-sine signal (default is 'original_swept_sine.wav')
        :param modified_filename: Filename for the modified swept-sine signal (default is 'modified_swept_sine.wav')
        """
        # Ensure the output directory exists
        output_dir = './output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Compute inverse frequency response
        inverted_magnitude, inverted_phase, frequencies = self.compute_inverse_frequency_response()

        # Generate both the original and modified swept-sine signals
        time_array, original_swept_sine_signal, modified_swept_sine_signal = self.generate_modified_swept_sine_signal(
            inverted_magnitude, 
            inverted_phase, 
            frequencies)

        # Normalize and convert the original swept-sine signal to 16-bit integer format
        normalized_original_signal = np.int16(original_swept_sine_signal / np.max(np.abs(original_swept_sine_signal)) * 32767)

        # Normalize and convert the modified swept-sine signal to 16-bit integer format
        normalized_modified_signal = np.int16(modified_swept_sine_signal / np.max(np.abs(modified_swept_sine_signal)) * 32767)

        # Construct the full paths for the output files
        original_output_filepath = os.path.join(output_dir, original_filename)
        modified_output_filepath = os.path.join(output_dir, modified_filename)

        # Save the original swept-sine signal as a .wav file
        wavfile.write(original_output_filepath, self.fs, normalized_original_signal)

        # Save the modified swept-sine signal as a .wav file
        wavfile.write(modified_output_filepath, self.fs, normalized_modified_signal)

        print(f"Original swept-sine signal saved as '{original_output_filepath}'.")
        print(f"Modified swept-sine signal saved as '{modified_output_filepath}'.")
