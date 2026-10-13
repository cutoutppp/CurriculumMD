"""
🤖 AI Curriculum Co-pilot: ผู้ช่วยครูอัจฉริยะด้านหลักสูตรและแผนการสอน
ดึงข้อมูลตรงจาก CurriculumMD Vault (2,056 ตัวชี้วัด สพฐ.)
มาพร้อมระบบ Strict Grade Boundary และ Semantic & Weighted Relevance Scoring
"""

import os
import re
import sys
import glob

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

VAULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Curriculum_Vault')

def parse_kpi_file(filepath):
    """อ่านและสกัดข้อมูลตัวชี้วัดจาก YAML Frontmatter และเนื้อหา Markdown"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
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
            elif line_str and not line_str.startswith('#') and not line_str.startswith('---'):
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

def normalize_grade_input(g):
    """แปลงรูปแบบระดับชั้นให้เป็นมาตรฐานเดียวกัน เช่น 'ป1' -> 'ป.1', 'ม1' -> 'ม.1'"""
    if not g:
        return None
    g = g.strip()
    g = re.sub(r'^ประถม(?:ศึกษา)?(?:\s*ปีที่)?', 'ป.', g)
    g = re.sub(r'^มัธยม(?:ศึกษา)?(?:\s*ปีที่)?', 'ม.', g)
    g = re.sub(r'^([ปม])(\d)', r'\1.\2', g)
    return g

def match_grade(file_grade, query_grade):
    """
    ตรวจสอบความสอดคล้องของระดับชั้นอย่างเข้มงวด (Strict Grade Boundary)
    ป้องกันการดึงตัวชี้วัดข้ามระดับชั้นโดยเด็ดขาด
    """
    if not query_grade:
        return True
    q = normalize_grade_input(query_grade)
    fg = file_grade.strip()
    
    if q == fg:
        return True
        
    # ช่วงชั้นประถมศึกษาตอนต้น (ป.1-3)
    if q in ['ป.1', 'ป.2', 'ป.3'] and fg in ['ป.1-3', 'ป.1', 'ป.2', 'ป.3']:
        return (q == fg) or (fg == 'ป.1-3')
        
    # ช่วงชั้นประถมศึกษาตอนปลาย (ป.4-6)
    if q in ['ป.4', 'ป.5', 'ป.6'] and fg in ['ป.4-6', 'ป.4', 'ป.5', 'ป.6']:
        return (q == fg) or (fg == 'ป.4-6')
        
    # ช่วงชั้นมัธยมศึกษาตอนต้น (ม.1-3)
    if q in ['ม.1', 'ม.2', 'ม.3'] and fg in ['ม.1-3', 'ม.1', 'ม.2', 'ม.3']:
        return (q == fg) or (fg == 'ม.1-3')
        
    # ช่วงชั้นมัธยมศึกษาตอนปลาย (ม.4-6)
    if q in ['ม.4', 'ม.5', 'ม.6', 'ม.ปลาย'] and fg in ['ม.4-6', 'ม.ปลาย', 'ม.4', 'ม.5', 'ม.6']:
        return True
        
    return False

def search_kpis(query, grade=None, limit=5):
    """
    ค้นหาตัวชี้วัดที่เกี่ยวข้องจากคลังข้อมูลตามคำค้นหาและระดับชั้น
    พร้อมระบบจัดอันดับคะแนนความเกี่ยวข้องเชิงความหมาย (Semantic & Relevance Scoring)
    คงความเข้มงวดของระดับชั้น ไม่มีการข้ามระดับชั้นโดยเด็ดขาด
    """
    candidates = []
    q_lower = query.lower().strip()
    norm_grade = normalize_grade_input(grade)
    
    q_tokens = [t.strip() for t in re.split(r'[\s,]+', q_lower) if len(t.strip()) > 1]
    
    for i in range(1, 9):
        subj_pattern = f"{VAULT_DIR}/0{i}_*/**/*.md"
        for fpath in glob.glob(subj_pattern, recursive=True):
            fname = os.path.basename(fpath)
            if fname.startswith('00_'):
                continue
            if not re.search(r'^[ทควสพศงต]\s*\d+\.\d+\s*[ปม]\.', fname):
                continue
                
            kpi = parse_kpi_file(fpath)
            if not kpi:
                continue
                
            # บังคับขอบเขตระดับชั้นอย่างเข้มงวด (Strict Grade Boundary)
            if norm_grade and not match_grade(kpi['grade'], norm_grade):
                continue
                
            # คำนวณคะแนนความเกี่ยวข้องแบบถ่วงน้ำหนัก (Weighted Multi-Tier Scoring)
            score = 0
            code_lower = kpi['code'].lower()
            desc_lower = kpi['desc'].lower()
            core_str = ' '.join(kpi['core']).lower()
            body_lower = kpi['body'].lower()
            
            # 1. ตรงกับรหัสตัวชี้วัดเป๊ะ ๆ เช่น "ว 1.1", "ว 1.1 ม.1/1"
            if q_lower == code_lower or q_lower in code_lower:
                score += 200
                
            # 2. ข้อความค้นหาปรากฏทั้งวลีในคำอธิบายตัวชี้วัด (Exact Phrase in Description)
            if q_lower in desc_lower:
                score += 100
                
            # 3. ข้อความค้นหาปรากฏในสาระการเรียนรู้แกนกลาง (Exact Phrase in Core Content)
            if q_lower in core_str:
                score += 60
                
            # 4. คะแนนการจับคู่รายคำ (Token Overlap Scoring)
            matched_tokens = 0
            for t in q_tokens:
                if t in desc_lower:
                    score += 25
                    matched_tokens += 1
                elif t in core_str:
                    score += 15
                    matched_tokens += 1
                elif t in body_lower:
                    score += 5
                    matched_tokens += 1
                    
            if q_tokens and matched_tokens == len(q_tokens):
                score += 30
                
            if score > 0:
                candidates.append((score, kpi))
                
    # จัดเรียงตามคะแนนความเกี่ยวข้องจากมากไปน้อย
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
        print(f"\n❌ ไม่พบตัวชี้วัดที่เกี่ยวข้องกับ '{topic}' สำหรับระดับชั้น {grade} ในหลักสูตรแกนกลาง")
        print("   (ระบบรักษาวินัยของระดับชั้นอย่างเคร่งครัด จะไม่มีการสุ่มดึงตัวชี้วัดของระดับชั้นอื่นมาแทนที่)")

if __name__ == '__main__':
    main()
