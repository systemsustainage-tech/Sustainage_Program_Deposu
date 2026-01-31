<?php
/**
 * Direct Survey Create - nginx/PHP body sorununu bypass eder
 */
error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once 'config.php';

// Log file
$logFile = __DIR__ . '/direct_create.log';
function logIt($msg) {
    global $logFile;
    file_put_contents($logFile, date('Y-m-d H:i:s') . " - $msg\n", FILE_APPEND);
}

logIt("=== NEW REQUEST ===");
logIt("Method: " . $_SERVER['REQUEST_METHOD']);

// API Key check
$api_key = isset($_SERVER['HTTP_X_API_KEY']) ? $_SERVER['HTTP_X_API_KEY'] : '';
$expected_key = ADMIN_API_KEY;

logIt("Received API Key: " . substr($api_key, 0, 50) . "...");
logIt("Expected API Key: " . substr($expected_key, 0, 50) . "...");
logIt("Received Length: " . strlen($api_key));
logIt("Expected Length: " . strlen($expected_key));
logIt("Match: " . ($api_key === $expected_key ? 'YES' : 'NO'));

if (!validateApiKey($api_key)) {
    http_response_code(401);
    echo json_encode([
        'success' => false,
        'error' => 'Unauthorized',
        'received_key_length' => strlen($api_key),
        'expected_key_length' => strlen($expected_key),
        'received_first_30' => substr($api_key, 0, 30),
        'expected_first_30' => substr($expected_key, 0, 30)
    ]);
    logIt("UNAUTHORIZED - API KEY MISMATCH");
    exit;
}

// GET parametrelerinden al (POST body yerine)
if (isset($_GET['json_data'])) {
    logIt("Using GET json_data parameter");
    $raw_input = urldecode($_GET['json_data']);
} else {
    logIt("Using POST body");
    $raw_input = file_get_contents('php://input');
}

logIt("Raw input length: " . strlen($raw_input));
logIt("Raw input (first 500): " . substr($raw_input, 0, 500));

if (empty($raw_input)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Empty input', 'method' => $_SERVER['REQUEST_METHOD']]);
    logIt("EMPTY INPUT!");
    exit;
}

$data = json_decode($raw_input, true);
if (!$data) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'JSON decode failed: ' . json_last_error_msg()]);
    logIt("JSON DECODE FAILED: " . json_last_error_msg());
    exit;
}

logIt("JSON decoded OK");
logIt("Keys: " . implode(', ', array_keys($data)));

// Required fields
if (empty($data['survey_name']) || empty($data['company_name']) || empty($data['topics'])) {
    http_response_code(400);
    $missing = [];
    if (empty($data['survey_name'])) $missing[] = 'survey_name';
    if (empty($data['company_name'])) $missing[] = 'company_name';
    if (empty($data['topics'])) $missing[] = 'topics';
    
    echo json_encode([
        'success' => false,
        'error' => 'Missing fields',
        'missing' => $missing,
        'received' => array_keys($data)
    ]);
    logIt("MISSING FIELDS: " . implode(', ', $missing));
    exit;
}

// Database
try {
    $db = getDatabase();
    logIt("DB connected");
    
    // Create survey
    // Python'dan gelen unique_token'ı kullan (varsa), yoksa oluştur
    $token = isset($data['unique_token']) && !empty($data['unique_token']) 
        ? cleanString($data['unique_token']) 
        : bin2hex(random_bytes(16));
    
    $survey_name = cleanString($data['survey_name']);
    $company_name = cleanString($data['company_name']);
    $survey_type = isset($data['survey_type']) ? cleanString($data['survey_type']) : 'materiality';
    $description = isset($data['description']) ? cleanString($data['description']) : '';
    $deadline_date = isset($data['deadline_date']) ? $data['deadline_date'] : date('Y-m-d', strtotime('+30 days'));
    
    $stmt = $db->prepare('
        INSERT INTO surveys 
        (survey_name, company_name, survey_type, description, created_date, deadline_date, status, unique_token, api_key, response_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ');
    
    $stmt->execute([
        $survey_name,
        $company_name,
        $survey_type,
        $description,
        date('Y-m-d H:i:s'),
        $deadline_date,
        'active',
        $token,
        ADMIN_API_KEY
    ]);
    
    $survey_id = $db->lastInsertId();
    logIt("Survey created: ID=$survey_id");
    
    // Add topics
    $topics_added = 0;
    foreach ($data['topics'] as $index => $topic) {
        $stmt = $db->prepare('
            INSERT INTO survey_topics 
            (survey_id, topic_code, topic_name, topic_category, description, display_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ');
        
        $stmt->execute([
            $survey_id,
            cleanString($topic['code']),
            cleanString($topic['name']),
            isset($topic['category']) ? cleanString($topic['category']) : '',
            isset($topic['description']) ? cleanString($topic['description']) : '',
            $index + 1
        ]);
        
        $topics_added++;
    }
    
    logIt("Topics added: $topics_added");
    
    $survey_url = BASE_URL . "/survey.php?token=$token";
    
    echo json_encode([
        'success' => true,
        'survey_id' => $survey_id,
        'survey_url' => $survey_url,
        'token' => $token,
        'topics_added' => $topics_added,
        'deadline_date' => $deadline_date
    ]);
    
    logIt("SUCCESS!");
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Database error: ' . $e->getMessage()]);
    logIt("DB ERROR: " . $e->getMessage());
}
?>

