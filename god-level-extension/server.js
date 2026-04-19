/**
 * GOD LEVEL AI - Server
 * Executes real Python code for each framework demo
 */

const { spawn } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');

const DEMOS = {
  langgraph: {
    name: 'LangGraph',
    script: '01_langgraph_demo.py',
    icon: '🔗',
    color: '#4facfe'
  },
  crewai: {
    name: 'CrewAI',
    script: '02_crewai_demo.py',
    icon: '👥',
    color: '#f5576c'
  },
  agno: {
    name: 'Agno',
    script: '03_agno_demo.py',
    icon: '🧠',
    color: '#30cfd0'
  },
  autogen: {
    name: 'AutoGen',
    script: '04_autogen_demo.py',
    icon: '🤖',
    color: '#fa709a'
  },
  llamaindex: {
    name: 'LlamaIndex',
    script: '05_llamaindex_demo.py',
    icon: '📚',
    color: '#a8edea'
  },
  chromadb: {
    name: 'ChromaDB',
    script: '06_chromadb_demo.py',
    icon: '💾',
    color: '#ff9a9e'
  },
  deepeval: {
    name: 'DeepEval',
    script: '07_deepeval_demo.py',
    icon: '🧪',
    color: '#ffecd2'
  },
  phoenix: {
    name: 'Arize Phoenix',
    script: '08_phoenix_demo.py',
    icon: '🔮',
    color: '#a18cd1'
  },
  weaviate: {
    name: 'Weaviate',
    script: '09_weaviate_demo.py',
    icon: '🚀',
    color: '#84fab0'
  }
};

function runPythonDemo(demoName) {
  return new Promise((resolve, reject) => {
    const demo = DEMOS[demoName];
    if (!demo) {
      reject(new Error(`Unknown demo: ${demoName}`));
      return;
    }

    const scriptPath = path.join(__dirname, 'demos', demo.script);
    console.log(`\n${demo.icon} Running ${demo.name}...`);

    const startTime = Date.now();
    const process = spawn('python', [scriptPath], {
      cwd: __dirname,
      shell: true
    });

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    process.on('close', (code) => {
      const duration = Date.now() - startTime;
      const result = {
        framework: demo.name,
        demo: demoName,
        success: code === 0,
        output: stdout,
        error: stderr,
        duration: `${duration}ms`
      };

      if (code === 0) {
        console.log(`✅ ${demo.name} completed in ${duration}ms`);
      } else {
        console.log(`❌ ${demo.name} failed with code ${code}`);
      }

      resolve(result);
    });

    process.on('error', (err) => {
      reject(err);
    });
  });
}

async function runAllDemos() {
  console.log('='.repeat(60));
  console.log('⚡ GOD LEVEL AI - Running All Framework Demos');
  console.log('='.repeat(60));

  const results = {};
  const startTime = Date.now();

  for (const [name, demo] of Object.entries(DEMOS)) {
    try {
      results[name] = await runPythonDemo(name);
    } catch (err) {
      results[name] = {
        framework: demo.name,
        demo: name,
        success: false,
        error: err.message
      };
    }
  }

  const totalDuration = Date.now() - startTime;
  const passed = Object.values(results).filter(r => r.success).length;
  const failed = Object.values(results).filter(r => !r.success).length;

  console.log('\n' + '='.repeat(60));
  console.log('📊 DEMO RESULTS SUMMARY');
  console.log('='.repeat(60));
  console.log(`Total: ${Object.keys(results).length} | ✅ Passed: ${passed} | ❌ Failed: ${failed}`);
  console.log(`Total time: ${totalDuration}ms`);
  console.log('='.repeat(60));

  return results;
}

// Simple HTTP server to serve HTML and API
const server = http.createServer(async (req, res) => {
  if (req.url === '/api/demos' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(Object.keys(DEMOS).map(k => ({
      id: k,
      ...DEMOS[k]
    })), null, 2));
    return;
  }

  if (req.url.startsWith('/api/run/') && req.method === 'GET') {
    const demoName = req.url.split('/')[3];
    try {
      const result = await runPythonDemo(demoName);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(result, null, 2));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
    return;
  }

  if (req.url === '/api/run-all' && req.method === 'GET') {
    const results = await runAllDemos();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(results, null, 2));
    return;
  }

  // Serve HTML file
  const htmlPath = path.join(__dirname, 'index.html');
  fs.readFile(htmlPath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(data);
  });
});

const PORT = 3500;

if (require.main === module) {
  if (process.argv.includes('--run-all')) {
    runAllDemos().then(() => process.exit(0));
  } else {
    server.listen(PORT, () => {
      console.log(`
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ⚡ GOD LEVEL AI - 100% POWER UNLOCKED ⚡                 ║
║                                                              ║
║     Server running at: http://localhost:${PORT}                 ║
║                                                              ║
║     API Endpoints:                                           ║
║     • GET /api/demos       - List all demos                  ║
║     • GET /api/run/{name}  - Run specific demo               ║
║     • GET /api/run-all     - Run all demos                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
      `);
    });
  }
}

module.exports = { runPythonDemo, runAllDemos, DEMOS };
