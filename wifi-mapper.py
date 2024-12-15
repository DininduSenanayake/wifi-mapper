import subprocess
import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def get_wifi_strength():
    """
    Get Wi-Fi signal strength using iwconfig command.
    Returns signal level in dBm.
    """
    try:
        # Run iwconfig command and capture output
        output = subprocess.check_output(['iwconfig', 'wlan0']).decode('utf-8')
        
        # Find the signal level in the output
        for line in output.split('\n'):
            if 'Signal level' in line:
                # Extract the dBm value
                signal_start = line.find('Signal level=') + 13
                signal_end = line.find(' dBm')
                return int(line[signal_start:signal_end])
    except:
        return None

def collect_measurements(duration_seconds=60, interval=1):
    """
    Collect Wi-Fi signal measurements over time.
    
    Args:
        duration_seconds (int): How long to collect data
        interval (int): Seconds between measurements
    
    Returns:
        list: List of dictionaries containing timestamp and signal strength
    """
    measurements = []
    start_time = time.time()
    
    while time.time() - start_time < duration_seconds:
        strength = get_wifi_strength()
        if strength is not None:
            measurements.append({
                'timestamp': datetime.now(),
                'strength': strength,
                'location': 'current'  # You can modify this for different locations
            })
        time.sleep(interval)
    
    return measurements

def plot_signal_strength(data):
    """
    Create visualizations of the Wi-Fi signal strength data.
    """
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Time series plot
    sns.lineplot(data=df, x='timestamp', y='strength', ax=ax1)
    ax1.set_title('Wi-Fi Signal Strength Over Time')
    ax1.set_ylabel('Signal Strength (dBm)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Distribution plot
    sns.histplot(data=df, x='strength', ax=ax2)
    ax2.set_title('Distribution of Signal Strength')
    ax2.set_xlabel('Signal Strength (dBm)')
    
    plt.tight_layout()
    plt.savefig('wifi_signal_analysis.png')
    plt.close()

def main():
    print("Starting Wi-Fi signal strength mapping...")
    print("Collecting measurements for 1 minute...")
    
    # Collect measurements
    measurements = collect_measurements(duration_seconds=60, interval=1)
    
    if not measurements:
        print("Error: No measurements collected. Please check your wireless interface.")
        return
    
    # Create visualizations
    print(f"Collected {len(measurements)} measurements. Creating visualizations...")
    plot_signal_strength(measurements)
    
    # Basic statistics
    df = pd.DataFrame(measurements)
    print("\nSignal Strength Statistics:")
    print(f"Average: {df['strength'].mean():.1f} dBm")
    print(f"Maximum: {df['strength'].max()} dBm")
    print(f"Minimum: {df['strength'].min()} dBm")
    
    print("\nVisualization saved as 'wifi_signal_analysis.png'")

if __name__ == "__main__":
    main()