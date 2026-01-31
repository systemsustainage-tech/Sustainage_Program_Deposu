<?php
/**
 * Sustainage Anket Sistemi - Ana Sayfa
 */
require_once 'config.php';
?>
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sustainage Anket Sistemi</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <header class="main-header">
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="images/logo.webp" alt="Sustainage" style="max-width: 200px; height: auto; background: white; padding: 15px; border-radius: 10px; display: inline-block;">
            </div>
            <h1>Sustainage Anket Sistemi</h1>
            <p class="tagline">Sürdürülebilirlik Yönetim Platformu</p>
        </header>

        <main class="main-content">
            <div class="info-box">
                <h2>🌱 Hoş Geldiniz</h2>
                <p>
                    Bu sistem, Sustainage Sürdürülebilirlik Yönetim Platformu'nun 
                    paydaş anket modülüdür.
                </p>
                <p>
                    Eğer size bir anket linki gönderildiyse, lütfen email'inizdeki 
                    linke tıklayarak ankete ulaşın.
                </p>
            </div>

            <div class="info-box">
                <h2>📧 Anket Nasıl Doldurulur?</h2>
                <ol>
                    <li>Email'inizdeki anket linkine tıklayın</li>
                    <li>Bilgilerinizi girin</li>
                    <li>Her konuyu değerlendirin (1-5 puan)</li>
                    <li>Gönder butonuna basın</li>
                </ol>
            </div>

            <div class="info-box">
                <h2>🔐 Güvenlik</h2>
                <p>
                    Tüm anketler SSL şifreli bağlantı ile korunmaktadır. 
                    Verileriniz güvende tutulmaktadır.
                </p>
            </div>

            <div class="info-box">
                <h2>❓ Yardım</h2>
                <p>
                    Sorularınız için: <a href="mailto:<?php echo COMPANY_EMAIL; ?>"><?php echo COMPANY_EMAIL; ?></a>
                </p>
                <p>
                    Web sitesi: <a href="<?php echo COMPANY_WEBSITE; ?>"><?php echo COMPANY_WEBSITE; ?></a>
                </p>
            </div>
        </main>

        <footer class="main-footer">
            <p>&copy; 2025 Sustainage - Sürdürülebilirlik Yönetim Platformu</p>
            <p>Tüm hakları saklıdır.</p>
        </footer>
    </div>
</body>
</html>

