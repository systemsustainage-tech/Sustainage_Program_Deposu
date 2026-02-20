import threading
import time
import requests
import argparse
import statistics
import random
from concurrent.futures import ThreadPoolExecutor

# Yapılandırma
DEFAULT_TARGET_URL = "http://72.62.150.207" # Uzak sunucu IP'si
DEFAULT_CONCURRENT_USERS = 50
DEFAULT_DURATION_SECONDS = 30

class LoadTester:
    def __init__(self, target_url, concurrent_users, duration):
        self.target_url = target_url.rstrip('/')
        self.concurrent_users = concurrent_users
        self.duration = duration
        self.results = []
        self.errors = 0
        self.error_counts = {}
        self.lock = threading.Lock()
        self.is_running = True
        
        # Test edilecek endpointler ve ağırlıkları
        self.endpoints = [
            ('/', 5),             # Ana sayfa (Çok sık)
            ('/login', 2),        # Login sayfası
            ('/register', 1),     # Kayıt sayfası
            ('/data', 3),         # Veri sayfası (Giriş gerektirir, 302 dönebilir)
            ('/reports', 2),      # Raporlar
        ]

    def get_random_endpoint(self):
        total_weight = sum(w for _, w in self.endpoints)
        r = random.uniform(0, total_weight)
        upto = 0
        for endpoint, weight in self.endpoints:
            if upto + weight >= r:
                return endpoint
            upto += weight
        return '/'

    def simulate_user(self, user_id):
        """Tek bir kullanıcının davranışını simüle eder."""
        try:
            session = requests.Session()
            start_time = time.time()
            
            # SSL uyarılarını kapat
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            while self.is_running and (time.time() - start_time < self.duration):
                try:
                    endpoint = self.get_random_endpoint()
                    url = f"{self.target_url}{endpoint}"
                    
                    req_start = time.time()
                    response = session.get(url, timeout=5, verify=False)
                    req_end = time.time()
                    
                    latency = (req_end - req_start) * 1000 # ms cinsinden
                    
                    with self.lock:
                        if response.status_code < 500: # 4xx hataları sunucu hatası sayılmaz (auth vs)
                            self.results.append(latency)
                        else:
                            self.errors += 1
                            code = response.status_code
                            self.error_counts[code] = self.error_counts.get(code, 0) + 1
                            if self.errors <= 10:
                                print(f"[User {user_id}] Sunucu Hatası ({endpoint}): {response.status_code}")
                    
                    # Kullanıcılar arasında rastgele bekleme (think time)
                    time.sleep(random.uniform(0.5, 2.0))
                    
                except requests.RequestException as e:
                    with self.lock:
                        self.errors += 1
                        error_type = type(e).__name__
                        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
                        # print(f"[User {user_id}] Bağlantı Hatası: {e}")
                    time.sleep(1)
        except Exception as e:
            print(f"[User {user_id}] Critical Error: {e}")

    def run(self):
        print(f"--- Yük Testi Başlatılıyor ---")
        print(f"Hedef: {self.target_url}")
        print(f"Eşzamanlı Kullanıcı: {self.concurrent_users}")
        print(f"Süre: {self.duration} saniye")
        print("------------------------------")

        executor = ThreadPoolExecutor(max_workers=self.concurrent_users)
        try:
            futures = [executor.submit(self.simulate_user, i) for i in range(self.concurrent_users)]
            
            # İlerleme çubuğu
            start_ts = time.time()
            while time.time() - start_ts < self.duration:
                time.sleep(1)
                elapsed = int(time.time() - start_ts)
                with self.lock:
                    count = len(self.results)
                    err = self.errors
                print(f"Süre: {elapsed}/{self.duration}s | İstek: {count} | Hata: {err}", flush=True)
            
            print("\nSüre doldu, durduruluyor...", flush=True)
            self.is_running = False
            
            print("Threadler kapatılıyor (beklenmeyecek)...", flush=True)
            executor.shutdown(wait=False)
            print("Threadler kapatma komutu verildi.", flush=True)
            
        except Exception as e:
             print(f"Executor error: {e}")
        finally:
            print("Rapor oluşturuluyor...", flush=True)
            self.print_report()

    def print_report(self):
        with open('load_test_results.txt', 'w', encoding='utf-8') as f:
            f.write("\n--- Test Sonuçları ---\n")
            total_requests = len(self.results) + self.errors
            f.write(f"Toplam İstek: {total_requests}\n")
            f.write(f"Başarılı İstek: {len(self.results)}\n")
            f.write(f"Hatalı İstek: {self.errors}\n")
            if self.errors > 0:
                f.write(f"Hata Dağılımı: {self.error_counts}\n")
            
            if self.results:
                avg_latency = statistics.mean(self.results)
                max_latency = max(self.results)
                min_latency = min(self.results)
                try:
                    p95_latency = statistics.quantiles(self.results, n=20)[18]
                except:
                    p95_latency = max_latency # Yeterli veri yoksa
                
                f.write(f"Ortalama Gecikme: {avg_latency:.2f} ms\n")
                f.write(f"Min Gecikme: {min_latency:.2f} ms\n")
                f.write(f"Max Gecikme: {max_latency:.2f} ms\n")
                f.write(f"95. Persentil: {p95_latency:.2f} ms\n")
                
                rps = len(self.results) / self.duration
                f.write(f"Saniye Başına İstek (RPS): {rps:.2f}\n")
                
                # Öneriler
                f.write("\n--- Öneriler ---\n")
                if avg_latency > 1000:
                    f.write("! Ortalama gecikme yüksek (>1s). Worker sayısını artırın veya DB indekslerini kontrol edin.\n")
                if self.errors > 0:
                    f.write("! Hatalar alındı. Logları kontrol edin (500/502/504).\n")
                if rps > 100:
                    f.write("* Sistem iyi yük kaldırıyor.\n")
                    
            else:
                f.write("Hiç başarılı istek yapılamadı.\n")
        
        # Also print to stdout for redundancy
        with open('load_test_results.txt', 'r', encoding='utf-8') as f:
            print(f.read())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sustainage Yük Testi Simülasyonu")
    parser.add_argument("--url", default=DEFAULT_TARGET_URL, help="Test edilecek hedef URL")
    parser.add_argument("--users", type=int, default=DEFAULT_CONCURRENT_USERS, help="Eşzamanlı kullanıcı sayısı")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION_SECONDS, help="Test süresi (saniye)")
    
    args = parser.parse_args()
    
    tester = LoadTester(args.url, args.users, args.duration)
    tester.run()
