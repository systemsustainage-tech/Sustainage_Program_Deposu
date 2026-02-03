import threading
import time
import requests
import argparse
import statistics
from concurrent.futures import ThreadPoolExecutor

# Yapılandırma
DEFAULT_TARGET_URL = "http://72.62.150.207" # Uzak sunucu IP'si
DEFAULT_CONCURRENT_USERS = 50
DEFAULT_DURATION_SECONDS = 30

class LoadTester:
    def __init__(self, target_url, concurrent_users, duration):
        self.target_url = target_url
        self.concurrent_users = concurrent_users
        self.duration = duration
        self.results = []
        self.errors = 0
        self.lock = threading.Lock()
        self.is_running = True

    def simulate_user(self, user_id):
        """Tek bir kullanıcının davranışını simüle eder."""
        session = requests.Session()
        start_time = time.time()
        
        while self.is_running and (time.time() - start_time < self.duration):
            try:
                req_start = time.time()
                # Ana sayfaya istek at
                response = session.get(self.target_url, timeout=5)
                req_end = time.time()
                
                latency = (req_end - req_start) * 1000 # ms cinsinden
                
                with self.lock:
                    if response.status_code < 400:
                        self.results.append(latency)
                    else:
                        self.errors += 1
                        print(f"[User {user_id}] Hata: Durum Kodu {response.status_code}")
                
                # Kullanıcılar arasında rastgele bekleme (think time)
                time.sleep(0.5) 
                
            except requests.RequestException as e:
                with self.lock:
                    self.errors += 1
                    print(f"[User {user_id}] Bağlantı Hatası: {e}")
                time.sleep(1)

    def run(self):
        print(f"--- Yük Testi Başlatılıyor ---")
        print(f"Hedef: {self.target_url}")
        print(f"Eşzamanlı Kullanıcı: {self.concurrent_users}")
        print(f"Süre: {self.duration} saniye")
        print("------------------------------")

        with ThreadPoolExecutor(max_workers=self.concurrent_users) as executor:
            futures = [executor.submit(self.simulate_user, i) for i in range(self.concurrent_users)]
            
            # Belirlenen süre kadar bekle (Threadler süre dolunca duracak, loop kontrolü var)
            time.sleep(self.duration)
            self.is_running = False
            
            # Threadlerin tamamlanmasını bekle
            for future in futures:
                future.result()

        self.print_report()

    def print_report(self):
        print("\n--- Test Sonuçları ---")
        total_requests = len(self.results) + self.errors
        print(f"Toplam İstek: {total_requests}")
        print(f"Başarılı İstek: {len(self.results)}")
        print(f"Hatalı İstek: {self.errors}")
        
        if self.results:
            avg_latency = statistics.mean(self.results)
            max_latency = max(self.results)
            min_latency = min(self.results)
            p95_latency = statistics.quantiles(self.results, n=20)[18] # %95 persentil
            
            print(f"Ortalama Gecikme: {avg_latency:.2f} ms")
            print(f"Min Gecikme: {min_latency:.2f} ms")
            print(f"Max Gecikme: {max_latency:.2f} ms")
            print(f"95. Persentil: {p95_latency:.2f} ms")
            
            rps = len(self.results) / self.duration
            print(f"Saniye Başına İstek (RPS): {rps:.2f}")
        else:
            print("Hiç başarılı istek yapılamadı.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sustainage Yük Testi Simülasyonu")
    parser.add_argument("--url", default=DEFAULT_TARGET_URL, help="Test edilecek hedef URL")
    parser.add_argument("--users", type=int, default=DEFAULT_CONCURRENT_USERS, help="Eşzamanlı kullanıcı sayısı")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION_SECONDS, help="Test süresi (saniye)")
    
    args = parser.parse_args()
    
    tester = LoadTester(args.url, args.users, args.duration)
    tester.run()
