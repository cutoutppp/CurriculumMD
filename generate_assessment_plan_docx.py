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
        return ["....................................................."]

    def extract_kpis_from_vault_md(self, course_code, folder_name):
        """Read detailed KPIs from existing vault without modifying it"""
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
            # extract KPI descriptions
            lines = text.splitlines()
            in_blueprint = False
            for line in lines:
                if "## 📋 รายละเอียดตัวชี้วัด" in line:
                    in_blueprint = True
                    continue
                if in_blueprint and re.match(r'^\s*\d+\.\s+(ตัวชี้วัด.*|[ก-ฮ]\s*\d+\.\d+.*)', line):
                    clean_kpi = re.sub(r'^\s*\d+\.\s*', '', line)
                    clean_kpi = clean_kpi.split('(เวลา')[0].strip()
                    if clean_kpi and clean_kpi not in kpis:
                        kpis.append(clean_kpi)
        except Exception:
            pass

        # Fallback 1: Extract from course indicators in matrix
        if not kpis:
            c_data = self.get_course_data(course_code)
            if c_data and c_data.get("indicators"):
                for ind in c_data["indicators"]:
                    if ind and ind not in kpis and not ind.startswith("สาระ") and not ind.startswith("กลุ่มสาระ"):
                        kpis.append(ind)

        return kpis

    def generate_docx(self, course_code, output_path, semester="2", academic_year="2569"):
        course = self.get_course_data(course_code)
        if not course:
            print(f"Error: Course {course_code} not found.")
            return False

        teachers = self.get_teachers(course_code)
        doc = docx.Document()

        # Set Margins matching template (Top=54pt, Bottom=54pt, Left=54pt, Right=40pt)
        section = doc.sections[0]
        section.top_margin = Pt(54)
        section.bottom_margin = Pt(54)
        section.left_margin = Pt(54)
        section.right_margin = Pt(40)

        course_name = course.get("course_name", "")
        learning_area = course.get("learning_area", "")
        level = course.get("grade_level") or course.get("level") or "มัธยมศึกษาปีที่ 1"
        if not level.startswith("มัธยมศึกษา") and not level.startswith("ม."):
            level = f"มัธยมศึกษาปีที่ {level}"
        credit = course.get("credits") or course.get("credit") or 1.0
        total_hours = course.get("hours") or course.get("hours_total") or int(credit * 40)
        is_basic = (len(course_code) > 2 and course_code[2] == '1') or "พื้นฐาน" in course.get("course_type", "")

        # -----------------------------------------------------------------
        # HEADER
        # -----------------------------------------------------------------
        add_p(doc, "แผนการวัดและประเมินผลการเรียนรู้", size_pt=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(f"รหัสวิชา {course_code} รายวิชา {course_name}")
        format_run(r, size_pt=16, bold=True)
        r2 = p.add_run(f"\tกลุ่มสาระการเรียนรู้{learning_area}")
        format_run(r2, size_pt=16, bold=True)

        p2 = doc.add_paragraph()
        p2.paragraph_format.space_after = Pt(2)
        r = p2.add_run(f"ระดับชั้น{level} ภาคเรียนที่ {semester} ปีการศึกษา {academic_year} \tเวลา {total_hours} คาบ/ภาคเรียน จำนวน {credit:.1f} หน่วยกิต")
        format_run(r, size_pt=16, bold=False)

        t_str = ", ".join([f"{idx+1}. {t}" if len(teachers)>1 else t for idx, t in enumerate(teachers)])
        p3 = doc.add_paragraph()
        p3.paragraph_format.space_after = Pt(4)
        r = p3.add_run(f"ครูผู้สอน {t_str}")
        format_run(r, size_pt=16, bold=False)

        add_p(doc, "……………………………………………………………………………………………………………", size_pt=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)

        # -----------------------------------------------------------------
        # 1. มาตรฐานการเรียนรู้ / ตัวชี้วัด หรือ ผลการเรียนรู้
        # -----------------------------------------------------------------
        kpis = self.extract_kpis_from_vault_md(course_code, course.get("folder_name", ""))
        if is_basic:
            add_p(doc, "1. มาตรฐานการเรียนรู้ / ตัวชี้วัด", size_pt=16, bold=True, space_after=2)
            if kpis:
                for k in kpis:
                    p = doc.add_paragraph()
                    p.paragraph_format.left_indent = Pt(20)
                    p.paragraph_format.space_after = Pt(1)
                    r = p.add_run(k)
                    format_run(r, size_pt=15)
            else:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Pt(20)
                r = p.add_run("(ระบุมาตรฐานและตัวชี้วัดตามหลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน)")
                format_run(r, size_pt=15)
        else:
            add_p(doc, "1. ผลการเรียนรู้", size_pt=16, bold=True, space_after=2)
            outcomes = [k for k in kpis if not k.startswith("ตัวชี้วัด")] if kpis else []
            if not outcomes:
                outcomes = [
                    "1. มีความรู้ความเข้าใจในเนื้อหาและหลักการสำคัญตามโครงสร้างรายวิชา",
                    "2. สามารถสืบค้น วิเคราะห์ และประยุกต์ใช้ทักษะกระบวนการในการปฏิบัติงานได้อย่างมีประสิทธิภาพ",
                    "3. ตระหนักและเห็นคุณค่า นำความรู้ไปประยุกต์ใช้ในชีวิตประจำวันอย่างมีคุณธรรมและจริยธรรม"
                ]
            for o in outcomes:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Pt(20)
                p.paragraph_format.space_after = Pt(1)
                r = p.add_run(o)
                format_run(r, size_pt=15)

        # -----------------------------------------------------------------
        # 2. การวัดและประเมินผลการเรียนรู้
        # -----------------------------------------------------------------
        add_p(doc, "2. การวัดและประเมินผลการเรียนรู้", size_pt=16, bold=True, space_before=4, space_after=2)
        ratio_overall = "70 : 30"
        ratio_breakdown = "70 : 15 : 15"
        kpa_str = "60 : 25 : 15"
        if "วิทย์" in learning_area or "คณิต" in learning_area:
            kpa_str = "70 : 20 : 10"
        elif "สังคม" in learning_area or "ไทย" in learning_area:
            kpa_str = "55 : 30 : 15"
        elif "ศิลปะ" in learning_area or "การงาน" in learning_area or "สุขศึกษา" in learning_area:
            kpa_str = "40 : 50 : 10"

        add_p(doc, f"อัตราส่วนการประเมินคะแนน\t\t= {ratio_overall}", size_pt=16, space_after=1)
        add_p(doc, f"ระหว่างภาค : กลางภาค : ปลายภาค \t= {ratio_breakdown}", size_pt=16, space_after=1)
        add_p(doc, f"K : P : A \t\t\t\t= {kpa_str}", size_pt=16, space_after=2)
        
        p_note = doc.add_paragraph()
        p_note.paragraph_format.space_after = Pt(3)
        r = p_note.add_run("หมายเหตุ คะแนน sgs ในแต่ละหน่วยช่องแบ่งได้มากที่สุด 9 ช่อง เพื่อให้สามารถกรอกคะแนนใน SGS การวัดผลก่อนสอบกลางภาคและการวัดผลหลังสอบกลางภาคได้ ในแผนวัดผลฯและ SGS จะต้องตรงกันและหากสอนรหัสเดียวกันครูผู้สอนทุกคนจะต้องแบ่งคะแนนเท่ากัน / ในแต่ละหน่วยการเรียนรู้ควรมีวิธีการประเมินผลที่หลากหลาย")
        format_run(r, size_pt=14, italic=True)

        # -----------------------------------------------------------------
        # 3. เวลาในการสอบ
        # -----------------------------------------------------------------
        add_p(doc, "3. เวลาในการสอบ", size_pt=16, bold=True, space_before=2, space_after=1)
        add_p(doc, "กลางภาค 60 นาที\tปลายภาค 60 นาที", size_pt=16, space_after=2)

        # -----------------------------------------------------------------
        # 4. เกณฑ์การให้ระดับคะแนน
        # -----------------------------------------------------------------
        add_p(doc, "4. เกณฑ์การให้ระดับคะแนน", size_pt=16, bold=True, space_before=2, space_after=1)
        add_p(doc, "(ดูตารางที่ 2 เกณฑ์การให้ระดับคะแนนตามระเบียบกระทรวงศึกษาธิการ)", size_pt=15, space_after=2)

        # -----------------------------------------------------------------
        # 5. เวลาเรียน
        # -----------------------------------------------------------------
        add_p(doc, "5. เวลาเรียน", size_pt=16, bold=True, space_before=2, space_after=1)
        h_80 = int(total_hours * 0.8)
        miss_80 = total_hours - h_80
        h_60 = int(total_hours * 0.6)
        miss_60 = total_hours - h_60
        add_p(doc, f"จำนวนคาบเรียนตามหลักสูตร 20 สัปดาห์ \t\t= {total_hours} คาบ/ภาคเรียน", size_pt=16, space_after=1)
        add_p(doc, f"จำนวนคาบเรียน  80% (ขาดได้ {miss_80} คาบ) \t\t= {h_80} คาบ/ภาคเรียน", size_pt=16, space_after=1)
        add_p(doc, f"จำนวนคาบเรียน  60% (ขาดได้ {miss_60} คาบ)\t\t= {h_60} คาบ/ภาคเรียน", size_pt=16, space_after=2)

        # -----------------------------------------------------------------
        # 6. การให้ผลการเรียน "0" "ร" และ "มส"
        # -----------------------------------------------------------------
        add_p(doc, "6. การให้ผลการเรียน  “0”  “ร”  และ “มส”  เป็นดังนี้", size_pt=16, bold=True, space_before=2, space_after=1)
        add_p(doc, "6.1 ได้ผลการเรียน “0” เนื่องจาก มีคะแนนรวมไม่ถึง 50 คะแนน และมีวิธีแก้ผลการเรียน “0” โดยทำแบบทดสอบตามตัวชี้วัด/ผลการเรียนรู้ที่ไม่ผ่านและส่งงานซ่อมเสริม", size_pt=15, space_after=1)
        add_p(doc, "6.2 ได้ผลการเรียน “ร” เนื่องจาก", size_pt=15, space_after=1)
        
        key_task_name = f"ชิ้นงานสำคัญเรื่องการประยุกต์ใช้ความรู้รายวิชา{course_name}"
        add_p(doc, f"     1. ไม่ส่งชิ้นงานสำคัญ คือ {key_task_name}", size_pt=15, space_after=1)
        add_p(doc, "     2. ผู้เรียนไม่ได้รับการประเมินผลตามหน่วยเรียนรู้ ในช่องของคะแนนวัดผลระหว่างเรียน", size_pt=15, space_after=1)
        add_p(doc, "     3. ผู้เรียนไม่ได้วัดผลกลางภาคเรียนหรือปลายภาคเรียน", size_pt=15, space_after=1)
        add_p(doc, "ได้ผลการเรียน “มส” เนื่องจาก มีเวลาเรียนไม่ถึง 80%", size_pt=15, space_after=6)

        # -----------------------------------------------------------------
        # TABLE 1: ตารางโครงสร้างการวัดและประเมินผล (แบบ วผ.19)
        # -----------------------------------------------------------------
        add_p(doc, "ตารางที่ 1 โครงสร้างการวัดและประเมินผลการเรียนรู้", size_pt=16, bold=True, space_before=4, space_after=2)
        
        units = course.get("units", [])
        if not units:
            units = [
                {"unit_no": 1, "unit_name": "หน่วยการเรียนรู้ที่ 1", "hours": (total_hours//2)-1, "score": 35},
                {"unit_no": 2, "unit_name": "หน่วยการเรียนรู้ที่ 2", "hours": (total_hours//2)-1, "score": 35}
            ]

        # 50:50 rule for hours:
        target_pre_mid_hours = (total_hours // 2) - 1
        target_post_mid_hours = (total_hours // 2) - 1

        table = doc.add_table(rows=2, cols=8)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        col_widths = [Inches(0.6), Inches(2.2), Inches(1.1), Inches(1.8), Inches(0.45), Inches(0.45), Inches(0.45), Inches(0.55)]

        headers_r1 = ["หน่วยที่", "ชื่อหน่วยการเรียนรู้ (จำนวนชั่วโมง)", "ตัวชี้วัด / ผลการเรียนรู้", "วิธีการประเมินผล", "คะแนน", "", "", ""]
        headers_r2 = ["หน่วยที่", "ชื่อหน่วยการเรียนรู้ (จำนวนชั่วโมง)", "ตัวชี้วัด / ผลการเรียนรู้", "วิธีการประเมินผล", "K", "P", "A", "รวม"]

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

        def split_score_to_rows(total_score, max_per_slot=15):
            """Split score so no row exceeds 15 points"""
            if total_score <= max_per_slot:
                return [total_score]
            parts = []
            rem = total_score
            while rem > 0:
                chunk = min(max_per_slot, rem)
                if rem - chunk < 5 and rem - chunk > 0:
                    chunk = rem // 2
                parts.append(chunk)
                rem -= chunk
            return parts

        # 1. การวัดผลก่อนสอบกลางภาค (เป้าหมาย 35 คะแนน, 19 ชั่วโมงสำหรับ 40 ชม.)
        add_cycle_header(table, "1. การวัดผลก่อนสอบกลางภาค")
        pre_scores = split_score_to_rows(35, max_per_slot=15) # e.g. [12, 12, 11] or [15, 10, 10]
        # Distribute hours
        pre_hours_dist = []
        rem_hrs = target_pre_mid_hours
        for i in range(len(pre_scores)):
            hrs = rem_hrs // (len(pre_scores) - i)
            pre_hours_dist.append(hrs)
            rem_hrs -= hrs

        tot_pre_k, tot_pre_p, tot_pre_a, tot_pre_score = 0, 0, 0, 0
        for i, sc in enumerate(pre_scores):
            u_idx = min(i, len(pre_units)-1)
            u = pre_units[u_idx]
            u_no = u.get("unit_no", i+1)
            u_name = u.get("unit_name", f"หน่วยการเรียนรู้ที่ {u_no}")
            u_hrs = pre_hours_dist[i]
            
            k_val = int(sc * 0.6)
            p_val = int(sc * 0.25)
            a_val = sc - k_val - p_val
            tot_pre_k += k_val
            tot_pre_p += p_val
            tot_pre_a += a_val
            nk_list = u.get("national_kpis", [])
            if is_basic and nk_list:
                if len(nk_list) <= 2:
                    kpi_txt = ", ".join(nk_list)
                else:
                    kpi_txt = f"{nk_list[0]}, {nk_list[1]} (+{len(nk_list)-2})"
            elif is_basic:
                kpi_txt = f"ตัวชี้วัดหน่วยที่ {u_no}"
            else:
                kpi_txt = f"ข้อที่ {u_no}"
            methods = "- กิจกรรม/ใบงาน\n- การสังเกตพฤติกรรม"
            if i == 0:
                methods += "\n- ชิ้นงานสำคัญ"
            else:
                methods += "\n- แบบทดสอบย่อย"
            add_data_row(table, u_no, f"{u_name} ({u_hrs} ชั่วโมง)", kpi_txt, methods, k_val, p_val, a_val, sc)

        add_subtotal_row(table, "รวมคะแนนการวัดผลก่อนสอบกลางภาค", tot_pre_k, tot_pre_p, tot_pre_a, tot_pre_score)

        # 2. การวัดผลกลางภาค (15 คะแนน, 1 ชั่วโมง)
        add_cycle_header(table, "2. การวัดผลกลางภาค")
        mid_kpi = f"ข้อที่ 1-{len(pre_units)}" if not is_basic else "ตัวชี้วัดหน่วยที่ 1-2"
        add_data_row(table, "-", "ทดสอบวัดผลกลางภาคเรียน (1 ชั่วโมง)", mid_kpi, "- การทดสอบวัดผลกลางภาคเรียน", 15, 0, 0, 15)
        add_subtotal_row(table, "รวมคะแนนการวัดผลกลางภาค", 15, 0, 0, 15)

        # 3. การวัดผลหลังสอบกลางภาค (เป้าหมาย 35 คะแนน, 19 ชั่วโมงสำหรับ 40 ชม.)
        add_cycle_header(table, "3. การวัดผลหลังสอบกลางภาค")
        post_scores = split_score_to_rows(35, max_per_slot=15)
        post_hours_dist = []
        rem_post_hrs = target_post_mid_hours
        for i in range(len(post_scores)):
            hrs = rem_post_hrs // (len(post_scores) - i)
            post_hours_dist.append(hrs)
            rem_post_hrs -= hrs

        tot_post_k, tot_post_p, tot_post_a, tot_post_score = 0, 0, 0, 0
        for i, sc in enumerate(post_scores):
            u_idx = min(i, len(post_units)-1)
            u = post_units[u_idx]
            u_no = u.get("unit_no", len(pre_units) + i + 1)
            u_name = u.get("unit_name", f"หน่วยการเรียนรู้ที่ {u_no}")
            u_hrs = post_hours_dist[i]
            
            k_val = int(sc * 0.6)
            p_val = int(sc * 0.25)
            a_val = sc - k_val - p_val
            tot_post_k += k_val
            tot_post_p += p_val
            tot_post_a += a_val
            tot_post_score += sc

            nk_list = u.get("national_kpis", [])
            if is_basic and nk_list:
                if len(nk_list) <= 2:
                    kpi_txt = ", ".join(nk_list)
                else:
                    kpi_txt = f"{nk_list[0]}, {nk_list[1]} (+{len(nk_list)-2})"
            elif is_basic:
                kpi_txt = f"ตัวชี้วัดหน่วยที่ {u_no}"
            else:
                kpi_txt = f"ข้อที่ {u_no}"
            methods = "- กิจกรรม/ใบงาน\n- การสังเกตพฤติกรรม\n- การอภิปรายกลุ่ม"
            add_data_row(table, u_no, f"{u_name} ({u_hrs} ชั่วโมง)", kpi_txt, methods, k_val, p_val, a_val, sc)

        add_subtotal_row(table, "รวมคะแนนการวัดผลหลังสอบกลางภาค", tot_post_k, tot_post_p, tot_post_a, tot_post_score)

        # 4. การวัดผลปลายภาค (15 คะแนน, 1 ชั่วโมง)
        add_cycle_header(table, "4. การวัดผลปลายภาค")
        final_kpi = f"ข้อที่ {len(pre_units)+1}-{len(units)}" if not is_basic else "ตัวชี้วัดหน่วยที่ 3-4"
        add_data_row(table, "-", "ทดสอบวัดผลปลายภาคเรียน (1 ชั่วโมง)", final_kpi, "- การทดสอบวัดผลปลายภาคเรียน", 15, 0, 0, 15)
        add_subtotal_row(table, "รวมคะแนนการวัดผลปลายภาค", 15, 0, 0, 15)

        # GRAND TOTAL
        grand_k = tot_pre_k + 15 + tot_post_k + 15
        grand_p = tot_pre_p + tot_post_p
        grand_a = tot_pre_a + tot_post_a
        grand_tot = grand_k + grand_p + grand_a
        add_subtotal_row(table, "รวมคะแนนทั้งหมด", grand_k, grand_p, grand_a, grand_tot)

        # -----------------------------------------------------------------
        # TABLE 2: เกณฑ์การให้ระดับคะแนน (ตารางตัดเกรด 8 ระดับ)
        # -----------------------------------------------------------------
        add_p(doc, "\nตารางที่ 2 เกณฑ์การให้ระดับคะแนน", size_pt=16, bold=True, space_before=4, space_after=2)
        t2 = doc.add_table(rows=9, cols=2)
        t2.alignment = WD_TABLE_ALIGNMENT.CENTER
        t2_widths = [Inches(2.5), Inches(2.5)]
        grades_data = [
            ("ระดับผลการเรียน", "ช่วงคะแนน"),
            ("4", "80 – 100"),
            ("3.5", "75 – 79"),
            ("3", "70 – 74"),
            ("2.5", "65 – 69"),
            ("2", "60 – 64"),
            ("1.5", "55 – 59"),
            ("1", "50 – 54"),
            ("0", "0 – 49")
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

        t3_row1 = ["1.1", key_task_name, mid_kpi, "สัปดาห์ที่ 3 (พ.ย. 69)", "สัปดาห์ที่ 8 (ธ.ค. 69)"]
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
        # SIGN-OFF BLOCK (5 Officials)
        # -----------------------------------------------------------------
        add_p(doc, "\n", size_pt=14, space_after=4)
        for t_name in teachers:
            add_p(doc, f"ลงชื่อ..................................................ครูผู้สอน", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=1)
            add_p(doc, f"({t_name})\t", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=3)

        add_p(doc, "ลงชื่อ..................................................หัวหน้างานวัดผลและประเมินผลการเรียนรู้", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=1)
        add_p(doc, "(นางสาวอโรชา  สลุงใหญ่)\t", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=3)

        add_p(doc, "ลงชื่อ..................................................หัวหน้ากลุ่มบริหารวิชาการ", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=1)
        add_p(doc, "(นายพงศธร  แสนเมือง)\t", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=3)

        add_p(doc, "ลงชื่อ..................................................รองผู้อำนวยการกลุ่มบริหารวิชาการ", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=1)
        add_p(doc, "(นางสาวกมลชนก สุวรรณประเวก)\t", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=3)

        add_p(doc, "ลงชื่อ..................................................ผู้อำนวยการโรงเรียนพัฒนานิคม", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=1)
        add_p(doc, "(นายธีรพงษ์  ภูธร)\t", size_pt=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=3)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        doc.save(output_path)
        print(f"Generated: {output_path}")
        return True

if __name__ == '__main__':
    gen = OfficialAssessmentPlanGenerator()
    out_dir = r"C:\Users\peera\Desktop\พัฒนานิคม_69\แผนวัด_2-69_generated"
    test_courses = ["ท21102", "ค21102", "ว21102", "ส21103"]
    for tc in test_courses:
        out_file = os.path.join(out_dir, f"วผ19_{tc}_แผนการวัดและประเมินผล_2-2569.docx")
        gen.generate_docx(tc, out_file, semester="2", academic_year="2569")
