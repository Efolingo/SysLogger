import os
import platform
import socket
import psutil
import GPUtil
import smtplib
import time
import requests
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from email.mime.image import MIMEImage
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Email configuration
EMAIL_CONFIG = {
    "sender": "your_email@gmail.com",
    "receiver": "recipient_email@gmail.com",
    "password": "your_app_password", 
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}

def send_email(subject, body, attachment_path=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["sender"]
        msg['To'] = EMAIL_CONFIG["receiver"]
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Ek varsa ekle
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEText(f.read().decode("utf-8-sig"), 'plain', 'utf-8')
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
                msg.attach(part)

        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
            server.sendmail(EMAIL_CONFIG["sender"], EMAIL_CONFIG["receiver"], msg.as_string())
        print("Email gönderildi")
    except Exception as e:
        print(f"Email gönderilemedi: {e}")
        
send_email(
    subject="Sistem Log Raporu",
    body="Log dosyası ektedir.",
    attachment_path="system_monitor.log"
)



def get_system_info():
    """Sistem bilgilerini toplar"""
    info = {
        "Zaman": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "İşletim Sistemi": platform.system(),
        "OS Versiyon": platform.version(),
        "Mimari": platform.architecture()[0],
        "İşlemci": platform.processor(),
        "RAM Kapasite": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
        "IP Adres": socket.gethostbyname(socket.gethostname()),
        "Host Adı": socket.gethostname(),
        "CPU Çekirdek": os.cpu_count(),
        "Disk Kullanım": f"{psutil.disk_usage('/').percent}%",
        "Çalışma Süresi": str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0],
        "CPU Yük": psutil.cpu_percent(interval=1),
        "Ağ Gönderim": f"{round(psutil.net_io_counters().bytes_sent / (1024 ** 2), 2)} MB",
        "Ağ Alım": f"{round(psutil.net_io_counters().bytes_recv / (1024 ** 2), 2)} MB",
        "Pil Durumu": get_battery_status(),
        "CPU Sıcaklık": get_cpu_temperature(),
        "GPU Bilgisi": get_gpu_info(),
        "Cpu Ve ram geçmişi": save_usage_graph(),
        "İnternet Bağlantısı": "Var" if check_internet() else "Yok",
        "Email gönderimi":send_email(),
        "Public İp":get_public_ip()

    }
    return info

def get_battery_status():
    """Pil durumunu kontrol eder"""
    battery = psutil.sensors_battery()
    return f"{battery.percent}% (Şarjda: {battery.power_plugged})" if battery else "Pil yok"

def get_cpu_temperature():
    """CPU sıcaklığını alır"""
    try:
        if platform.system() == "Linux":
            temp = psutil.sensors_temperatures().get("coretemp", [])
            return f"{temp[0].current}°C" if temp else "N/A"
        return "N/A"
    except Exception as e:
        return f"Hata: {str(e)}"
    

def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False
    
def get_public_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return "Erişilemedi"


def get_gpu_info():
    """GPU bilgilerini alır"""
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return "GPU bulunamadı"
        
        gpu = gpus[0]
        return {
            "GPU Adı": gpu.name,
            "GPU Yük": f"{gpu.load * 100}%",
            "GPU Bellek": f"{gpu.memoryUsed} MB / {gpu.memoryTotal} MB",
            "GPU Sıcaklık": f"{gpu.temperature}°C" if gpu.temperature != -1 else "N/A"
        }
    except Exception as e:
        return f"Hata: {str(e)}"

def get_disk_partitions():
    """Disk bölümlerini listeler"""
    partitions = psutil.disk_partitions()
    disk_info = {}
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info[partition.device] = {
                "Bağlama Noktası": partition.mountpoint,
                "Dosya Sistemi": partition.fstype,
                "Kullanım": f"{usage.percent}%",
                "Toplam": f"{round(usage.total / (1024 ** 3), 2)} GB",
                "Kullanılan": f"{round(usage.used / (1024 ** 3), 2)} GB",
                "Boş": f"{round(usage.free / (1024 ** 3), 2)} GB"
            }
        except Exception as e:
            disk_info[partition.device] = f"Hata: {str(e)}"
    return disk_info

def launch_gui():
    def update_stats():
        try:
            info = get_system_info()

            cpu_label.config(text=f"CPU Yükü: {info['CPU Yük']}%")
            ram_label.config(text=f"RAM: {info['RAM Kapasite']}")
            disk_label.config(text=f"Disk: {info['Disk Kullanım']}")
            internet_label.config(text=f"İnternet: {info['İnternet Bağlantısı']}")
            battery_label.config(text=f"Batarya: {info['Pil Durumu']}")

            gpu = info["GPU Bilgisi"]
            if isinstance(gpu, dict):
                gpu_label.config(text=f"GPU: {gpu['GPU Adı']} ({gpu['GPU Yük']})")
            else:
                gpu_label.config(text=str(gpu))

        except Exception as e:
            cpu_label.config(text=f"Hata: {e}")

        
        window.after(5000, update_stats)

    window = tk.Tk()
    window.title("Sistem Durumu Paneli")
    window.geometry("400x250")
    window.resizable(False, False)

    style = ttk.Style(window)
    style.theme_use("clam")

    title = tk.Label(window, text="🖥️ Sistem Durumu", font=("Arial", 16, "bold"))
    title.pack(pady=10)

    cpu_label = tk.Label(window, text="", font=("Arial", 12))
    cpu_label.pack()

    ram_label = tk.Label(window, text="", font=("Arial", 12))
    ram_label.pack()

    disk_label = tk.Label(window, text="", font=("Arial", 12))
    disk_label.pack()

    internet_label = tk.Label(window, text="", font=("Arial", 12))
    internet_label.pack()

    battery_label = tk.Label(window, text="", font=("Arial", 12))
    battery_label.pack()

    gpu_label = tk.Label(window, text="", font=("Arial", 12))
    gpu_label.pack()

    update_stats()
    window.mainloop()


def send_email_with_graph(subject, body, image_path=None):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_CONFIG["sender"]
    msg['To'] = EMAIL_CONFIG["receiver"]
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if image_path and os.path.exists(image_path):
        with open(image_path, 'rb') as img:
            mime_img = MIMEImage(img.read())
            mime_img.add_header('Content-ID', '<graph>')
            msg.attach(mime_img)

    with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
        server.starttls()
        server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
        server.sendmail(EMAIL_CONFIG["sender"], EMAIL_CONFIG["receiver"], msg.as_string())

def create_log_file():
    """Log dosyasını oluşturur veya açar"""
    log_file = "system_monitor.log"
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("=== Sistem İzleme Logu ===\n")
    return log_file

def save_usage_graph(cpu_usage_list, ram_usage_list, timestamps):
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, cpu_usage_list, label="CPU Kullanımı (%)")
    plt.plot(timestamps, ram_usage_list, label="RAM Kullanımı (%)")
    plt.xlabel("Zaman")
    plt.ylabel("Kullanım (%)")
    plt.title("Sistem Kaynak Kullanımı")
    plt.legend()
    plt.tight_layout()
    plt.savefig("usage_graph.png")
    plt.close()

def write_log():
    """Sistem bilgilerini log dosyasına yazar"""
    try:
        log_file = create_log_file()
        
        with open(log_file, "a", encoding="utf-8") as f:
            system_info = get_system_info()
            f.write(f"\n=== Sistem Bilgileri ({system_info['Zaman']}) ===\n")
            
            for key, value in system_info.items():
                if isinstance(value, dict):
                    f.write(f"{key}:\n")
                    for sub_key, sub_value in value.items():
                        f.write(f"  {sub_key}: {sub_value}\n")
                else:
                    f.write(f"{key}: {value}\n")
            
            f.write("\nDisk Bölümleri:\n")
            for part, info in get_disk_partitions().items():
                f.write(f"{part}:\n")
                if isinstance(info, dict):
                    for k, v in info.items():
                        f.write(f"  {k}: {v}\n")
                else:
                    f.write(f"  {info}\n")
            
            f.write("\n" + "="*50 + "\n")
        
        # Kritik durum kontrolü
        check_critical_conditions(system_info)
        
        print(f"Sistem bilgileri {log_file} dosyasına kaydedildi")
        
    except Exception as e:
        print(f"Log yazma hatası: {e}")

def check_critical_conditions(system_info):
    """Kritik durumları kontrol eder"""
    try:
        cpu_usage = system_info["CPU Yük"]
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        alerts = []
        if cpu_usage > 90:
            alerts.append(f"CPU kullanımı %{cpu_usage}")
        if ram_usage > 85:
            alerts.append(f"RAM kullanımı %{ram_usage}")
        if disk_usage > 90:
            alerts.append(f"Disk kullanımı %{disk_usage}")
        
        if alerts:
            send_email(
                "KRİTİK SİSTEM UYARISI",
                "UYARI: Aşağıdaki kritik durumlar tespit edildi:\n\n" +
                "\n".join(alerts) +
                f"\n\nDetaylı sistem bilgisi:\n{system_info}"
            )
    except Exception as e:
        print(f"Kritik durum kontrol hatası: {e}")

def main():
    """Ana program"""
    print("Mod seçin:")
    print("1. Terminal üzerinden sistem izleme (Log ve e-mail)")
    print("2. Arayüz (tkinter panel)")
    secim = input("Seçim (1/2): ").strip()

    if secim == "2":
        launch_gui()
    else:
        print("Sistem izleme başlatıldı...")
        while True:
            try:
                write_log()
                print(f"Son kontrol: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("5 dakika bekleniyor... (Çıkmak için Ctrl+C)")
                time.sleep(300)
            except KeyboardInterrupt:
                print("\nProgram sonlandırılıyor...")
                break
            except Exception as e:
                print(f"Beklenmeyen hata: {e}")
                time.sleep(60)
 

if __name__ == "__main__":
    main()