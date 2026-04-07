import subprocess
import re
import pythoncom
import wmi
from PyQt5.QtCore import QThread, pyqtSignal

ERROR_LOG = "error_log.txt"


def get_disk_info():
    try:
        c = wmi.WMI()
        return [(disk.DeviceID, disk.SerialNumber) for disk in c.Win32_DiskDrive()]
    except Exception as e:
        log_error("get_disk_info", e)
        return []

def get_mac_address():
    try:
        output = subprocess.check_output(['ipconfig', '/all'])
        mac = re.search(r'Physical Address[\. ]+: ([\w\-]+)', str(output))
        return mac.group(1) if mac else "MAC Address not found"
    except Exception as e:
        log_error("get_mac_address", e)
        return "Error"

def get_motherboard_info():
    try:
        output = subprocess.check_output(
            ['wmic', 'baseboard', 'get', 'Manufacturer,Product,SerialNumber']
        )
        lines = output.decode('utf-8').strip().split('\n')
        return lines[1].strip() if len(lines) >= 2 else "Motherboard info not found"
    except Exception as e:
        log_error("get_motherboard_info", e)
        return "Error"

def get_cpu_id():
    try:
        output = subprocess.check_output(['wmic', 'cpu', 'get', 'ProcessorID'])
        return output.decode('utf-8').split('\n')[1].strip()
    except Exception as e:
        log_error("get_cpu_id", e)
        return "Error"

def get_volume_info():
    try:
        c = wmi.WMI()
        return [
            (disk.Caption, f"{disk.VolumeSerialNumber[:4]}-{disk.VolumeSerialNumber[4:]}")
            for disk in c.Win32_LogicalDisk()
        ]
    except Exception as e:
        log_error("get_volume_info", e)
        return []

def log_error(function_name, error):
    with open(ERROR_LOG, "a") as f:
        f.write(f"Error in {function_name}: {error}\n")

def read_error_log() -> str:
    try:
        with open(ERROR_LOG, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def clear_error_log():
    open(ERROR_LOG, "w").close()


class LoaderThread(QThread):
    done = pyqtSignal(dict)

    def run(self):
        # WMI requires COM to be initialized on each thread
        pythoncom.CoInitialize()
        try:
            disk = get_disk_info()
            volume = get_volume_info()
            self.done.emit({
                "disk":        "\n".join(f"Disk {i}: {sn}" for i, (_, sn) in enumerate(disk, 1)) or "No disks found",
                "mac":         get_mac_address(),
                "motherboard": get_motherboard_info(),
                "cpu":         get_cpu_id(),
                "volume":      "\n".join(f"Drive {d}: {vid}" for d, vid in volume) or "No volumes found",
            })
        finally:
            pythoncom.CoUninitialize()
