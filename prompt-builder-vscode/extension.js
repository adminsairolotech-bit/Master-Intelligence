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

function detectLanguage(text) {
  const hindiPattern = /[\u0900-\u097F]/;
  const langIndicator = document.getElementById('inputLang');
  if (hindiPattern.test(text)) {
    langIndicator.textContent = 'HI';
    return 'Hindi';
  }
  langIndicator.textContent = 'EN';
  return 'English';
}

function generatePrompt(text) {
  const lower = text.toLowerCase();
  detectLanguage(text);

  // Get selected role or auto-detect
  let selectedRole = selectedSkill ? roles[selectedSkill] : null;

  if (!selectedRole) {
    // Auto-detect based on keywords
    const keywords = {
      'code-review': ['review', 'check code', 'analyze code'],
      'bug-fix': ['fix', 'bug', 'error', 'issue', 'crash'],
      'documentation': ['document', 'readme', 'docs', 'explain'],
      'blog-post': ['blog', 'article', 'write about', 'post'],
      'api-design': ['api', 'endpoint', 'rest', 'graphql'],
      'test-case': ['test', 'unit test', 'testing'],
      'email': ['email', 'mail', 'message to'],
      'presentation': ['presentation', 'slides', 'deck', 'pitch']
    };

    for (const [skill, patterns] of Object.entries(keywords)) {
      if (patterns.some(p => lower.includes(p))) {
        selectedRole = roles[skill];
        break;
      }
    }

    if (!selectedRole) {
      // Default based on content
      if (lower.includes('explain') || lower.includes('what is')) {
        selectedRole = roles.educator;
      } else if (lower.includes('write') || lower.includes('create')) {
        selectedRole = roles.writer;
      } else if (lower.includes('code') || lower.includes('function')) {
        selectedRole = roles.engineer;
      } else {
        selectedRole = roles.engineer; // Default
      }
    }
  }

  // Detect format
  let format = 'structured and well-organized';
  if (lower.includes('step') || lower.includes('how to')) format = 'step-by-step with clear numbering';
  else if (lower.includes('example')) format = 'with practical examples';
  else if (lower.includes('list')) format = 'bullet or numbered list format';
  else if (lower.includes('code')) format = 'with code snippets and explanations';
  else if (lower.includes('summary')) format = 'concise summary with key takeaways';

  // Detect tone
  let tone = 'clear, helpful, and action-oriented';
  if (lower.includes('formal')) tone = 'formal and professional';
  else if (lower.includes('casual')) tone = 'casual and friendly';
  else if (lower.includes('technical')) tone = 'highly technical and precise';
  else if (lower.includes('simple')) tone = 'simple enough for beginners';

  // Detect detail level
  let detail = 'balanced mix of depth and clarity';
  if (lower.includes('simple') || lower.includes('basic')) detail = 'beginner-friendly with foundational concepts';
  else if (lower.includes('detailed') || lower.includes('comprehensive')) detail = 'comprehensive with deep analysis';
  else if (lower.includes('quick') || lower.includes('brief')) detail = 'concise and to-the-point';

  // Language hint
  const lang = detectLanguage(text);
  const langHint = lang === 'Hindi' ? '\n• Language: Respond in Hindi with English technical terms where appropriate.' : '';

  // Build structured prompt
  return "# ROLE\n" +
    selectedRole.role + ".\n\n" +
    "# EXPERTISE\n" +
    "Your core strength: " + selectedRole.expertise + ".\n\n" +
    "# TASK\n" +
    text + "\n\n" +
    "# REQUIREMENTS\n" +
    "• Tone: Be " + tone + "\n" +
    "• Detail Level: " + detail + "\n" +
    "• Format: Structure your response " + format + langHint + "\n\n" +
    "# CONSTRAINTS\n" +
    "• Start with the most important information\n" +
    "• Use clear section headers for organization\n" +
    "• Include specific details, numbers, or code where relevant\n" +
    "• Anticipate follow-up questions\n" +
    "• End with actionable next steps or summary";
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
