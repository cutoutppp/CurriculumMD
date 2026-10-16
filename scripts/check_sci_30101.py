import docx

doc = docx.Document('school_curriculum_raw/หลักสูตรกลุ่มสาระฯ 69/วิทยาศาสตร์และ IS 69/ม.4/ว30101_ณรัณทร/1.คำอธิบายรายวิชา_ว30101.docx')
for i, p in enumerate(doc.paragraphs):
    if p.text.strip():
        print(f"P{i}: {p.text.strip()}")
