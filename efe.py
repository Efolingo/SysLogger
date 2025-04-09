import os
import platform
import socket
import psutil
import GPUtil  # GPU Utility lib
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email
def send_email(subject, body):
    """Sends an email with the system alert."""
    try:
        sender_email = "your_email@example.com"  # sender email
        receiver_email = "recipient@example.com"  # receiver email
        password = "your_password"  # Your email password or app password

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_system_info():
    """Collects detailed system information."""
    info = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Operating System": platform.system(),
        "OS Version": platform.version(),
        "Architecture": platform.architecture()[0],
        "Processor": platform.processor(),
        "RAM Capacity": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
        "IP Address": socket.gethostbyname(socket.gethostname()),
        "Host Name": socket.gethostname(),
        "CPU Cores": os.cpu_count(),
        "Disk Usage": f"{psutil.disk_usage('/').percent}% used",
        "Uptime": str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0],  # uptime formatted as hh:mm:ss
        "System Load": psutil.cpu_percent(interval=1),  # CPU usage over 1 second
        "Network Sent": f"{round(psutil.net_io_counters().bytes_sent / (1024 ** 2), 2)} MB",
        "Network Received": f"{round(psutil.net_io_counters().bytes_recv / (1024 ** 2), 2)} MB",
        "Battery Status": get_battery_status(),
        "CPU Temperature": get_cpu_temperature(),  #  CPU temperature
        "GPU Info": get_gpu_info()  #  GPU information
    }
    return info

def get_battery_status():
    """Returns battery status if available (for laptops)."""
    battery = psutil.sensors_battery()
    if battery:
        return f"{battery.percent}% (Plugged In: {battery.power_plugged})"
    else:
        return "No battery information available"

def get_cpu_temperature():
    """Returns the CPU temperature if available (for supported platforms)."""
    try:
        # For Linux-based systems, using psutil for CPU temperature
        if platform.system() == "Linux":
            temp = psutil.sensors_temperatures().get("coretemp", [])
            if temp:
                return f"{temp[0].current}°C"
        return "N/A"  # Return N/A for unsupported platforms or systems 
    except Exception as e:
        return "Error fetching temperature"

def get_gpu_info():
    """Fetches GPU information (if available)."""
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return "No GPU detected"

        # Get GPU stats for the first GPU you can modify to loop through all GPUs if needed)
        gpu = gpus[0]
        gpu_info = {
            "GPU Name": gpu.name,
            "GPU Load": f"{gpu.load * 100}%",
            "GPU Memory Usage": f"{gpu.memoryUsed} MB / {gpu.memoryTotal} MB",
            "GPU Temperature": f"{gpu.temperature}°C" if gpu.temperature != -1 else "N/A"  # If temperature is not available
        }
        return gpu_info

    except Exception as e:
        return f"Error fetching GPU info: {e}"

def rotate_logs(log_file):
    """Rotate logs when the log file exceeds 1MB."""
    if os.path.getsize(log_file) > 1 * 1024 * 1024:  # 1MB
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.rename(log_file, log_file.replace(".txt", f"_{timestamp}.txt"))
        print(f"Log file rotated: {log_file.replace('.txt', f'_{timestamp}.txt')}")
        return open(log_file, "w", encoding="utf-8")  # Create a new log file
    else:
        return open(log_file, "a", encoding="utf-8")

def write_log_to_desktop():
    """Writes the system information to a log file on the desktop."""
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        log_file = os.path.join(desktop_path, "syslog.txt")

        # Log rotation
        log_file = rotate_logs(log_file)

        system_info = get_system_info()
        for key, value in system_info.items():
            if isinstance(value, dict):  # If it's GPU info (which is a dict), format nicely
                log_file.write(f"{key}:\n")
                for sub_key, sub_value in value.items():
                    log_file.write(f"  {sub_key}: {sub_value}\n")
            else:
                log_file.write(f"{key}: {value}\n")
        log_file.write("\n" + "="*50 + "\n\n")

        # Send email notification if CPU usage, RAM usage, or disk usage
        if system_info["System Load"] > 90:
            send_email("Critical System Alert", f"CPU usage is at {system_info['System Load']}%.")
        if psutil.virtual_memory().percent > 85:
            send_email("Critical System Alert", f"RAM usage is at {psutil.virtual_memory().percent}%.")
        if psutil.disk_usage('/').percent > 90:
            send_email("Critical System Alert", f"Disk usage is at {psutil.disk_usage('/').percent}%.")
        
        print(f"System information successfully written to {log_file.name}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    write_log_to_desktop()
