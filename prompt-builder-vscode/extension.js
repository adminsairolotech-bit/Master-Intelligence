const vscode = require('vscode');

function activate(context) {
  const disposable = vscode.commands.registerCommand('promptBuilderChat.open', () => {
    const panel = vscode.window.createWebviewPanel(
      'promptBuilder',
      'Prompt Builder Pro',
      vscode.ViewColumn.One,
      { enableScripts: true }
    );
    panel.webview.html = getWebviewContent();
  });
  context.subscriptions.push(disposable);
}

function getWebviewContent() {
  return `<!DOCTYPE html>
<html>
<head>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe WPC', sans-serif;
    background: #1e1e1e; color: #ccc; padding: 15px; height: 100vh;
    overflow: hidden;
  }

  /* Header */
  .header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 15px;
  }
  .header h1 { color: #4ec9b0; font-size: 18px; }
  .header-controls { display: flex; gap: 10px; align-items: center; }

  /* Toggle Switch */
  .toggle-container {
    display: flex; align-items: center; gap: 8px;
    font-size: 12px;
  }
  .toggle {
    position: relative; width: 44px; height: 22px;
    background: #3c3c3c; border-radius: 11px; cursor: pointer;
    transition: background 0.3s;
  }
  .toggle.active { background: #4caf50; }
  .toggle::after {
    content: ''; position: absolute; top: 2px; left: 2px;
    width: 18px; height: 18px; background: #fff; border-radius: 50%;
    transition: transform 0.3s;
  }
  .toggle.active::after { transform: translateX(22px); }

  /* Skill Chips */
  .skill-chips {
    display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;
  }
  .chip {
    padding: 4px 10px; border-radius: 12px; font-size: 11px;
    background: #3c3c3c; color: #aaa; cursor: pointer;
    border: 1px solid transparent; transition: all 0.2s;
  }
  .chip:hover { background: #4a4a4a; color: #fff; }
  .chip.selected {
    background: #0e639c; color: #fff; border-color: #1177bb;
  }

  /* Tabs */
  .tabs {
    display: flex; gap: 5px; margin-bottom: 10px;
  }
  .tab {
    padding: 6px 14px; border-radius: 6px; font-size: 12px;
    background: #2d2d2d; color: #888; cursor: pointer; border: none;
  }
  .tab.active { background: #0e639c; color: #fff; }

  /* Panels */
  .panel { display: none; }
  .panel.active { display: block; }

  /* Template Cards */
  .template-grid {
    display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;
    max-height: 200px; overflow-y: auto;
  }
  .template-card {
    background: #252526; border: 1px solid #3c3c3c; border-radius: 8px;
    padding: 12px; cursor: pointer; transition: all 0.2s;
  }
  .template-card:hover { border-color: #4ec9b0; background: #2d2d30; }
  .template-card h4 { color: #4ec9b0; font-size: 13px; margin-bottom: 4px; }
  .template-card p { color: #888; font-size: 11px; }

  /* History List */
  .history-list {
    max-height: 200px; overflow-y: auto;
  }
  .history-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px; background: #252526; border-radius: 6px; margin-bottom: 6px;
    cursor: pointer; transition: background 0.2s;
  }
  .history-item:hover { background: #2d2d30; }
  .history-item .text {
    flex: 1; font-size: 12px; color: #ccc;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .history-item .time { font-size: 10px; color: #666; margin-left: 10px; }
  .history-item .delete {
    color: #f48771; margin-left: 8px; font-size: 10px; cursor: pointer;
  }

  /* Chat Box */
  .chat-box {
    height: 45%; border: 1px solid #3c3c3c; border-radius: 8px;
    background: #252526; padding: 10px; overflow-y: auto; margin-bottom: 10px;
  }
  .message { margin: 8px 0; padding: 8px 12px; border-radius: 8px; font-size: 13px; }
  .user { background: #0e639c; color: #fff; margin-left: 15%; }
  .bot { background: #2d2d2d; color: #dcdcaa; margin-right: 15%; }

  /* Prompt Result */
  .prompt-result {
    background: #1a1a1a; border: 1px solid #4ec9b0; border-radius: 8px;
    padding: 12px; margin-bottom: 10px; font-family: monospace; font-size: 12px;
    white-space: pre-wrap; color: #4ec9b0; display: none; max-height: 150px; overflow-y: auto;
  }
  .prompt-result-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 8px;
  }
  .prompt-result-header span { font-size: 11px; color: #888; }

  /* Input Area */
  .input-area { display: flex; gap: 10px; }
  .input-wrapper { flex: 1; position: relative; }
  input {
    width: 100%; padding: 12px; background: #3c3c3c; color: #fff;
    border: 1px solid #3c3c3c; border-radius: 8px; font-size: 14px;
  }
  input:focus { outline: none; border-color: #0e639c; }
  .input-lang {
    position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
    font-size: 10px; color: #888; background: #2d2d2d; padding: 2px 6px;
    border-radius: 4px;
  }
  button {
    padding: 12px 20px; background: #4caf50; color: #fff;
    border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: bold;
  }
  button:hover { background: #45a049; }
  .copy-btn { background: #0e639c; }
  .copy-btn:hover { background: #1177bb; }
  .clear-btn { background: #f48771; }
  .clear-btn:hover { background: #d8635c; }
  .api-btn { background: #9b59b6; }
  .api-btn:hover { background: #8e44ad; }
  .api-btn.active { background: #27ae60; }

  /* API Status */
  .api-status {
    display: none; padding: 8px; background: #2d2d2d; border-radius: 6px;
    margin-bottom: 10px; font-size: 11px; color: #888;
  }
  .api-status.active { display: block; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: #4a4a4a; border-radius: 3px; }

  /* Command Search - REMOVED */
  /* Settings Panel */
  #settingsPanel {
    background: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    max-height: 300px;
    overflow-y: auto;
  }
</style>
</head>
<body>
  <div class="header">
    <h1>🎯 Prompt Builder Pro</h1>
    <div class="header-controls">
      <div class="toggle-container">
        <span>Chat</span>
        <div class="toggle" id="chatToggle" onclick="toggleChat()"></div>
      </div>
    </div>
  </div>

  <!-- Skill Chips -->
  <div class="skill-chips" id="skillChips">
    <span class="chip" onclick="selectSkill(this, 'educator')">📚 Educator</span>
    <span class="chip" onclick="selectSkill(this, 'engineer')">💻 Engineer</span>
    <span class="chip" onclick="selectSkill(this, 'debugger')">🔧 Debugger</span>
    <span class="chip" onclick="selectSkill(this, 'reviewer')">👀 Reviewer</span>
    <span class="chip" onclick="selectSkill(this, 'writer')">✍️ Writer</span>
    <span class="chip" onclick="selectSkill(this, 'devops')">🚀 DevOps</span>
    <span class="chip" onclick="selectSkill(this, 'security')">🔒 Security</span>
    <span class="chip" onclick="selectSkill(this, 'data')">📊 Data</span>
    <span class="chip" onclick="selectSkill(this, 'business')">💼 Business</span>
    <span class="chip" onclick="selectSkill(this, 'support')">🎧 Support</span>
  </div>

  <!-- Command Search Bar - REMOVED PER USER REQUEST -->
  <!-- Users now just type naturally - system auto-detects task type -->

  <!-- Tabs -->
  <div class="tabs">
    <button class="tab active" onclick="switchTab('chat')">💬 Chat</button>
    <button class="tab" onclick="switchTab('templates')">📋 Templates</button>
    <button class="tab" onclick="switchTab('history')">📜 History</button>
    <button class="tab" onclick="switchTab('settings')">⚙️ Settings</button>
  </div>

  <!-- Chat Panel -->
  <div class="panel active" id="chatPanel">
    <div class="chat-box" id="chatBox">
      <div class="message bot">👋 Welcome! Type your idea below or select a template. Your prompt will be auto-generated with the best role and format.</div>
    </div>
    <div class="prompt-result" id="promptResult">
      <div class="prompt-result-header">
        <span>Generated Prompt:</span>
        <button class="copy-btn" style="padding:4px 8px;font-size:10px;" onclick="copyPrompt()">📋 Copy</button>
      </div>
      <div id="promptText"></div>
    </div>
    <div class="api-status" id="apiStatus">🔄 Generating with AI...</div>
    <div class="input-area">
      <div class="input-wrapper">
        <input id="userInput" placeholder="Type your idea... (Hindi/English supported)" onkeypress="if(event.key==='Enter')buildPrompt()">
        <span class="input-lang" id="inputLang">EN</span>
      </div>
      <button onclick="buildPrompt()">✨ Build</button>
      <button class="api-btn" id="apiBtn" onclick="toggleAPI()">🤖 AI</button>
      <button class="api-btn" id="claudeBtn" onclick="toggleClaude()" title="Opus 4.6 Fallback">🎭 Claude</button>
    </div>
  </div>

  <!-- API Settings Panel -->
  <div class="panel" id="settingsPanel">
    <div style="padding:10px;">
      <h3 style="color:#4ec9b0;margin-bottom:15px;">⚙️ API Configuration</h3>
      <div style="margin-bottom:15px;">
        <label style="font-size:12px;color:#888;display:block;margin-bottom:5px;">Gemini API Key</label>
        <input type="password" id="geminiKey" placeholder="Enter Gemini API Key" style="width:100%;padding:8px;border-radius:6px;background:#3c3c3c;border:1px solid #3c3c3c;color:#fff;font-size:12px;">
      </div>
      <div style="margin-bottom:15px;">
        <label style="font-size:12px;color:#888;display:block;margin-bottom:5px;">Claude API Key (Fallback)</label>
        <input type="password" id="claudeKey" placeholder="Enter Claude API Key" style="width:100%;padding:8px;border-radius:6px;background:#3c3c3c;border:1px solid #3c3c3c;color:#fff;font-size:12px;">
      </div>
      <div style="margin-bottom:15px;">
        <label style="font-size:12px;color:#888;display:block;margin-bottom:5px;">API Mode</label>
        <select id="apiMode" style="width:100%;padding:8px;border-radius:6px;background:#3c3c3c;border:1px solid #3c3c3c;color:#fff;font-size:12px;">
          <option value="gemini">Gemini API (Primary)</option>
          <option value="claude">Claude Opus 4.6 (Fallback)</option>
          <option value="auto">Auto - Gemini → Claude Fallback</option>
        </select>
      </div>
      <button onclick="saveSettings()" style="background:#0e639c;padding:8px 16px;">💾 Save Settings</button>
      <div id="settingsStatus" style="margin-top:10px;font-size:11px;color:#4caf50;"></div>
    </div>
  </div>

  <!-- Templates Panel -->
  <div class="panel" id="templatesPanel">
    <div class="template-grid">
      <div class="template-card" onclick="useTemplate('code-review')">
        <h4>🔍 Code Review</h4>
        <p>Review code quality, security, and performance</p>
      </div>
      <div class="template-card" onclick="useTemplate('bug-fix')">
        <h4>🐛 Bug Fix</h4>
        <p>Debug and fix issues with root cause analysis</p>
      </div>
      <div class="template-card" onclick="useTemplate('documentation')">
        <h4>📄 Documentation</h4>
        <p>Create comprehensive README and docs</p>
      </div>
      <div class="template-card" onclick="useTemplate('blog-post')">
        <h4>📝 Blog Post</h4>
        <p>Write engaging SEO-optimized articles</p>
      </div>
      <div class="template-card" onclick="useTemplate('api-design')">
        <h4>🔌 API Design</h4>
        <p>Design clean REST/GraphQL APIs</p>
      </div>
      <div class="template-card" onclick="useTemplate('test-case')">
        <h4>🧪 Test Cases</h4>
        <p>Generate comprehensive unit tests</p>
      </div>
      <div class="template-card" onclick="useTemplate('email')">
        <h4>📧 Email</h4>
        <p>Professional business emails</p>
      </div>
      <div class="template-card" onclick="useTemplate('presentation')">
        <h4>📊 Presentation</h4>
        <p>Pitch decks and slides structure</p>
      </div>
    </div>
  </div>

  <!-- History Panel -->
  <div class="panel" id="historyPanel">
    <div style="margin-bottom:10px;">
      <button class="clear-btn" onclick="clearHistory()" style="padding:6px 12px;font-size:11px;">🗑️ Clear All</button>
    </div>
    <div class="history-list" id="historyList">
      <div class="message bot" style="margin:10px 0;">No history yet. Your generated prompts will appear here.</div>
    </div>
  </div>

<script>
// State
let chatEnabled = true;
let selectedSkill = null;
let useAI = false;
let useClaude = false;
let history = JSON.parse(localStorage.getItem('promptHistory') || '[]');
let settings = JSON.parse(localStorage.getItem('promptBuilderSettings') || '{}');

// Role configurations
const roles = {
  educator: {
    name: 'Expert Educator',
    role: 'You are an expert educator with 15+ years of teaching experience',
    expertise: 'break down complex concepts into digestible parts with real-world examples'
  },
  engineer: {
    name: 'Software Engineer',
    role: 'You are a Principal Software Architect with deep expertise in clean code principles',
    expertise: 'write production-ready, maintainable code with proper error handling'
  },
  debugger: {
    name: 'Debugging Expert',
    role: 'You are a Senior Debugging Engineer and Root Cause Analysis Expert',
    expertise: 'identify root causes and provide precise solutions with explanations'
  },
  reviewer: {
    name: 'Code Reviewer',
    role: 'You are a Staff-level Code Reviewer and Software Quality Expert',
    expertise: 'provide actionable feedback that improves code quality and performance'
  },
  writer: {
    name: 'Content Writer',
    role: 'You are a Senior Content Strategist and Professional Writer',
    expertise: 'create engaging, SEO-optimized content that resonates with target audiences'
  },
  devops: {
    name: 'DevOps Architect',
    role: 'You are a DevOps Architect with expertise in modern deployment strategies',
    expertise: 'design robust, scalable infrastructure with best practices'
  },
  security: {
    name: 'Security Expert',
    role: 'You are a Chief Security Officer (CSO) with deep security expertise',
    expertise: 'identify security risks and implement robust security measures'
  },
  data: {
    name: 'Data Scientist',
    role: 'You are a Senior Data Scientist and Business Intelligence Expert',
    expertise: 'transform raw data into actionable insights with clear visualizations'
  },
  business: {
    name: 'Business Consultant',
    role: 'You are a Business Strategy Consultant with MBA-level expertise',
    expertise: 'provide data-driven recommendations with clear ROI analysis'
  },
  support: {
    name: 'Support Specialist',
    role: 'You are a Customer Support Specialist with excellent communication skills',
    expertise: 'provide helpful, patient, and solution-oriented assistance'
  }
};

// Templates
const templates = {
  'code-review': 'Review this code for quality, security issues, performance problems, and suggest improvements. Code: ',
  'bug-fix': 'Debug this issue and provide the exact fix with root cause analysis. Issue: ',
  'documentation': 'Create comprehensive documentation including overview, installation, usage examples, and API reference. Topic: ',
  'blog-post': 'Write an engaging SEO-optimized blog post with compelling introduction, body, and conclusion. Include relevant headings and keywords. Topic: ',
  'api-design': 'Design a clean REST/GraphQL API with proper endpoints, authentication, error handling, and documentation. Requirements: ',
  'test-case': 'Generate comprehensive unit tests with edge cases, mocks, and assertions. Function to test: ',
  'email': 'Write a professional business email that is clear, concise, and action-oriented. Purpose: ',
  'presentation': 'Create a presentation outline with slide structure, key points, and speaker notes. Topic: '
};

function toggleChat() {
  chatEnabled = !chatEnabled;
  document.getElementById('chatToggle').classList.toggle('active', chatEnabled);
  document.getElementById('chatBox').style.display = chatEnabled ? 'block' : 'none';
}

function toggleAPI() {
  useAI = !useAI;
  useClaude = false;
  document.getElementById('apiBtn').classList.toggle('active', useAI);
  document.getElementById('claudeBtn').classList.remove('active');
  document.getElementById('apiStatus').classList.toggle('active', useAI);
  document.getElementById('apiStatus').textContent = useAI ? '🤖 AI Mode: Using Gemini API' : '📝 Manual Mode: Using template generation';
}

function toggleClaude() {
  useClaude = !useClaude;
  useAI = false;
  document.getElementById('claudeBtn').classList.toggle('active', useClaude);
  document.getElementById('apiBtn').classList.remove('active');
  document.getElementById('apiStatus').classList.toggle('active', useClaude);
  document.getElementById('apiStatus').textContent = useClaude ? '🎭 Claude Opus 4.6 Mode' : '📝 Manual Mode: Using template generation';
}

function saveSettings() {
  settings = {
    geminiKey: document.getElementById('geminiKey').value,
    claudeKey: document.getElementById('claudeKey').value,
    apiMode: document.getElementById('apiMode').value
  };
  localStorage.setItem('promptBuilderSettings', JSON.stringify(settings));
  document.getElementById('settingsStatus').textContent = '✓ Settings saved!';
  setTimeout(() => {
    document.getElementById('settingsStatus').textContent = '';
  }, 2000);
}

function loadSettings() {
  if (settings.geminiKey) document.getElementById('geminiKey').value = settings.geminiKey;
  if (settings.claudeKey) document.getElementById('claudeKey').value = settings.claudeKey;
  if (settings.apiMode) document.getElementById('apiMode').value = settings.apiMode;
}

function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`.tab[onclick="switchTab('${tab}')"]`).classList.add('active');
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById(tab + 'Panel').classList.add('active');

  if (tab === 'history') renderHistory();
}

function selectSkill(chip, skill) {
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('selected'));
  if (selectedSkill === skill) {
    selectedSkill = null;
  } else {
    chip.classList.add('selected');
    selectedSkill = skill;
  }
}

function useTemplate(key) {
  const template = templates[key];
  document.getElementById('userInput').value = template;
  switchTab('chat');
  addMessage('Template selected: ' + key.replace('-', ' '), 'bot');
}

// INTELLIGENT PROMPT GENERATOR v2
// Samajhta hai koi bhi task - Hindi/English mix mein!
// Fixed: Better Hindi detection, more patterns

function detectLanguage(text) {
  const hindiPattern = /[\u0900-\u097F]/;
  const langIndicator = document.getElementById('inputLang');
  if (hindiPattern.test(text)) {
    langIndicator.textContent = 'HI';
    return 'Hindi';
  }
  // Also detect common Hindi words in Roman script
  const hindiWords = ['mujhe', 'mera', 'meri', 'hai', 'ka', 'ke', 'ki', 'ko', 'se', 'aur', 'bhi', 'nahi', 'kya', 'kaise', 'kyun', 'iska', 'iski', 'iske', 'tum', 'aap', 'hum', 'sab', 'kuch', 'batao', 'samjhao', 'pata', 'lena', 'dena', 'karna', 'hona', 'raha', 'rahi', 'the', 'tha', 'thi'];
  const words = text.toLowerCase().split(/\s+/);
  const hindiCount = words.filter(w => hindiWords.includes(w)).length;
  if (hindiCount >= 2) {
    langIndicator.textContent = 'HI';
    return 'Hindi';
  }
  langIndicator.textContent = 'EN';
  return 'English';
}

function analyzeTask(text) {
  const lower = text.toLowerCase();
  const lang = detectLanguage(text);

  // ===== DOMAIN DETECTION (PRIORITY-BASED SYSTEM) =====
  // TIER 1: High-priority domains (specific intent)
  // TIER 2: Medium-priority domains (action-based)
  // TIER 3: Low-priority domains (catch-all)

  // TIER 1: Debugging (if error/bug keywords present)
  const debugPatterns = ['bug', 'error', 'issue', 'problem', 'fail', 'not working', 'kaam nahi', 'chal nahi', 'thik karo', 'sudhar', 'exception', 'crash', 'ruk gaya', 'band ho'];
  const hasDebug = debugPatterns.some(p => lower.includes(p));
  if (hasDebug) {
    return buildPromptResult(roles.debugger, 'debugging', [], lang, text);
  }

  // TIER 1: Security (if security keywords present)
  const secPatterns = ['security', 'auth', 'password', 'encrypt', 'jwt', 'oauth', 'secure', 'permission', 'hack', 'vulnerability', 'ssl', 'https', 'firewall'];
  const hasSec = secPatterns.some(p => lower.includes(p));
  if (hasSec) {
    return buildPromptResult(roles.security, 'security', detectTech(lower), lang, text);
  }

  // TIER 2: Review (explicit review intent)
  const reviewPatterns = ['review', 'audit', 'analyze', 'check karo', 'improve', 'optimize', 'quality'];
  const hasReview = reviewPatterns.some(p => lower.includes(p));
  if (hasReview) {
    return buildPromptResult(roles.reviewer, 'review', detectTech(lower), lang, text);
  }

  // TIER 2: Education (explicit learning intent)
  const eduPatterns = ['explain', 'what is', 'kya hai', 'samjhao', 'batao', 'pata nahi', 'kaise kaam', 'simple', 'basics', 'understand', 'kuch bhi', 'seekho', 'shuru', 'kaise'];
  const hasEdu = eduPatterns.some(p => lower.includes(p));
  if (hasEdu) {
    return buildPromptResult(roles.educator, 'education', detectTech(lower), lang, text);
  }

  // TIER 2: DevOps (setup/deploy context)
  const devOpsPatterns = ['setup', 'deploy', 'docker', 'server', 'linux', 'aws', 'azure', 'kubernetes', 'hosting', 'install', 'configuration', 'container'];
  const hasDevOps = devOpsPatterns.some(p => lower.includes(p));
  if (hasDevOps) {
    return buildPromptResult(roles.devops, 'devops', detectTech(lower), lang, text);
  }

  // TIER 3: Coding (default - general dev context)
  const codingPatterns = ['code', 'program', 'function', 'class', 'api', 'component', 'banana', 'banao', 'website', 'web', 'app', 'page', 'button', 'script', 'build'];
  const hasCoding = codingPatterns.some(p => lower.includes(p));
  if (hasCoding) {
    return buildPromptResult(roles.engineer, 'coding', detectTech(lower), lang, text);
  }

  // TIER 3: Writing
  const writePatterns = ['write', 'article', 'blog', 'content', 'post', 'email', 'readme'];
  const hasWrite = writePatterns.some(p => lower.includes(p));
  if (hasWrite) {
    return buildPromptResult(roles.writer, 'writing', [], lang, text);
  }

  // DEFAULT: Engineer role
  return buildPromptResult(roles.engineer, 'coding', detectTech(lower), lang, text);
}

// Helper: Detect technology stack
function detectTech(lower) {
  const techs = [];
  const techsMap = {
    'React': ['react', 'jsx', 'tsx'],
    'Vue': ['vue', 'nuxt'],
    'Angular': ['angular'],
    'Node.js': ['node', 'nodejs', 'express'],
    'Python': ['python', 'python3'],
    'JavaScript': ['javascript', 'js'],
    'TypeScript': ['typescript', 'ts'],
    'Java': ['java', 'spring'],
    'Go': ['golang'],
    'Rust': ['rust'],
    'C#': ['csharp', 'dotnet'],
    'PHP': ['php', 'laravel'],
    'MongoDB': ['mongodb', 'mongo'],
    'PostgreSQL': ['postgresql', 'postgres'],
    'MySQL': ['mysql', 'mariadb'],
    'Docker': ['docker', 'container'],
    'Kubernetes': ['kubernetes', 'k8s', 'kubectl'],
    'AWS': ['aws', 'ec2', 's3', 'lambda'],
    'Azure': ['azure'],
    'Git': ['git', 'github'],
    'GraphQL': ['graphql'],
    'REST API': ['rest', 'api', 'endpoint'],
    'Web': ['website', 'html', 'css', 'frontend'],
    'Mobile': ['mobile', 'android', 'ios', 'app'],
  };

  for (const [tech, patterns] of Object.entries(techsMap)) {
    if (patterns.some(p => lower.includes(p))) {
      techs.push(tech);
    }
  }
  return techs;
}

// Helper: Build prompt result
function buildPromptResult(role, taskType, techStacks, lang, text) {
  const techStackSection = techStacks.length > 0 ?
    `\n• **Tech Stack**: ${techStacks.join(', ')}` : '';

  const langHint = lang === 'Hindi' ?
    '\n• **Language**: Respond in Hindi (हिंदी) with English technical terms.' :
    '\n• **Language**: Respond in English with standard technical terms.';

  const format = lower.includes('step') || lower.includes('kaise') ?
    'numbered step-by-step list' :
    lower.includes('code') || lower.includes('function') ?
    'code snippets with explanations' :
    'clear paragraphs with proper structure';

  const tone = lower.includes('simple') || lower.includes('basic') ?
    'simple for beginners' :
    lower.includes('technical') ?
    'highly technical' :
    'professional and helpful';

  return '# ROLE\n' + role.role + '\n\n# EXPERTISE\nYour core strength: ' + role.expertise + '\n\n# TASK\n' + text + '\n\n# CONTEXT ANALYSIS\n• **Domain**: ' + taskType + '\n• **Detected Tech**: ' + (techStacks.length > 0 ? techStacks.join(', ') : 'General') + '\n• **Priority**: Essential first, advanced optional' + techStackSection + '\n\n# REQUIREMENTS\n• **Tone**: Be ' + tone + langHint + '\n• **Format**: Structure as ' + format + '\n• **Depth**: Cover essentials, then optional details\n\n# RESPONSE STRUCTURE\n1. Quick Summary (1-2 lines)\n2. Main Content\n3. Code Examples (if applicable)\n4. Common Pitfalls\n5. Next Steps\n\n# CONSTRAINTS\n• Start immediately with useful content\n• Use clear headers (## Header)\n• Include working code examples\n• Anticipate follow-up questions\n• End with actionable next steps';
}

// Legacy function for backward compatibility
function detectLanguage(text) {
  const hindiPattern = /[\u0900-\u097F]/;
  const langIndicator = document.getElementById('inputLang');
  if (hindiPattern.test(text)) {
    langIndicator.textContent = 'HI';
    return 'Hindi';
  }
  const hindiWords = ['mujhe', 'mera', 'meri', 'hai', 'ka', 'ke', 'ki', 'ko', 'se', 'aur', 'bhi', 'nahi', 'kya', 'kaise', 'kyun', 'iska', 'iski', 'iske', 'tum', 'aap', 'hum', 'sab', 'kuch', 'batao', 'samjhao', 'pata', 'lena', 'dena', 'karna', 'hona', 'raha', 'rahi', 'the', 'tha', 'thi'];
  const words = text.toLowerCase().split(/\s+/);
  const hindiCount = words.filter(w => hindiWords.includes(w)).length;
  if (hindiCount >= 2) {
    langIndicator.textContent = 'HI';
    return 'Hindi';
  }
  langIndicator.textContent = 'EN';
  return 'English';
}

// Legacy generatePrompt
function generatePrompt(text) {
  return analyzeTask(text);
}

// PLACEHOLDER for remaining code (chat, history, etc.)
function switchTab(tab) { document.getElementById(tab + 'Panel').classList.add('active'); }
function addMessage(text, sender) { const chatBox = document.getElementById('chatBox'); const div = document.createElement('div'); div.className = 'message ' + sender; div.textContent = text; chatBox.appendChild(div); }
function copyPrompt() { navigator.clipboard.writeText(document.getElementById('promptText').innerText); }
function buildPrompt() { const input = document.getElementById('userInput').value.trim(); if (!input) return; document.getElementById('promptText').textContent = analyzeTask(input); document.getElementById('promptResult').style.display = 'block'; addMessage(input, 'user'); document.getElementById('userInput').value = ''; }
      patterns: [
        'help', 'support', 'assist', 'customer', 'user', 'question',
        'how to', 'guide', 'instructions', 'mujhe', 'chahiye', 'chaiye'
      ],
      role: roles.support,
      weight: 0
    }
  };

  // Calculate domain weights based on pattern matches
  for (const [domain, data] of Object.entries(domains)) {
    data.weight = data.patterns.filter(p => lower.includes(p)).length;
  }

  // Get best matching domain
  let bestDomain = domains.coding;
  let maxWeight = 0;
  for (const [domain, data] of Object.entries(domains)) {
    if (data.weight > maxWeight) {
      maxWeight = data.weight;
      bestDomain = data;
    }
  }

  // Manual skill selection override
  if (selectedSkill && roles[selectedSkill]) {
    bestDomain = { role: roles[selectedSkill] };
  }

  // ===== TECHNOLOGY STACK DETECTION (with Hindi patterns) =====
  const techStacks = [];
  const techPatterns = {
    'React': ['react', 'jsx', 'tsx', 'usestate', 'useeffect', 'component', 'reactjs'],
    'Vue': ['vue', 'nuxt', 'vuex', 'pinia', 'vuejs'],
    'Angular': ['angular', 'ngmodule', '@component', 'angularjs'],
    'Node.js': ['node', 'nodejs', 'express', 'npm', 'yarn', 'backend api'],
    'Python': ['python', 'django', 'flask', 'fastapi', 'pip', 'python3'],
    'Java': ['java', 'spring', 'maven', 'gradle', 'jdk'],
    'Go': ['golang', ' go ', 'go-lang'],
    'Rust': ['rust', 'cargo'],
    'C#': ['csharp', 'dotnet', '.net', 'asp.net'],
    'TypeScript': ['typescript', 'tsconfig', 'ts-node'],
    'MongoDB': ['mongodb', 'mongoose', 'no-sql', 'mongo'],
    'PostgreSQL': ['postgresql', 'postgres', 'pg-', 'psql'],
    'MySQL': ['mysql', 'mariadb', 'mysql'],
    'Docker': ['docker', 'container', 'dockerfile', 'docker-compose', 'containerization'],
    'Kubernetes': ['kubernetes', 'k8s', 'kubectl', 'helm', 'cluster'],
    'AWS': ['aws', 'amazon', 'ec2', 's3', 'lambda', 'dynamodb', 'cloudwatch'],
    'Azure': ['azure', 'microsoft', 'az'],
    'Git': ['git', 'github', 'gitlab', 'bitbucket', 'commit', 'branch', 'github'],
    'GraphQL': ['graphql', 'apollo'],
    'REST API': ['rest', 'restful', 'api', 'endpoint', 'http'],
    // Hindi tech terms
    'Web Development': ['website', 'web', 'page', 'html', 'css', 'frontend', 'backend'],
    'Database': ['database', 'db', 'data', 'table', 'schema', 'sql'],
    'Mobile': ['mobile', 'android', 'ios', 'react native', 'flutter', 'app'],
  };

  for (const [tech, patterns] of Object.entries(techPatterns)) {
    if (patterns.some(p => lower.includes(p))) {
      techStacks.push(tech);
    }
  }
    'Node.js': ['node', 'express', 'npm', 'yarn', 'backend api'],
    'Python': ['python', 'django', 'flask', 'fastapi', 'pip'],
    'Java': ['java', 'spring', 'maven', 'gradle'],
    'Go': ['golang', ' go ', 'go-lang'],
    'Rust': ['rust', 'cargo'],
    'C#': ['csharp', 'dotnet', '.net'],
    'TypeScript': ['typescript', 'tsconfig', 'ts-node'],
    'MongoDB': ['mongodb', 'mongoose', 'no-sql'],
    'PostgreSQL': ['postgresql', 'postgres', 'pg-'],
    'MySQL': ['mysql', 'mariadb'],
    'Docker': ['docker', 'container', 'dockerfile', 'docker-compose'],
    'Kubernetes': ['kubernetes', 'k8s', 'kubectl', 'helm'],
    'AWS': ['aws', 'amazon', 'ec2', 's3', 'lambda', 'dynamodb'],
    'Azure': ['azure', 'microsoft'],
    'Git': ['git', 'github', 'gitlab', 'bitbucket', 'commit', 'branch'],
    'GraphQL': ['graphql', 'apollo'],
    'REST API': ['rest', 'restful', 'api endpoint', 'http request'],
  };

  for (const [tech, patterns] of Object.entries(techPatterns)) {
    if (patterns.some(p => lower.includes(p))) {
      techStacks.push(tech);
    }
  }

  // ===== TASK TYPE DETECTION =====
  let taskType = 'general';
  const taskPatterns = {
    'create': ['create', 'build', 'make', 'develop', 'implement', 'banana', 'banao', 'lena'],
    'fix': ['fix', 'bug', 'error', 'issue', 'problem', 'thik', 'sudhar', 'solve'],
    'explain': ['explain', 'what is', 'how does', 'why', 'kya hai', 'kyunki', 'kaise kaam'],
    'review': ['review', 'check', 'analyze', 'audit', 'evaluate'],
    'optimize': ['optimize', 'improve', 'enhance', 'performance', 'speed'],
    'secure': ['secure', 'protect', 'encrypt', 'hash', 'safe'],
    'test': ['test', 'testing', 'jest', 'pytest', 'unittest'],
    'debug': ['debug', 'trace', 'stack', 'console log'],
    'document': ['document', 'readme', 'docs', 'comment', 'specification'],
    'deploy': ['deploy', 'release', 'publish', 'host', 'production'],
  };

  for (const [type, patterns] of Object.entries(taskPatterns)) {
    if (patterns.some(p => lower.includes(p))) {
      taskType = type;
      break;
    }
  }

  // ===== FORMAT DETECTION =====
  let format = 'clear paragraphs with proper structure';
  if (lower.includes('step') || lower.includes('step by step') || lower.includes('numbered') || lower.includes('순서')) {
    format = 'numbered step-by-step list (1, 2, 3...)';
  }
  if (lower.includes('code') || lower.includes('snippet') || lower.includes('example')) {
    format = 'code snippets with explanations (```language)';
  }
  if (lower.includes('list') || lower.includes('bullet') || lower.includes('points')) {
    format = 'bullet points for easy scanning';
  }
  if (lower.includes('table') || lower.includes('comparison')) {
    format = 'table format for comparison';
  }
  if (lower.includes('diagram') || lower.includes('flowchart')) {
    format = 'ASCII diagrams or flowchart representation';
  }

  // ===== TONE DETECTION =====
  let tone = 'professional and helpful';
  if (lower.includes('simple') || lower.includes('basic') || lower.includes('beginner') || lower.includes('shuru')) {
    tone = 'simple for beginners with explanations';
  }
  if (lower.includes('technical') || lower.includes('advanced') || lower.includes('expert')) {
    tone = 'highly technical with deep details';
  }
  if (lower.includes('casual') || lower.includes('friendly') || lower.includes('informal')) {
    tone = 'conversational and friendly';
  }
  if (lower.includes('formal') || lower.includes('business')) {
    tone = 'formal and business-appropriate';
  }

  // ===== PRIORITY DETECTION =====
  let priority = 'comprehensive coverage';
  if (lower.includes('quick') || lower.includes('brief') || lower.includes('short') || lower.includes('fast')) {
    priority = 'quick overview - most important only';
  }
  if (lower.includes('detailed') || lower.includes('comprehensive') || lower.includes('full')) {
    priority = 'comprehensive and detailed with all edge cases';
  }

  // ===== LANGUAGE HINT =====
  const langHint = lang === 'Hindi' ?
    '\n• **Language**: Respond in Hindi (हिंदी) with English technical terms where standard.' :
    '\n• **Language**: Respond in English with technical terms as standard.';

  // ===== BUILD STRUCTURED PROMPT =====
  const techStackSection = techStacks.length > 0 ?
    `\n• **Tech Stack**: ${techStacks.join(', ')}` : '';

  return `# ROLE
${bestDomain.role.role}

# EXPERTISE
Your core strength: ${bestDomain.role.expertise}

# TASK (Original Input)
${text}

# CONTEXT ANALYSIS
• **Domain**: ${taskType.charAt(0).toUpperCase() + taskType.slice(1)}
• **Detected Tech**: ${techStacks.length > 0 ? techStacks.join(', ') : 'General/Unspecified'}
• **Priority Level**: ${priority}${techStackSection}

# REQUIREMENTS
• **Tone**: Be ${tone}
• **Format**: Structure response as ${format}${langHint}
• **Depth**: Cover essential points first, then optional advanced details

# RESPONSE STRUCTURE
1. Quick Summary (1-2 lines)
2. Main Content (well-organized sections)
3. Code Examples (if applicable)
4. Common Pitfalls / Gotchas
5. Related Commands / Next Steps

# CONSTRAINTS
• Start immediately with useful content - no preamble
• Use clear headers (## Header) for organization
• Include working code examples where applicable
• Anticipate follow-up questions
• End with actionable next steps or quick reference`;
}

function generatePrompt(text) {
  return analyzeTask(text);
}

async function buildPrompt() {
  const input = document.getElementById('userInput').value.trim();
  if (!input) return;

  if (chatEnabled) {
    addMessage(input, 'user');
  }
  document.getElementById('userInput').value = '';

  let generatedPrompt = generatePrompt(input);
  const apiMode = settings.apiMode || 'auto';

  // Try AI enhancement if enabled
  if (useAI || useClaude || apiMode === 'auto') {
    document.getElementById('apiStatus').classList.add('active');

    try {
      let enhanced = null;

      // Try Gemini first
      if ((useAI || apiMode === 'auto') && settings.geminiKey) {
        document.getElementById('apiStatus').textContent = '🤖 Trying Gemini API...';
        enhanced = await callGeminiAPI(input, generatedPrompt, settings.geminiKey);
      }

      // Fallback to Claude if Gemini fails or if Claude mode is enabled
      if (!enhanced && settings.claudeKey) {
        document.getElementById('apiStatus').textContent = '🎭 Falling back to Claude Opus 4.6...';
        enhanced = await callClaudeAPI(input, generatedPrompt, settings.claudeKey);
      }

      if (enhanced) {
        generatedPrompt = enhanced;
        if (chatEnabled) {
          addMessage('✨ Prompt enhanced by AI!', 'bot');
        }
      } else {
        throw new Error('No API available');
      }

    } catch (error) {
      console.log('API Error:', error);
      if (apiMode === 'auto' && !settings.claudeKey) {
        if (chatEnabled) {
          addMessage('⚠️ API not configured. Using template generation. Add API keys in Settings tab.', 'bot');
        }
      }
    }

    document.getElementById('apiStatus').classList.remove('active');
  }

  // Show result
  const resultDiv = document.getElementById('promptResult');
  const promptText = document.getElementById('promptText');
  resultDiv.style.display = 'block';
  promptText.textContent = generatedPrompt;

  // Save to history
  saveToHistory(input, generatedPrompt);

  if (chatEnabled && !useAI && !useClaude) {
    addMessage('✨ Prompt generated! Click Copy or use the structured prompt above.', 'bot');
  }
}

async function callGeminiAPI(input, prompt, apiKey) {
  try {
    const url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + apiKey;
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: 'Enhance this prompt to be super high quality, professional, and actionable. Keep the structure but improve clarity and effectiveness:\n\n' + prompt
          }]
        }],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 2048
        }
      })
    });

    if (!response.ok) throw new Error('Gemini API failed');

    const data = await response.json();
    return data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts && data.candidates[0].content.parts[0] ? data.candidates[0].content.parts[0].text : null;
  } catch (e) {
    console.log('Gemini failed:', e);
    return null;
  }
}

async function callClaudeAPI(input, prompt, apiKey) {
  try {
    const response = await fetch('https://api.opusmax.pro/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + apiKey
      },
      body: JSON.stringify({
        model: 'claude-opus-4-7',
        messages: [{
          role: 'user',
          content: 'You are a prompt engineering expert. Enhance this prompt to be super high quality, professional, and actionable. Keep the structure but improve clarity and effectiveness:\n\n' + prompt
        }],
        temperature: 0.7,
        max_tokens: 2048
      })
    });

    if (!response.ok) throw new Error('Claude API failed');

    const data = await response.json();
    return data.choices && data.choices[0] && data.choices[0].message ? data.choices[0].message.content : null;
  } catch (e) {
    console.log('Claude failed:', e);
    return null;
  }
}

function addMessage(text, sender) {
  const chatBox = document.getElementById('chatBox');
  const div = document.createElement('div');
  div.className = 'message ' + sender;
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function copyPrompt() {
  const text = document.getElementById('promptText').innerText;
  navigator.clipboard.writeText(text).then(() => {
    if (chatEnabled) {
      addMessage('📋 Prompt copied to clipboard!', 'bot');
    } else {
      // Show toast
      const toast = document.createElement('div');
      toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#4caf50;color:#fff;padding:10px 20px;border-radius:8px;font-size:14px;z-index:1000;';
      toast.textContent = '✓ Copied to clipboard!';
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 2000);
    }
  });
}

function saveToHistory(input, prompt) {
  const item = {
    id: Date.now(),
    input: input.substring(0, 100),
    prompt: prompt,
    time: new Date().toLocaleTimeString()
  };
  history.unshift(item);
  if (history.length > 50) history.pop(); // Keep last 50
  localStorage.setItem('promptHistory', JSON.stringify(history));
}

function renderHistory() {
  const list = document.getElementById('historyList');
  if (history.length === 0) {
    list.innerHTML = '<div class="message bot" style="margin:10px 0;">No history yet. Your generated prompts will appear here.</div>';
    return;
  }

  list.innerHTML = history.map(item => \`
    <div class="history-item" onclick="loadHistory(\${item.id})">
      <span class="text">\${item.input}</span>
      <span class="time">\${item.time}</span>
      <span class="delete" onclick="event.stopPropagation();deleteHistory(\${item.id})">✕</span>
    </div>
  \`).join('');
}

function loadHistory(id) {
  const item = history.find(h => h.id === id);
  if (item) {
    switchTab('chat');
    document.getElementById('promptResult').style.display = 'block';
    document.getElementById('promptText').textContent = item.prompt;
    addMessage('Loaded from history: ' + item.input, 'bot');
  }
}

function deleteHistory(id) {
  history = history.filter(h => h.id !== id);
  localStorage.setItem('promptHistory', JSON.stringify(history));
  renderHistory();
}

function clearHistory() {
  if (confirm('Clear all history?')) {
    history = [];
    localStorage.setItem('promptHistory', JSON.stringify(history));
    renderHistory();
  }
}

// Initialize
toggleChat(); // Start with chat enabled
loadSettings(); // Load saved API settings
</script>
</body>
</html>`;
}

module.exports = { activate };
