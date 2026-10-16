import docx

for f in ['รหัสวิชา23101วิทย์5.docx', 'รหัสวิชา23101วิทย์6.docx']:
    path = f'school_curriculum_raw/หลักสูตรกลุ่มสาระฯ 69/วิทยาศาสตร์และ IS 69/ม.3/เยาวลักษณ์_ว 23101_ว 23102/{f}'
    doc = docx.Document(path)
    print(f"=== {f} ===")
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if any(k in t for k in ['รหัส', 'ตัวชี้วัด', 'ว 2.1', 'ว 2.3']):
            print(f"  P{i}: {t}")
