import serial
import time
import matplotlib.pyplot as plt
from collections import deque
from tabulate import tabulate
import pywhatkit as kit

# Seri port ayarları (Arduino'nun bağlı olduğu portu kontrol edin)
SERIAL_PORT = "COM7"  # Arduino'nun bağlı olduğu portu belirleyin
BAUD_RATE = 9600
PHONE_NUMBER = "+905446961727"  # WhatsApp mesajı gönderilecek numara

# Veri saklamak için sıralar
temperature_data = deque(maxlen=50)
current_data = deque(maxlen=50)
voltage_data = deque(maxlen=50)
time_data = deque(maxlen=50)

# Son bir dakikalık veriler
last_minute_data = []


# Yapay zeka karar mekanizması
def analyze_battery(current, temperature):
    if temperature > 50:
        return "Sıcaklık: Yüksek"
    elif temperature < 0:
        return "Sıcaklık: Düşük"
    elif current > 5:
        return "Akım: Yüksek"
    elif current < 1:
        return "Akım: Düşük"
    else:
        return "Normal"


# WhatsApp mesajı gönderme
def send_whatsapp_message(message):
    try:
        current_time = time.localtime()
        hour = current_time.tm_hour
        minute = (current_time.tm_min + 1) % 60  # Bir dakika sonraya ayarla
        kit.sendwhatmsg(PHONE_NUMBER, message, hour, minute)
        print(f"WhatsApp mesajı gönderildi: {message}")
    except Exception as e:
        print(f"WhatsApp mesaj gönderim hatası: {e}")


# Gelen veriyi işleme
def process_data(data, current_time):
    try:
        if "Current" in data and "Temperature" in data:
            current = float(data.split("Current: ")[1].split(",")[0])
            temperature = float(data.split("Temperature: ")[1].split(",")[0])
            voltage = float(data.split("Voltage: ")[1].split(",")[0]) if "Voltage" in data else 0

            status = analyze_battery(current, temperature)

            # Kritik durumlarda veriyi kaydet
            last_minute_data.append(
                f"Zaman: {current_time}s, Akım: {current}A, Sıcaklık: {temperature}°C, Voltaj: {voltage}V, Durum: {status}")

            # Verileri sıralara ekle
            temperature_data.append(temperature)
            voltage_data.append(voltage)
            current_data.append(current)
            time_data.append(current_time)

            return current, temperature, voltage, status
        else:
            raise ValueError("Hatalı veri formatı")
    except Exception:
        # Hatalı veri durumunda varsayılan değerler kullanılır
        print("Hatalı veri alındı, varsayılan değerler kullanılıyor...")
        current = 0
        temperature = 0
        voltage = 0
        status = "Hatalı Veri"

        # Varsayılan değerlerle sıraları güncelle
        temperature_data.append(temperature)
        voltage_data.append(voltage)
        current_data.append(current)
        time_data.append(current_time)

        return current, temperature, voltage, status


# Grafik ayarları
plt.ion()
fig, ax = plt.subplots(3, 1, figsize=(12, 10))


def update_plot():
    if len(time_data) == 0 or len(temperature_data) == 0:
        print("Grafik için yeterli veri yok.")
        return

    ax[0].clear()
    ax[1].clear()
    ax[2].clear()

    # Sıcaklık grafiği
    ax[0].plot(time_data, temperature_data, label="Sıcaklık (°C)", color='red')
    ax[0].set_title("Pil Sıcaklığı")
    ax[0].set_xlabel("Zaman (saniye)")
    ax[0].set_ylabel("Sıcaklık (°C)")
    ax[0].legend()
    ax[0].grid()

    # Voltaj grafiği
    ax[1].plot(time_data, voltage_data, label="Voltaj (V)", color='green')
    ax[1].set_title("Pil Voltajı")
    ax[1].set_xlabel("Zaman (saniye)")
    ax[1].set_ylabel("Voltaj (V)")
    ax[1].legend()
    ax[1].grid()

    # Akım grafiği
    ax[2].plot(time_data, current_data, label="Akım (A)", color='blue')
    ax[2].set_title("Pil Akımı")
    ax[2].set_xlabel("Zaman (saniye)")
    ax[2].set_ylabel("Akım (A)")
    ax[2].legend()
    ax[2].grid()

    plt.pause(0.1)


# Tabloyu güncelle
def update_table():
    table_data = list(zip(time_data, current_data, temperature_data, voltage_data))
    headers = ["Zaman (s)", "Akım (A)", "Sıcaklık (°C)", "Voltaj (V)"]
    print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))


# Seri porttan veri okuma
def read_serial_data():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            start_time = time.time()
            last_message_time = time.time()
            print("Veri okumaya başlandı...")

            while True:
                if ser.in_waiting > 0:
                    current_time = round(time.time() - start_time, 2)
                    data = ser.readline().decode('utf-8').strip()
                    print(f"Gelen Veri: {data}")
                    current, temperature, voltage, status = process_data(data, current_time)

                    update_table()  # Tabloyu güncelle
                    update_plot()  # Grafiği güncelle

                    # Her dakika başında WhatsApp mesajı gönder
                    if time.time() - last_message_time >= 60:
                        if last_minute_data:
                            message = "\n".join(last_minute_data)
                            send_whatsapp_message(f"Son 1 Dakika Verileri:\n{message}")
                            last_minute_data.clear()  # Verileri sıfırla
                        last_message_time = time.time()

    except serial.SerialException as e:
        print(f"Seri bağlantı hatası: {e}")
    except Exception as e:
        print(f"Genel hata: {e}")


# Ana program
if __name__ == "__main__":
    read_serial_data()
