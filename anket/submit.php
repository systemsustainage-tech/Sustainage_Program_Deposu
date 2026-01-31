<?php
/**
 * Sustainage Anket Sistemi - Yanıt Kaydetme (MySQL)
 */
require_once 'config.php';

// Sadece POST isteklerine izin ver
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: index.php');
    exit;
}

// Form verilerini al ve temizle
$survey_id = isset($_POST['survey_id']) ? intval($_POST['survey_id']) : 0;
$token = isset($_POST['token']) ? cleanString($_POST['token']) : '';
$stakeholder_name = isset($_POST['stakeholder_name']) ? cleanString($_POST['stakeholder_name']) : '';
$stakeholder_email = isset($_POST['stakeholder_email']) ? cleanString($_POST['stakeholder_email']) : '';
$stakeholder_organization = isset($_POST['stakeholder_organization']) ? cleanString($_POST['stakeholder_organization']) : '';
$stakeholder_role = isset($_POST['stakeholder_role']) ? cleanString($_POST['stakeholder_role']) : '';

// Zorunlu alanları kontrol et
if (empty($survey_id) || empty($token) || empty($stakeholder_name) || empty($stakeholder_email)) {
    die('
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Hata - Sustainage</title>
        <link rel="stylesheet" href="css/style.css">
    </head>
    <body>
        <div class="container">
            <div class="error-box">
                <h1>❌ Eksik Bilgi</h1>
                <p>Lütfen tüm zorunlu alanları doldurun.</p>
                <a href="javascript:history.back()" class="btn">Geri Dön</a>
            </div>
        </div>
    </body>
    </html>
    ');
}

// Email formatı kontrolü
if (!filter_var($stakeholder_email, FILTER_VALIDATE_EMAIL)) {
    die('
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Hata - Sustainage</title>
        <link rel="stylesheet" href="css/style.css">
    </head>
    <body>
        <div class="container">
            <div class="error-box">
                <h1>❌ Geçersiz Email</h1>
                <p>Lütfen geçerli bir email adresi girin.</p>
                <a href="javascript:history.back()" class="btn">Geri Dön</a>
            </div>
        </div>
    </body>
    </html>
    ');
}

// Veritabanına bağlan
$db = getDatabase();

// Token'ı ve anketi doğrula
$stmt = $db->prepare('SELECT survey_id, status, deadline_date FROM surveys WHERE survey_id = ? AND unique_token = ?');
$stmt->execute([$survey_id, $token]);
$survey = $stmt->fetch();

if (!$survey) {
    die('
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Hata - Sustainage</title>
        <link rel="stylesheet" href="css/style.css">
    </head>
    <body>
        <div class="container">
            <div class="error-box">
                <h1>❌ Geçersiz Anket</h1>
                <p>Anket bulunamadı veya token geçersiz.</p>
                <a href="index.php" class="btn">Ana Sayfaya Dön</a>
            </div>
        </div>
    </body>
    </html>
    ');
}

// Anket durumu kontrolü
if ($survey['status'] !== 'active' || strtotime($survey['deadline_date']) < time()) {
    die('
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Hata - Sustainage</title>
        <link rel="stylesheet" href="css/style.css">
    </head>
    <body>
        <div class="container">
            <div class="error-box">
                <h1>❌ Anket Kapalı</h1>
                <p>Bu anket artık yanıt kabul etmemektedir.</p>
                <a href="index.php" class="btn">Ana Sayfaya Dön</a>
            </div>
        </div>
    </body>
    </html>
    ');
}

// IP adresi
$ip_address = getClientIp();
$user_agent = isset($_SERVER['HTTP_USER_AGENT']) ? substr($_SERVER['HTTP_USER_AGENT'], 0, 255) : '';

// Konuları al
$stmt = $db->prepare('SELECT topic_code, topic_name FROM survey_topics WHERE survey_id = ? ORDER BY display_order');
$stmt->execute([$survey_id]);
$topics = $stmt->fetchAll();

$inserted_count = 0;
$errors = [];

// Transaction başlat
$db->beginTransaction();

try {
    $submitted_date = date('Y-m-d H:i:s');
    
    // Her konu için yanıtları kaydet
    foreach ($topics as $topic) {
        $topic_code = $topic['topic_code'];
        $importance = isset($_POST["importance_$topic_code"]) ? intval($_POST["importance_$topic_code"]) : null;
        $impact = isset($_POST["impact_$topic_code"]) ? intval($_POST["impact_$topic_code"]) : null;
        $comment = isset($_POST["comment_$topic_code"]) ? cleanString($_POST["comment_$topic_code"]) : '';

        // Puanların geçerliliğini kontrol et
        if ($importance < 1 || $importance > 5 || $impact < 1 || $impact > 5) {
            $errors[] = "Geçersiz puan: {$topic['topic_name']}";
            continue;
        }

        // Yanıtı kaydet
        $stmt = $db->prepare('
            INSERT INTO survey_responses 
            (survey_id, stakeholder_name, stakeholder_email, stakeholder_organization, 
             stakeholder_role, topic_code, topic_name, importance_score, impact_score, comment, 
             submitted_date, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ');
        
        if ($stmt->execute([
            $survey_id,
            $stakeholder_name,
            $stakeholder_email,
            $stakeholder_organization,
            $stakeholder_role,
            $topic_code,
            $topic['topic_name'],
            $importance,
            $impact,
            $comment,
            $submitted_date,
            $ip_address,
            $user_agent
        ])) {
            $inserted_count++;
        } else {
            $errors[] = "Kayıt hatası: {$topic['topic_name']}";
        }
    }

    // Hata yoksa commit
    if (empty($errors) && $inserted_count > 0) {
        $db->commit();
        $success = true;
        
        // Log
        logMessage("Survey submitted: Survey ID=$survey_id, Stakeholder=$stakeholder_name ($stakeholder_email), Topics=$inserted_count", 'SUCCESS');
        
        // Yanıt sayısını güncelle
        $stmt = $db->prepare('
            UPDATE surveys 
            SET response_count = (
                SELECT COUNT(DISTINCT stakeholder_email) 
                FROM survey_responses 
                WHERE survey_id = ?
            )
            WHERE survey_id = ?
        ');
        $stmt->execute([$survey_id, $survey_id]);
        
    } else {
        $db->rollBack();
        $success = false;
        logMessage("Survey submission failed: Survey ID=$survey_id, Errors=" . implode(', ', $errors), 'ERROR');
    }

} catch (Exception $e) {
    $db->rollBack();
    $success = false;
    logMessage("Survey submission exception: " . $e->getMessage(), 'ERROR');
}

// Sonuç sayfası
if ($success):
?>
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teşekkürler - Sustainage</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <div class="thank-you-box">
            <div style="text-align: right; margin-bottom: 10px;">
                <a href="index.php" class="btn-back" style="text-decoration: none; display: inline-block;">
                    ← Ana Sayfaya Dön
                </a>
            </div>
            <img src="images/logo.png" alt="Sustainage" class="logo">
            <div class="success-icon">✅</div>
            <h1>Teşekkür Ederiz!</h1>
            <p class="success-message">
                Anket yanıtlarınız başarıyla kaydedildi.
            </p>
            <div class="stats-box">
                <div class="stat-item">
                    <span class="stat-number"><?php echo $inserted_count; ?></span>
                    <span class="stat-label">Değerlendirilen Konu</span>
                </div>
            </div>
            <p class="thank-you-text">
                Görüşleriniz bizim için çok değerli. Sürdürülebilirlik hedeflerimize 
                ulaşmamızda önemli bir katkı sağladınız.
            </p>
            <div class="action-buttons">
                <a href="<?php echo COMPANY_WEBSITE; ?>" class="btn btn-primary">
                    🌐 Web Sitemizi Ziyaret Edin
                </a>
                <a href="index.php" class="btn btn-secondary">
                    🏠 Ana Sayfaya Dön
                </a>
            </div>
        </div>
        
        <footer class="survey-footer">
            <p>&copy; 2025 Sustainage - Sürdürülebilirlik Yönetim Platformu</p>
        </footer>
    </div>
</body>
</html>
<?php else: ?>
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hata - Sustainage</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <div class="error-box">
            <h1>❌ Kayıt Hatası</h1>
            <p>Yanıtlarınız kaydedilirken bir hata oluştu.</p>
            <?php if (!empty($errors)): ?>
                <ul>
                    <?php foreach ($errors as $error): ?>
                        <li><?php echo htmlspecialchars($error); ?></li>
                    <?php endforeach; ?>
                </ul>
            <?php endif; ?>
            <p>Lütfen daha sonra tekrar deneyin veya bizimle iletişime geçin.</p>
            <a href="javascript:history.back()" class="btn">Geri Dön</a>
        </div>
    </div>
</body>
</html>
<?php endif; ?>

