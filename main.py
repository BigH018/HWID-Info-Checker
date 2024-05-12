import subprocess
import re
import wmi
import tkinter as tk
from tkinter import ttk


def get_disk_info():
    """Fetches Disk Information using WMI."""
    try:
        c = wmi.WMI()
        disk_info = [(disk.DeviceID, disk.SerialNumber) for disk in c.Win32_DiskDrive()]
        return disk_info
    except Exception as e:
        log_error("get_disk_info", e)
        return []

def get_mac_address():
    """Fetches MAC Address."""
    try:
        output = subprocess.check_output(['ipconfig', '/all'])
        mac_address = re.search(r'Physical Address[\. ]+: ([\w\-]+)', str(output))
        return mac_address.group(1) if mac_address else "MAC Address not found"
    except Exception as e:
        log_error("get_mac_address", e)
        return "Error"

def get_motherboard_info():
    """Fetches Motherboard Information."""
    try:
        output = subprocess.check_output(['wmic', 'baseboard', 'get', 'Manufacturer,Product,SerialNumber'])
        lines = output.decode('utf-8').strip().split('\n')
        return lines[1].strip() if len(lines) >= 2 else "Motherboard info not found"
    except Exception as e:
        log_error("get_motherboard_info", e)
        return "Error"

def get_cpu_id():
    """Fetches CPU ID."""
    try:
        output = subprocess.check_output(['wmic', 'cpu', 'get', 'ProcessorID'])
        return output.decode('utf-8').split('\n')[1].strip()
    except Exception as e:
        log_error("get_cpu_id", e)
        return "Error"

def get_volume_id():
    """Fetches Volume ID."""
    try:
        c = wmi.WMI()
        volume_info = [(disk.Caption, f"{disk.VolumeSerialNumber[:4]}-{disk.VolumeSerialNumber[4:]}") for disk in c.Win32_LogicalDisk()]
        return volume_info
    except Exception as e:
        log_error("get_volume_id", e)
        return []

def log_error(function_name, error):
    """Logs errors."""
    with open("error_log.txt", "a") as f:
        f.write(f"Error in {function_name}: {error}\n")

def update_labels():
    disk_info = get_disk_info()
    labels[0].config(state=tk.NORMAL)
    labels[0].delete(1.0, tk.END)
    labels[0].insert(tk.END, "\n".join([f"Disk {i}: {serial_number}" for i, (_, serial_number) in enumerate(disk_info, start=1)]))
    labels[0].config(state=tk.DISABLED)
    
    mac_address = get_mac_address()
    labels[1].config(state=tk.NORMAL)
    labels[1].delete(1.0, tk.END)
    labels[1].insert(tk.END, mac_address)
    labels[1].config(state=tk.DISABLED)
    
    motherboard_info = get_motherboard_info()
    labels[2].config(state=tk.NORMAL)
    labels[2].delete(1.0, tk.END)
    labels[2].insert(tk.END, motherboard_info)
    labels[2].config(state=tk.DISABLED)
    
    cpu_id = get_cpu_id()
    labels[3].config(state=tk.NORMAL)
    labels[3].delete(1.0, tk.END)
    labels[3].insert(tk.END, cpu_id)
    labels[3].config(state=tk.DISABLED)
    
    volume_info = get_volume_id()
    labels[4].config(state=tk.NORMAL)
    labels[4].delete(1.0, tk.END)
    labels[4].insert(tk.END, "\n".join([f"Drive {drive}: {volume_id}" for drive, volume_id in volume_info]))
    labels[4].config(state=tk.DISABLED)

# GUI setup
root = tk.Tk()
root.title("HWID Info")
root.geometry("600x400")
root.configure(bg="#f0f0f0")  # Set background color



# Container frame
container = ttk.Frame(root)
container.pack(fill='both', expand=True, padx=20, pady=20)

# Styles
style = ttk.Style()
style.configure("Title.TLabel", font=('Helvetica', 14, 'bold'), background="#f0f0f0")  # Style for title labels
style.configure("Info.TLabel", font=('Helvetica', 12), background="#f0f0f0")  # Style for info labels

# Titles and labels to display information
titles = ["Disk Information", "MAC Address", "Motherboard", "CPU ID", "Volume Information"]
labels = []

for title in titles:
    title_label = ttk.Label(container, text=title, style="Title.TLabel")
    title_label.pack(fill='x', pady=(0, 5))
    text = tk.Text(container, wrap='word', height=2, width=50, font=('Helvetica', 12), borderwidth=0, highlightthickness=0, takefocus=0, state=tk.DISABLED, bg="#ffffff")
    text.pack(fill='x', padx=5)
    labels.append(text)

# Initial update
update_labels()

root.mainloop()