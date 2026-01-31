import ftplib
import os

FTP_HOST = "72.62.150.207"
FTP_USER = "cursorsustainageftp"
FTP_PASS = "Kayra_1507_Sk!"

def deploy_test():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        
        with open('c:/SDG/test_cgi.py', 'rb') as f:
            ftp.storbinary('STOR /httpdocs/test_cgi.py', f)
        
        # Try to chmod
        try:
            ftp.sendcmd('SITE CHMOD 755 /httpdocs/test_cgi.py')
            print("Chmod 755 success")
        except:
            print("Chmod failed (might not be supported)")
            
        ftp.quit()
        print("Uploaded test_cgi.py")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    deploy_test()
