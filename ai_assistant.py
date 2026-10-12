"""
🤖 AI Curriculum Co-pilot: ผู้ช่วยครูอัจฉริยะด้านหลักสูตรและแผนการสอน
ดึงข้อมูลตรงจาก CurriculumMD Vault (2,056 ตัวชี้วัด สพฐ.)
"""

import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

VAULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Curriculum_Vault')

def parse_kpi_file(filepath):
    """อ่านและสกัดข้อมูลตัวชี้วัดจาก YAML Frontmatter และเนื้อหา Markdown"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return None
    
    if not content.startswith('---'):
        return None
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None
        
    fm_text = parts[1]
    body = parts[2]
    
    # Parse frontmatter
    fm = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if ':' in line and not line.startswith('#'):
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
            
    code = fm.get('code', os.path.splitext(os.path.basename(filepath))[0])
    grade = fm.get('grade', '')
    kpi_type = fm.get('indicator_type', fm.get('type', 'ไม่ระบุ'))
    
    # Extract description (> ...)
    desc_match = re.search(r'>\s*(.+)', body)
    desc = desc_match.group(1).strip() if desc_match else ''
    clean_desc = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', desc)
    
    # Extract core content
    core_bullets = []
    if '**สาระการเรียนรู้แกนกลาง:**' in body:
        core_part = body.split('**สาระการเรียนรู้แกนกลาง:**')[1].strip()
        for line in core_part.splitlines():
            line_str = line.strip()
            if line_str.startswith(('-', '•', '*')):
                clean_bullet = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', line_str.lstrip('-•* ')).strip()
                if clean_bullet:
                    core_bullets.append(clean_bullet)
            elif line_str and not line_str.startswith('#'):
                clean_bullet = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', line_str).strip()
                if clean_bullet:
                    core_bullets.append(clean_bullet)
                    
    return {
        'id': fm.get('id', ''),
        'code': code,
        'grade': grade,
        'type': kpi_type,
        'desc': clean_desc,
        'core': core_bullets,
        'body': body,
        'file': filepath
    }

def match_grade(file_grade, query_grade):
    """ตรวจสอบความสอดคล้องของระดับชั้น รวมถึงช่วงชั้นมัธยมศึกษาตอนปลาย (ม.4-6)"""
    if not query_grade:
        return True
    q = query_grade.strip()
    fg = file_grade.strip()
    if q == fg:
        return True
    # จับคู่ ม.4, ม.5, ม.6 กับช่วงชั้น ม.4-6
    if q in ['ม.4', 'ม.5', 'ม.6', 'ม.ปลาย'] and fg in ['ม.4-6', 'ม.ปลาย', 'ม.4', 'ม.5', 'ม.6']:
        return True
    return False

def search_kpis(query, grade=None, limit=5):
    """ค้นหาตัวชี้วัดที่เกี่ยวข้องจากคลังข้อมูลตามคำค้นหาและระดับชั้น พร้อมจัดอันดับความตรงกัน"""
    candidates = []
    q_lower = query.lower().strip()
    
    for root, dirs, files in os.walk(VAULT_DIR):
        if '09_หลักสูตรสถานศึกษา' in root:
            continue
        for f in files:
            if not f.endswith('.md') or f.startswith('00_'):
                continue
            
            fpath = os.path.join(root, f)
            kpi = parse_kpi_file(fpath)
            if not kpi:
                continue
                
            if grade and not match_grade(kpi['grade'], grade):
                continue
                
            # จัดอันดับคะแนนความตรงกัน (Relevance Ranking)
            score = 0
            if q_lower in kpi['code'].lower():
                score += 100
            if q_lower in kpi['desc'].lower():
                score += 50
            for b in kpi['core']:
                if q_lower in b.lower():
                    score += 20
                    break
            if q_lower in kpi['body'].lower() and score == 0:
                score += 5
                
            if score > 0:
                candidates.append((score, kpi))
                
    # เรียงลำดับตามคะแนนความตรงกันสูงสุด
    candidates.sort(key=lambda x: x[0], reverse=True)
    return [kpi for _, kpi in candidates[:limit]]

def build_lesson_plan_prompt(topic, grade, kpis):
    """สร้าง Prompt สำหรับนำไปให้ AI (Gemini / Claude / ChatGPT) เขียนแผนการสอน"""
    kpi_text = ""
    for k in kpis:
        core_str = ', '.join(k['core'][:3]) if k['core'] else '-'
        kpi_text += f"- รหัส: {k['code']} ({k['type']})\n  คำอธิบาย: {k['desc']}\n  สาระแกนกลาง: {core_str}\n"
        
    prompt = f"""
คุณคือผู้เชี่ยวชาญด้านการออกแบบหลักสูตรและการจัดการเรียนรู้เชิงรุก (Active Learning) ระดับชาติ
โปรดเขียน 'แผนการจัดการเรียนรู้ 1 คาบ (50 นาที)' สำหรับระดับชั้น {grade} ในหัวข้อ '{topic}'

ข้อมูลตัวชี้วัดทางการจาก สพฐ. ๒๕๖๖:
{kpi_text}

โครงสร้างแผนการสอนที่ต้องการ:
1. สาระสำคัญ / ความคิดรวบยอด (Key Concept)
2. จุดประสงค์การเรียนรู้ (K-P-A):
   - ด้านความรู้ (Knowledge: K)
   - ด้านทักษะ/กระบวนการ (Process: P)
   - ด้านคุณลักษณะอันพึงประสงค์ (Attitude: A)
3. กิจกรรมการเรียนรู้ (รูปแบบ Active Learning / 5E / Problem-based):
   - ขั้นนำ (10 นาที): การกระตุ้นความสนใจและเชื่อมโยงประสบการณ์เดิม
   - ขั้นสอน/สืบเสาะ (30 นาที): กิจกรรมลงมือปฏิบัติ การทำงานกลุ่ม
   - ขั้นสรุป (10 นาที): การสะท้อนคิดและการประเมินตนเอง
4. สื่อและแหล่งการเรียนรู้
5. การวัดและประเมินผล:
   - การประเมินตัวชี้วัดระหว่างทาง (Formative Assessment)
   - การประเมินตัวชี้วัดปลายทาง (Summative Assessment)
   - เกณฑ์การให้คะแนน (Rubric)
"""
    return prompt.strip()

def main():
    print("=" * 70)
    print("🤖 ยินดีต้อนรับสู่ AI Curriculum Co-pilot (ผู้ช่วยออกแบบการสอน)")
    print("=" * 70)
    
    topic = input("📌 ป้อนหัวข้อ/เนื้อหาที่ต้องการสอน (เช่น การสังเคราะห์ด้วยแสง, อัตราส่วน, คำซ้อน): ").strip()
    if not topic: topic = "เซลล์"
    
    grade = input("📌 ป้อนระดับชั้น (เช่น ป.1, ม.1, ม.3, ม.4, ม.5): ").strip()
    if not grade: grade = "ม.1"
    
    print(f"\n🔍 กำลังค้นหาตัวชี้วัดที่ตรงกับ '{topic}' ระดับชั้น {grade} ในคลัง 2,056 ตัวชี้วัด...")
    matches = search_kpis(topic, grade=grade, limit=3)
    
    if matches:
        print(f"\n✅ พบ {len(matches)} ตัวชี้วัดทางการที่เกี่ยวข้อง:")
        for idx, m in enumerate(matches, 1):
            print(f"  {idx}. [{m['type']}] {m['code']} ({m['grade']}): {m['desc']}")
            if m['core']:
                print(f"     สาระแกนกลาง: {m['core'][0][:80]}...")
        
        prompt = build_lesson_plan_prompt(topic, grade, matches)
        print("\n" + "=" * 70)
        print("📋 PROMPT อัจฉริยะสำหรับนำไปสร้างแผนการสอน (Copy ไปใช้ได้ทันที):")
        print("=" * 70)
        print(prompt)
        print("=" * 70)
    else:
        print(f"❌ ไม่พบตัวชี้วัดที่เกี่ยวข้องกับ '{topic}' สำหรับระดับชั้น {grade}")

if __name__ == '__main__':
    main()
