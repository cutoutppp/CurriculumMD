import docx

def check_structure(p):
    print(f"\n=== {p} ===")
    doc = docx.Document(p)
    for t_idx, table in enumerate(doc.tables):
        print(f"Table {t_idx} (rows: {len(table.rows)}, cols: {len(table.columns)})")
        for r_idx, row in enumerate(table.rows[:15]):
            txt = " | ".join(c.text.strip().replace('\n', ' ') for c in row.cells)
            print(f"  R{r_idx}: {txt[:120]}")

check_structure('school_curriculum_raw/หลักสูตรกลุ่มสาระฯ 69/วิทยาศาสตร์และ IS 69/รวมหลักสูตร ม.ต้น/โครงสร้าง_ต้น_69.docx')
check_structure('school_curriculum_raw/หลักสูตรกลุ่มสาระฯ 69/วิทยาศาสตร์และ IS 69/รวมหลักสูตร ม.ปลาย/โครงสร้างรายวิชา-ุรวม69.docx')
