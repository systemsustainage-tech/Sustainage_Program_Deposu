<?php
/**
 * Sustainage Anket Sistemi - REST API (MySQL)
 * Sustainage Desktop uygulaması ile iletişim için
 */
require_once 'config.php';

// JSON response
header('Content-Type: application/json; charset=UTF-8');

// API Key kontrolü
$api_key = isset($_SERVER['HTTP_X_API_KEY']) ? $_SERVER['HTTP_X_API_KEY'] : '';
if (!validateApiKey($api_key)) {
    http_response_code(401);
    echo json_encode([
        'success' => false,
        'error' => 'Unauthorized',
        'message' => 'Geçersiz API Key'
    ]);
    logMessage("API unauthorized access attempt from " . getClientIp(), 'WARNING');
    exit;
}

// Action parametresi
$action = isset($_GET['action']) ? cleanString($_GET['action']) : '';

if (empty($action)) {
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'error' => 'Bad Request',
        'message' => 'Action parametresi gerekli'
    ]);
    exit;
}

// Veritabanına bağlan
$db = getDatabase();

// Action'lara göre işlem
switch ($action) {
    
    // ============================================================
    // YENİ ANKET OLUŞTUR
    // ============================================================
    case 'create_survey':
        $raw_input = file_get_contents('php://input');
        $data = json_decode($raw_input, true);
        
        if (!$data) {
            http_response_code(400);
            $error_msg = 'Invalid JSON';
            if (json_last_error() !== JSON_ERROR_NONE) {
                $error_msg .= ': ' . json_last_error_msg();
            }
            echo json_encode([
                'success' => false, 
                'error' => $error_msg,
                'raw_input_length' => strlen($raw_input)
            ]);
            logMessage("JSON decode error: $error_msg", 'ERROR');
            break;
        }
        
        // Zorunlu alanları kontrol et - Detaylı hata mesajı
        $missing_fields = [];
        if (empty($data['survey_name'])) $missing_fields[] = 'survey_name';
        if (empty($data['company_name'])) $missing_fields[] = 'company_name';
        if (empty($data['topics'])) $missing_fields[] = 'topics';
        
        if (!empty($missing_fields)) {
            http_response_code(400);
            echo json_encode([
                'success' => false, 
                'error' => 'Missing required fields',
                'missing_fields' => $missing_fields,
                'received_fields' => array_keys($data)
            ]);
            logMessage("Missing fields: " . implode(', ', $missing_fields), 'ERROR');
            break;
        }
        
        // Benzersiz token oluştur
        $token = bin2hex(random_bytes(16));
        
        // Varsayılan değerler
        $survey_name = cleanString($data['survey_name']);
        $company_name = cleanString($data['company_name']);
        $survey_type = isset($data['survey_type']) ? cleanString($data['survey_type']) : 'materiality';
        $description = isset($data['description']) ? cleanString($data['description']) : '';
        $deadline_date = isset($data['deadline_date']) ? $data['deadline_date'] : date('Y-m-d', strtotime('+30 days'));
        
        // Anketi oluştur
        $stmt = $db->prepare('
            INSERT INTO surveys 
            (survey_name, company_name, survey_type, description, created_date, deadline_date, status, unique_token, api_key, response_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        ');
        
        if (!$stmt->execute([
            $survey_name,
            $company_name,
            $survey_type,
            $description,
            date('Y-m-d H:i:s'),
            $deadline_date,
            'active',
            $token,
            $api_key
        ])) {
            http_response_code(500);
            echo json_encode(['success' => false, 'error' => 'Database error']);
            logMessage("Failed to create survey: $survey_name", 'ERROR');
            break;
        }
        
        $survey_id = $db->lastInsertId();
        
        // Konuları ekle
        $topics_added = 0;
        foreach ($data['topics'] as $index => $topic) {
            $stmt = $db->prepare('
                INSERT INTO survey_topics 
                (survey_id, topic_code, topic_name, topic_category, description, display_order)
                VALUES (?, ?, ?, ?, ?, ?)
            ');
            
            if ($stmt->execute([
                $survey_id,
                cleanString($topic['code']),
                cleanString($topic['name']),
                isset($topic['category']) ? cleanString($topic['category']) : '',
                isset($topic['description']) ? cleanString($topic['description']) : '',
                $index + 1
            ])) {
                $topics_added++;
            }
        }
        
        $survey_url = BASE_URL . "/survey.php?token=$token";
        
        logMessage("Survey created: ID=$survey_id, Name=$survey_name, Topics=$topics_added", 'SUCCESS');
        
        echo json_encode([
            'success' => true,
            'survey_id' => $survey_id,
            'survey_url' => $survey_url,
            'token' => $token,
            'topics_added' => $topics_added,
            'deadline_date' => $deadline_date
        ]);
        break;
    
    // ============================================================
    // ANKET YANITLARINI GETIR (TOKEN İLE)
    // ============================================================
    case 'get_responses':
        // Token veya survey_id ile çalışır
        $token = isset($_GET['token']) ? cleanString($_GET['token']) : '';
        $survey_id = isset($_GET['survey_id']) ? intval($_GET['survey_id']) : 0;
        
        // Token varsa, survey_id'yi bul
        if (!empty($token)) {
            $stmt = $db->prepare('SELECT survey_id FROM surveys WHERE unique_token = ?');
            $stmt->execute([$token]);
            $survey = $stmt->fetch();
            
            if (!$survey) {
                http_response_code(404);
                echo json_encode(['success' => false, 'error' => 'Survey not found with this token']);
                break;
            }
            
            $survey_id = $survey['survey_id'];
        }
        
        if ($survey_id <= 0) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Invalid survey_id or token']);
            break;
        }
        
        // Yanıtları getir
        $stmt = $db->prepare('
            SELECT * FROM survey_responses 
            WHERE survey_id = ? 
            ORDER BY submitted_date DESC
        ');
        $stmt->execute([$survey_id]);
        $responses = $stmt->fetchAll();
        
        // Her yanıt için değerlendirmeleri grupla
        $grouped_responses = [];
        foreach ($responses as $response) {
            $email = $response['stakeholder_email'];
            
            if (!isset($grouped_responses[$email])) {
                $grouped_responses[$email] = [
                    'stakeholder_name' => $response['stakeholder_name'],
                    'stakeholder_email' => $response['stakeholder_email'],
                    'stakeholder_organization' => $response['stakeholder_organization'],
                    'stakeholder_role' => $response['stakeholder_role'],
                    'response_date' => $response['submitted_date'],
                    'ip_address' => $response['ip_address'],
                    'evaluations' => []
                ];
            }
            
            $grouped_responses[$email]['evaluations'][] = [
                'topic_code' => $response['topic_code'],
                'topic_name' => $response['topic_name'],
                'importance' => $response['importance_score'],
                'impact' => $response['impact_score'],
                'comment' => $response['comment']
            ];
        }
        
        // Array değerlerini al
        $final_responses = array_values($grouped_responses);
        
        echo json_encode([
            'success' => true,
            'survey_id' => $survey_id,
            'total_responses' => count($final_responses),
            'responses' => $final_responses
        ]);
        
        logMessage("API: get_responses - Survey ID=$survey_id, Token=$token, Count=" . count($final_responses), 'INFO');
        break;
    
    // ============================================================
    // ÖZET İSTATİSTİKLER
    // ============================================================
    case 'get_summary':
        $survey_id = isset($_GET['survey_id']) ? intval($_GET['survey_id']) : 0;
        
        if ($survey_id <= 0) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Invalid survey_id']);
            break;
        }
        
        // Konu bazında istatistikler
        $stmt = $db->prepare('
            SELECT 
                sr.topic_code,
                st.topic_name,
                st.topic_category,
                AVG(sr.importance_score) as avg_importance,
                AVG(sr.impact_score) as avg_impact,
                COUNT(*) as response_count,
                MIN(sr.importance_score) as min_importance,
                MAX(sr.importance_score) as max_importance,
                MIN(sr.impact_score) as min_impact,
                MAX(sr.impact_score) as max_impact
            FROM survey_responses sr
            LEFT JOIN survey_topics st ON sr.topic_code = st.topic_code AND sr.survey_id = st.survey_id
            WHERE sr.survey_id = ? 
            GROUP BY sr.topic_code
            ORDER BY avg_importance DESC, avg_impact DESC
        ');
        $stmt->execute([$survey_id]);
        $results = $stmt->fetchAll();
        
        $summary = [];
        foreach ($results as $row) {
            $summary[] = [
                'topic_code' => $row['topic_code'],
                'topic_name' => $row['topic_name'],
                'topic_category' => $row['topic_category'],
                'avg_importance' => round($row['avg_importance'], 2),
                'avg_impact' => round($row['avg_impact'], 2),
                'materiality_score' => round($row['avg_importance'] * $row['avg_impact'], 2),
                'response_count' => $row['response_count'],
                'min_importance' => $row['min_importance'],
                'max_importance' => $row['max_importance'],
                'min_impact' => $row['min_impact'],
                'max_impact' => $row['max_impact']
            ];
        }
        
        // Toplam yanıt sayısı
        $stmt = $db->prepare('SELECT COUNT(DISTINCT stakeholder_email) as total_stakeholders FROM survey_responses WHERE survey_id = ?');
        $stmt->execute([$survey_id]);
        $row = $stmt->fetch();
        $total_stakeholders = $row['total_stakeholders'];
        
        echo json_encode([
            'success' => true,
            'survey_id' => $survey_id,
            'total_stakeholders' => $total_stakeholders,
            'total_topics' => count($summary),
            'summary' => $summary
        ]);
        
        logMessage("API: get_summary - Survey ID=$survey_id, Topics=" . count($summary), 'INFO');
        break;
    
    // ============================================================
    // ANKETLERİ LİSTELE
    // ============================================================
    case 'list_surveys':
        $status = isset($_GET['status']) ? cleanString($_GET['status']) : 'all';
        
        if ($status === 'all') {
            $stmt = $db->prepare('SELECT * FROM surveys ORDER BY created_date DESC');
            $stmt->execute();
        } else {
            $stmt = $db->prepare('SELECT * FROM surveys WHERE status = ? ORDER BY created_date DESC');
            $stmt->execute([$status]);
        }
        
        $results = $stmt->fetchAll();
        $surveys = [];
        
        foreach ($results as $row) {
            // Konu sayısını al
            $stmt2 = $db->prepare('SELECT COUNT(*) as topic_count FROM survey_topics WHERE survey_id = ?');
            $stmt2->execute([$row['survey_id']]);
            $row2 = $stmt2->fetch();
            
            $surveys[] = [
                'survey_id' => $row['survey_id'],
                'survey_name' => $row['survey_name'],
                'company_name' => $row['company_name'],
                'survey_type' => $row['survey_type'],
                'status' => $row['status'],
                'created_date' => $row['created_date'],
                'deadline_date' => $row['deadline_date'],
                'response_count' => $row['response_count'],
                'topic_count' => $row2['topic_count'],
                'survey_url' => BASE_URL . "/survey.php?token=" . $row['unique_token']
            ];
        }
        
        echo json_encode([
            'success' => true,
            'total_surveys' => count($surveys),
            'surveys' => $surveys
        ]);
        break;
    
    // ============================================================
    // ANKET DURUMU GÜNCELLE
    // ============================================================
    case 'update_status':
        $survey_id = isset($_GET['survey_id']) ? intval($_GET['survey_id']) : 0;
        $status = isset($_GET['status']) ? cleanString($_GET['status']) : '';
        
        if ($survey_id <= 0 || !in_array($status, ['active', 'closed', 'draft'])) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Invalid parameters']);
            break;
        }
        
        $stmt = $db->prepare('UPDATE surveys SET status = ? WHERE survey_id = ?');
        
        if ($stmt->execute([$status, $survey_id])) {
            echo json_encode(['success' => true, 'survey_id' => $survey_id, 'new_status' => $status]);
            logMessage("Survey status updated: ID=$survey_id, Status=$status", 'INFO');
        } else {
            http_response_code(500);
            echo json_encode(['success' => false, 'error' => 'Update failed']);
        }
        break;
    
    // ============================================================
    // ANKET SİL
    // ============================================================
    case 'delete_survey':
        $survey_id = isset($_GET['survey_id']) ? intval($_GET['survey_id']) : 0;
        
        if ($survey_id <= 0) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Invalid survey_id']);
            break;
        }
        
        // Foreign key cascade delete sayesinde yanıtlar ve konular otomatik silinecek
        $stmt = $db->prepare('DELETE FROM surveys WHERE survey_id = ?');
        
        if ($stmt->execute([$survey_id])) {
            echo json_encode(['success' => true, 'survey_id' => $survey_id, 'message' => 'Survey deleted']);
            logMessage("Survey deleted: ID=$survey_id", 'INFO');
        } else {
            http_response_code(500);
            echo json_encode(['success' => false, 'error' => 'Delete failed']);
        }
        break;
    
    // ============================================================
    // YORUMLARI GETIR
    // ============================================================
    case 'get_comments':
        $survey_id = isset($_GET['survey_id']) ? intval($_GET['survey_id']) : 0;
        
        if ($survey_id <= 0) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Invalid survey_id']);
            break;
        }
        
        $stmt = $db->prepare('
            SELECT 
                sr.topic_code,
                st.topic_name,
                sr.stakeholder_name,
                sr.stakeholder_email,
                sr.comment,
                sr.submitted_date
            FROM survey_responses sr
            LEFT JOIN survey_topics st ON sr.topic_code = st.topic_code AND sr.survey_id = st.survey_id
            WHERE sr.survey_id = ? AND sr.comment != ""
            ORDER BY sr.submitted_date DESC
        ');
        $stmt->execute([$survey_id]);
        $comments = $stmt->fetchAll();
        
        echo json_encode([
            'success' => true,
            'survey_id' => $survey_id,
            'total_comments' => count($comments),
            'comments' => $comments
        ]);
        break;
    
    // ============================================================
    // GEÇERSİZ ACTION
    // ============================================================
    default:
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'error' => 'Invalid action',
            'message' => "Action '$action' bulunamadı"
        ]);
        break;
}
?>

