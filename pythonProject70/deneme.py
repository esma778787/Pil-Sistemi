import serial
import pywhatkit as kit
import time

# Seri port ayarları (Arduino bağlı olduğu portu belirleyin)
SERIAL_PORT = "COM8"  # Arduino'nun bağlı olduğu portu kontrol edin
BAUD_RATE = 9600
PHONE_NUMBER = "+905446961727"  # Mesaj göndermek istediğiniz numara


def send_whatsapp_message(message):
    try:
        # Mesajı şu anki zamandan 1 dakika sonrasına planla
        current_time = time.localtime()
        hour = current_time.tm_hour
        minute = (current_time.tm_min + 1) % 600  # Bir dakika sonraya ayarla
        kit.sendwhatmsg(PHONE_NUMBER, message, hour, minute)
        print(f"Mesaj WhatsApp'a başarıyla gönderildi: {message}")
    except Exception as e:
        print(f"WhatsApp mesaj gönderiminde hata: {e}")


def read_from_arduino():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            print("Arduino'dan veri bekleniyor...")
            while True:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8').strip()
                    print(f"Gelen Veri: {data}")

                    # Gelen veriyi işleme ve WhatsApp mesajı olarak gönderme
                    if "Current" in data and "Temperature" in data:
                        send_whatsapp_message(data)
    except serial.SerialException as e:
        print(f"Seri bağlantı hatası: {e}")
    except Exception as e:
        print(f"Genel bir hata oluştu: {e}")


if __name__ == "__main__":
    read_from_arduino()
