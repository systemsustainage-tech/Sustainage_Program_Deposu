<?php
/**
 * API Debug - Çok Detaylı Versiyon
 * Her şeyi loglar
 */
error_reporting(E_ALL);
ini_set('display_errors', 1);
ini_set('log_errors', 1);
ini_set('error_log', __DIR__ . '/api_verbose.log');

// Her şeyi logla
function verboseLog($message) {
    $timestamp = date('Y-m-d H:i:s');
    $logFile = __DIR__ . '/api_verbose.log';
    file_put_contents($logFile, "[$timestamp] $message\n", FILE_APPEND);
}

verboseLog("=== NEW REQUEST ===");
verboseLog("Method: " . ($_SERVER['REQUEST_METHOD'] ?? 'N/A'));
verboseLog("URI: " . ($_SERVER['REQUEST_URI'] ?? 'N/A'));
verboseLog("Query String: " . ($_SERVER['QUERY_STRING'] ?? 'N/A'));

// Headers
verboseLog("--- HEADERS ---");
foreach (getallheaders() as $name => $value) {
    if ($name === 'X-API-Key') {
        verboseLog("$name: " . substr($value, 0, 50) . "...");
    } else {
        verboseLog("$name: $value");
    }
}

// Raw Input
$raw_input = file_get_contents('php://input');
verboseLog("--- RAW INPUT ---");
verboseLog("Length: " . strlen($raw_input));
if (strlen($raw_input) > 0) {
    verboseLog("Content: " . $raw_input);
    
    // JSON decode attempt
    $data = json_decode($raw_input, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        verboseLog("JSON ERROR: " . json_last_error_msg());
        verboseLog("JSON ERROR CODE: " . json_last_error());
    } else {
        verboseLog("JSON PARSED OK");
        verboseLog("Keys: " . implode(', ', array_keys($data)));
        
        // Check topics
        if (isset($data['topics'])) {
            verboseLog("Topics field exists");
            verboseLog("Topics type: " . gettype($data['topics']));
            verboseLog("Topics count: " . (is_array($data['topics']) ? count($data['topics']) : 'NOT ARRAY'));
            if (is_array($data['topics']) && count($data['topics']) > 0) {
                verboseLog("First topic: " . json_encode($data['topics'][0]));
            }
        } else {
            verboseLog("!!! TOPICS FIELD MISSING !!!");
        }
    }
}

verboseLog("=== END REQUEST ===\n");

echo "OK - Logged to api_verbose.log";
?>

