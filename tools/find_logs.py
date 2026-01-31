import ftplib
import os

FTP_HOST = "72.62.150.207"
FTP_USER = "cursorsustainageftp"
FTP_PASS = "Kayra_1507_Sk!"

def find_logs_ftp():
    print(f"Connecting to FTP {FTP_HOST}...")
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print("Connected.")
        
        # List root directory
        print("\nListing root directory:")
        try:
            ftp.dir()
        except Exception as e:
            print(f"Error listing root: {e}")

        # Try to find logs directory
        potential_paths = ['/logs', '/statistics/logs', '/var/log', 'logs']
        
        for path in potential_paths:
            print(f"\nChecking {path}...")
            try:
                ftp.cwd(path)
                print(f"Success! Listing {path}:")
                ftp.dir()
                
                # If we find error_log, try to read the last few lines
                files = ftp.nlst()
                for log_file in ['error_log', 'proxy_error_log', 'error.log']:
                    if log_file in files:
                        print(f"\nReading tail of {path}/{log_file}...")
                        
                        # Read the file content
                        # Since files can be large, we might want to just get the tail.
                        # But FTP doesn't support 'tail'. We have to download it or read it all.
                        # We'll read it and print the last 20 lines.
                        
                        lines = []
                        def handle_line(line):
                            lines.append(line)
                            
                        ftp.retrlines(f'RETR {log_file}', handle_line)
                        
                        print(f"--- Last 20 lines of {log_file} ---")
                        for line in lines[-20:]:
                            print(line)
                        print("-----------------------------------")
                        
                ftp.cwd('/') # Go back to root
            except Exception as e:
                print(f"Could not access {path}: {e}")
                try:
                    ftp.cwd('/') # Ensure we are back at root
                except:
                    pass

        ftp.quit()
    except Exception as e:
        print(f"FTP Error: {e}")

if __name__ == "__main__":
    find_logs_ftp()
