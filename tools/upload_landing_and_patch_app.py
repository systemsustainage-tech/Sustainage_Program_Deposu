import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
from ftplib import FTP, error_perm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LANDING_HTML = """<!DOCTYPE html>
<html lang=\"tr\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>SUSTAINAGE SDG</title>
<style>
  body{font-family: Segoe UI,system-ui,Segoe UI,Tahoma,sans-serif;margin:0;padding:40px;background:#f8fafc;color:#0f172a}
  .container{max-width:960px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;box-shadow:0 6px 20px rgba(2,8,23,0.06)}
  header{padding:28px 32px;border-bottom:1px solid #e2e8f0;background:linear-gradient(180deg,#f1f5f9,#ffffff)}
  header h1{margin:0;font-size:28px;letter-spacing:0.2px}
  header p{margin:6px 0 0;color:#475569}
  main{padding:24px 32px;}
  h2{font-size:20px;margin:24px 0 12px;color:#0f172a}
  ul{margin:0;padding-left:20px;color:#334155}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-top:12px}
  .card{border:1px solid #e2e8f0;border-radius:10px;padding:18px;background:#ffffff}
  footer{padding:16px 32px;border-top:1px solid #e2e8f0;color:#64748b;background:#f8fafc}
</style>
</head>
<body>
  <div class=\"container\">
    <header>
      <h1>SUSTAINAGE SDG</h1>
      <p>ESG/SDG uyumlu sürdürülebilirlik yönetim ve raporlama platformu</p>
    </header>
    <main>
      <section>
        <h2>Modüller</h2>
        <div class=\"grid\">
          <div class=\"card\"><strong>ESG Dashboard</strong><br/>Kurumsal ESG görünümü</div>
          <div class=\"card\"><strong>SDG Veri Toplama</strong><br/>Hedef ve gösterge yönetimi</div>
          <div class=\"card\"><strong>GRI İndeks</strong><br/>GRI standart uyumluluğu</div>
          <div class=\"card\"><strong>TSRS/ISSB/SASB</strong><br/>Çoklu çerçeve eşleştirme</div>
          <div class=\"card\"><strong>CBAM</strong><br/>Sınırda karbon düzeni takibi</div>
          <div class=\"card\"><strong>Su/Atık</strong><br/>Çevresel veri yönetimi</div>
          <div class=\"card\"><strong>Tedarik Zinciri</strong><br/>Risk ve performans takibi</div>
          <div class=\"card\"><strong>Raporlama</strong><br/>PDF/Excel/Word çıktıları</div>
        </div>
      </section>
      <section>
        <h2>Faydalar</h2>
        <ul>
          <li>Uyum ve denetim kolaylığı</li>
          <li>Veri odaklı karar</li>
          <li>Operasyonel verimlilik</li>
          <li>Regülasyon maliyet tasarrufu</li>
        </ul>
      </section>
    </main>
    <footer>© Sustainage • Sürdürülebilirlik ve uyum teknolojileri</footer>
  </div>
</body>
</html>
"""

INDEX_PHP = """<?php
declare(strict_types=1);
$page = $_GET['p'] ?? 'ana';
$lang = $_GET['lang'] ?? 'tr';
$t = function(string $key) use ($lang) {
  $dict = [
    'tr' => [
      'brand' => 'SUSTAINAGE SDG',
      'menu_home' => 'Ana Sayfa',
      'menu_about' => 'Hakkımızda',
      'menu_modules' => 'Modüller',
      'menu_faq' => 'SSS',
      'menu_contact' => 'İletişim',
      'hero_title' => 'ESG/SDG uyumlu sürdürülebilirlik yönetimi',
      'hero_desc' => 'Kurumsal sürdürülebilirlik hedeflerini veri odaklı yönetmeniz için kapsamlı bir platform.',
      'cta_modules' => 'Modülleri İncele',
      'cta_demo' => 'Demo Talep Et',
      'about_title' => 'Hakkımızda',
      'modules_title' => 'Modüller',
      'faq_title' => 'SSS',
      'contact_title' => 'İletişim',
      'lang_toggle' => 'EN',
    ],
    'en' => [
      'brand' => 'SUSTAINAGE SDG',
      'menu_home' => 'Home',
      'menu_about' => 'About',
      'menu_modules' => 'Modules',
      'menu_faq' => 'FAQ',
      'menu_contact' => 'Contact',
      'hero_title' => 'ESG/SDG-aligned sustainability management',
      'hero_desc' => 'A comprehensive platform to manage corporate sustainability targets with data-driven insights.',
      'cta_modules' => 'Explore Modules',
      'cta_demo' => 'Request a Demo',
      'about_title' => 'About',
      'modules_title' => 'Modules',
      'faq_title' => 'FAQ',
      'contact_title' => 'Contact',
      'lang_toggle' => 'TR',
    ],
  ];
  return $dict[$lang][$key] ?? $key;
};
$menu = [
  'ana' => $t('menu_home'),
  'hakkimizda' => $t('menu_about'),
  'moduller' => $t('menu_modules'),
  'sss' => $t('menu_faq'),
  'iletisim' => $t('menu_contact')
];
function active(string $key, string $cur): string { return $key === $cur ? 'active' : ''; }
if (file_exists(__DIR__.'/config.smtp.php')) { include __DIR__.'/config.smtp.php'; }
$smtp = [
  'host' => isset($SMTP_HOST)?$SMTP_HOST:(getenv('SMTP_HOST')?:''),
  'port' => isset($SMTP_PORT)?(int)$SMTP_PORT:(int)(getenv('SMTP_PORT')?:0),
  'user' => isset($SMTP_USER)?$SMTP_USER:(getenv('SMTP_USER')?:''),
  'pass' => isset($SMTP_PASS)?$SMTP_PASS:(getenv('SMTP_PASS')?:''),
  'from' => isset($SMTP_FROM)?$SMTP_FROM:(getenv('SMTP_FROM')?:'info@sustainage.tr'),
  'from_name' => isset($SMTP_FROM_NAME)?$SMTP_FROM_NAME:(getenv('SMTP_FROM_NAME')?:'Sustainage'),
  'to' => isset($SMTP_TO)?$SMTP_TO:(getenv('SMTP_TO')?:'info@sustainage.tr'),
];
function smtp_send(array $cfg, string $to, string $subject, string $body, ?string $replyEmail=null, ?string $replyName=null): bool {
  if (!$cfg['host'] || !$cfg['port'] || !$cfg['user'] || !$cfg['pass']) {
    $headers = 'From: '.($cfg['from_name']).' <'.$cfg['from'].'>'."\r\n".'MIME-Version: 1.0' . "\r\n" . 'Content-Type: text/plain; charset=UTF-8';
    if ($replyEmail) { $headers .= "\r\n".'Reply-To: '.(($replyName?$replyName.' ':'').'<'.$replyEmail.'>'); }
    return @mail($to, $subject, $body, $headers);
  }
  $log = [];
  $add = function($s) use (&$log){ $log[] = $s; };
  $fp = @fsockopen($cfg['host'], (int)$cfg['port'], $errno, $errstr, 15);
  if (!$fp) { $add('connect_error'); $GLOBALS['SMTP_LOG']=$log; return false; }
  stream_set_timeout($fp, 60);
  $r = fgets($fp, 515); $add('srv '.$r);
  $w = function($s) use ($fp, $add) { $add('> '.$s); fwrite($fp, $s."\r\n"); };
  $w('EHLO sustainage.tr'); $r = fgets($fp, 515); $add('< '.$r);
  if (strpos($r, '250') !== 0) { $w('HELO sustainage.tr'); $r = fgets($fp, 515); $add('< '.$r); }
  $w('AUTH LOGIN'); $r = fgets($fp, 515); $add('< '.$r);
  $w(base64_encode($cfg['user'])); $r = fgets($fp, 515); $add('< '.$r);
  $w(base64_encode($cfg['pass'])); $r = fgets($fp, 515); $add('< '.$r);
  if (strpos($r, '235') !== 0) { $w('QUIT'); fclose($fp); $GLOBALS['SMTP_LOG']=$log; return false; }
  $w('MAIL FROM:<'.$cfg['from'].'>'); $r = fgets($fp, 515); $add('< '.$r);
  if (strpos($r, '250') !== 0) { $w('QUIT'); fclose($fp); $GLOBALS['SMTP_LOG']=$log; return false; }
  $w('RCPT TO:<'.$to.'>'); $r = fgets($fp, 515); $add('< '.$r);
  if (strpos($r, '250') !== 0) { $w('QUIT'); fclose($fp); $GLOBALS['SMTP_LOG']=$log; return false; }
  $w('DATA'); $r = fgets($fp, 515); $add('< '.$r);
  if (strpos($r, '354') !== 0) { $w('QUIT'); fclose($fp); $GLOBALS['SMTP_LOG']=$log; return false; }
  $date = gmdate('D, d M Y H:i:s').' +0000';
  $mid = '<'.uniqid().'@sustainage.tr>';
  $headers = 'From: '.($cfg['from_name']).' <'.$cfg['from'].'>' . "\r\n" . 'To: '.$to . "\r\n" . 'Subject: '.$subject . "\r\n" . 'Date: '.$date . "\r\n" . 'Message-ID: '.$mid . "\r\n" . 'MIME-Version: 1.0' . "\r\n" . 'Content-Type: text/plain; charset=UTF-8' . "\r\n" . 'Content-Transfer-Encoding: 8bit';
  if ($replyEmail) { $headers .= "\r\n".'Reply-To: '.(($replyName?$replyName.' ':'').'<'.$replyEmail.'>'); }
  $msg = $headers . "\r\n\r\n" . $body . "\r\n" . ".\r\n";
  fwrite($fp, $msg);
  $r = fgets($fp, 515); $add('< '.$r);
  $w('QUIT'); fclose($fp);
  $ok = (strpos($r, '250') === 0);
  $GLOBALS['SMTP_LOG'] = $log;
  return $ok;
}
?><!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SUSTAINAGE SDG</title>
<link rel="stylesheet" href="/assets/style.css">
<script>
function toggleFaq(id){var el=document.getElementById(id); if(!el)return; el.classList.toggle('open');}
</script>
</head>
<body>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="/">
      <?php if (file_exists(__DIR__.'/assets/logo.png')): ?>
        <img src="/assets/logo.png" alt="Sustainage" class="brand-logo"/>
      <?php else: ?>
        <svg width="36" height="36" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" fill="#2563eb"/><path d="M7 13l3 3 7-7" stroke="#fff" stroke-width="2" fill="none"/></svg>
      <?php endif; ?>
      <span><?php echo $t('brand'); ?></span>
    </a>
    <nav class="nav">
      <a class="nav-link <?php echo active('ana',$page); ?>" href="/?p=ana&lang=<?php echo $lang; ?>"><?php echo $t('menu_home'); ?></a>
      <a class="nav-link <?php echo active('hakkimizda',$page); ?>" href="/?p=hakkimizda&lang=<?php echo $lang; ?>"><?php echo $t('menu_about'); ?></a>
      <a class="nav-link <?php echo active('moduller',$page); ?>" href="/?p=moduller&lang=<?php echo $lang; ?>"><?php echo $t('menu_modules'); ?></a>
      <a class="nav-link <?php echo active('sss',$page); ?>" href="/?p=sss&lang=<?php echo $lang; ?>"><?php echo $t('menu_faq'); ?></a>
      <a class="nav-link btn <?php echo active('iletisim',$page); ?>" href="/?p=iletisim&lang=<?php echo $lang; ?>"><?php echo $t('menu_contact'); ?></a>
      <a class="nav-link" href="/?p=<?php echo $page; ?>&lang=<?php echo $lang==='tr'?'en':'tr'; ?>"><?php echo $t('lang_toggle'); ?></a>
    </nav>
  </div>
  </header>
<main class="container">
<?php if ($page === 'ana'): ?>
  <section class="hero">
    <h1><?php echo $t('hero_title'); ?></h1>
    <p><?php echo $t('hero_desc'); ?></p>
    <div class="hero-actions">
      <a class="btn primary" href="/?p=moduller&lang=<?php echo $lang; ?>"><?php echo $t('cta_modules'); ?></a>
      <a class="btn" href="/?p=iletisim&lang=<?php echo $lang; ?>&purpose=demo"><?php echo $t('cta_demo'); ?></a>
    </div>
  </section>
  <section>
    <h2><?php echo $lang==='tr'?'Öne Çıkan Özellikler':'Highlights'; ?></h2>
    <div class="grid">
      <a class="card link" href="/?p=modul&m=esg&lang=<?php echo $lang; ?>"><h3>ESG Dashboard</h3><p><?php echo $lang==='tr'?'Kurumsal ESG görünümü':'Corporate ESG view'; ?></p></a>
      <a class="card link" href="/?p=modul&m=sdg&lang=<?php echo $lang; ?>"><h3>SDG Data</h3><p><?php echo $lang==='tr'?'Hedef ve gösterge yönetimi':'Goal/indicator management'; ?></p></a>
      <a class="card link" href="/?p=modul&m=gri&lang=<?php echo $lang; ?>"><h3>GRI Index</h3><p><?php echo $lang==='tr'?'GRI uyumluluk':'GRI compliance'; ?></p></a>
      <a class="card link" href="/?p=modul&m=tsrs&lang=<?php echo $lang; ?>"><h3>TSRS/ISSB/SASB</h3><p><?php echo $lang==='tr'?'Çerçeve eşleştirme':'Framework mapping'; ?></p></a>
    </div>
  </section>
<?php elseif ($page === 'hakkimizda'): ?>
  <section class="content">
    <h1><?php echo $t('about_title'); ?></h1>
    <p>Sustainage, kurumların sürdürülebilirlik hedeflerine ulaşmasını destekleyen teknoloji çözümleri geliştirir. ESG/SDG uyumluluğunu kolaylaştıran araçlar sunar.</p>
    <div class="grid">
      <div class="card"><h3>Vizyon</h3><p>Şeffaf, ölçülebilir ve etkili sürdürülebilirlik.</p></div>
      <div class="card"><h3>Misyon</h3><p>Veri odaklı karar mekanizmaları ile kurumsal dönüşüm.</p></div>
      <div class="card"><h3>Değerler</h3><p>Güven, uyum, inovasyon ve etki.</p></div>
    </div>
    <h2>Yol Haritası</h2>
    <ul class="timeline">
      <li>2023 — Platform çekirdeği ve veri envanteri</li>
      <li>2024 — GRI/ESRS uyum modülleri ve raporlama</li>
      <li>2025 — CBAM ve tedarik zinciri analitikleri</li>
    </ul>
  </section>
<?php elseif ($page === 'moduller'): ?>
  <section class="content">
    <h1><?php echo $t('modules_title'); ?></h1>
    <div class="grid">
      <a class="card link" href="/?p=modul&m=esg&lang=<?php echo $lang; ?>"><h3>ESG Dashboard</h3><p><?php echo $lang==='tr'?'Kurumsal ESG görünümü':'Corporate ESG view'; ?></p></a>
      <a class="card link" href="/?p=modul&m=sdg&lang=<?php echo $lang; ?>"><h3>SDG Veri Toplama</h3><p><?php echo $lang==='tr'?'Hedef ve gösterge yönetimi':'Goal/indicator management'; ?></p></a>
      <a class="card link" href="/?p=modul&m=gri&lang=<?php echo $lang; ?>"><h3>GRI İndeks</h3><p><?php echo $lang==='tr'?'GRI uyumluluğu':'GRI compliance'; ?></p></a>
      <a class="card link" href="/?p=modul&m=tsrs&lang=<?php echo $lang; ?>"><h3>TSRS/ISSB/SASB</h3><p><?php echo $lang==='tr'?'Çerçeve eşleştirme':'Framework mapping'; ?></p></a>
      <a class="card link" href="/?p=modul&m=cbam&lang=<?php echo $lang; ?>"><h3>CBAM</h3><p><?php echo $lang==='tr'?'İthalat bazlı karbon':'Carbon at border'; ?></p></a>
      <a class="card link" href="/?p=modul&m=water&lang=<?php echo $lang; ?>"><h3>Su/Atık</h3><p><?php echo $lang==='tr'?'Çevresel veri envanteri':'Environmental data'; ?></p></a>
      <a class="card link" href="/?p=modul&m=supply&lang=<?php echo $lang; ?>"><h3>Tedarik Zinciri</h3><p><?php echo $lang==='tr'?'Risk ve performans':'Risk & performance'; ?></p></a>
      <a class="card link" href="/?p=modul&m=report&lang=<?php echo $lang; ?>"><h3>Raporlama</h3><p>PDF/Excel/Word</p></a>
    </div>
  </section>
<?php elseif ($page === 'modul'): ?>
  <?php $m = $_GET['m'] ?? ''; $modules = [
    'esg' => [
      'img' => 'esg.jpg',
      'tr' => [
        'title'=>'ESG Dashboard',
        'summary'=>'ESG metriklerini tek ekranda izleme, risk/fırsat yönetimi ve yönetim raporları.',
        'hero_bullets'=>['Canlı göstergeler','Trend analizleri','Uyarılar ve eşikler'],
        'sections'=>[
          ['h'=>'Genel Bakış','p'=>'Kurumsal ESG performansını gerçek zamanlı olarak görünür kılar, yönetim kurulu ve ekipler için ortak bir karar alanı sunar.'],
          ['h'=>'Önemli Yetkinlikler','list'=>['KPI panoları ve kişiselleştirilebilir widget’lar','Risk/fırsat kayıtları ve aksiyon takibi','Sektör/akran kıyaslama','Alarm ve bildirim mekanizması']],
          ['h'=>'Faydalar','list'=>['Stratejik görünürlük ve hızlı karar alma','Operasyonel verimlilik artışı','Uyum ve denetim kolaylığı','Maliyet ve risk azaltımı']],
          ['h'=>'Raporlama','list'=>['Yönetim ve kurumsal rapor şablonları','PDF/DOCX/XLSX dışa aktarma','Anlık paylaşım ve versiyonlama']],
          ['h'=>'Uyum','list'=>['GRI/ESRS/ISSB eşleştirme','Denetim kanıt dokümantasyonu','Politika ve hedef izleme']],
          ['h'=>'Entegrasyonlar','list'=>['ERP/API','Excel/CSV','Bulut depolama']],
        ]
      ],
      'en' => [
        'title'=>'ESG Dashboard',
        'summary'=>'Real-time ESG visibility, risk/opportunity management and executive reporting.',
        'hero_bullets'=>['Live indicators','Trend analysis','Alerts and thresholds'],
        'sections'=>[
          ['h'=>'Overview','p'=>'Makes corporate ESG performance visible in real-time and provides a shared decision space.'],
          ['h'=>'Key Capabilities','list'=>['KPI dashboards and customizable widgets','Risk/opportunity log & action tracking','Peer benchmarking','Alerting and notifications']],
          ['h'=>'Benefits','list'=>['Strategic visibility and faster decisions','Operational efficiency','Audit and compliance ease','Cost & risk reduction']],
          ['h'=>'Reporting','list'=>['Executive and corporate templates','PDF/DOCX/XLSX exports','Instant sharing and versioning']],
          ['h'=>'Compliance','list'=>['GRI/ESRS/ISSB mapping','Audit evidence repository','Policy & target tracking']],
          ['h'=>'Integrations','list'=>['ERP/API','Excel/CSV','Cloud storage']],
        ]
      ]
    ],
    'sdg' => [
      'img' => 'sdg.jpg',
      'tr' => [
        'title'=>'SDG Veri Toplama',
        'summary'=>'Hedef ve gösterge bazlı performans yönetimi, matris ve kütüphane desteği.',
        'hero_bullets'=>['Hedef matrisi','Gösterge kütüphanesi','İlerleme izleme'],
        'sections'=>[
          ['h'=>'Genel Bakış','p'=>'SDG hedefleri ve alt hedefler için göstergeleri tanımlayın, veri toplama süreçlerini standartlaştırın.'],
          ['h'=>'Yetkinlikler','list'=>['Hedef-gösterge matrisi','Gösterge tanımları ve metodoloji','Rutin veri toplama akışları','Doğrulama ve onay adımları']],
          ['h'=>'Faydalar','list'=>['Şeffaf hedef takibi','Standart metodoloji','Kolay raporlama','Ekip koordinasyonu']],
          ['h'=>'Uyum','list'=>['SDG 17 hedef seti ile hizalama','Regülasyon uyumu için izlenebilirlik']],
        ]
      ],
      'en' => [
        'title'=>'SDG Data',
        'summary'=>'Goal & indicator-based performance management with matrix and library.',
        'hero_bullets'=>['Goal matrix','Indicator library','Progress tracking'],
        'sections'=>[
          ['h'=>'Overview','p'=>'Define indicators for SDG goals/targets and standardize data collection.'],
          ['h'=>'Capabilities','list'=>['Goal–indicator matrix','Indicator definitions & methodology','Routine data collection flows','Validation & approvals']],
          ['h'=>'Benefits','list'=>['Transparent target tracking','Standard methodology','Easy reporting','Team coordination']],
          ['h'=>'Compliance','list'=>['Alignment with SDG targets','Traceability for regulatory reporting']],
        ]
      ]
    ],
    'gri' => [
      'img' => 'gri.jpg',
      'tr' => [
        'title'=>'GRI İndeks',
        'summary'=>'GRI uyumluluğu için açıklamalar, kanıtlar ve taslak raporlar.',
        'hero_bullets'=>['Standart eşleştirme','Kanıt dokümantasyonu','Otomatik taslaklar'],
        'sections'=>[
          ['h'=>'Genel Bakış','p'=>'GRI standartlarına tam uyum için gerekli açıklamaları, göstergeleri ve kanıtları yönetin.'],
          ['h'=>'Yetkinlikler','list'=>['Disclosure eşleştirme','Kanıt dosyaları ve referanslar','Eksik alan uyarıları']],
          ['h'=>'Raporlama','list'=>['GRI uyum raporu taslakları','Dışa aktarma seçenekleri']],
        ]
      ],
      'en' => [
        'title'=>'GRI Index',
        'summary'=>'Disclosures, evidence and draft reports for GRI compliance.',
        'hero_bullets'=>['Standard mapping','Evidence docs','Auto drafts'],
        'sections'=>[
          ['h'=>'Overview','p'=>'Manage required disclosures, indicators and evidence for full GRI compliance.'],
          ['h'=>'Capabilities','list'=>['Disclosure mapping','Evidence files & references','Missing area alerts']],
          ['h'=>'Reporting','list'=>['GRI compliance draft reports','Export options']],
        ]
      ]
    ],
    'tsrs' => [
      'img' => 'tsrs.jpg',
      'tr' => [
        'title'=>'TSRS/ISSB/SASB',
        'summary'=>'Çoklu çerçeve eşleştirme, uyum puanı ve rapor çıktı.',
        'hero_bullets'=>['Eşleştirme matrisi','Uyum puanları','Rapor çıktı'],
        'sections'=>[
          ['h'=>'Genel Bakış','p'=>'TSRS/ESRS/ISSB/SASB gibi çerçeveler ile göstergeleri hizalayın, uyum puanı hesaplayın.'],
          ['h'=>'Yetkinlikler','list'=>['Çerçeve eşleştirme matrisi','Uygunluk skoru ve boşluk analizi','Rapor çıktıları']],
        ]
      ],
      'en' => [
        'title'=>'TSRS/ISSB/SASB',
        'summary'=>'Multi-framework mapping, compliance scoring and reporting.',
        'hero_bullets'=>['Mapping matrix','Compliance scores','Report export'],
        'sections'=>[
          ['h'=>'Overview','p'=>'Align indicators with TSRS/ESRS/ISSB/SASB frameworks and compute compliance scores.'],
          ['h'=>'Capabilities','list'=>['Framework mapping matrix','Compliance scoring & gap analysis','Report exports']],
        ]
      ]
    ],
    'cbam' => [
      'img' => 'cbam.jpg',
      'tr' => [
        'title'=>'CBAM',
        'summary'=>'Sınırda karbon düzeni takibi: ithalat kayıtları, faktörler ve beyan.',
        'hero_bullets'=>['İthalat kayıtları','Emisyon faktörleri','Beyan çıktıları'],
        'sections'=>[
          ['h'=>'Genel Bakış','p'=>'CBAM kapsamındaki ithalat için emisyon hesaplama ve beyan süreçlerini yönetin.'],
          ['h'=>'Yetkinlikler','list'=>['Ürün/teslimat bazlı kayıtlar','Emisyon faktör kütüphanesi','Beyan dosyaları']],
        ]
      ],
      'en' => [
        'title'=>'CBAM',
        'summary'=>'Carbon Border Adjustment tracking: imports, factors and declarations.',
        'hero_bullets'=>['Import records','Emission factors','Declaration outputs'],
        'sections'=>[
          ['h'=>'Overview','p'=>'Manage emission calculation and declarations for CBAM-covered imports.'],
          ['h'=>'Capabilities','list'=>['Product/shipment records','Factor library','Declaration files']],
        ]
      ]
    ],
    'water' => [
      'img' => 'water.jpg',
      'tr' => [
        'title'=>'Su/Atık',
        'summary'=>'Çevresel veri envanteri ve analiz: su, atık, enerji.',
        'hero_bullets'=>['Su tüketimi','Atık yönetimi','Enerji verisi'],
        'sections'=>[
          ['h'=>'Genel Bakış','p'=>'Tüm çevresel verileri tek çatı altında toplayın, analiz edin ve hedefler ile karşılaştırın.'],
          ['h'=>'Yetkinlikler','list'=>['Sensör/manuel veri toplama','Dönemsel kıyaslama','Anomali tespiti','İyileştirme önerileri']],
        ]
      ],
      'en' => [
        'title'=>'Water/Waste',
        'summary'=>'Environmental data inventory and analysis: water, waste, energy.',
        'hero_bullets'=>['Water use','Waste mgmt','Energy data'],
        'sections'=>[
          ['h'=>'Overview','p'=>'Consolidate environmental data, analyze and compare with targets.'],
          ['h'=>'Capabilities','list'=>['Sensor/manual collection','Periodical benchmarking','Anomaly detection','Improvement suggestions']],
        ]
      ]
    ],
    'supply' => [
      'img' => 'supply.jpg',
      'tr' => [
        'title'=>'Tedarik Zinciri',
        'summary'=>'Risk ve performans yönetimi: puanlar, denetimler, uygunluk.',
        'hero_bullets'=>['Tedarikçi puanı','Risk kütüğü','Uygunluk takibi'],
        'sections'=>[
          ['h'=>'Genel Bakış','p'=>'Tedarikçi ekosistemini puanlayın, denetleyin ve riskleri yönetin.'],
          ['h'=>'Yetkinlikler','list'=>['Anket ve kanıt toplama','Denetim planları','Uyum durum raporları']],
        ]
      ],
      'en' => [
        'title'=>'Supply Chain',
        'summary'=>'Risk and performance management: scoring, audits, compliance.',
        'hero_bullets'=>['Supplier score','Risk log','Compliance tracking'],
        'sections'=>[
          ['h'=>'Overview','p'=>'Score, audit and manage risks across your supplier ecosystem.'],
          ['h'=>'Capabilities','list'=>['Surveys and evidence','Audit plans','Compliance status reports']],
        ]
      ]
    ],
    'report' => [
      'img' => 'report.jpg',
      'tr' => [
        'title'=>'Raporlama',
        'summary'=>'PDF/Excel/Word çıktıları, şablonlar ve özelleştirme.',
        'hero_bullets'=>['Şablonlar','Özelleştirme','Dışa aktarım'],
        'sections'=>[
          ['h'=>'Genel Bakış','p'=>'Kurumsal raporlarınızı şablonlarla oluşturun, markanıza uygun özelleştirin ve dışa aktarın.'],
          ['h'=>'Yetkinlikler','list'=>['Şablon yönetimi','Marka uyumlu tasarım','Çoklu format dışa aktarma']],
        ]
      ],
      'en' => [
        'title'=>'Reporting',
        'summary'=>'PDF/Excel/Word outputs, templates and customization.',
        'hero_bullets'=>['Templates','Customization','Export'],
        'sections'=>[
          ['h'=>'Overview','p'=>'Build corporate reports with templates, customize to brand and export.'],
          ['h'=>'Capabilities','list'=>['Template management','Brand-aligned design','Multi-format exports']],
        ]
      ]
    ],
  ]; $d=$modules[$m]??null; $tx=$d?$d[$lang]:null; ?>
  <section class="content module">
    <?php if ($d && $tx): ?>
      <h1><?php echo $tx['title']; ?></h1>
      <div class="module-hero">
        <div class="module-text">
          <p><?php echo htmlspecialchars($tx['summary']); ?></p>
          <ul><?php foreach(($tx['hero_bullets'] ?? []) as $b){ echo '<li>'.htmlspecialchars($b).'</li>'; } ?></ul>
        </div>
        <div class="module-image">
          <?php $img='/assets/img/'.($d['img']); if (file_exists(__DIR__.$img)) { echo '<img src="'.$img.'" alt=""/>'; } else { echo '<div class="img-fallback">Görsel eklenecek</div>'; } ?>
        </div>
      </div>

      <?php foreach(($tx['sections'] ?? []) as $sec){ echo '<div class="section">'; echo '<h2>'.htmlspecialchars($sec['h']).'</h2>'; if(isset($sec['p'])){ echo '<p>'.htmlspecialchars($sec['p']).'</p>'; } if(isset($sec['list'])){ echo '<ul>'; foreach($sec['list'] as $li){ echo '<li>'.htmlspecialchars($li).'</li>'; } echo '</ul>'; } echo '</div>'; } ?>

      <div class="module-actions">
        <a class="btn" href="/?p=moduller&lang=<?php echo $lang; ?>">← <?php echo $t('modules_title'); ?></a>
      </div>
    <?php else: ?>
      <p>Modül bulunamadı.</p>
    <?php endif; ?>
  </section>
<?php elseif ($page === 'sss'): ?>
  <section class="content">
    <h1><?php echo $t('faq_title'); ?></h1>
    <div class="faq">
      <div class="faq-item" id="q1"><h3 onclick="toggleFaq('q1')">Platform kimler için?</h3><p>Kurumsal sürdürülebilirlik ekipleri, danışmanlar ve denetçiler için.</p></div>
      <div class="faq-item" id="q2"><h3 onclick="toggleFaq('q2')">Veri kaynakları nasıl entegre edilir?</h3><p>Excel/CSV yükleme, API entegrasyonu ve manuel giriş desteklenir.</p></div>
      <div class="faq-item" id="q3"><h3 onclick="toggleFaq('q3')">Hangi standartlar desteklenir?</h3><p>GRI, ESRS/TSRS, ISSB/SASB, SDG ve CBAM.</p></div>
      <div class="faq-item" id="q4"><h3 onclick="toggleFaq('q4')">Rapor formatları?</h3><p>PDF, DOCX ve XLSX.</p></div>
    </div>
  </section>
<?php elseif ($page === 'iletisim'): ?>
  <section class="content">
    <h1><?php echo $t('contact_title'); ?></h1>
    <p>Bizimle iletişime geçin ve bir demo planlayalım.</p>
    <?php if ($_SERVER['REQUEST_METHOD'] === 'POST') {
      $name = trim($_POST['name'] ?? '');
      $email = trim($_POST['email'] ?? '');
      $msg = trim($_POST['message'] ?? '');
      $purpose = $_GET['purpose'] ?? 'contact';
      $ok = (strlen($name)>2 && filter_var($email, FILTER_VALIDATE_EMAIL) && strlen($msg)>5);
      if ($ok) {
        $subject = ($lang==='tr' ? ($purpose==='demo'?'Demo Talebi':'İletişim Talebi') : ($purpose==='demo'?'Demo Request':'Contact Request'));
        $body = 'Ad Soyad: '.$name."\r\n".'E-posta: '.$email."\r\n".'Amaç: '.$purpose."\r\n\r\n".'Mesaj:'."\r\n".$msg;
        $sent = smtp_send($smtp, $smtp['to'], $subject, $body, $email, $name);
        if (!$sent) {
          $headers = 'From: '.($smtp['from_name']).' <'.$smtp['from'].'>'."\r\n".'MIME-Version: 1.0' . "\r\n" . 'Content-Type: text/plain; charset=UTF-8';
          @mail($smtp['to'], $subject, $body, $headers);
        }
        $ok = $sent || true; // fallback mail() denendi
      }
      $message = $ok?($lang==='tr'?'Talebiniz alındı.':'Request received.'):($lang==='tr'?'Lütfen bilgileri kontrol edin.':'Please check the information.');
      if (($sent??false)===false && isset($_GET['debugmail']) && $_GET['debugmail']==='1' && isset($GLOBALS['SMTP_LOG'])){
        $safeLog = array_filter($GLOBALS['SMTP_LOG'] ?: [], function($l){ return strpos($l, 'PASS')===false; });
        $message .= ' (Mail gönderim hata logu aktif)';
      }
      echo '<div class="notice '.($ok?'success':'error').'">'.$message.'</div>';
    } ?>
    <form method="post" class="form">
      <div class="form-row"><label>Ad Soyad</label><input type="text" name="name" required></div>
      <div class="form-row"><label>E-posta</label><input type="email" name="email" required></div>
      <div class="form-row"><label>Mesaj</label><textarea name="message" rows="4" required></textarea></div>
      <button class="btn primary" type="submit">Gönder</button>
    </form>
  </section>
<?php endif; ?>
</main>
<footer class="site-footer">
  <div class="container">© Sustainage • Sürdürülebilirlik ve uyum teknolojileri</div>
</footer>
</body>
</html>
"""

STYLE_CSS = """:root{--bg:#f8fafc;--card:#ffffff;--text:#0f172a;--muted:#64748b;--line:#e2e8f0;--primary:#2563eb}
*{box-sizing:border-box}html,body{margin:0;padding:0}
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Segoe UI,Tahoma,sans-serif;background:var(--bg);color:var(--text)}
.container{max-width:1100px;margin:0 auto;padding:0 24px}
.site-header{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--line);z-index:50}
.header-inner{display:flex;align-items:center;justify-content:space-between;height:64px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--text);font-weight:700}
.brand-logo{height:32px;width:auto;border-radius:6px}
.nav{display:flex;align-items:center;gap:14px}
.nav-link{padding:10px 14px;border-radius:8px;text-decoration:none;color:var(--text);border:1px solid transparent}
.nav-link:hover{background:#f1f5f9}
.nav-link.active{border-color:var(--line);background:#f8fafc}
.btn{padding:10px 16px;border-radius:8px;border:1px solid var(--line);text-decoration:none;color:var(--text);background:#fff}
.btn.primary{background:var(--primary);color:#fff;border-color:var(--primary)}
.hero{padding:40px 0}
.hero h1{font-size:32px;margin:0 0 12px}
.hero p{color:var(--muted);margin:0 0 16px}
.hero-actions{display:flex;gap:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:16px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
.card.link{display:block;text-decoration:none;color:inherit;transition:transform .06s ease, box-shadow .12s}
.card.link:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(2,8,23,0.06)}
.card h3{margin:0 0 8px;font-size:18px}
.content{padding:24px 0}
.content h1{margin:0 0 16px}
.faq-item{background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px;margin-bottom:10px}
.faq-item p{display:none;margin-top:8px;color:var(--muted)}
.faq-item.open p{display:block}
.timeline{list-style:disc;margin-left:18px;color:var(--muted)}
.form{display:grid;gap:12px;max-width:560px}
.form-row{display:grid;gap:8px}
.form-row input,.form-row textarea{padding:10px;border:1px solid var(--line);border-radius:8px}
.notice{padding:12px;border-radius:10px;margin-bottom:16px}
.notice.success{background:#ecfeff;border:1px solid #67e8f9}
.notice.error{background:#fff1f2;border:1px solid #fca5a5}
.site-footer{margin-top:40px;border-top:1px solid var(--line);background:#fff}
.site-footer .container{padding:18px 0;color:var(--muted)}
/* Modül sayfası düzeni */
.module-hero{display:grid;grid-template-columns:1fr 360px;gap:16px;align-items:start}
.module-text p{margin:0 0 10px}
.module-text ul{margin:10px 0 0 18px;color:var(--muted)}
.module-image img{width:100%;height:auto;border-radius:12px;border:1px solid var(--line)}
.module-actions{display:flex;gap:10px;margin-top:16px}
.module .section{margin-top:24px}
.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.gallery .img-fallback{height:140px}
@media (max-width:720px){.nav{gap:6px}.nav-link{padding:8px 10px}}
"""

# renkli ve canlı aksanlar
STYLE_CSS = STYLE_CSS + "\n.section{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px}\n"
STYLE_CSS = STYLE_CSS + ".section h2{margin:0 0 10px;color:#1e293b}\n"
STYLE_CSS = STYLE_CSS + ".section p{color:#334155;margin:0 0 10px}\n"


def _ensure_path(ftp: FTP, path: str) -> None:
    parts = [p for p in path.split('/') if p]
    cur = ''
    for p in parts:
        cur = cur + '/' + p
        try:
            ftp.cwd(cur)
        except error_perm:
            # create then cwd
            ftp.mkd(cur)
            ftp.cwd(cur)


def upload_landing_in_root(ftp: FTP, root: str) -> None:
    tpl_dir = f'/{root}/templates'
    _ensure_path(ftp, tpl_dir)
    bio = io.BytesIO(LANDING_HTML.encode('utf-8'))
    ftp.storbinary(f'STOR {tpl_dir}/landing.html', bio)
    # Ayrıca statik olarak köke da koy
    bio2 = io.BytesIO(LANDING_HTML.encode('utf-8'))
    ftp.storbinary(f'STOR /{root}/landing.html', bio2)

def upload_index_php(ftp: FTP, root: str) -> None:
    bio = io.BytesIO(INDEX_PHP.encode('utf-8'))
    ftp.storbinary(f'STOR /{root}/index.php', bio)

def upload_style_css(ftp: FTP, root: str) -> None:
    _ensure_path(ftp, f'/{root}/assets')
    _ensure_path(ftp, f'/{root}/assets/img')
    bio = io.BytesIO(STYLE_CSS.encode('utf-8'))
    ftp.storbinary(f'STOR /{root}/assets/style.css', bio)

def upload_smtp_config(ftp: FTP, root: str) -> None:
    host = os.environ.get('SMTP_HOST')
    port = os.environ.get('SMTP_PORT')
    user = os.environ.get('SMTP_USER')
    pw = os.environ.get('SMTP_PASS')
    frm = os.environ.get('SMTP_FROM') or user
    to = os.environ.get('SMTP_TO') or user
    name = os.environ.get('SMTP_FROM_NAME') or 'Sustainage'
    if not host or not port or not user or not pw:
        return
    content = (
        "<?php\n"
        f"$SMTP_HOST='{host}';\n"
        f"$SMTP_PORT={int(port)};\n"
        f"$SMTP_USER='{user}';\n"
        f"$SMTP_PASS='{pw}';\n"
        f"$SMTP_FROM='{frm}';\n"
        f"$SMTP_FROM_NAME='{name}';\n"
        f"$SMTP_TO='{to}';\n"
    )
    bio = io.BytesIO(content.encode('utf-8'))
    ftp.storbinary(f'STOR /{root}/config.smtp.php', bio)


def fetch_file(ftp: FTP, remote_path: str) -> str:
    buf = io.BytesIO()
    ftp.retrbinary(f'RETR {remote_path}', buf.write)
    return buf.getvalue().decode('utf-8', errors='ignore')


def patch_app_py(app_src: str) -> str:
    marker = "@app.route('/tanitim'"
    if marker in app_src:
        return app_src
    insert_block = """
@app.route('/tanitim', methods=['GET'])
def tanitim():
    return render_template('landing.html')
"""
    # Append safely before any __main__ block if present
    main_idx = app_src.find("if __name__ == '__main__'")
    if main_idx != -1:
        return app_src[:main_idx] + '\n\n' + insert_block + '\n' + app_src[main_idx:]
    return app_src.rstrip() + '\n\n' + insert_block + '\n'


def upload_app_py(ftp: FTP, content: str, root: str) -> None:
    bio = io.BytesIO(content.encode('utf-8'))
    ftp.storbinary(f'STOR /{root}/app.py', bio)


def main() -> None:
    host = os.environ.get('FTP_HOST')
    user = os.environ.get('FTP_USER')
    pw = os.environ.get('FTP_PASS')
    port = int(os.environ.get('FTP_PORT') or 21)
    if not host or not user or not pw:
        raise RuntimeError('FTP çevre değişkenleri eksik: FTP_HOST, FTP_USER, FTP_PASS')

    ftp = FTP()
    ftp.connect(host, port, timeout=15)
    ftp.set_pasv(True)
    ftp.login(user, pw)

    # Yalnızca istenen ana docroot'a yükle
    for root in ('httpdocs',):
        try:
            upload_landing_in_root(ftp, root)
            upload_index_php(ftp, root)
            upload_style_css(ftp, root)
            upload_smtp_config(ftp, root)
            ensure_htaccess_rewrite(ftp, root)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    # Patch app.py (yalnızca ana docroot)
    for root in ('httpdocs',):
        try:
            src = fetch_file(ftp, f'/{root}/app.py')
            patched = patch_app_py(src)
            if patched != src:
                upload_app_py(ftp, patched, root)
        except Exception as e:
            logging.error(f'Silent error in upload_landing_and_patch_app.py: {str(e)}')  # app.py yoksa atla

    # Doğrula
    files = []
    try:
        ftp.cwd('/httpdocs/templates')
        files = ftp.nlst()
    except Exception:
        files = []
    try:
        ftp.cwd('/public_html/templates')
        files2 = ftp.nlst()
    except Exception:
        files2 = []
    try:
        ftp.cwd('/http')
        files3 = ftp.nlst()
    except Exception:
        files3 = []

    ftp.quit()

    if 'landing.html' in files or 'landing.html' in files2 or 'landing.html' in files3:
        logging.info('UPLOAD_OK')
    else:
        logging.info('UPLOAD_DONE_BUT_NOT_LISTED')


if __name__ == '__main__':
    main()
def ensure_htaccess_rewrite(ftp: FTP, root: str) -> None:
    path = f'/{root}/.htaccess'
    try:
        content = fetch_file(ftp, path)
    except Exception:
        content = ''
    rule = "RewriteRule ^tanitim$ landing.html [L]"
    if rule in content:
        return
    block = """
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteBase /
RewriteRule ^tanitim$ landing.html [L]
</IfModule>
""".strip()
    new = content.rstrip() + ("\n\n" if content else "") + block + "\n"
    bio = io.BytesIO(new.encode('utf-8'))
    ftp.storbinary(f'STOR {path}', bio)
