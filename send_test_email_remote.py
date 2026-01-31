import sys
import os

sys.path.append('/var/www/sustainage')

try:
    from services.email_service import EmailService
except ImportError as e:
    print(f"Error importing EmailService: {e}")
    sys.exit(1)


def send_all_test_emails():
    print("Initializing EmailService...")
    try:
        email_service = EmailService()
    except Exception as e:
        print(f"Error initializing EmailService: {e}")
        sys.exit(1)

    to_email = "kivanc.kasoglu@sustainage.tr"

    total = 0
    success_count = 0

    def run(label, func):
        nonlocal total, success_count
        total += 1
        print(f"\n--- {label} ---")
        try:
            ok = func()
            if ok:
                print(f"{label}: OK")
                success_count += 1
            else:
                print(f"{label}: FAILED (returned False)")
        except Exception as ex:
            print(f"{label}: ERROR -> {ex}")

    run(
        "Basic HTML test",
        lambda: email_service.send_email(
            to_email,
            "Sistem Test Maili - Sustainage (Basic)",
            """
<!DOCTYPE html>
<html>
<body>
    <h1>Merhaba,</h1>
    <p>Bu bir temel test mailidir. Uzak sunucudan gönderilmektedir.</p>
    <p>Sustainage SDG Platform</p>
</body>
</html>
""",
        ),
    )

    run(
        "Yeni kullanıcı hoş geldiniz",
        lambda: email_service.send_template_email(
            to_email,
            "new_user_welcome",
            {
                "program_name": "Sustainage SDG Platformu",
                "user_name": "Test Kullanıcı",
                "short_description": "Bu bir test hoş geldiniz e-postasıdır.",
                "login_url": "https://sustainage.cloud/login",
                "support_email": "sdg@sustainage.tr",
            },
        ),
    )

    run(
        "Yeni kullanıcı giriş bilgileri",
        lambda: email_service.send_template_email(
            to_email,
            "new_user_credentials",
            {
                "user_name": "Test Kullanıcı",
                "username": "test.user",
                "temp_password": "Test1234!",
                "login_url": "https://sustainage.cloud/login",
            },
        ),
    )

    run(
        "Anket daveti",
        lambda: email_service.send_template_email(
            to_email,
            "survey_invitation",
            {
                "stakeholder_name": "Test Paydaş",
                "company_name": "Sustainage A.Ş.",
                "survey_name": "Sürdürülebilirlik Önceliklendirme Anketi",
                "survey_description": "Bu anket, sürdürülebilirlik konularının önem düzeyini belirlemek için hazırlanmıştır.",
                "survey_url": "https://sustainage.cloud/survey/test",
                "deadline_date": "2026-12-31",
            },
        ),
    )

    run(
        "Anket hatırlatma",
        lambda: email_service.send_template_email(
            to_email,
            "survey_reminder",
            {
                "stakeholder_name": "Test Paydaş",
                "company_name": "Sustainage A.Ş.",
                "survey_name": "Sürdürülebilirlik Önceliklendirme Anketi",
                "deadline_date": "2026-12-31",
                "days_left": "7",
                "survey_url": "https://sustainage.cloud/survey/test",
            },
        ),
    )

    run(
        "Anket teşekkür maili",
        lambda: email_service.send_template_email(
            to_email,
            "survey_thank_you",
            {
                "stakeholder_name": "Test Paydaş",
                "survey_name": "Sürdürülebilirlik Önceliklendirme Anketi",
                "response_date": "2026-01-17",
            },
        ),
    )

    run(
        "Görev atandı bildirimi",
        lambda: email_service.send_template_email(
            to_email,
            "task_assigned",
            {
                "task_title": "SDG 7 - Enerji Tüketimi Verileri",
                "task_description": "Son 12 aylık enerji tüketim verilerini sisteme giriniz.",
                "priority": "Yüksek",
                "due_date": "2026-02-01",
                "assigned_by": "Sustainage Yönetici",
                "task_url": "https://sustainage.cloud/",
            },
        ),
    )

    run(
        "Görev güncellendi bildirimi",
        lambda: email_service.send_template_email(
            to_email,
            "task_updated",
            {
                "task_title": "SDG 7 - Enerji Tüketimi Verileri",
                "status": "Devam ediyor",
                "progress": "50",
                "note": "İlk veri seti başarıyla girildi.",
            },
        ),
    )

    run(
        "Görev tamamlandı bildirimi",
        lambda: email_service.send_template_email(
            to_email,
            "task_completed",
            {
                "task_title": "SDG 7 - Enerji Tüketimi Verileri",
                "completion_date": "2026-01-17",
                "completed_by": "Test Kullanıcı",
            },
        ),
    )

    run(
        "Şifre sıfırlama maili",
        lambda: email_service.send_password_reset_email(
            to_email,
            "Test Kullanıcı",
            "123456",
        ),
    )

    print(f"\nToplam: {total}, Başarılı: {success_count}, Başarısız: {total - success_count}")


if __name__ == "__main__":
    send_all_test_emails()
