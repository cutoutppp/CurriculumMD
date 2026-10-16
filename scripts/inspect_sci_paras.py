import docx

def check_file(path, out):
    out.write(f"\n=================== {path} ===================\n")
    doc = docx.Document(path)
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if not t:
            continue
        if any(h in t for h in ['รหัสวิชา', 'รหัส ว', 'คำอธิบายรายวิชาพื้นฐาน', 'ตัวชี้วัด', 'ว 1.', 'ว 2.', 'ว 3.', 'ว 4.']):
            out.write(f"P{i}: {t}\n")

with open('sci_paras_out_utf8.txt', 'w', encoding='utf-8') as out:
    check_file('school_curriculum_raw/หลักสูตรกลุ่มสาระฯ 69/วิทยาศาสตร์และ IS 69/รวมหลักสูตร ม.ต้น/คำอธิบายรายวิชา_ต้น_69.docx', out)
    check_file('school_curriculum_raw/หลักสูตรกลุ่มสาระฯ 69/วิทยาศาสตร์และ IS 69/รวมหลักสูตร ม.ปลาย/คำอธิบายรายวิชาพื้นฐาน-รวม69.docx', out)

print("done")
