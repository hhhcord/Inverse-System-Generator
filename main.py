import copy
from ClassFiles.AudioLoader import AudioLoader  # Import the AudioLoader class
from ClassFiles.FrequencyResponseAnalyzer import FrequencyResponseAnalyzer  # Import the FrequencyResponseAnalyzer class
from ClassFiles.ControlSystemSimulation import ControlSystemSimulation
from ClassFiles.StateFeedbackControllerSimulation import StateFeedbackController

def main():
    # Create an instance of AudioLoader
    print("Creating AudioLoader instance...")
    al = AudioLoader()

    # Specify the duration in seconds to read
    # time_test = 20  # Time duration for input/output audio data
    time_test = 60
    # time_input = 20  # Time duration for test audio data
    time_input = 27
    # time_input = 255

    # Load the input audio signal for a specified time period
    print("\nPlease select the .wav file for the input audio signal")
    input_data, sampling_rate = al.load_audio(time_test)
    print("Input audio signal loaded.")

    # Load the output audio signal for the same time period
    print("\nPlease select the .wav file for the output audio signal")
    output_data, _ = al.load_audio(time_test)
    print("Output audio signal loaded.")

    # Load the test audio signal for a different time period
    print("\nPlease select the .wav file for the test audio signal")
    test_data, _ = al.load_audio(time_input)
    print("Test audio signal loaded.")

    # Create an instance of FrequencyResponseAnalyzer and perform analysis
    print("Creating FrequencyResponseAnalyzer instance and analyzing frequency response...")
    fra = FrequencyResponseAnalyzer(input_signal=input_data, output_signal=output_data, sampling_rate=sampling_rate, time_duration=time_test)
    fra.analyze_and_save_bode_plot()
    print("Frequency response analysis completed and Bode plot saved.")

    # Specify the order of the system for simulation
    system_order = 149
    # system_order = 2

    # Set up the control system simulation
    print("Setting up the control system simulation...")
    simulation = ControlSystemSimulation(n=system_order, t_end=time_test, num_points=len(input_data))

    # Plot the input and output signals
    print("Plotting input and output signals...")
    simulation.plot_input_output(input_data, output_data, filename='input_output_plot.png')

    # Identify the system using SRIM method
    print("Identifying system using SRIM method...")
    SRIM_plant_system = simulation.identify_system_SRIM(input_data, output_data)
    print("System identification completed.")

    # Plot the step response for the identified system
    print("Plotting step response for the identified system...")
    simulation.plot_step_response_SRIM(SRIM_plant_system)

    # Plot the eigenvalues for the identified system
    print("Plotting eigenvalues for the identified system...")
    simulation.plot_eigenvalues_SRIM(SRIM_plant_system)

    # Plot the Bode plot for the identified system
    print("Plotting Bode plot for the identified system...")
    simulation.plot_bode_SRIM(SRIM_plant_system)

    # Process the system matrix and save the natural frequencies
    print("Processing system matrix and saving natural frequencies...")
    simulation.process_matrix_and_save(SRIM_plant_system.A, filename="plant_system_eigenvalues_frequencies.csv")

    # Set up the State Feedback Controller
    print("Setting up State Feedback Controller...")
    SFC = StateFeedbackController(
        n=system_order, 
        plant_system=SRIM_plant_system, 
        ideal_system=None, 
        input_signal=input_data, 
        test_signal=test_data, 
        sampling_rate=sampling_rate, 
        F_ini=None, 
        F_ast=None
    )

    # Simulate the system and get the output signals
    print("Running the State Feedback Controller simulation...")
    uncontrolled_output = SFC.optimal_equalization()
    print("Simulation completed.")

    # Save the resulting audio signals
    print("Saving the simulated output signals as audio files...")
    al.save_audio(uncontrolled_output, sampling_rate, 'InverseSystemOutput')
    print("All audio files saved.")

if __name__ == "__main__":
    main()
