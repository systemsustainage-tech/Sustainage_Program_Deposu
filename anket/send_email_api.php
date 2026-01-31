<?php
/**
 * Email Gönderme API
 * Hosting'den PHP mail() ile email gönderir
 */
require_once 'config.php';

header('Content-Type: application/json; charset=UTF-8');

// API Key check
$api_key = isset($_SERVER['HTTP_X_API_KEY']) ? $_SERVER['HTTP_X_API_KEY'] : '';
if (!validateApiKey($api_key)) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

// Input
$raw_input = file_get_contents('php://input');
if (isset($_GET['json_data'])) {
    $raw_input = urldecode($_GET['json_data']);
}

$data = json_decode($raw_input, true);

if (!$data || !isset($data['to']) || !isset($data['survey_url'])) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Missing required fields']);
    exit;
}

$to = $data['to'];
$survey_name = isset($data['survey_name']) ? $data['survey_name'] : 'Materyalite Anketi';
$survey_url = $data['survey_url'];
$stakeholder_name = isset($data['stakeholder_name']) ? $data['stakeholder_name'] : '';

// Email content
$subject = $survey_name . ' - Görüşleriniz Bizim İçin Önemli';

$message = "<!DOCTYPE html>
<html>
<head>
    <meta charset='UTF-8'>
    <style>
        body { font-family: Segoe UI, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2E7D32; color: white; padding: 20px; text-align: center; }
        .content { background: #f9f9f9; padding: 30px; }
        .button { background: #2E7D32; color: white; padding: 15px 30px; text-decoration: none; 
                  display: inline-block; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h1>Sustainage</h1>
            <p>Sürdürülebilirlik Yönetim Platformu</p>
        </div>
        <div class='content'>";

if ($stakeholder_name) {
    $message .= "<p>Sayın <strong>$stakeholder_name</strong>,</p>";
} else {
    $message .= "<p>Sayın Paydaşımız,</p>";
}

$message .= "
            <p>Sürdürülebilirlik stratejimizi geliştirmek için görüşlerinize ihtiyacımız var.</p>
            
            <p>Lütfen aşağıdaki butona tıklayarak anketi doldurun:</p>
            
            <div style='text-align: center;'>
                <a href='$survey_url' class='button'>Anketi Doldur</a>
            </div>
            
            <p>Anket yaklaşık 10 dakika sürmektedir.</p>
            
            <p>Görüşleriniz bizim için çok değerli.</p>
            
            <p>Teşekkür ederiz,<br>
            <strong>Sustainage Ekibi</strong></p>
        </div>
        <div class='footer'>
            <p>© 2025 Sustainage - Tüm hakları saklıdır</p>
            <p>Bu email otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>";

// Headers
$headers = "MIME-Version: 1.0" . "\r\n";
$headers .= "Content-type:text/html;charset=UTF-8" . "\r\n";
$headers .= "From: Sustainage <" . COMPANY_EMAIL . ">" . "\r\n";

// Send email
$sent = mail($to, $subject, $message, $headers);

if ($sent) {
    echo json_encode(['success' => true, 'message' => 'Email sent']);
    logMessage("Email sent to: $to", 'INFO');
} else {
    echo json_encode(['success' => false, 'error' => 'Failed to send email']);
    logMessage("Failed to send email to: $to", 'ERROR');
}
?>

