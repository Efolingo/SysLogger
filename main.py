import os
import platform
import socket
import psutil
from datetime import datetime

def get_system_info():
    info = {
        "Tarih ve Saat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "İşletim Sistemi": platform.system(),
        "OS Sürümü": platform.version(),
        "Mimari": platform.architecture()[0],
        "İşlemci": platform.processor(),
        "RAM Kapasitesi": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
        "IP Adresi": socket.gethostbyname(socket.gethostname()),
        "Ağ Adı": socket.gethostname(),
        "Çekirdek Sayısı": os.cpu_count()
    }
    return info

def write_log_to_desktop():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    log_file = os.path.join(desktop_path, "syslog.txt")
    
    system_info = get_system_info()
    with open(log_file, "w", encoding="utf-8") as file:
        for key, value in system_info.items():
            file.write(f"{key}: {value}\n")
    
    print(f"Sistem bilgileri başarıyla {log_file} dosyasına yazıldı.")

if __name__ == "__main__":
    write_log_to_desktop()
