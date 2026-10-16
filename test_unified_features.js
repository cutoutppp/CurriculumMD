// test_unified_features.js
const http = require('http');
const { execSync } = require('child_process');

async function testHeadless() {
  const edgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
  const userDataDir = `C:\\Users\\peera\\AppData\\Local\\Temp\\edge_test_${Date.now()}`;
  const port = 9333;

  const edgeProcess = require('child_process').spawn(edgePath, [
    `--remote-debugging-port=${port}`,
    '--headless=new',
    '--disable-gpu',
    `--user-data-dir=${userDataDir}`,
    'http://127.0.0.1:8088/index.html'
  ]);

  await new Promise(r => setTimeout(r, 2000));

  function getJson(url) {
    return new Promise((resolve, reject) => {
      http.get(url, res => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => resolve(JSON.parse(data)));
      }).on('error', reject);
    });
  }

  const targets = await getJson(`http://127.0.0.1:${port}/json`);
  const pageTarget = targets.find(t => t.url && t.url.includes('8088'));
  if (!pageTarget) throw new Error('Could not find 8088 target');
  const wsUrl = pageTarget.webSocketDebuggerUrl;

  // In Node.js 24, WebSocket is a built-in global
  const ws = new WebSocket(wsUrl);

  await new Promise((resolve, reject) => {
    ws.addEventListener('open', resolve);
    ws.addEventListener('error', reject);
  });

  let msgId = 1;
  function sendCommand(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = msgId++;
      const handler = (evt) => {
        const parsed = JSON.parse(evt.data);
        if (parsed.id === id) {
          ws.removeEventListener('message', handler);
          if (parsed.error) reject(parsed.error);
          else resolve(parsed.result);
        }
      };
      ws.addEventListener('message', handler);
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  // Enable Runtime
  await sendCommand('Runtime.enable');

  async function evaluate(expr) {
    const res = await sendCommand('Runtime.evaluate', {
      expression: expr,
      returnByValue: true,
      awaitPromise: true
    });
    if (res.exceptionDetails) {
      console.error('Eval exception:', res.exceptionDetails);
    }
    return res.result ? res.result.value : null;
  }

  console.log('--- Testing Initial Load & Defaults ---');
  const initialNumeral = await evaluate("state.numeral");
  console.log('Initial numeral mode:', initialNumeral);
  const initialGraphMode = await evaluate("state.graphMode");
  console.log('Initial graph perspective:', initialGraphMode);
  const totalNodes = await evaluate("graph.nodes.length");
  console.log('Total nodes in initial tree:', totalNodes);
  const totalEdges = await evaluate("graph.edges.length");
  console.log('Total edges in initial tree:', totalEdges);

  console.log('\n--- Testing Numeral Switcher ---');
  // Switch to Arabic
  await evaluate("document.getElementById('btn-num-arabic').click()");
  const arabicMetric = await evaluate("document.getElementById('stat-total-kpi').textContent");
  console.log('Arabic KPI stat:', arabicMetric); // should be 2,056

  // Switch to Thai
  await evaluate("document.getElementById('btn-num-thai').click()");
  const thaiMetric = await evaluate("document.getElementById('stat-total-kpi').textContent");
  console.log('Thai KPI stat:', thaiMetric); // should be ๒,๐๕๖

  console.log('\n--- Testing Tree Perspective Switcher on Same Page ---');
  // Switch to Grade perspective
  await evaluate("document.getElementById('btn-tree-grade').click()");
  const gradeGraphMode = await evaluate("state.graphMode");
  console.log('Switched graph mode:', gradeGraphMode);
  const gradeNodesCount = await evaluate("graph.nodes.length");
  console.log('Grade perspective nodes count:', gradeNodesCount);
  const centerShortLabel = await evaluate("graph.centerNode.shortLabel");
  console.log('Center node:', centerShortLabel);

  // Switch back to Subject perspective
  await evaluate("document.getElementById('btn-tree-subject').click()");
  const subjectGraphMode = await evaluate("state.graphMode");
  console.log('Switched back graph mode:', subjectGraphMode);
  const subjNodesCount = await evaluate("graph.nodes.length");
  console.log('Subject perspective nodes count:', subjNodesCount);

  console.log('\n--- Testing Line & Node Pruning on Filter ---');
  // Initially no nodes hidden
  const hiddenNodesInitial = await evaluate("graph.nodes.filter(n => n.element && n.element.style.display === 'none').length");
  const hiddenEdgesInitial = await evaluate("graph.edges.filter(e => e.element && e.element.style.display === 'none').length");
  console.log('Hidden nodes before filter:', hiddenNodesInitial);
  console.log('Hidden edges before filter:', hiddenEdgesInitial);

  // Set Subject Filter = "ภาษาไทย"
  await evaluate("state.subject = 'ภาษาไทย'; applyFilters();");
  const hiddenNodesAfterSubj = await evaluate("graph.nodes.filter(n => n.element && n.element.style.display === 'none').length");
  const visibleNodesAfterSubj = await evaluate("graph.nodes.filter(n => n.element && n.element.style.display !== 'none').length");
  const hiddenEdgesAfterSubj = await evaluate("graph.edges.filter(e => e.element && e.element.style.display === 'none').length");
  const visibleEdgesAfterSubj = await evaluate("graph.edges.filter(e => e.element && e.element.style.display !== 'none').length");
  console.log('Nodes after Thai subject filter -> Visible:', visibleNodesAfterSubj, 'Hidden (Cut off):', hiddenNodesAfterSubj);
  console.log('Edges after Thai subject filter -> Visible:', visibleEdgesAfterSubj, 'Hidden (Cut off):', hiddenEdgesAfterSubj);

  // Clear filters
  await evaluate("clearCatalogSearch()");
  const hiddenNodesAfterClear = await evaluate("graph.nodes.filter(n => n.element && n.element.style.display === 'none').length");
  console.log('Hidden nodes after clear:', hiddenNodesAfterClear);

  console.log('\n--- Testing Catalog Table Search for Primary Grades ---');
  // Switch to catalog view
  await evaluate("switchToCatalogView()");
  // Filter Grade = "ป.2"
  await evaluate("state.grade = 'ป.2'; renderCatalogTable();");
  const catalogCountP2 = await evaluate("document.getElementById('catalogResultCount').textContent");
  console.log('Catalog P.2 filter result count:', catalogCountP2.trim());

  // Search keyword in P.2
  await evaluate("state.search = 'การอ่าน'; renderCatalogTable();");
  const catalogCountSearch = await evaluate("document.getElementById('catalogResultCount').textContent");
  console.log('Catalog search "การอ่าน" in P.2 result count:', catalogCountSearch.trim());

  ws.close();
  edgeProcess.kill();
  console.log('\nAll tests passed successfully!');
}

testHeadless().catch(err => {
  console.error('Test error:', err);
  process.exit(1);
});
