import os
import platform
import psutil

def get_system_status() -> str:
    battery = psutil.sensors_battery()
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    
    status = f"CPU usage is at {cpu} percent. Memory is at {ram} percent. "
    
    if battery:
        plugged = "plugged in and charging" if battery.power_plugged else "on battery power"
        status += f"Battery is at {battery.percent} percent and is {plugged}."
    else:
        status += "Battery information is not available."
        
    return status

def shutdown_pc():
    if platform.system() == "Windows":
        os.system("shutdown /s /t 5")
        
def restart_pc():
    if platform.system() == "Windows":
        os.system("shutdown /r /t 5")

def sleep_pc():
    if platform.system() == "Windows":
        # rundll32 SetSuspendState often fails on modern Windows (Modern Standby).
        # Use PowerShell with .NET call — more reliable.
        os.system(
            'powershell -Command "'
            'Add-Type -AssemblyName System.Windows.Forms; '
            '[System.Windows.Forms.Application]::SetSuspendState('
            '[System.Windows.Forms.PowerState]::Suspend, $false, $false)'
            '"'
        )

def set_volume(level: int):
    print(f"Mock: Setting volume to {level}%")
