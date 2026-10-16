const fs = require('fs');

// Read kpi_data.js
let kpiCode = fs.readFileSync('kpi_data.js', 'utf8');
kpiCode = kpiCode.replace('const OPEN_CURRICULUM_DATA', 'global.OPEN_CURRICULUM_DATA');
eval(kpiCode);
const data = global.OPEN_CURRICULUM_DATA;

console.log('Total KPIs:', data.kpis.length);
console.log('Total Subjects:', Object.keys(data.subject_meta).length);
console.log('Total Standards:', Object.keys(data.standards).length);

// Read semester_catalog.json
let catalog = {};
if (fs.existsSync('semester_catalog.json')) {
  catalog = JSON.parse(fs.readFileSync('semester_catalog.json', 'utf8'));
  console.log('Total Courses in catalog:', Object.keys(catalog.by_course_code || {}).length);
}

// Build Graph Nodes & Edges
function buildCurriculumGraph() {
  const rootNode = {
    id: 'root-curriculum',
    kind: 'root',
    name: 'หลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน',
    shortLabel: 'CurriculumMD',
    subLabel: 'พ.ศ. ๒๕๕๑ (ปรับปรุง ๒๕๖๐) • โรงเรียนพัฒนานิคม',
    x: 0,
    y: 0,
    size: 20,
    color: '#0d3d70'
  };

  const ringRadius = {
    subject: 140,
    standard: 280,
    kpi: 460,
    course: 630
  };

  const subjectOrder = [
    'ภาษาไทย',
    'คณิตศาสตร์',
    'วิทยาศาสตร์และเทคโนโลยี',
    'สังคมศึกษา ศาสนา และวัฒนธรรม',
    'สุขศึกษาและพลศึกษา',
    'ศิลปะ',
    'การงานอาชีพ',
    'ภาษาต่างประเทศ'
  ];

  const totalKpis = data.kpis.length;
  let angleCursor = -Math.PI / 2;

  const subjectNodes = [];
  const standardNodes = [];
  const kpiNodes = [];
  const edges = [];

  // Group KPIs by subject and standard
  const kpisBySubject = {};
  const standardsBySubject = {};

  data.kpis.forEach(k => {
    if (!kpisBySubject[k.subject]) kpisBySubject[k.subject] = [];
    kpisBySubject[k.subject].push(k);

    if (!standardsBySubject[k.subject]) standardsBySubject[k.subject] = new Set();
    standardsBySubject[k.subject].add(k.standard);
  });

  subjectOrder.forEach(subj => {
    const sMeta = data.subject_meta[subj] || { color: '#64748b' };
    const sKpis = kpisBySubject[subj] || [];
    const span = (Math.PI * 2 * sKpis.length) / totalKpis;

    const startAngle = angleCursor;
    const endAngle = angleCursor + span;
    const midAngle = (startAngle + endAngle) / 2;

    const sNode = {
      id: `subj-${sMeta.code || subj}`,
      kind: 'subject',
      name: subj,
      code: sMeta.code || '',
      color: sMeta.color || '#3b82f6',
      kpiCount: sKpis.length,
      startAngle,
      endAngle,
      angle: midAngle,
      x: Math.round(Math.cos(midAngle) * ringRadius.subject),
      y: Math.round(Math.sin(midAngle) * ringRadius.subject),
      size: 14
    };
    subjectNodes.push(sNode);

    // Edge from root to subject
    edges.push({
      sourceId: rootNode.id,
      targetId: sNode.id,
      color: sNode.color,
      width: 2.5
    });

    // Standards under this subject
    const sStandards = Array.from(standardsBySubject[subj] || []).sort();
    if (sStandards.length > 0) {
      const stdAngleStep = (endAngle - startAngle) / sStandards.length;
      sStandards.forEach((stdCode, stdIdx) => {
        const stdAngle = startAngle + stdAngleStep * (stdIdx + 0.5);
        const stdKpis = sKpis.filter(k => k.standard === stdCode);
        const stdDesc = data.standards[stdCode] || '';

        const stdNode = {
          id: `std-${stdCode.replace(/\s+/g, '_')}`,
          kind: 'standard',
          code: stdCode,
          name: `มาตรฐาน ${stdCode}`,
          subject: subj,
          desc: stdDesc,
          kpiCount: stdKpis.length,
          angle: stdAngle,
          x: Math.round(Math.cos(stdAngle) * ringRadius.standard),
          y: Math.round(Math.sin(stdAngle) * ringRadius.standard),
          size: 8,
          color: sNode.color
        };
        standardNodes.push(stdNode);

        edges.push({
          sourceId: sNode.id,
          targetId: stdNode.id,
          color: sNode.color,
          width: 1.5
        });

        // KPIs under this standard
        const kpiStep = stdAngleStep / Math.max(stdKpis.length, 1);
        stdKpis.forEach((k, kIdx) => {
          const kAngle = startAngle + stdAngleStep * stdIdx + kpiStep * (kIdx + 0.5);
          // Radius variation to avoid clumping
          const radiusOffset = (kIdx % 3) * 14;
          const kRadius = ringRadius.kpi + radiusOffset;

          const kNode = {
            id: `kpi-${k.id || k.code.replace(/\s+/g, '_')}`,
            kind: 'kpi',
            code: k.code,
            name: `${k.code} ${k.text.slice(0, 35)}...`,
            fullText: k.text,
            coreContent: k.core_content || '',
            type: k.type, // 'ระหว่างทาง' or 'ปลายทาง'
            grade: k.grade,
            gradeBand: k.grade_band,
            standard: k.standard,
            subject: subj,
            courses: k.courses || [],
            angle: kAngle,
            x: Math.round(Math.cos(kAngle) * kRadius),
            y: Math.round(Math.sin(kAngle) * kRadius),
            size: k.type === 'ปลายทาง' ? 5.5 : 4,
            color: k.type === 'ปลายทาง' ? '#f59e0b' : '#38bdf8'
          };
          kpiNodes.push(kNode);

          edges.push({
            sourceId: stdNode.id,
            targetId: kNode.id,
            color: kNode.color,
            width: 0.8
          });
        });
      });
    }

    angleCursor = endAngle;
  });

  return { rootNode, subjectNodes, standardNodes, kpiNodes, edges };
}

const g = buildCurriculumGraph();
console.log('Graph built successfully:');
console.log('Root node:', g.rootNode.name);
console.log('Subject nodes:', g.subjectNodes.length);
console.log('Standard nodes:', g.standardNodes.length);
console.log('KPI nodes:', g.kpiNodes.length);
console.log('Edges count:', g.edges.length);
console.log('Sample edge:', g.edges[0]);
console.log('Sample KPI node:', g.kpiNodes[0].code, 'x:', g.kpiNodes[0].x, 'y:', g.kpiNodes[0].y);
