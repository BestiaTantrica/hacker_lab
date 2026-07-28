import sqlite3, json
db_path = '/home/ubuntu/c2_panel/c2_db.sqlite'
with open('/home/ubuntu/nuclei_forced.json', 'r') as f:
    data = json.load(f)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(findings)')
cols = [col[1] for col in cursor.fetchall()]
if 'status_interno' not in cols:
    cursor.execute('ALTER TABLE findings ADD COLUMN status_interno TEXT DEFAULT "Pendiente"')

inserted = 0
for finding in data:
    target = finding.get('host', 'N/A')
    vuln_type = finding.get('info', {}).get('name', 'Unknown')
    severity = finding.get('info', {}).get('severity', 'High')
    evidence = json.dumps(finding)
    
    cursor.execute('''
        INSERT INTO findings (target, vuln_type, severity, evidence, status_interno, verified)
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (target, vuln_type, severity, evidence, 'Pendiente'))
    inserted += 1
    
conn.commit()
conn.close()
print(f'Successfully inserted {inserted} findings into OCI-2.')
