<?php
/**
 * Sustainage Anket Sistemi - Konfigürasyon (SQLite)
 * Server: 72.62.150.207
 */

// Hata raporlama
error_reporting(E_ALL);
ini_set('display_errors', 0); // Production'da 0
ini_set('log_errors', 1);
ini_set('error_log', __DIR__ . '/error.log');

// ============================================================
// VERİTABANI AYARLARI (SQLite)
// ============================================================

function get_db_path() {
    if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
        return 'C:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite';
    } else {
        return '/var/www/sustainage/sustainage.db';
    }
}

// API Güvenlik
define('ADMIN_API_KEY', 'sustainage_secure_api_key_2025_6b2c4b5a054d5046c92c6274389f27c5');

// Şirket Bilgileri
define('COMPANY_NAME', 'Sustainage');
define('COMPANY_EMAIL', 'system@sustainage.cloud');
define('COMPANY_WEBSITE', 'https://sustainage.cloud');

// URL Ayarları
define('BASE_URL', 'https://sustainage.cloud/anket');

// Timezone
date_default_timezone_set('Europe/Istanbul');

// CORS
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-API-Key');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

header('Content-Type: text/html; charset=UTF-8');

/**
 * Veritabanı bağlantısı oluştur (SQLite)
 */
function getDatabase() {
    try {
        $dsn = "sqlite:" . get_db_path();
        $pdo = new PDO($dsn);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
        $pdo->exec("PRAGMA foreign_keys = ON;");
        return $pdo;
        
    } catch (PDOException $e) {
        error_log('Database connection error: ' . $e->getMessage());
        // For security, don't show full path in production output
        die('Veritabanı bağlantı hatası. Lütfen daha sonra tekrar deneyin.');
    }
}

/**
 * API Key kontrolü
 */
function validateApiKey($provided_key) {
    return $provided_key === ADMIN_API_KEY;
}

/**
 * Log fonksiyonu
 */
function logMessage($message, $type = 'INFO') {
    $log_file = __DIR__ . '/activity.log';
    $timestamp = date('Y-m-d H:i:s');
    $log_entry = "[$timestamp] [$type] $message\n";
    file_put_contents($log_file, $log_entry, FILE_APPEND);
}

/**
 * IP adresi al
 */
function getClientIp() {
    if (!empty($_SERVER['HTTP_CLIENT_IP'])) {
        return $_SERVER['HTTP_CLIENT_IP'];
    } elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        return $_SERVER['HTTP_X_FORWARDED_FOR'];
    } else {
        return $_SERVER['REMOTE_ADDR'];
    }
}
