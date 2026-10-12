"""
🤖 AI Curriculum Co-pilot: ผู้ช่วยครูอัจฉริยะด้านหลักสูตรและแผนการสอน
ดึงข้อมูลตรงจาก CurriculumMD Vault (2,024 ตัวชี้วัด สพฐ.)
"""

import os
import re
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

VAULT_DIR = os.path.join(os.path.dirname(__file__), 'Curriculum_Vault')

def search_kpis(query, grade=None, limit=5):
    """ค้นหาตัวชี้วัดที่เกี่ยวข้องจากคลังข้อมูลตามคำค้นหาและระดับชั้น"""
    results = []
    for root, dirs, files in os.walk(VAULT_DIR):
        for f in files:
            if not f.endswith('.md') or f.startswith('00_'): continue
            if grade and f" {grade}-" not in f and f" {grade}/" not in f:
                continue
            
            fpath = os.path.join(root, f)
            with open(fpath, 'r', encoding='utf-8') as fp:
                content = fp.read()
            
            if query.lower() in content.lower():
                # Extract code and description
                m_alias = re.search(r'aliases:\s*\["([^"]+)"\]', content)
                code = m_alias.group(1) if m_alias else f[:-3].replace('-', '/')
                m_desc = re.search(r'>\s*(.+)', content)
                desc = m_desc.group(1).strip() if m_desc else ''
                m_type = re.search(r'ประเภทตัวชี้วัด:\s*(.+)', content)
                kpi_type = m_type.group(1).strip() if m_type else 'ไม่ระบุ'
                
                # Extract core content
                core_bullets = []
                if '**สาระการเรียนรู้แกนกลาง:**' in content:
                    parts = content.split('**สาระการเรียนรู้แกนกลาง:**')[1].strip().split('\n')
                    core_bullets = [b.strip('-• ').strip() for b in parts if b.strip().startswith(('-', '•'))]

                results.append({
                    'code': code,
                    'type': kpi_type,
                    'desc': desc,
                    'core': core_bullets,
                    'file': fpath
                })
                if len(results) >= limit:
                    break
        if len(results) >= limit:
            break
    return results

def build_lesson_plan_prompt(topic, grade, kpis):
    """สร้าง Prompt สำหรับนำไปให้ AI (Gemini / Claude / ChatGPT) เขียนแผนการสอน"""
    kpi_text = ""
    for k in kpis:
        kpi_text += f"- รหัส: {k['code']} ({k['type']})\n  คำอธิบาย: {k['desc']}\n  สาระแกนกลาง: {', '.join(k['core'])}\n"
        
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
    
    grade = input("📌 ป้อนระดับชั้น (เช่น ป.1, ม.1, ม.3, ม.4): ").strip()
    if not grade: grade = "ม.1"
    
    print(f"\n🔍 กำลังค้นหาตัวชี้วัดที่ตรงกับ '{topic}' ระดับชั้น {grade} ในคลัง 2,024 ตัวชี้วัด...")
    matches = search_kpis(topic, grade=grade, limit=3)
    
    if not matches:
        print("⚠️ ไม่พบตัวชี้วัดที่ตรงกับเงื่อนไขตรง ๆ ลองค้นหาแบบกว้างขึ้น...")
        matches = search_kpis(topic, limit=3)

    if matches:
        print(f"\n✅ พบ {len(matches)} ตัวชี้วัดทางการที่เกี่ยวข้อง:")
        for idx, m in enumerate(matches, 1):
            print(f"  {idx}. [{m['type']}] {m['code']}: {m['desc']}")
            if m['core']:
                print(f"     สาระแกนกลาง: {m['core'][0][:80]}...")
        
        prompt = build_lesson_plan_prompt(topic, grade, matches)
        print("\n" + "=" * 70)
        print("📋 PROMPT อัจฉริยะสำหรับนำไปสร้างแผนการสอน (Copy ไปใช้ได้ทันที):")
        print("=" * 70)
        print(prompt)
        print("=" * 70)
    else:
        print("❌ ไม่พบตัวชี้วัดที่เกี่ยวข้อง")

if __name__ == '__main__':
    main()
