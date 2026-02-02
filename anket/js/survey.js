/**
 * Sustainage Anket Sistemi - JavaScript
 * Tarih: 2025-10-23
 * Form validasyonu ve kullanıcı deneyimi iyileştirmeleri
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ==================== FORM ELEMENTI ====================
    const form = document.getElementById('surveyForm');
    if (!form) return;
    
    const submitBtn = document.getElementById('submitBtn');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const topicCards = document.querySelectorAll('.topic-card');
    const totalTopics = topicCards.length;
    
    // ==================== İLERLEME TAKİBİ ====================
    let completedTopics = 0;
    const topicStatus = {};
    
    // Her konu için durum takibi başlat
    topicCards.forEach((card, index) => {
        const topicCode = card.querySelector('.importance-input').dataset.topic;
        topicStatus[topicCode] = {
            importance: false,
            impact: false
        };
    });
    
    /**
     * İlerleme çubuğunu güncelle
     */
    function updateProgress() {
        completedTopics = 0;
        
        // Tamamlanan konuları say
        Object.keys(topicStatus).forEach(topicCode => {
            if (topicStatus[topicCode].importance && topicStatus[topicCode].impact) {
                completedTopics++;
            }
        });
        
        // Progress bar güncelle
        const percentage = (completedTopics / totalTopics) * 100;
        progressFill.style.width = percentage + '%';
        progressText.textContent = `Tamamlanan: ${completedTopics}/${totalTopics}`;
        
        // Tamamlanan kartları işaretle
        topicCards.forEach(card => {
            const topicCode = card.querySelector('.importance-input').dataset.topic;
            if (topicStatus[topicCode].importance && topicStatus[topicCode].impact) {
                card.classList.add('completed');
            } else {
                card.classList.remove('completed');
            }
        });
        
        // Submit butonunu aktif/pasif yap
        if (completedTopics === totalTopics) {
            submitBtn.disabled = false;
            submitBtn.style.opacity = '1';
        } else {
            submitBtn.disabled = false; // Her durumda gönder (HTML5 validation çalışacak)
        }
    }
    
    /**
     * Radio butonlarına event listener ekle
     */
    function attachRadioListeners() {
        // Önem derecesi
        document.querySelectorAll('.importance-input').forEach(input => {
            input.addEventListener('change', function() {
                const topicCode = this.dataset.topic;
                topicStatus[topicCode].importance = true;
                updateProgress();
                
                // Animasyon ekle
                this.closest('.rating-group').classList.add('completed');
                setTimeout(() => {
                    this.closest('.rating-group').classList.remove('completed');
                }, 300);
            });
        });
        
        // Etki derecesi
        document.querySelectorAll('.impact-input').forEach(input => {
            input.addEventListener('change', function() {
                const topicCode = this.dataset.topic;
                topicStatus[topicCode].impact = true;
                updateProgress();
                
                // Animasyon ekle
                this.closest('.rating-group').classList.add('completed');
                setTimeout(() => {
                    this.closest('.rating-group').classList.remove('completed');
                }, 300);
            });
        });
    }
    
    attachRadioListeners();
    
    // ==================== FORM VALİDASYONU ====================
    form.addEventListener('submit', function(e) {
        // Temel bilgiler kontrolü
        const stakeholderName = document.getElementById('stakeholder_name').value.trim();
        const stakeholderEmail = document.getElementById('stakeholder_email').value.trim();
        
        if (!stakeholderName || !stakeholderEmail) {
            e.preventDefault();
            showNotification('Lütfen adınızı ve e-posta adresinizi girin.', 'error');
            return false;
        }
        
        // Email formatı kontrolü
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(stakeholderEmail)) {
            e.preventDefault();
            showNotification('Lütfen geçerli bir e-posta adresi girin.', 'error');
            return false;
        }
        
        // Her konu için kontrol
        let allCompleted = true;
        let missingTopics = [];
        
        topicCards.forEach((card, index) => {
            const topicName = card.querySelector('h3') ? card.querySelector('h3').textContent.trim() : `Konu ${index + 1}`;
            const topicCode = card.querySelector('.importance-input') ? card.querySelector('.importance-input').dataset.topic : '';
            
            if (!topicCode) return; // Eğer topic code yoksa atla
            
            const importanceChecked = card.querySelector(`input[name="importance_${topicCode}"]:checked`);
            const impactChecked = card.querySelector(`input[name="impact_${topicCode}"]:checked`);
            
            if (!importanceChecked || !impactChecked) {
                allCompleted = false;
                if (topicName) {
                    missingTopics.push(topicName);
                }
            }
        });
        
        if (!allCompleted && missingTopics.length > 0) {
            e.preventDefault();
            
            let message = 'Lütfen tüm konuları değerlendirin.\n\nEksik konular:\n';
            missingTopics.forEach((topic, i) => {
                message += `${i + 1}. ${topic}\n`;
            });
            
            showNotification(message, 'warning');
            
            // İlk eksik konuya scroll
            const firstMissing = document.querySelector('.topic-card:not(.completed)');
            if (firstMissing) {
                firstMissing.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstMissing.style.border = '3px solid #D32F2F';
                setTimeout(() => {
                    firstMissing.style.border = '';
                }, 2000);
            }
            
            return false;
        }
        
        // Onay penceresi
        const confirmed = confirm(
            `Anketi göndermek üzeresiniz.\n\n` +
            `Değerlendirilen konu sayısı: ${totalTopics}\n` +
            `Paydaş: ${stakeholderName}\n` +
            `E-posta: ${stakeholderEmail}\n\n` +
            `Form gönderildikten sonra değişiklik yapılamaz.\n\n` +
            `Devam etmek istiyor musunuz?`
        );
        
        if (!confirmed) {
            e.preventDefault();
            return false;
        }
        
        // Gönder butonunu devre dışı bırak (çift tıklama önleme)
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Gönderiliyor...';
        
        // beforeunload event'ini devre dışı bırak (çıkış uyarısını kaldır)
        window.onbeforeunload = null;
        
        return true;
    });
    
    // ==================== OTOMATIK KAYDETME (LocalStorage) ====================
    const formInputs = form.querySelectorAll('input[type="text"], input[type="email"], textarea');
    const surveyToken = document.querySelector('input[name="token"]').value;
    const storageKey = `sustainage_survey_${surveyToken}`;
    
    /**
     * Formu LocalStorage'a kaydet
     */
    function saveFormData() {
        const formData = {};
        
        formInputs.forEach(input => {
            if (input.value) {
                formData[input.name] = input.value;
            }
        });
        
        // Radio butonları kaydet
        document.querySelectorAll('input[type="radio"]:checked').forEach(radio => {
            formData[radio.name] = radio.value;
        });
        
        localStorage.setItem(storageKey, JSON.stringify(formData));
    }
    
    /**
     * LocalStorage'dan formu yükle
     */
    function loadFormData() {
        const savedData = localStorage.getItem(storageKey);
        if (!savedData) return;
        
        try {
            const formData = JSON.parse(savedData);
            
            // Text ve email inputları doldur
            Object.keys(formData).forEach(key => {
                const input = document.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'radio') {
                        const radio = document.querySelector(`[name="${key}"][value="${formData[key]}"]`);
                        if (radio) {
                            radio.checked = true;
                            // Status güncelle
                            const topicCode = radio.dataset.topic;
                            if (radio.classList.contains('importance-input')) {
                                topicStatus[topicCode].importance = true;
                            } else if (radio.classList.contains('impact-input')) {
                                topicStatus[topicCode].impact = true;
                            }
                        }
                    } else {
                        input.value = formData[key];
                    }
                }
            });
            
            updateProgress();
            
            // Bilgilendirme göster
            showNotification('✓ Kaydedilmiş verileriniz yüklendi', 'success');
            
        } catch (e) {
            console.error('Form verileri yüklenemedi:', e);
        }
    }
    
    // Otomatik kaydetme (her değişiklikte)
    formInputs.forEach(input => {
        input.addEventListener('input', saveFormData);
    });
    
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', saveFormData);
    });
    
    // Sayfa yüklendiğinde kaydedilmiş verileri yükle
    loadFormData();
    
    // Form gönderildiğinde LocalStorage'ı temizle
    form.addEventListener('submit', function() {
        localStorage.removeItem(storageKey);
    });
    
    // ==================== KLAVYE KISAYOLLARI ====================
    document.addEventListener('keydown', function(e) {
        // Ctrl+S ile kaydet
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            saveFormData();
            showNotification('✓ İlerlemeniz kaydedildi!', 'success');
        }
        
        // Escape ile onay
        if (e.key === 'Escape') {
            if (confirm('Anketten çıkmak istediğinizden emin misiniz?\n\nİlerlemeniz kaydedildi, daha sonra devam edebilirsiniz.')) {
                window.location.href = 'index.php';
            }
        }
    });
    
    // ==================== SAYFA ÇIKIŞ UYARISI ====================
    window.addEventListener('beforeunload', function(e) {
        // Eğer form doldurulmaya başlanmışsa uyar
        if (completedTopics > 0 && completedTopics < totalTopics) {
            e.preventDefault();
            e.returnValue = 'Anketi doldurmayı bitirmediniz. Çıkmak istediğinizden emin misiniz?';
            return e.returnValue;
        }
    });
    
    // ==================== SMOOTH SCROLL ====================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    // ==================== RESPONSIVE TABLO ====================
    // Mobilde tabloları kaydırılabilir yap
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        const wrapper = document.createElement('div');
        wrapper.style.cssText = 'overflow-x: auto; -webkit-overflow-scrolling: touch;';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
    
    // ==================== BAŞLANGIÇ MESAJI ====================
    // Console logları temizlendi
    
    // İlk yüklemede progress güncelle
    updateProgress();
});

// ==================== CSS ANIMATIONS ====================
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
    
    .rating-group.completed {
        animation: pulse 0.3s ease;
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
`;
document.head.appendChild(style);

