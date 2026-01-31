<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "<h1>API Test</h1>";

// Config yükle
require_once 'config.php';

echo "<h2>1. Config Yüklendi ✅</h2>";
echo "DB_HOST: " . DB_HOST . "<br>";
echo "DB_NAME: " . DB_NAME . "<br>";
echo "API_KEY: " . substr(ADMIN_API_KEY, 0, 30) . "...<br>";

// Database bağlantısı test et
try {
    $db = getDatabase();
    echo "<h2>2. Database Bağlantısı ✅</h2>";
} catch (Exception $e) {
    die("<h2>2. Database Hatası ❌</h2>" . $e->getMessage());
}

// API endpoint simülasyonu
echo "<h2>3. API Endpoint Test</h2>";

// Simulate API request
$test_data = [
    'survey_name' => 'API Test Anketi',
    'company_name' => 'Test Company',
    'survey_type' => 'materiality',
    'description' => 'Test from direct API',
    'deadline_date' => date('Y-m-d', strtotime('+30 days')),
    'topics' => [
        ['code' => 'TEST_01', 'name' => 'Test Topic', 'category' => 'Test']
    ]
];

$token = bin2hex(random_bytes(16));

try {
    $stmt = $db->prepare('
        INSERT INTO surveys 
        (survey_name, company_name, survey_type, description, created_date, deadline_date, status, unique_token, api_key, response_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ');
    
    $result = $stmt->execute([
        $test_data['survey_name'],
        $test_data['company_name'],
        $test_data['survey_type'],
        $test_data['description'],
        date('Y-m-d H:i:s'),
        $test_data['deadline_date'],
        'active',
        $token,
        ADMIN_API_KEY
    ]);
    
    if ($result) {
        $survey_id = $db->lastInsertId();
        echo "✅ Survey Created! ID: $survey_id<br>";
        echo "✅ Token: $token<br>";
        echo "✅ URL: <a href='survey.php?token=$token' target='_blank'>Test Survey</a><br>";
    } else {
        echo "❌ Insert Failed<br>";
    }
    
} catch (Exception $e) {
    echo "❌ Error: " . $e->getMessage();
}

echo "<h2>4. Test Tamamlandı</h2>";
?>