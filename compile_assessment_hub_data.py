# -*- coding: utf-8 -*-
import os
import json
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

target_dir = r"c:\Users\peera\Desktop\AntigravityProject\AssessmentHub\assessment-plan"
os.makedirs(os.path.join(target_dir, "data"), exist_ok=True)
os.makedirs(os.path.join(target_dir, "templates"), exist_ok=True)

# 1. Load curriculum matrix and schedule mapping
curriculum_path = r"c:\Users\peera\Desktop\AntigravityProject\CurriculumMD\school_courses_assessment_matrix.json"
schedule_path = r"c:\Users\peera\Desktop\AntigravityProject\CurriculumMD\semester2_teachers_mapping.json"

with open(curriculum_path, "r", encoding="utf-8") as f:
    curriculum = json.load(f)

with open(schedule_path, "r", encoding="utf-8") as f:
    schedule = json.load(f)

# Approved Blueprint for Anti-Corruption Courses in Assessment Plan System (วผ.19)
CORRUPTION_CODES = {
    'ส20223', 'ส20224', 'ส20225', 'ส20226', 'ส20227', 'ส20228',
    'ส30247', 'ส30248', 'ส30249', 'ส30250', 'ส30251', 'ส30252'
}

CORRUPTION_APPROVED_UNITS = [
    {
        "unit_no": "1",
        "unit_name": "STRONG / จิตพอเพียงต้านทุจริต",
        "hours": 5,
        "score_k": 20,
        "score_p": 0,
        "score_a": 0,
        "score_total": 20,
        "indicators": ["ข้อที่ 1-2"],
        "concepts": ["STRONG : จิตพอเพียงต้านทุจริต สร้างจิตสำนึกและปฏิบัติตนเป็นผู้ต้านการทุจริต"],
        "eval_method": "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน",
        "assessments": [{
            "eval_methods": "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน",
            "score_k": 20,
            "score_p": "-",
            "score_a": "-",
            "score_total": 20
        }]
    },
    {
        "unit_no": "2",
        "unit_name": "พลเมืองกับความรับผิดชอบต่อสังคม",
        "hours": 4,
        "score_k": 20,
        "score_p": 0,
        "score_a": 0,
        "score_total": 20,
        "indicators": ["ข้อที่ 3-4"],
        "concepts": ["พลเมืองกับความรับผิดชอบต่อสังคม การปฏิบัติตนตามหน้าที่พลเมืองและมีส่วนร่วมรับผิดชอบต่อสังคม"],
        "eval_method": "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน",
        "assessments": [{
            "eval_methods": "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน",
            "score_k": 20,
            "score_p": "-",
            "score_a": "-",
            "score_total": 20
        }]
    },
    {
        "unit_no": "3",
        "unit_name": "ความสำคัญของการต่อต้านและป้องกันการทุจริต",
        "hours": 4,
        "score_k": 20,
        "score_p": 0,
        "score_a": 0,
        "score_total": 20,
        "indicators": ["ข้อที่ 5"],
        "concepts": ["ความสำคัญของการต่อต้านและป้องกันการทุจริต สร้างความตระหนักและเห็นคุณค่าของความซื่อสัตย์สุจริต"],
        "eval_method": "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน",
        "assessments": [{
            "eval_methods": "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน",
            "score_k": 20,
            "score_p": "-",
            "score_a": "-",
            "score_total": 20
        }]
    },
    {
        "unit_no": "4",
        "unit_name": "บูรณาการความรู้ สู่การป้องกันการทุจริต",
        "hours": 5,
        "score_k": 20,
        "score_p": 0,
        "score_a": 0,
        "score_total": 20,
        "indicators": ["ข้อที่ 1-5"],
        "concepts": ["บูรณาการความรู้สู่การป้องกันการทุจริต การประยุกต์ความรู้และทักษะเพื่อสร้างแนวทางการป้องกันการทุจริตในชีวิตจริง"],
        "eval_method": "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน",
        "assessments": [{
            "eval_methods": "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน",
            "score_k": 20,
            "score_p": "-",
            "score_a": "-",
            "score_total": 20
        }]
    }
]

CORRUPTION_INDICATORS = [
    "1. มีความรู้ ความเข้าใจเกี่ยวกับ STRONG : จิตพอเพียงต้านทุจริต",
    "2. ปฏิบัติตนเป็นผู้ที่ STRONG : จิตพอเพียงต้านทุจริต",
    "3. มีความรู้ ความเข้าใจเกี่ยวกับพลเมืองและมีความรับผิดชอบต่อสังคม",
    "4. ปฏิบัติตนตามหน้าที่พลเมืองและมีความรับผิดชอบต่อสังคม",
    "5. ตระหนักและเห็นความสำคัญของการต่อต้านและป้องกันการทุจริต"
]

# 2. Merge and enrich courses for 2/2569
compiled_courses = {}

for code, c in curriculum.items():
    is_corruption = (code in CORRUPTION_CODES) or ("การป้องกันการทุจริต" in c.get("course_name", "")) or (c.get("score_ratio") == "80:20")

    # Teacher from schedule or course itself
    sch_entry = schedule.get(code, {})
    teachers = sch_entry.get("teachers", []) or c.get("teachers", [])
    if is_corruption:
        teachers = ["....................................................."]
    elif not teachers:
        teachers = ["....................................................."]
    
    credits = float(c.get("credits") or c.get("credit") or (0.5 if is_corruption else 1.0))
    total_hours = int(c.get("total_hours") or c.get("hours") or c.get("hours_total") or int(credits * 40))
    is_basic = (len(code) > 2 and code[2] == '1') or "พื้นฐาน" in c.get("course_type", "")
    if is_corruption:
        is_basic = False

    # Target hours for 50:50 split
    target_pre_h = 9 if is_corruption else int(c.get("target_pre_hours") or ((total_hours // 2) - 1))
    target_post_h = 9 if is_corruption else int(c.get("target_post_hours") or ((total_hours // 2) - 1))

    # Units
    if is_corruption:
        clean_units = CORRUPTION_APPROVED_UNITS
        all_kpis = CORRUPTION_INDICATORS
    else:
        raw_units = c.get("units", [])
        clean_units = []
        
        if raw_units:
            for idx, u in enumerate(raw_units):
                u_no = u.get("unit_no", str(idx+1))
                u_name = u.get("unit_name", f"หน่วยการเรียนรู้ที่ {u_no}")
                try:
                    u_h = int(u.get("hours", 0))
                except:
                    u_h = 0
                
                # Scores
                try:
                    sk = int(u.get("score_k", 0))
                except:
                    sk = 0
                try:
                    sp = int(u.get("score_p", 0))
                except:
                    sp = 0
                try:
                    sa = int(u.get("score_a", 0))
                except:
                    sa = 0
                try:
                    stot = int(u.get("score_total", sk + sp + sa))
                except:
                    stot = sk + sp + sa

                # Indicators
                kpis = u.get("indicators_raw", [])
                concepts = u.get("key_concepts", [])
                eval_method = u.get("eval_method", "")
                u_assessments = u.get("assessments")

                clean_units.append({
                    "unit_no": u_no,
                    "unit_name": u_name,
                    "hours": u_h,
                    "score_k": sk,
                    "score_p": sp,
                    "score_a": sa,
                    "score_total": stot,
                    "indicators": kpis,
                    "concepts": concepts,
                    "eval_method": eval_method,
                    "assessments": u_assessments
                })
        else:
            # Fallback 4 units
            clean_units = [
                {"unit_no": "1", "unit_name": "หน่วยการเรียนรู้ที่ 1", "hours": target_pre_h // 2, "score_k": 8, "score_p": 2, "score_a": 0, "score_total": 10, "indicators": ["ผลการเรียนรู้ที่ 1"], "concepts": []},
                {"unit_no": "2", "unit_name": "หน่วยการเรียนรู้ที่ 2", "hours": target_pre_h - (target_pre_h // 2), "score_k": 10, "score_p": 3, "score_a": 2, "score_total": 15, "indicators": ["ผลการเรียนรู้ที่ 2"], "concepts": []},
                {"unit_no": "3", "unit_name": "หน่วยการเรียนรู้ที่ 3", "hours": target_post_h // 2, "score_k": 7, "score_p": 5, "score_a": 3, "score_total": 15, "indicators": ["ผลการเรียนรู้ที่ 3"], "concepts": []},
                {"unit_no": "4", "unit_name": "หน่วยการเรียนรู้ที่ 4", "hours": target_post_h - (target_post_h // 2), "score_k": 6, "score_p": 2, "score_a": 2, "score_total": 10, "indicators": ["ผลการเรียนรู้ที่ 4"], "concepts": []}
            ]

        # Overall KPIs
        all_kpis = []
        if c.get("indicators") and isinstance(c.get("indicators"), list) and len(c.get("indicators")) > 0:
            all_kpis = c.get("indicators")
        else:
            for u in clean_units:
                for ind in u.get("indicators", []):
                    if ind and ind not in all_kpis:
                        all_kpis.append(ind)
            
            if not all_kpis:
                all_kpis = [
                    "1. มีความรู้ความเข้าใจในเนื้อหาและหลักการสำคัญตามโครงสร้างรายวิชา",
                    "2. สามารถสืบค้น วิเคราะห์ และประยุกต์ใช้ทักษะกระบวนการในการปฏิบัติงานได้อย่างมีประสิทธิภาพ",
                    "3. ตระหนักและเห็นคุณค่า นำความรู้ไปประยุกต์ใช้ในชีวิตประจำวันอย่างมีคุณธรรมและจริยธรรม"
                ]

    compiled_courses[code] = {
        "course_code": code,
        "course_name": c.get("course_name", ""),
        "learning_area": c.get("learning_area", c.get("normalized_area", "")),
        "grade_level": c.get("grade_level", "ม.1"),
        "credits": credits,
        "total_hours": total_hours,
        "is_basic": is_basic,
        "target_pre_hours": target_pre_h,
        "target_post_hours": target_post_h,
        "teachers": teachers,
        "units": clean_units,
        "indicators": all_kpis,
        "is_scheduled_term2": code in schedule,
        "score_ratio": "80:20" if is_corruption else c.get("score_ratio", "70:30"),
        "ratio_display": "80:20 (40:10:40:10)" if is_corruption else c.get("ratio_display", ""),
        "kpa_ratio": "100:-:-" if is_corruption else c.get("kpa_ratio", ""),
        "score_pre_mid": 40 if is_corruption else c.get("score_pre_mid"),
        "score_mid": 10 if is_corruption else c.get("score_mid"),
        "score_post_mid": 40 if is_corruption else c.get("score_post_mid"),
        "score_final": 10 if is_corruption else c.get("score_final"),
        "target_mid_score": 10 if is_corruption else c.get("target_mid_score"),
        "target_fin_score": 10 if is_corruption else c.get("target_fin_score"),
        "midExamScores": [5, 5] if is_corruption else c.get("midExamScores", []),
        "finExamScores": [5, 5] if is_corruption else c.get("finExamScores", []),
        "exam_schedule": "สอบนอกตาราง" if is_corruption else c.get("exam_schedule", ""),
        "exam_duration_text": "สอบนอกตาราง" if is_corruption else c.get("exam_duration_text", ""),
        "key_task": "-" if is_corruption else c.get("key_task", "")
    }

# Write courses_2_2569.json
out_json = os.path.join(target_dir, "data", "courses_2_2569.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(compiled_courses, f, ensure_ascii=False, indent=2)

# Write courses_2_2569.js
out_js = os.path.join(target_dir, "data", "courses_2_2569.js")
with open(out_js, "w", encoding="utf-8") as f:
    f.write("/* Auto-generated from compile_assessment_hub_data.py */\n")
    f.write("window.COURSES_DATA = ")
    json.dump(compiled_courses, f, ensure_ascii=False)
    f.write(";\n")

# Copy template docx to AssessmentHub
template_src = r"c:\Users\peera\Desktop\AntigravityProject\CurriculumMD\templates"
template_dest = os.path.join(target_dir, "templates")
if os.path.exists(template_src):
    for item in os.listdir(template_src):
        if item.endswith(".docx"):
            s = os.path.join(template_src, item)
            d = os.path.join(template_dest, item)
            shutil.copy2(s, d)
            print(f"Copied template: {item}")

print(f"Compiled {len(compiled_courses)} courses to {out_json}")
print(f"Compiled {len(compiled_courses)} courses to {out_js}")
print("Data & Templates ready!")
