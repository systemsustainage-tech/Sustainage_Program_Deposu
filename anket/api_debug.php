<?php
/**
 * API Debug - Detayli log ve test
 * Sustainage'den gelen istekleri yakalar
 */
error_reporting(E_ALL);
ini_set('display_errors', 1);
ini_set('log_errors', 1);
ini_set('error_log', __DIR__ . '/api_debug.log');

require_once 'config.php';

// Log fonksiyonu
function debugLog($message) {
    $timestamp = date('Y-m-d H:i:s');
    $logFile = __DIR__ . '/api_debug.log';
    file_put_contents($logFile, "[$timestamp] $message\n", FILE_APPEND);
    echo "[$timestamp] $message<br>\n";
}

debugLog("=== API DEBUG START ===");
debugLog("Client IP: " . getClientIp());

// Headers log
debugLog("REQUEST_METHOD: " . ($_SERVER['REQUEST_METHOD'] ?? 'N/A'));
debugLog("HTTP_X_API_KEY: " . (isset($_SERVER['HTTP_X_API_KEY']) ? substr($_SERVER['HTTP_X_API_KEY'], 0, 40) . '...' : 'NOT SET'));
debugLog("CONTENT_TYPE: " . ($_SERVER['CONTENT_TYPE'] ?? 'N/A'));
debugLog("HTTP_USER_AGENT: " . ($_SERVER['HTTP_USER_AGENT'] ?? 'N/A'));

// GET parameters
if (!empty($_GET)) {
    debugLog("GET PARAMS: " . json_encode($_GET));
}

// Input log
$raw_input = file_get_contents('php://input');
debugLog("RAW INPUT LENGTH: " . strlen($raw_input));
if ($raw_input) {
    debugLog("RAW INPUT (first 1000 chars): " . substr($raw_input, 0, 1000));
    debugLog("RAW INPUT (last 200 chars): " . substr($raw_input, -200));
}

// JSON decode test
if ($raw_input) {
    $data = json_decode($raw_input, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        debugLog("JSON ERROR: " . json_last_error_msg());
        debugLog("JSON ERROR CODE: " . json_last_error());
    } else {
        debugLog("JSON DECODED SUCCESSFULLY");
        debugLog("DATA KEYS: " . implode(', ', array_keys($data)));
        if (isset($data['survey_name'])) {
            debugLog("Survey Name: " . $data['survey_name']);
        }
        if (isset($data['topics'])) {
            debugLog("Topics Count: " . count($data['topics']));
        }
    }
}

// Database test
try {
    $db = getDatabase();
    debugLog("DATABASE CONNECTION: SUCCESS");
    
    // Test query
    $stmt = $db->query("SELECT COUNT(*) as cnt FROM surveys");
    $result = $stmt->fetch();
    debugLog("SURVEYS COUNT: " . $result['cnt']);
    
    $stmt2 = $db->query("SELECT COUNT(*) as cnt FROM survey_topics");
    $result2 = $stmt2->fetch();
    debugLog("TOPICS COUNT: " . $result2['cnt']);
    
} catch (Exception $e) {
    debugLog("DATABASE ERROR: " . $e->getMessage());
}

// API Key validation test
if (isset($_SERVER['HTTP_X_API_KEY'])) {
    $provided_key = $_SERVER['HTTP_X_API_KEY'];
    $expected_key = ADMIN_API_KEY;
    
    if ($provided_key === $expected_key) {
        debugLog("API KEY VALIDATION: PASSED");
    } else {
        debugLog("API KEY VALIDATION: FAILED");
        debugLog("Provided (first 40): " . substr($provided_key, 0, 40) . "...");
        debugLog("Expected (first 40): " . substr($expected_key, 0, 40) . "...");
        debugLog("Provided Length: " . strlen($provided_key));
        debugLog("Expected Length: " . strlen($expected_key));
    }
}

debugLog("=== API DEBUG END ===");

?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>API Debug</title>
    <style>
        body { font-family: monospace; margin: 20px; }
        h1 { color: #2E7D32; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>API Debug Tamamlandi</h1>
    <p>Log dosyasi: <strong>api_debug.log</strong></p>
    <p>Bu sayfayi acin, sonra Sustainage'den anket olusturun.</p>
    <p>Ardindan <a href="api_debug.log" target="_blank">api_debug.log</a> dosyasini kontrol edin.</p>
</body>
</html>

