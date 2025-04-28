import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from google.cloud import storage

def load_battery_data_from_file(file_path):
    """JSON dosyasından pil verilerini yükler."""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"JSON dosyasını okurken hata oluştu: {e}")
        return None

def train_battery_model():
    """Örnek verilere dayalı olarak bir Random Forest modeli eğitir."""
    # Örnek eğitim verileri (şarj döngüleri, sıcaklık) ve hedefler (tahmini pil ömrü)
    X = np.array([
        [-4, 20.75],
        [25, 100],
        [-15, 77],
        [25, 75],
        [0, 60]
    ])
    y = np.array([90, 80, 70, 60, 50, 40, 30])  # Tahmini pil ömrü (yüzde olarak)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def predict_battery_life(model, charge_cycles, temperature):
    """Eğitilmiş model kullanarak pil ömrünü tahmin eder."""
    input_data = np.array([[charge_cycles, temperature]])
    predicted_life = model.predict(input_data)
    return max(0, predicted_life[0])  # Pil ömrü negatif olamaz

def analyze_battery_data(data, model):
    """Pil verilerini analiz eder ve pil ömrüyle ilgili bilgi verir."""
    if not data:
        print("Analiz için geçerli veri yok.")
        return

    # Örnek veriler: {"battery_percentage": 85, "temperature": 32, "charge_cycles": 300}
    battery_percentage = data.get("battery_percentage", None)
    temperature = data.get("temperature", None)
    charge_cycles = data.get("charge_cycles", None)

    print("\n--- Pil Durumu Analizi ---")

    if battery_percentage is not None:
        print(f"Mevcut Pil Yüzdesi: {battery_percentage}%")
        if battery_percentage < 20:
            print("Uyarı: Pil seviyesi çok düşük. Şarj etmeniz önerilir.")
        elif battery_percentage > 80:
            print("Pil seviyesi yüksek, bu iyi bir durum.")

    if temperature is not None:
        print(f"Pil Sıcaklığı: {temperature}°C")
        if temperature > 45:
            print("Uyarı: Pil sıcaklığı çok yüksek! Soğutulması gerekebilir.")
        elif temperature < 0:
            print("Uyarı: Pil sıcaklığı çok düşük! Etkili çalışmayabilir.")

    if charge_cycles is not None:
        print(f"Şarj Döngü Sayısı: {charge_cycles}")
        if charge_cycles > 500:
            print("Uyarı: Pil döngü ömrü sona yaklaşıyor. Değişim zamanı olabilir.")

        # Pil ömrü tahmini yap
        predicted_life = predict_battery_life(model, charge_cycles, temperature)
        print(f"Tahmini Kalan Pil Ömrü: {predicted_life:.2f}%")

    print("\nAnaliz tamamlandı.")

# Google Cloud Storage kimlik bilgilerini ayarlayın
service_account_json = {
    "type": "service_account",
    "project_id": "proje-447622",
    "private_key_id": "f241e9a6be38098daeb2c9a73c71f143024b39fd",
    "private_key": "-----BEGIN PRIVATE KEY-----\nM IIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCVo28F6L8B+mxZ\nkp7xAFIllbZ2vdibHqM/QV0b9PMGVgGGbKtrsIEmH1SVLQa1tRJovULvLjOLMuJL\nldqV7P55+t+hGKANzs5LW/X94nH+2ApUFqn9KXQ23zmedifpVyD12hJNYDF8PMjl\nB3RrKG7+Upjy4rKjT4detEGnl07NVJEWSXjS1SJIREf4a7hvLknobRRk3DC6PzGb\nUWZz9V1R+HLqh/GyP8DlfBA7HrpjkAI0dDFFntT1A+rZHfZ3gF1KnA9CVipa7UIj\nVyZvAt8I9ts4/SrnRIGN/2Pu5azC0dNixNYs8J5Saw96gxL+eeY7GKTZPlgHe3EG\niVXf2o+/AgMBAAECggEAQhrpORsRBraylv+G58DUiXYSHXLQ9fYa+B7QG0Gi+vGT\nyubG89QNueGtZBl4FV3gvBSgNTmb26qm/e09m24PHaQOlwRh8LejuvbtPTOEWKjo\nJy27+vMNPBBxS+e2ygaLsRCddUFBmzjfJw6cB5rdLc0fdG1hrXO8wcGwH3FghqRg\nIk5jSZsJhE6tDKaYDD0V0zmW0HtxAIS2x/aMh9MYmBEebgnD5y02MyjcJnrDKkF7\nHdvQvARSki1SWaQix3Bxu5gq5ZzANWwhs+t2K0/RrZOMUPEc8YGorLPhh6jMlrZN\n8JoYryfoC5VcD1lyFOQSNvQTSF3mM6fha5xCbdEkQQKBgQDO2aMrq7og/kbl3MM8\n1y92w8tvMxPqB5Xhq1o84+IhCoKZEsL/aANzd4a9mgmHFjOUdTA67g5VbvWMf+k0\nOxC3XOYeuKm+7wI1YJvXXUDX0dIV6qq4yLKWm8xiG1Bj5baISPYxZd/QkZtJXB9s\nnsRF/AIwsuvgZ8Eb4uMX2F5bPQKBgQC5MbLFwr5Pmf4UICc0DYQlsPr4FLBspik2\nXBOPKBgKvBeAA2mtdCxWw30THNATNq8S2tzWy2NhQtsvY0OlM7T198800cInxutX\nLSV3wSJ4azstiKH5RrDPlcaC0iXVxxTixbMdhBJd9OXGyNGQUYHsr+340IG7ltT0\nsVuPgDP2qwKBgC6Gq3oGLV6Ac0f+qPeFW0q2bYq8jW0leaQB29E4XMObzpZJrwyt\nw6D0MJ1zCVOWPdHVrhyDMTwsMhUBLF4wLulffu9ID/4/WlrRORxvAEfLDRsa5n2b\nvve7YXRrumBN6gmrh5zC0l3icnBExVi0OWeYcJGtnPqju77fAL97TnXtAoGAZG/u\nq9BlVFiI8rNJb7KQ47wrMFZQJGytVzzyoqY0+8Vs3VF8g8TIszmMYMw0kOcMZiZq\ntNdTi5EtvHKSYks7rlZ6ewPzz4zTX9EtS9hj8Hj/fD9o0P+krsBlC9gbCujQi/h6\nntxc9bX21CtfdGywEQSNBG9YnLs9vYNey+HUzMcCgYBdqfsptnZvipYVoWUdY5LN\n2gmEFfkEapamthZlnibMJ6JW58dhyXygZ3Hzhyyixe8lyHcWDRxdWfs4an5keauY\nWgQX8POIDHLqtedUNKHQPO5d1UU/Xx7LGLnUVp6ACHp8PVdmhipP9To3OeJql4z+\n+iPnDXUeTP2Q64MKCDywnw==\n-----END PRIVATE KEY-----\n",
    "client_email": "proje-417@proje-447622.iam.gserviceaccount.com",
    "client_id": "106699581007540081157",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/proje-417%40proje-447622.iam.gserviceaccount.com"
}

# Örnek bir JSON dosyasından veriyi okuma
file_path = "battery_data.json"  # Yerel dosyanın yolu
battery_data = load_battery_data_from_file(file_path)

# Modeli eğit
battery_model = train_battery_model()

# Verileri analiz et
analyze_battery_data(battery_data, battery_model)
