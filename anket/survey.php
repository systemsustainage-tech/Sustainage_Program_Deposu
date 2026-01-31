<?php
/**
 * Sustainage Anket Sistemi - Anket Formu (MySQL)
 */
require_once 'config.php';

// Token'ı al
$token = isset($_GET['token']) ? cleanString($_GET['token']) : '';

if (empty($token)) {
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
                <h1>❌ Geçersiz Anket Linki</h1>
                <p>Lütfen email\'inizdeki linki kullanın.</p>
                <a href="index.php" class="btn">Ana Sayfaya Dön</a>
            </div>
        </div>
    </body>
    </html>
    ');
}

// Veritabanına bağlan
$db = getDatabase();

// Anketi bul
$stmt = $db->prepare('SELECT * FROM surveys WHERE unique_token = ?');
$stmt->execute([$token]);
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
                <h1>❌ Anket Bulunamadı</h1>
                <p>Bu anket mevcut değil veya süresi dolmuş olabilir.</p>
                <a href="index.php" class="btn">Ana Sayfaya Dön</a>
            </div>
        </div>
    </body>
    </html>
    ');
}

// Anket durumu kontrolü
if ($survey['status'] !== 'active') {
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
                <h1>⚠️ Anket Kapalı</h1>
                <p>Bu anket artık yanıt kabul etmemektedir.</p>
                <a href="index.php" class="btn">Ana Sayfaya Dön</a>
            </div>
        </div>
    </body>
    </html>
    ');
}

// Son tarih kontrolü
if (strtotime($survey['deadline_date']) < time()) {
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
                <h1>⏰ Anket Süresi Doldu</h1>
                <p>Bu anketin son yanıt tarihi geçmiştir.</p>
                <p>Son tarih: ' . date('d.m.Y', strtotime($survey['deadline_date'])) . '</p>
                <a href="index.php" class="btn">Ana Sayfaya Dön</a>
            </div>
        </div>
    </body>
    </html>
    ');
}

// Konuları getir
$stmt = $db->prepare('SELECT * FROM survey_topics WHERE survey_id = ? ORDER BY display_order');
$stmt->execute([$survey['survey_id']]);
$topics = $stmt->fetchAll();

// Konular yoksa hata
if (empty($topics)) {
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
                <h1>⚠️ Anket İçeriği Bulunamadı</h1>
                <p>Bu ankete henüz konu eklenmemiş.</p>
                <a href="index.php" class="btn">Ana Sayfaya Dön</a>
            </div>
        </div>
    </body>
    </html>
    ');
}

logMessage("Survey viewed: {$survey['survey_name']} (Token: $token)", 'INFO');
?>
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($survey['survey_name'], ENT_QUOTES, 'UTF-8'); ?> - Sustainage</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="survey-header">
            <div style="text-align: right; margin-bottom: 15px;">
                <a href="index.php" class="btn-back" style="display: inline-block; text-decoration: none; color: white; background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px;">
                    ← Ana Sayfaya Dön
                </a>
            </div>
            
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="images/logo.webp" alt="Sustainage" style="max-width: 150px; height: auto; background: white; padding: 10px; border-radius: 8px; margin: 0 auto; display: inline-block;">
            </div>
            
            <h1><?php echo $survey['survey_name']; ?></h1>
            <p class="company"><?php echo $survey['company_name']; ?></p>
            <p class="deadline">
                <strong>Son Yanıt Tarihi:</strong> 
                <?php echo date('d.m.Y', strtotime($survey['deadline_date'])); ?>
            </p>
            <?php if (!empty($survey['description'])): ?>
                <p class="description"><?php echo nl2br($survey['description']); ?></p>
            <?php endif; ?>
        </header>

        <!-- Form -->
        <form id="surveyForm" method="POST" action="submit.php">
            <input type="hidden" name="survey_id" value="<?php echo $survey['survey_id']; ?>">
            <input type="hidden" name="token" value="<?php echo $token; ?>">

            <!-- Paydaş Bilgileri -->
            <section class="stakeholder-info">
                <h2>📋 Bilgileriniz</h2>
                <div class="form-group">
                    <label for="stakeholder_name">Adınız Soyadınız <span class="required">*</span></label>
                    <input type="text" 
                           id="stakeholder_name" 
                           name="stakeholder_name" 
                           required 
                           placeholder="Örn: Ahmet Yılmaz">
                </div>
                <div class="form-group">
                    <label for="stakeholder_email">E-posta Adresiniz <span class="required">*</span></label>
                    <input type="email" 
                           id="stakeholder_email" 
                           name="stakeholder_email" 
                           required 
                           placeholder="Örn: ahmet@example.com">
                </div>
                <div class="form-group">
                    <label for="stakeholder_organization">Kuruluş/Şirket (Opsiyonel)</label>
                    <input type="text" 
                           id="stakeholder_organization" 
                           name="stakeholder_organization" 
                           placeholder="Örn: ABC Şirketi">
                </div>
                <div class="form-group">
                    <label for="stakeholder_role">Pozisyon/Görev (Opsiyonel)</label>
                    <input type="text" 
                           id="stakeholder_role" 
                           name="stakeholder_role" 
                           placeholder="Örn: Sürdürülebilirlik Müdürü">
                </div>
            </section>

            <!-- Konular -->
            <section class="survey-questions">
                <h2>🌱 Sürdürülebilirlik Konularının Değerlendirmesi</h2>
                <div class="instruction-box">
                    <p>
                        <strong>Değerlendirme Kriterleri:</strong>
                    </p>
                    <p>
                        Lütfen her sürdürülebilirlik konusu için aşağıdaki puanlama sistemini kullanarak değerlendirin:
                    </p>
                    <div class="rating-legend">
                        <div class="rating-item">
                            <span class="rating-number">1</span>
                            <span class="rating-label">Çok Düşük</span>
                        </div>
                        <div class="rating-item">
                            <span class="rating-number">2</span>
                            <span class="rating-label">Düşük</span>
                        </div>
                        <div class="rating-item">
                            <span class="rating-number">3</span>
                            <span class="rating-label">Orta</span>
                        </div>
                        <div class="rating-item">
                            <span class="rating-number">4</span>
                            <span class="rating-label">Yüksek</span>
                        </div>
                        <div class="rating-item">
                            <span class="rating-number">5</span>
                            <span class="rating-label">Çok Yüksek</span>
                        </div>
                    </div>
                    <p>
                        <strong>Önem Derecesi:</strong> Bu konu sizin için ne kadar önemli?<br>
                        <strong>Etki Derecesi:</strong> Bu konunun şirket üzerindeki etkisi ne kadar büyük?
                    </p>
                </div>

                <div class="progress-info">
                    <p>Toplam Konu: <strong><?php echo count($topics); ?></strong></p>
                    <div class="progress-bar">
                        <div id="progressFill" class="progress-fill" style="width: 0%"></div>
                    </div>
                    <p id="progressText">Tamamlanan: 0/<?php echo count($topics); ?></p>
                </div>

                <?php foreach ($topics as $index => $topic): ?>
                <div class="topic-card" data-topic-index="<?php echo $index; ?>">
                    <div class="topic-header">
                        <span class="topic-number"><?php echo $index + 1; ?>/<?php echo count($topics); ?></span>
                        <h3><?php echo $topic['topic_name']; ?></h3>
                    </div>
                    
                    <?php if (!empty($topic['topic_category'])): ?>
                        <p class="category">
                            <strong>Kategori:</strong> <?php echo $topic['topic_category']; ?>
                        </p>
                    <?php endif; ?>

                    <?php if (!empty($topic['description'])): ?>
                        <p class="topic-description"><?php echo $topic['description']; ?></p>
                    <?php endif; ?>

                    <!-- Önem Derecesi -->
                    <div class="rating-group">
                        <label class="rating-label-main">
                            Önem Derecesi <span class="required">*</span>
                        </label>
                        <div class="rating-buttons">
                            <?php for ($i = 1; $i <= 5; $i++): ?>
                                <label class="radio-label">
                                    <input type="radio" 
                                           name="importance_<?php echo $topic['topic_code']; ?>" 
                                           value="<?php echo $i; ?>" 
                                           class="importance-input"
                                           data-topic="<?php echo $topic['topic_code']; ?>"
                                           required>
                                    <span class="radio-button"><?php echo $i; ?></span>
                                </label>
                            <?php endfor; ?>
                        </div>
                    </div>

                    <!-- Etki Derecesi -->
                    <div class="rating-group">
                        <label class="rating-label-main">
                            Etki Derecesi <span class="required">*</span>
                        </label>
                        <div class="rating-buttons">
                            <?php for ($i = 1; $i <= 5; $i++): ?>
                                <label class="radio-label">
                                    <input type="radio" 
                                           name="impact_<?php echo $topic['topic_code']; ?>" 
                                           value="<?php echo $i; ?>" 
                                           class="impact-input"
                                           data-topic="<?php echo $topic['topic_code']; ?>"
                                           required>
                                    <span class="radio-button"><?php echo $i; ?></span>
                                </label>
                            <?php endfor; ?>
                        </div>
                    </div>

                    <!-- Yorum -->
                    <div class="form-group">
                        <label for="comment_<?php echo $topic['topic_code']; ?>">
                            Yorumunuz (Opsiyonel)
                        </label>
                        <textarea id="comment_<?php echo $topic['topic_code']; ?>"
                                  name="comment_<?php echo $topic['topic_code']; ?>" 
                                  rows="3" 
                                  placeholder="İsteğe bağlı görüş ve önerileriniz..."></textarea>
                    </div>
                </div>
                <?php endforeach; ?>

                <!-- Gönder Butonu -->
                <div class="submit-section">
                    <p class="submit-note">
                        * Form gönderildikten sonra değişiklik yapılamaz. 
                        Lütfen tüm alanları kontrol edin.
                    </p>
                    <button type="submit" class="btn-submit" id="submitBtn">
                        ✅ Anketi Gönder
                    </button>
                </div>
            </section>
        </form>

        <!-- Footer -->
        <footer class="survey-footer">
            <p>&copy; 2025 Sustainage - Sürdürülebilirlik Yönetim Platformu</p>
            <p>
                <a href="<?php echo COMPANY_WEBSITE; ?>"><?php echo COMPANY_WEBSITE; ?></a> | 
                <a href="mailto:<?php echo COMPANY_EMAIL; ?>"><?php echo COMPANY_EMAIL; ?></a>
            </p>
        </footer>
    </div>

    <script src="js/survey.js"></script>
</body>
</html>

