const fs = require('fs');

// Read kpi_data.js
let kpiCode = fs.readFileSync('kpi_data.js', 'utf8');
kpiCode = kpiCode.replace('const OPEN_CURRICULUM_DATA', 'global.OPEN_CURRICULUM_DATA');
eval(kpiCode);
const data = global.OPEN_CURRICULUM_DATA;

function build5LevelGraph() {
  const rootNode = {
    id: 'root-curriculum',
    kind: 'root',
    name: 'หลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน',
    code: 'CurriculumMD',
    shortLabel: 'หลักสูตรแกนกลาง',
    subLabel: 'พ.ศ. ๒๕๕๑ (ปรับปรุง ๒๕๖๐) • ๘ กลุ่มสาระ • ๓๑ สาระ • ๕๕ มาตรฐาน',
    x: 0,
    y: 0,
    size: 20,
    color: '#0d3d70'
  };

  const ringRadius = {
    subject: 130,
    strand: 250,
    standard: 380,
    kpi: 530
  };

  const subjectOrder = [
    'ภาษาไทย', 'คณิตศาสตร์', 'วิทยาศาสตร์และเทคโนโลยี', 'สังคมศึกษา ศาสนา และวัฒนธรรม',
    'สุขศึกษาและพลศึกษา', 'ศิลปะ', 'การงานอาชีพ', 'ภาษาต่างประเทศ'
  ];

  const totalKpis = data.kpis.length;
  let angleCursor = -Math.PI / 2;

  const nodes = [rootNode];
  const nodeById = new Map([[rootNode.id, rootNode]]);
  const edges = [];
  const neighborMap = new Map([[rootNode.id, new Set([rootNode.id])]]);

  // Group KPIs hierarchically: Subject -> Strand -> Standard -> KPIs
  const hierarchy = {};

  data.kpis.forEach(k => {
    const subj = k.subject;
    const strand = k.strand || 'สาระทั่วไป';
    const std = k.standard;

    if (!hierarchy[subj]) hierarchy[subj] = {};
    if (!hierarchy[subj][strand]) hierarchy[subj][strand] = {};
    if (!hierarchy[subj][strand][std]) hierarchy[subj][strand][std] = [];

    hierarchy[subj][strand][std].push(k);
  });

  let strandNodeCount = 0;
  let standardNodeCount = 0;
  let kpiNodeCount = 0;

  subjectOrder.forEach(subj => {
    const sMeta = data.subject_meta[subj] || { color: '#64748b' };
    const strandsObj = hierarchy[subj] || {};
    const sKpis = data.kpis.filter(k => k.subject === subj);
    const sSpan = (Math.PI * 2 * sKpis.length) / totalKpis;

    const sStartAngle = angleCursor;
    const sEndAngle = angleCursor + sSpan;
    const sMidAngle = (sStartAngle + sEndAngle) / 2;

    const sNode = {
      id: `subj-${sMeta.code || subj}`,
      kind: 'subject',
      name: subj,
      code: sMeta.code || subj,
      shortLabel: subj,
      color: sMeta.color || '#3b82f6',
      kpiCount: sKpis.length,
      startAngle: sStartAngle,
      endAngle: sEndAngle,
      angle: sMidAngle,
      x: Math.round(Math.cos(sMidAngle) * ringRadius.subject),
      y: Math.round(Math.sin(sMidAngle) * ringRadius.subject),
      size: 14,
      data: {
        why: data.subject_overviews?.[subj]?.why || '',
        what: data.subject_overviews?.[subj]?.what || '',
        quality: data.subject_overviews?.[subj]?.quality || {}
      }
    };

    nodes.push(sNode);
    nodeById.set(sNode.id, sNode);
    neighborMap.set(sNode.id, new Set([sNode.id, rootNode.id]));
    neighborMap.get(rootNode.id).add(sNode.id);

    edges.push({
      id: `edge-${rootNode.id}-${sNode.id}`,
      source: rootNode.id,
      target: sNode.id,
      color: sNode.color,
      width: 2.5
    });

    // Strands (สาระ)
    const strandEntries = Object.entries(strandsObj);
    let strandAngleCursor = sStartAngle;

    strandEntries.forEach(([strandName, stdObj], stIdx) => {
      strandNodeCount++;
      const stKpis = Object.values(stdObj).flat();
      const stSpan = (sSpan * stKpis.length) / Math.max(sKpis.length, 1);
      const stStartAngle = strandAngleCursor;
      const stEndAngle = strandAngleCursor + stSpan;
      const stMidAngle = (stStartAngle + stEndAngle) / 2;

      // Extract short strand label, e.g. "สาระที่ 1" or "สาระ 1: การอ่าน"
      const strandMatch = strandName.match(/สาระที่\s*([0-9๑-๙]+)\s*(.*)/);
      const strandNum = strandMatch ? strandMatch[1] : String(stIdx + 1);
      const strandTitle = strandMatch && strandMatch[2] ? strandMatch[2].trim() : strandName;

      const stNode = {
        id: `strand-${sMeta.code}-${strandNum}`,
        kind: 'strand',
        name: strandName,
        shortLabel: `สาระที่ ${strandNum}`,
        subLabel: strandTitle,
        fullTitle: strandName,
        subject: subj,
        kpiCount: stKpis.length,
        standardsCount: Object.keys(stdObj).length,
        color: sNode.color,
        angle: stMidAngle,
        x: Math.round(Math.cos(stMidAngle) * ringRadius.strand),
        y: Math.round(Math.sin(stMidAngle) * ringRadius.strand),
        size: 10
      };

      nodes.push(stNode);
      nodeById.set(stNode.id, stNode);
      neighborMap.set(stNode.id, new Set([stNode.id, sNode.id]));
      neighborMap.get(sNode.id).add(stNode.id);

      edges.push({
        id: `edge-${sNode.id}-${stNode.id}`,
        source: sNode.id,
        target: stNode.id,
        color: sNode.color,
        width: 1.8
      });

      // Standards (มาตรฐาน)
      const stdEntries = Object.entries(stdObj);
      let stdAngleCursor = stStartAngle;

      stdEntries.forEach(([stdCode, stdKpis], stdIdx) => {
        standardNodeCount++;
        const stdSpan = (stSpan * stdKpis.length) / Math.max(stKpis.length, 1);
        const stdStartAngle = stdAngleCursor;
        const stdEndAngle = stdAngleCursor + stdSpan;
        const stdMidAngle = (stdStartAngle + stdEndAngle) / 2;
        const stdDesc = data.standards[stdCode] || '';

        const stdNode = {
          id: `std-${stdCode.replace(/\s+/g, '_')}`,
          kind: 'standard',
          code: stdCode,
          name: `มาตรฐาน ${stdCode}`,
          shortLabel: stdCode,
          subLabel: stdDesc,
          strand: strandName,
          subject: subj,
          kpiCount: stdKpis.length,
          color: sNode.color,
          angle: stdMidAngle,
          x: Math.round(Math.cos(stdMidAngle) * ringRadius.standard),
          y: Math.round(Math.sin(stdMidAngle) * ringRadius.standard),
          size: 7
        };

        nodes.push(stdNode);
        nodeById.set(stdNode.id, stdNode);
        neighborMap.set(stdNode.id, new Set([stdNode.id, stNode.id]));
        neighborMap.get(stNode.id).add(stdNode.id);

        edges.push({
          id: `edge-${stNode.id}-${stdNode.id}`,
          source: stNode.id,
          target: stdNode.id,
          color: sNode.color,
          width: 1.2
        });

        // KPIs (ตัวชี้วัด)
        const kpiStep = stdSpan / Math.max(stdKpis.length, 1);
        stdKpis.forEach((k, kIdx) => {
          kpiNodeCount++;
          const kAngle = stdStartAngle + kpiStep * (kIdx + 0.5);
          const radiusOffset = (kIdx % 4) * 12;
          const kRadius = ringRadius.kpi + radiusOffset;

          const kNode = {
            id: `kpi-${k.id || k.code.replace(/\s+/g, '_')}`,
            kind: 'kpi',
            code: k.code,
            name: k.code,
            shortLabel: k.code.split(' ').pop() || k.code,
            fullText: k.text,
            coreContent: k.core_content || '',
            type: k.type,
            grade: k.grade,
            gradeBand: k.grade_band,
            strand: strandName,
            standard: stdCode,
            standardDesc: stdDesc,
            subject: subj,
            courses: k.courses || [],
            angle: kAngle,
            x: Math.round(Math.cos(kAngle) * kRadius),
            y: Math.round(Math.sin(kAngle) * kRadius),
            size: k.type === 'ปลายทาง' ? 5 : 4,
            color: k.type === 'ปลายทาง' ? '#f59e0b' : '#38bdf8'
          };

          nodes.push(kNode);
          nodeById.set(kNode.id, kNode);
          neighborMap.set(kNode.id, new Set([kNode.id, stdNode.id]));
          neighborMap.get(stdNode.id).add(kNode.id);

          edges.push({
            id: `edge-${stdNode.id}-${kNode.id}`,
            source: stdNode.id,
            target: kNode.id,
            color: kNode.color,
            width: 0.7
          });
        });

        stdAngleCursor = stdEndAngle;
      });

      strandAngleCursor = stEndAngle;
    });

    angleCursor = sEndAngle;
  });

  return { rootNode, nodes, nodeById, edges, neighborMap, strandNodeCount, standardNodeCount, kpiNodeCount };
}

const g = build5LevelGraph();
console.log('5-Level Graph Summary:');
console.log('Total Nodes:', g.nodes.length);
console.log('Root:', 1);
console.log('Subjects:', 8);
console.log('Strands (สาระ):', g.strandNodeCount);
console.log('Standards (มาตรฐาน):', g.standardNodeCount);
console.log('KPIs (ตัวชี้วัด):', g.kpiNodeCount);
console.log('Edges:', g.edges.length);
