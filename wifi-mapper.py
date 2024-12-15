import subprocess
import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def list_wifi_interfaces():
    """
    List all available wireless interfaces
    """
    try:
        output = subprocess.check_output(['iwconfig'], stderr=subprocess.STDOUT).decode('utf-8')
        interfaces = []
        for line in output.split('\n'):
            if 'IEEE 802.11' in line:  # This line contains wireless interface
                interfaces.append(line.split()[0])
        return interfaces
    except subprocess.CalledProcessError:
        return []

def get_interface_details(interface):
    """
    Get details about a specific wireless interface
    """
    try:
        output = subprocess.check_output(['iwconfig', interface]).decode('utf-8')
        return output
    except subprocess.CalledProcessError:
        return None

def get_wifi_strength(interface):
    """
    Get Wi-Fi signal strength using iwconfig command for specified interface.
    Returns signal level in dBm.
    """
    try:
        output = subprocess.check_output(['iwconfig', interface]).decode('utf-8')
        
        for line in output.split('\n'):
            if 'Signal level' in line:
                signal_start = line.find('Signal level=') + 13
                signal_end = line.find(' dBm')
                return int(line[signal_start:signal_end])
    except:
        return None

def collect_measurements(interface, duration_seconds=60, interval=1):
    """
    Collect Wi-Fi signal measurements over time.
    
    Args:
        interface (str): Name of wireless interface to use
        duration_seconds (int): How long to collect data
        interval (int): Seconds between measurements
    
    Returns:
        list: List of dictionaries containing timestamp and signal strength
    """
    measurements = []
    start_time = time.time()
    
    while time.time() - start_time < duration_seconds:
        strength = get_wifi_strength(interface)
        if strength is not None:
            measurements.append({
                'timestamp': datetime.now(),
                'strength': strength,
                'interface': interface,
                'location': 'current'
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
    ax1.set_title(f'Wi-Fi Signal Strength Over Time ({df.interface.iloc[0]})')
    ax1.set_ylabel('Signal Strength (dBm)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Distribution plot
    sns.histplot(data=df, x='strength', ax=ax2)
    ax2.set_title('Distribution of Signal Strength')
    ax2.set_xlabel('Signal Strength (dBm)')
    
    plt.tight_layout()
    plt.savefig(f'wifi_signal_analysis_{df.interface.iloc[0]}.png')
    plt.close()

def main():
    # List available interfaces
    interfaces = list_wifi_interfaces()
    
    if not interfaces:
        print("No wireless interfaces found!")
        return
    
    print("Available wireless interfaces:")
    for i, interface in enumerate(interfaces, 1):
        print(f"{i}. {interface}")
        details = get_interface_details(interface)
        if details:
            print(f"   Details: {details.split('\n')[0]}")
        print()
    
    # Let user select interface
    while True:
        try:
            choice = int(input(f"Select interface (1-{len(interfaces)}): ")) - 1
            if 0 <= choice < len(interfaces):
                selected_interface = interfaces[choice]
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")
    
    print(f"\nUsing interface: {selected_interface}")
    print("Starting Wi-Fi signal strength mapping...")
    print("Collecting measurements for 1 minute...")
    
    # Collect measurements
    measurements = collect_measurements(selected_interface, duration_seconds=60, interval=1)
    
    if not measurements:
        print(f"Error: No measurements collected. Please check if {selected_interface} is connected to a network.")
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
    
    print(f"\nVisualization saved as 'wifi_signal_analysis_{selected_interface}.png'")

if __name__ == "__main__":
    main()