import sqlite3
import os
import ftplib
import json
import traceback

# FTP Bilgileri
FTP_HOST = "72.62.150.207"
FTP_USER = "cursorsustainageftp"
FTP_PASS = "Kayra_1507_Sk!"
REMOTE_DB_PATH = "/httpdocs/backend/data/sdg_desktop.sqlite"
LOCAL_TEMP_DIR = "c:/SDG/temp_diagnose"
LOCAL_TEMP_DB = os.path.join(LOCAL_TEMP_DIR, "remote_db_populate.sqlite")

# Data Paths
SASB_METRICS_PATH = "c:/SDG/server/backend/modules/sasb/data/sasb_metrics.json"

def ensure_dir(path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

def populate_sasb(conn):
    print("Populating SASB Standards...")
    cursor = conn.cursor()
    
    # Check if empty
    cursor.execute("SELECT COUNT(*) FROM sasb_standards")
    if cursor.fetchone()[0] > 0:
        print("SASB Standards already populated. Skipping.")
        return

    try:
        if os.path.exists(SASB_METRICS_PATH):
            with open(SASB_METRICS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                metrics = data.get('sasb_metrics', [])
                
                for m in metrics:
                    cursor.execute("""
                        INSERT INTO sasb_standards (code, sector, topic, metric, unit)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        m.get('metric_code'),
                        "General", # Placeholder
                        m.get('topic_code'),
                        m.get('metric_name'),
                        m.get('unit_of_measure')
                    ))
            print(f"Inserted {len(metrics)} SASB metrics.")
        else:
            print(f"SASB metrics file not found at {SASB_METRICS_PATH}")
    except Exception as e:
        print(f"Error populating SASB: {e}")

def populate_tcfd(conn):
    print("Populating TCFD Recommendations...")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tcfd_recommendations")
    if cursor.fetchone()[0] > 0:
        print("TCFD Recommendations already populated. Skipping.")
        return

    recommendations = [
        ("Governance", "Board Oversight", "The board's oversight of climate-related risks and opportunities."),
        ("Governance", "Management Role", "Management's role in assessing and managing climate-related risks and opportunities."),
        ("Strategy", "Risks and Opportunities", "Climate-related risks and opportunities the organization has identified over the short, medium, and long term."),
        ("Strategy", "Impact on Organization", "The impact of climate-related risks and opportunities on the organization's businesses, strategy, and financial planning."),
        ("Strategy", "Resilience of Strategy", "The resilience of the organization's strategy, taking into consideration different climate-related scenarios, including a 2°C or lower scenario."),
        ("Risk Management", "Risk Identification", "The organization's processes for identifying and assessing climate-related risks."),
        ("Risk Management", "Risk Management", "The organization's processes for managing climate-related risks."),
        ("Risk Management", "Integration", "How processes for identifying, assessing, and managing climate-related risks are integrated into the organization's overall risk management."),
        ("Metrics and Targets", "Metrics", "The metrics used by the organization to assess climate-related risks and opportunities in line with its strategy and risk management process."),
        ("Metrics and Targets", "Scope 1, 2, 3 GHG Emissions", "Scope 1, Scope 2, and, if appropriate, Scope 3 greenhouse gas (GHG) emissions, and the related risks."),
        ("Metrics and Targets", "Targets", "The targets used by the organization to manage climate-related risks and opportunities and performance against targets.")
    ]

    for rec in recommendations:
        cursor.execute("INSERT INTO tcfd_recommendations (pillar, recommendation, description) VALUES (?, ?, ?)", rec)
    
    print(f"Inserted {len(recommendations)} TCFD recommendations.")

def populate_esrs(conn):
    print("Populating ESRS Standards...")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM esrs_standards")
    if cursor.fetchone()[0] > 0:
        print("ESRS Standards already populated. Skipping.")
        return

    standards = [
        ("ESRS 1", "General Requirements", "Cross-cutting", "General requirements for sustainability reporting"),
        ("ESRS 2", "General Disclosures", "Cross-cutting", "General disclosures regarding strategy, governance, and materiality"),
        ("E1", "Climate Change", "Environmental", "Climate change mitigation and adaptation"),
        ("E2", "Pollution", "Environmental", "Pollution of air, water, soil"),
        ("E3", "Water and Marine Resources", "Environmental", "Water consumption and marine resources"),
        ("E4", "Biodiversity and Ecosystems", "Environmental", "Biodiversity loss and ecosystem restoration"),
        ("E5", "Resource Use and Circular Economy", "Environmental", "Resource inflows and outflows, waste management"),
        ("S1", "Own Workforce", "Social", "Working conditions, equal treatment"),
        ("S2", "Workers in the Value Chain", "Social", "Working conditions in the value chain"),
        ("S3", "Affected Communities", "Social", "Impacts on local communities"),
        ("S4", "Consumers and End-users", "Social", "Impacts on consumers"),
        ("G1", "Business Conduct", "Governance", "Business ethics, anti-corruption")
    ]

    for std in standards:
        cursor.execute("INSERT INTO esrs_standards (code, title, category, description) VALUES (?, ?, ?, ?)", std)
    
    print(f"Inserted {len(standards)} ESRS standards.")

def populate_tnfd(conn):
    print("Populating TNFD Recommendations...")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tnfd_recommendations")
    if cursor.fetchone()[0] > 0:
        print("TNFD Recommendations already populated. Skipping.")
        return

    recommendations = [
        ("Governance", "Board Oversight", "Board oversight of nature-related dependencies, impacts, risks and opportunities."),
        ("Governance", "Management Role", "Management’s role in assessing and managing nature-related dependencies, impacts, risks and opportunities."),
        ("Strategy", "Nature-related Dependencies", "Nature-related dependencies, impacts, risks and opportunities identified over the short, medium, and long term."),
        ("Strategy", "Impact on Organization", "The impact of nature-related dependencies, impacts, risks and opportunities on the organization’s businesses, strategy, and financial planning."),
        ("Strategy", "Resilience of Strategy", "The resilience of the organization’s strategy to nature-related risks."),
        ("Strategy", "Locating Interfaces", "The locations of assets and activities in the organization’s direct operations and value chain that meet the criteria for priority locations."),
        ("Risk Management", "Identification Process", "The organization’s processes for identifying and assessing nature-related dependencies, impacts, risks and opportunities."),
        ("Risk Management", "Management Process", "The organization’s processes for managing nature-related dependencies, impacts, risks and opportunities."),
        ("Risk Management", "Integration", "How processes for identifying, assessing, and managing nature-related risks are integrated into the organization’s overall risk management."),
        ("Metrics and Targets", "Metrics", "The metrics used by the organization to assess and manage material nature-related dependencies, impacts, risks and opportunities."),
        ("Metrics and Targets", "Targets", "The targets used by the organization to manage nature-related dependencies, impacts, risks and opportunities and performance against targets.")
    ]

    for rec in recommendations:
        cursor.execute("INSERT INTO tnfd_recommendations (pillar, recommendation, description) VALUES (?, ?, ?)", rec)
    
    print(f"Inserted {len(recommendations)} TNFD recommendations.")

def main():
    ensure_dir(LOCAL_TEMP_DB)
    
    print(f"Connecting to FTP {FTP_HOST}...")
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print("Connected.")
        
        print(f"Downloading {REMOTE_DB_PATH}...")
        try:
            with open(LOCAL_TEMP_DB, 'wb') as f:
                ftp.retrbinary(f'RETR {REMOTE_DB_PATH}', f.write)
            print("Download complete.")
        except Exception as e:
            print(f"Download failed: {e}")
            ftp.quit()
            return

        conn = sqlite3.connect(LOCAL_TEMP_DB)
        
        populate_sasb(conn)
        populate_tcfd(conn)
        populate_esrs(conn)
        populate_tnfd(conn)
        
        conn.commit()
        conn.close()
        
        print(f"Uploading populated DB back to {REMOTE_DB_PATH}...")
        with open(LOCAL_TEMP_DB, 'rb') as f:
            ftp.storbinary(f'STOR {REMOTE_DB_PATH}', f)
        print("Upload complete.")
        
        ftp.quit()
        print("\nSUCCESS: Remote database populated with standard data.")
        
    except Exception as e:
        print(f"FTP/Processing Error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()
