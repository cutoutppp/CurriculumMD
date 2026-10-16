import docx
import os

def check_tech():
    with open('tech_audit.txt', 'w', encoding='utf-8') as out:
        tech_root = 'school_curriculum_raw/หลักสูตรกลุ่มสาระฯ 69/เทคโนโลยี 69'
        for r, d, files in os.walk(tech_root):
            for f in files:
                if f.endswith('.docx'):
                    p = os.path.join(r, f)
                    out.write(f"\n=== FILE: {p} ===\n")
                    try:
                        doc = docx.Document(p)
                        for i, para in enumerate(doc.paragraphs):
                            t = para.text.strip()
                            if any(k in t for k in ['รหัส', 'ตัวชี้วัด', 'ผลการเรียนรู้', 'ว 4.', 'ว4.']):
                                out.write(f"  P{i}: {t}\n")
                    except Exception as e:
                        out.write(f"  ERR: {e}\n")

check_tech()
print("tech_audit.txt written")
