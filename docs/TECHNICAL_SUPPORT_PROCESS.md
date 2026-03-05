
# Sustainage - Teknik Destek ve Bakım Süreci

## 1. Destek Kanalları
Müşterilerimiz aşağıdaki kanallardan destek talebinde bulunabilirler:
- **E-posta**: support@sustainage.com (7/24 Kayıt)
- **Portal**: https://support.sustainage.com (Bilet Sistemi)
- **Telefon**: +90 (212) 555 00 00 (Hafta içi 09:00 - 18:00)

## 2. Hizmet Seviyesi Anlaşması (SLA)

| Öncelik Seviyesi | Tanım | İlk Yanıt Süresi | Çözüm Hedefi |
|---|---|---|---|
| **P1 - Kritik** | Sistem tamamen erişilemez, veri kaybı riski var. | 1 Saat | 4 Saat |
| **P2 - Yüksek** | Ana modüllerden biri çalışmıyor (örn. Raporlama), iş süreci aksıyor. | 4 Saat | 24 Saat |
| **P3 - Normal** | Sistemsel hata var ancak iş akışı devam edebiliyor. | 1 İş Günü | 3 İş Günü |
| **P4 - Düşük** | Kozmetik hatalar, bilgi talepleri, yeni özellik istekleri. | 2 İş Günü | Bir sonraki sürüm |

## 3. Destek Süreci Akışı

### Adım 1: Talep Oluşturma
Müşteri, hatanın ekran görüntüsü ve yeniden oluşturma adımları ile birlikte talep açar.

### Adım 2: Sınıflandırma ve Atama
L1 Destek ekibi talebi inceler, öncelik seviyesini belirler ve ilgili teknik ekibe (L2/L3) atar.

### Adım 3: Müdahale ve Çözüm
- **L1**: Kullanıcı hatası veya konfigürasyon sorunlarını çözer.
- **L2**: Kod hatası şüphesi varsa logları inceler, geçici çözüm üretir.
- **L3**: Yazılım geliştirme ekibi, kod değişikliği gerektiren bugfix'leri uygular.

### Adım 4: Doğrulama ve Kapanış
Çözüm müşteriye iletilir ve onayı alındıktan sonra talep kapatılır.

## 4. Kötüye Kullanım ve Güvenlik Olayları
- Lisans ihlali veya saldırı tespiti durumunda (Rate Limit aşımı, şüpheli IP), sistem otomatik olarak "Security Alert" oluşturur.
- Güvenlik ekibi 1 saat içinde müdahale ederek ilgili IP/Hesabı askıya alır ve müşteriyi bilgilendirir.

## 5. Güncelleme ve Bakım
- Planlı bakım çalışmaları en az 48 saat önceden müşterilere duyurulur.
- Kritik güvenlik yamaları (Hotfix) mesai saatleri dışında ve kesintisiz (Rolling Update) uygulanır.
