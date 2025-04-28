from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from google.cloud import storage

# Google Cloud Storage'a bağlantı
storage_client = storage.Client.from_service_account_json("service_account.json")
bucket_name = "my_bucketpil"
bucket = storage_client.bucket(bucket_name)

# Verinin yükleneceği dosya yolu
file_path = "your_data.csv"

# Dosya değişikliği olaylarını izleyen sınıf
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(file_path):
            print(f"{file_path} dosyası değişti, veriler yükleniyor...")
            # Dosyayı yükleme
            blob = bucket.blob(file_path)
            blob.upload_from_filename(file_path)
            print(f"{file_path} başarıyla yüklendi!")

# Observer ve event handler
event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path='./', recursive=False)

# İzlemeyi başlat
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
