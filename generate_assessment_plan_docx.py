import os
import re
import json
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_border(cell, **kwargs):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f'w:{edge}'
            element = parse_xml(f'<{tag} {nsdecls("w")} w:val="{edge_data.get("val", "single")}" w:sz="{edge_data.get("sz", 4)}" w:space="0" w:color="{edge_data.get("color", "auto")}"/>')
            tcBorders.append(element)
    tcPr.append(tcBorders)

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def format_run(run, font_name="TH SarabunPSK", size_pt=16, bold=False, italic=False, color_rgb=(0,0,0)):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>')
    rPr.append(rFonts)

def add_p(doc, text="", font_name="TH SarabunPSK", size_pt=16, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=0, line_spacing=1.0):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        r = p.add_run(text)
        format_run(r, font_name, size_pt, bold, italic)
    return p

class OfficialAssessmentPlanGenerator:
    def __init__(self, curriculum_path="school_courses_assessment_matrix.json", teachers_map_path="semester2_teachers_mapping.json"):
        with open(curriculum_path, "r", encoding="utf-8") as f:
            self.curriculum = json.load(f)
        if os.path.exists(teachers_map_path):
            with open(teachers_map_path, "r", encoding="utf-8") as f:
                self.teachers_map = json.load(f)
        else:
            self.teachers_map = {}

    def get_course_data(self, course_code):
        return self.curriculum.get(course_code)

    def get_teachers(self, course_code):
        if course_code in self.teachers_map:
            t = self.teachers_map[course_code].get("teachers", [])
            if t:
                return t
        c = self.get_course_data(course_code)
        if c and c.get("teachers"):
            return c["teachers"]
        return ["....................................................."]

    def extract_kpis_from_vault_md(self, course_code, folder_name):
        """Read detailed KPIs from existing vault without modifying it"""
        c_data = self.get_course_data(course_code)
        if c_data and c_data.get("learning_outcomes"):
            return c_data["learning_outcomes"]
        if c_data and c_data.get("indicators"):
            return c_data["indicators"]

        vault_dir = r"Curriculum_Vault/09_หลักสูตรสถานศึกษา"
        target_dir = os.path.join(vault_dir, folder_name) if folder_name else vault_dir
        if not os.path.exists(target_dir):
            target_dir = vault_dir
            
        md_file = None
        for root, dirs, files in os.walk(target_dir):
            for f in files:
                if f.startswith(course_code) and f.endswith(".md"):
                    md_file = os.path.join(root, f)
                    break
            if md_file:
                break
                
        if not md_file:
            return []

        kpis = []
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                text = f.read()
            lines = text.splitlines()
            in_blueprint = False
            for line in lines:
                if "## 📋 รายละเอียดตัวชี้วัด" in line or "## 📋 รายละเอียดผลการเรียนรู้" in line:
                    in_blueprint = True
                    continue
                if in_blueprint and re.match(r'^\s*\d+\.\s+(ตัวชี้วัด.*|[ก-ฮ]\s*\d+\.\d+.*|มีความรู้.*|ปฏิบัติตน.*|ตระหนัก.*)', line):
                    clean_kpi = re.sub(r'^\s*\d+\.\s*', '', line)
                    clean_kpi = clean_kpi.split('(เวลา')[0].strip()
                    if clean_kpi and clean_kpi not in kpis:
                        kpis.append(clean_kpi)
        except Exception:
            pass

        return kpis

    def generate_docx(self, course_code, output_path, semester="2", academic_year="2569"):
        course = self.get_course_data(course_code)
        if not course:
            print(f"Error: Course {course_code} not found.")
            return False

        teachers = self.get_teachers(course_code)
        doc = docx.Document()

        # Set Margins matching template (Top=37.85pt, Bottom=29.1pt, Left=72pt, Right=42.45pt)
        section = doc.sections[0]
        section.top_margin = Pt(38)
        section.bottom_margin = Pt(30)
        section.left_margin = Pt(72)
        section.right_margin = Pt(42.5)

        course_name = course.get("course_name", "")
        learning_area = course.get("learning_area", "")
        level = course.get("grade_level") or course.get("level") or "มัธยมศึกษาปีที่ 1"
        if not level.startswith("มัธยมศึกษา") and not level.startswith("ม."):
            level = f"มัธยมศึกษาปีที่ {level}"
        credit = course.get("credits") or course.get("credit") or 0.5
        total_hours = course.get("hours") or course.get("hours_total") or course.get("total_hours") or int(credit * 40)
        is_basic = (len(course_code) > 2 and course_code[2] == '1') or "พื้นฐาน" in course.get("course_type", "")
        is_corruption = "การป้องกันการทุจริต" in course_name or course.get("score_ratio") == "80:20"

        # -----------------------------------------------------------------
        # HEADER
        # -----------------------------------------------------------------
        add_p(doc, "แผนการวัดและประเมินผลการเรียนรู้", size_pt=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(f"รหัสวิชา {course_code} รายวิชา {course_name}      กลุ่มสาระการเรียนรู้{learning_area}")
        format_run(r, size_pt=16, bold=True)

        p2 = doc.add_paragraph()
        p2.paragraph_format.space_after = Pt(2)
        r = p2.add_run(f"ระดับชั้น{level}  ภาคเรียนที่ {semester}  ปีการศึกษา {academic_year}   เวลา {total_hours} คาบ/ภาคเรียน  จำนวน {credit:.1f} หน่วยกิต")
        format_run(r, size_pt=16, bold=False)

        # Teachers: if > 2, group 3 per line
        if len(teachers) > 2:
            p3 = doc.add_paragraph()
            p3.paragraph_format.space_after = Pt(1)
            pPr = p3._p.get_or_add_pPr()
            pPr.append(parse_xml(f'<w:tabs {nsdecls("w")}><w:tab w:val="left" w:pos="851"/></w:tabs>'))
            line1_teachers = ", ".join([f"{idx+1}. {t}" for idx, t in enumerate(teachers[:3])]) + (", " if len(teachers) > 3 else "")
            r = p3.add_run(f"ครูผู้สอน \t{line1_teachers}")
            format_run(r, size_pt=16, bold=False)

            for idx in range(3, len(teachers), 3):
                p_sub = doc.add_paragraph()
                p_sub.paragraph_format.space_after = Pt(1)
                pPr_sub = p_sub._p.get_or_add_pPr()
                pPr_sub.append(parse_xml(f'<w:tabs {nsdecls("w")}><w:tab w:val="left" w:pos="851"/></w:tabs>'))
                chunk = ", ".join([f"{idx+c_idx+1}. {t}" for c_idx, t in enumerate(teachers[idx:idx+3])])
                if idx + 3 < len(teachers):
                    chunk += ","
                r = p_sub.add_run(f"\t{chunk}")
                format_run(r, size_pt=16, bold=False)
        else:
            t_str = ", ".join([f"{idx+1}. {t}" if len(teachers)>1 else t for idx, t in enumerate(teachers)])
            p3 = doc.add_paragraph()
            p3.paragraph_format.space_after = Pt(4)
            r = p3.add_run(f"ครูผู้สอน \t{t_str}")
            format_run(r, size_pt=16, bold=False)

        add_p(doc, "……………………………………………………………………………………………………………", size_pt=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)

        # -----------------------------------------------------------------
        # 1. ผลการเรียนรู้ / ตัวชี้วัด
        # -----------------------------------------------------------------
        kpis = self.extract_kpis_from_vault_md(course_code, course.get("folder_name", ""))
        if is_basic:
            add_p(doc, "1. มาตรฐานการเรียนรู้ / ตัวชี้วัด", size_pt=16, bold=True, space_after=2)
            for k in kpis:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Pt(20)
                p.paragraph_format.space_after = Pt(1)
                r = p.add_run(k)
                format_run(r, size_pt=15)
        else:
            add_p(doc, "1. ผลการเรียนรู้", size_pt=16, bold=True, space_after=2)
            for idx, o in enumerate(kpis):
                clean_o = re.sub(r'^\s*\d+\.\s*', '', o)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Pt(36)
                p.paragraph_format.first_line_indent = Pt(-18)
                p.paragraph_format.space_after = Pt(1)
                r = p.add_run(f"\t{idx+1}. {clean_o}")
                format_run(r, size_pt=16)

        # -----------------------------------------------------------------
        # 2. การวัดและประเมินผลการเรียนรู้
        # -----------------------------------------------------------------
        add_p(doc, "2. การวัดและประเมินผลการเรียนรู้", size_pt=16, bold=True, space_before=4, space_after=2)
        if is_corruption:
            ratio_overall = "80 : 20"
            ratio_breakdown = "80 : 10 : 10"
            kpa_str = "100 : - : -"
        else:
            ratio_overall = course.get("score_ratio", "70 : 30")
            ratio_breakdown = "70 : 15 : 15"
            kpa_str = "60 : 25 : 15"
            if "วิทย์" in learning_area or "คณิต" in learning_area:
                kpa_str = "70 : 20 : 10"
            elif "สังคม" in learning_area or "ไทย" in learning_area:
                kpa_str = "55 : 30 : 15"
            elif "ศิลปะ" in learning_area or "การงาน" in learning_area or "สุขศึกษา" in learning_area:
                kpa_str = "40 : 50 : 10"

        add_p(doc, f"    อัตราส่วนการประเมินคะแนน\t\t\t= {ratio_overall}", size_pt=16, space_after=1)
        add_p(doc, f"ระหว่างภาค : กลางภาค : ปลายภาค \t= {ratio_breakdown}", size_pt=16, space_after=1)
        add_p(doc, f"\tK : P : A \t\t\t\t= {kpa_str}", size_pt=16, space_after=2)

        # -----------------------------------------------------------------
        # 3. เวลาในการสอบ
        # -----------------------------------------------------------------
        add_p(doc, "3. เวลาในการสอบ", size_pt=16, bold=True, space_before=2, space_after=1)
        if is_corruption or course.get("exam_schedule") == "สอบนอกตาราง":
            add_p(doc, "สอบนอกตาราง", size_pt=16, space_after=2)
        else:
            add_p(doc, "กลางภาค 60 นาที\tปลายภาค 60 นาที", size_pt=16, space_after=2)

        # -----------------------------------------------------------------
        # 4. เกณฑ์การให้ระดับคะแนน
        # -----------------------------------------------------------------
        add_p(doc, "4. เกณฑ์การให้ระดับคะแนน", size_pt=16, bold=True, space_before=2, space_after=1)

        # -----------------------------------------------------------------
        # 5. เวลาเรียน
        # -----------------------------------------------------------------
        add_p(doc, "5. เวลาเรียน", size_pt=16, bold=True, space_before=2, space_after=1)
        h_80 = int(total_hours * 0.8)
        miss_80 = total_hours - h_80
        h_60 = int(total_hours * 0.6)
        miss_60 = total_hours - h_60
        add_p(doc, f"จำนวนคาบเรียนตามหลักสูตร 20 สัปดาห์ \t= {total_hours} คาบ/ภาคเรียน", size_pt=16, space_after=1)
        add_p(doc, f"จำนวนคาบเรียน  80% (ขาดได้ {miss_80} คาบ) \t= {h_80} คาบ/ภาคเรียน", size_pt=16, space_after=1)
        add_p(doc, f"จำนวนคาบเรียน  60% (ขาดได้ {miss_60} คาบ)\t= {h_60} คาบ/ภาคเรียน", size_pt=16, space_after=2)

        # -----------------------------------------------------------------
        # 6. การให้ผลการเรียน "0" "ร" และ "มส"
        # -----------------------------------------------------------------
        add_p(doc, "6. การให้ผลการเรียน “0” “ร” และ “มส” เป็นดังนี้", size_pt=16, bold=True, space_before=2, space_after=1)
        add_p(doc, "6.1 ได้ผลการเรียน “0” เนื่องจาก มีคะแนนรวมไม่ถึง 50 และมีวิธีแก้ผลการเรียน “0” โดยทำงานซ่อมเสริม จากนั้นทำแบบทดสอบโดยต้องได้คะแนนเกินครึ่งหนึ่ง หากผู้เรียนดำเนินการสอบแก้ตัวผ่านและส่งงานเพิ่มเติมแล้ว จะเปลี่ยนผลการเรียนได้ไม่เกิน 1", size_pt=15, space_after=1)
        add_p(doc, "6.2 ได้ผลการเรียน “ร” เนื่องจาก", size_pt=15, space_after=1)
        
        key_task_name = "-" if is_corruption or course.get("key_task") == "-" else (course.get("key_task") or f"ชิ้นงานสำคัญเรื่องการประยุกต์ใช้ความรู้รายวิชา{course_name}")
        add_p(doc, f"     1. ไม่ส่งชิ้นงานสำคัญ คือ {key_task_name}", size_pt=15, space_after=1)
        add_p(doc, "2. ผู้เรียนไม่ได้รับการประเมินผลตัวชี้วัด/ผลการเรียนรู้ ในช่องของคะแนนวัดระหว่างเรียน", size_pt=15, space_after=1)
        add_p(doc, "3. ผู้เรียนไม่ได้สอบวัดผลกลางภาคเรียนหรือปลายภาคเรียน", size_pt=15, space_after=1)
        add_p(doc, "6.3 ได้ผลการเรียน “มส” เนื่องจาก เวลาเรียนไม่ถึง 80%", size_pt=15, space_after=6)

        # -----------------------------------------------------------------
        # TABLE 1: ตารางโครงสร้างการวัดและประเมินผล (แบบ วผ.19)
        # -----------------------------------------------------------------
        add_p(doc, "ตารางที่ 1 โครงสร้างการวัดและประเมินผลการเรียนรู้", size_pt=16, bold=True, space_before=4, space_after=2)
        
        units = course.get("units", [])
        if not units:
            units = [
                {"unit_no": 1, "unit_name": "หน่วยการเรียนรู้ที่ 1", "hours": 9, "score": 35},
                {"unit_no": 2, "unit_name": "หน่วยการเรียนรู้ที่ 2", "hours": 9, "score": 35}
            ]

        table = doc.add_table(rows=2, cols=8)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        col_widths = [Inches(0.6), Inches(2.2), Inches(1.1), Inches(1.8), Inches(0.45), Inches(0.45), Inches(0.45), Inches(0.55)]

        headers_r1 = ["หน่วยที่", "ชื่อหน่วยการเรียนรู้\n(จำนวนชั่วโมง)", "ผลการเรียนรู้", "วิธีการประเมินผล", "คะแนน", "", "", ""]
        headers_r2 = ["หน่วยที่", "ชื่อหน่วยการเรียนรู้\n(จำนวนชั่วโมง)", "ผลการเรียนรู้", "วิธีการประเมินผล", "K", "P", "A", "รวม"]

        for i in range(8):
            cell = table.cell(0, i)
            cell.text = headers_r1[i]
            cell.width = col_widths[i]
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            set_cell_border(cell, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})
            set_cell_shading(cell, "F2F2F2")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if p.runs:
                format_run(p.runs[0], size_pt=14, bold=True)

        for i in range(8):
            cell = table.cell(1, i)
            cell.text = headers_r2[i]
            cell.width = col_widths[i]
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            set_cell_border(cell, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})
            set_cell_shading(cell, "F2F2F2")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if p.runs:
                format_run(p.runs[0], size_pt=14, bold=True)

        table.cell(0, 0).merge(table.cell(1, 0))
        table.cell(0, 1).merge(table.cell(1, 1))
        table.cell(0, 2).merge(table.cell(1, 2))
        table.cell(0, 3).merge(table.cell(1, 3))
        table.cell(0, 4).merge(table.cell(0, 7))

        half_idx = max(1, len(units) // 2)
        pre_units = units[:half_idx]
        post_units = units[half_idx:]

        def add_cycle_header(tbl, title):
            row = tbl.add_row()
            cell = row.cells[0]
            cell.text = title
            for c_idx in range(8):
                set_cell_margins(row.cells[c_idx], top=80, bottom=80, left=100, right=100)
                set_cell_border(row.cells[c_idx], top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})
                set_cell_shading(row.cells[c_idx], "EAEAEA")
            a = row.cells[0]
            for c_idx in range(1, 8):
                a.merge(row.cells[c_idx])
            p = a.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if p.runs:
                format_run(p.runs[0], size_pt=14, bold=True)

        def add_data_row(tbl, u_no, u_name, kpi_txt, methods_txt, k, p_sc, a, total):
            row = tbl.add_row()
            vals = [str(u_no), u_name, kpi_txt, methods_txt, str(k) if k else "-", str(p_sc) if p_sc else "-", str(a) if a else "-", str(total)]
            aligns = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER]
            for c_idx in range(8):
                cell = row.cells[c_idx]
                cell.text = vals[c_idx]
                cell.width = col_widths[c_idx]
                set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
                set_cell_border(cell, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})
                p = cell.paragraphs[0]
                p.alignment = aligns[c_idx]
                if p.runs:
                    format_run(p.runs[0], size_pt=13, bold=(c_idx==7))

        def add_subtotal_row(tbl, title, k, p_sc, a, total):
            row = tbl.add_row()
            row.cells[0].text = title
            for c_idx in range(8):
                set_cell_margins(row.cells[c_idx], top=70, bottom=70, left=80, right=80)
                set_cell_border(row.cells[c_idx], top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})
                set_cell_shading(row.cells[c_idx], "F7F7F7")
            m_cell = row.cells[0]
            m_cell.merge(row.cells[1]).merge(row.cells[2]).merge(row.cells[3])
            p_m = m_cell.paragraphs[0]
            p_m.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if p_m.runs:
                format_run(p_m.runs[0], size_pt=14, bold=True)
            
            sub_vals = [str(k) if k else "-", str(p_sc) if p_sc else "-", str(a) if a else "-", str(total)]
            for idx, sv in enumerate(sub_vals):
                cell = row.cells[4+idx]
                cell.text = sv
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if p.runs:
                    format_run(p.runs[0], size_pt=14, bold=True)

        if is_corruption:
            # 1. การวัดผลก่อนสอบกลางภาค
            add_cycle_header(table, "1. การวัดผลก่อนสอบกลางภาค")
            eval_methods_def = "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน"
            add_data_row(table, "1", "STRONG /\nจิตพอเพียงต้านทุจริต\n(5 ชั่วโมง)", "ข้อที่ 1-2", eval_methods_def, 20, "-", "-", 20)
            add_data_row(table, "2", "พลเมืองกับความรับผิดชอบต่อสังคม\n(4 ชั่วโมง)", "ข้อที่ 3-4", eval_methods_def, 20, "-", "-", 20)
            add_subtotal_row(table, "รวมคะแนนการวัดผลก่อนสอบกลางภาค", 40, "-", "-", 40)

            # 2. การวัดผลกลางภาค
            add_cycle_header(table, "2. การวัดผลกลางภาค")
            add_data_row(table, "1", "STRONG /\nจิตพอเพียงต้านทุจริต", "ข้อที่ 1-2", "- แบบทดสอบวัดผลกลางภาคเรียน", 5, "-", "-", 10)
            add_data_row(table, "2", "พลเมืองกับความรับผิดชอบต่อสังคม\n(1 ชั่วโมง)", "ข้อที่ 3-4", "- แบบทดสอบวัดผลกลางภาคเรียน", 5, "-", "-", 10)
            add_subtotal_row(table, "รวมคะแนนการวัดผลกลางภาค", 10, "-", "-", 10)

            # 3. การวัดผลหลังสอบกลางภาค
            add_cycle_header(table, "3. การวัดผลหลังสอบกลางภาค")
            add_data_row(table, "3", "ความสำคัญของการต่อต้านและป้องกันการทุจริต\n(4 ชั่วโมง)", "ข้อที่ 5", eval_methods_def, 20, "-", "-", 20)
            add_data_row(table, "4", "บูรณาการความรู้\nสู่การป้องกันการทุจริต\n(5 ชั่วโมง)", "ข้อที่ 1-5", eval_methods_def, 20, "-", "-", 20)
            add_subtotal_row(table, "รวมคะแนนการวัดผลหลังสอบกลางภาค", 40, "-", "-", 40)

            # 4. การวัดผลปลายภาค
            add_cycle_header(table, "4. การวัดผลปลายภาค")
            add_data_row(table, "3", "ความสำคัญของการต่อต้านและป้องกันการทุจริต", "ข้อที่ 5", "- แบบทดสอบวัดผลปลายภาคเรียน", 5, "-", "-", 10)
            add_data_row(table, "4", "บูรณาการความรู้\nสู่การป้องกันการทุจริต\n(1 ชั่วโมง)", "ข้อที่ 1-5", "- แบบทดสอบวัดผลปลายภาคเรียน", 5, "-", "-", 10)
            add_subtotal_row(table, "รวมคะแนนการวัดผลปลายภาค", 10, "-", "-", 10)

            # Grand Total
            add_subtotal_row(table, "รวมคะแนนทั้งหมด", 100, "-", "-", 100)
        else:
            # General courses split logic
            add_cycle_header(table, "1. การวัดผลก่อนสอบกลางภาค")
            add_data_row(table, "1", f"{pre_units[0].get('unit_name', 'หน่วยที่ 1')} (19 ชั่วโมง)", "ข้อที่ 1-2", "- กิจกรรม/ใบงาน\n- การสังเกตพฤติกรรม", 20, 10, 5, 35)
            add_subtotal_row(table, "รวมคะแนนการวัดผลก่อนสอบกลางภาค", 20, 10, 5, 35)

            add_cycle_header(table, "2. การวัดผลกลางภาค (1 ชั่วโมง)")
            add_data_row(table, "-", "ทดสอบวัดผลกลางภาคเรียน (1 ชั่วโมง)", "ข้อที่ 1-2", "- การทดสอบวัดผลกลางภาคเรียน", 15, "-", "-", 15)
            add_subtotal_row(table, "รวมคะแนนการวัดผลกลางภาค", 15, "-", "-", 15)

            add_cycle_header(table, "3. การวัดผลหลังสอบกลางภาค")
            add_data_row(table, "2", f"{post_units[0].get('unit_name', 'หน่วยที่ 2')} (19 ชั่วโมง)", "ข้อที่ 3-4", "- กิจกรรม/ใบงาน\n- การสังเกตพฤติกรรม", 20, 10, 5, 35)
            add_subtotal_row(table, "รวมคะแนนการวัดผลหลังสอบกลางภาค", 20, 10, 5, 35)

            add_cycle_header(table, "4. การวัดผลปลายภาค (1 ชั่วโมง)")
            add_data_row(table, "-", "ทดสอบวัดผลปลายภาคเรียน (1 ชั่วโมง)", "ข้อที่ 3-4", "- การทดสอบวัดผลปลายภาคเรียน", 15, "-", "-", 15)
            add_subtotal_row(table, "รวมคะแนนการวัดผลปลายภาค", 15, "-", "-", 15)

            add_subtotal_row(table, "รวมคะแนนทั้งหมด", 70, 20, 10, 100)

        # -----------------------------------------------------------------
        # TABLE 2: เกณฑ์การให้ระดับคะแนน (ตารางตัดเกรด 8 ระดับ)
        # -----------------------------------------------------------------
        add_p(doc, "\nตารางที่ 2 เกณฑ์การให้ระดับคะแนน", size_pt=16, bold=True, space_before=4, space_after=2)
        t2 = doc.add_table(rows=9, cols=2)
        t2.alignment = WD_TABLE_ALIGNMENT.CENTER
        t2_widths = [Inches(2.5), Inches(2.5)]
        grades_data = [
            ("ระดับผลการเรียน", "ช่วงคะแนน"),
            ("4", "80 - 100"),
            ("3.5", "75 - 79"),
            ("3", "70 - 74"),
            ("2.5", "65 - 69"),
            ("2", "60 - 64"),
            ("1.5", "55 - 59"),
            ("1", "50 - 54"),
            ("0", "0 - 49")
        ]
        for r_idx, (g_lvl, g_range) in enumerate(grades_data):
            for c_idx, val in enumerate([g_lvl, g_range]):
                cell = t2.cell(r_idx, c_idx)
                cell.text = val
                cell.width = t2_widths[c_idx]
                set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
                set_cell_border(cell, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})
                if r_idx == 0:
                    set_cell_shading(cell, "F2F2F2")
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if p.runs:
                    format_run(p.runs[0], size_pt=14, bold=(r_idx==0))

        # -----------------------------------------------------------------
        # TABLE 3: ตารางกำหนดภาระงาน/ชิ้นงานสำคัญ
        # -----------------------------------------------------------------
        add_p(doc, "\nตารางที่ 3 กำหนดภาระงาน/ชิ้นงานสำคัญ (ไม่เกิน 2 ชิ้นงาน)", size_pt=16, bold=True, space_before=4, space_after=2)
        t3 = doc.add_table(rows=2, cols=5)
        t3.alignment = WD_TABLE_ALIGNMENT.CENTER
        t3_widths = [Inches(0.6), Inches(2.2), Inches(1.3), Inches(1.4), Inches(1.4)]
        t3_headers = ["ที่", "ชิ้นงานสำคัญ", "มาตรฐาน/ตัวชี้วัด (หรือ ผลการเรียนรู้)", "กำหนดมอบหมายงาน", "กำหนดส่ง"]
        for c_idx, h in enumerate(t3_headers):
            cell = t3.cell(0, c_idx)
            cell.text = h
            cell.width = t3_widths[c_idx]
            set_cell_margins(cell, top=70, bottom=70, left=80, right=80)
            set_cell_border(cell, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})
            set_cell_shading(cell, "F2F2F2")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if p.runs:
                format_run(p.runs[0], size_pt=14, bold=True)

        if key_task_name == "-":
            for c_idx in range(5):
                cell = t3.cell(1, c_idx)
                cell.text = "-"
                cell.width = t3_widths[c_idx]
                set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
                set_cell_border(cell, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if p.runs:
                    format_run(p.runs[0], size_pt=13)
        else:
            t3_row1 = ["1.1", key_task_name, "ข้อที่ 1-2", "สัปดาห์ที่ 3 (พ.ย. 69)", "สัปดาห์ที่ 8 (ธ.ค. 69)"]
            for c_idx, val in enumerate(t3_row1):
                cell = t3.cell(1, c_idx)
                cell.text = val
                cell.width = t3_widths[c_idx]
                set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
                set_cell_border(cell, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2, 3, 4] else WD_ALIGN_PARAGRAPH.LEFT
                if p.runs:
                    format_run(p.runs[0], size_pt=13)

        # -----------------------------------------------------------------
        # SIGN-OFF BLOCK
        # -----------------------------------------------------------------
        add_p(doc, "\n", size_pt=14, space_after=4)
        if len(teachers) > 2:
            for i in range(0, len(teachers), 2):
                t1 = teachers[i]
                t2 = teachers[i+1] if i+1 < len(teachers) else ""
                
                p_dots = doc.add_paragraph()
                p_dots.paragraph_format.space_before = Pt(4)
                p_dots.paragraph_format.space_after = Pt(1)
                pPr1 = p_dots._p.get_or_add_pPr()
                tabs1 = parse_xml(f'<w:tabs {nsdecls("w")}><w:tab w:val="center" w:pos="2400"/><w:tab w:val="center" w:pos="7200"/></w:tabs>')
                pPr1.append(tabs1)
                txt_dots = f"\tลงชื่อ..................................................ครูผู้สอน" + (f"\tลงชื่อ..................................................ครูผู้สอน" if t2 else "")
                r1 = p_dots.add_run(txt_dots)
                format_run(r1, size_pt=15)

                p_name = doc.add_paragraph()
                p_name.paragraph_format.space_before = Pt(0)
                p_name.paragraph_format.space_after = Pt(3)
                pPr2 = p_name._p.get_or_add_pPr()
                tabs2 = parse_xml(f'<w:tabs {nsdecls("w")}><w:tab w:val="center" w:pos="2400"/><w:tab w:val="center" w:pos="7200"/></w:tabs>')
                pPr2.append(tabs2)
                txt_name = f"\t({t1})" + (f"\t({t2})" if t2 else "")
                r2 = p_name.add_run(txt_name)
                format_run(r2, size_pt=15)
        else:
            for t_name in teachers:
                add_p(doc, f"ลงชื่อ..................................................ครูผู้สอน", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=1)
                add_p(doc, f"({t_name})\t", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=3)

        admins = [
            ("หัวหน้างานวัดและประเมินผลการเรียนรู้", "นางสาวอโรชา สลุงใหญ่"),
            ("หัวหน้ากลุ่มบริหารวิชาการ", "นายพงศธร แสนเมือง"),
            ("รองผู้อำนวยการกลุ่มบริหารวิชาการ", "นางสาวกมลชนก สุวรรณประเวก"),
            ("ผู้อำนวยการโรงเรียนพัฒนานิคม", "นายธีรพงษ์ ภูธร")
        ]
        for role, name in admins:
            add_p(doc, f"ลงชื่อ..................................................{role}", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=1)
            add_p(doc, f"({name})\t", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=3)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        doc.save(output_path)
        print(f"Generated: {output_path}")
        return True

if __name__ == '__main__':
    gen = OfficialAssessmentPlanGenerator()
    out_dir = r"C:\Users\peera\Desktop\AntigravityProject\CurriculumMD\test_generated"
    test_courses = ["ส30248", "ส20224"]
    for tc in test_courses:
        out_file = os.path.join(out_dir, f"วผ19_{tc}_แผนการวัดและประเมินผล_2-2569.docx")
        gen.generate_docx(tc, out_file, semester="2", academic_year="2569")
