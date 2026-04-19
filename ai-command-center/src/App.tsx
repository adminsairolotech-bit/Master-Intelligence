import { useState } from 'react';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const switchTab = (tab: string) => {
    setActiveTab(tab);
  };

  return (
    <div className="app">
      <div className="bg-glow cyan" />
      <div className="bg-glow purple" />

      <header className="header">
        <div className="header-left">
          <div className="logo">
            <i className="ri-robot-2-fill" />
          </div>
          <div className="header-title">
            <h1>AI Command Center</h1>
            <p>SAI Rolotech - Unified AI Dashboard</p>
          </div>
        </div>
        <div className="header-stats">
          <div className="stat-item">
            <div className="stat-value">13</div>
            <div className="stat-label">AI Tools</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">9</div>
            <div className="stat-label">Frameworks</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">100%</div>
            <div className="stat-label">Status</div>
          </div>
        </div>
      </header>

      <div className="container">
        <div className="tabs">
          <button className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => switchTab('dashboard')}>
            Dashboard
          </button>
          <button className={`tab ${activeTab === 'tools' ? 'active' : ''}`} onClick={() => switchTab('tools')}>
            AI Tools
          </button>
          <button className={`tab ${activeTab === 'frameworks' ? 'active' : ''}`} onClick={() => switchTab('frameworks')}>
            Frameworks
          </button>
          <button className={`tab ${activeTab === 'changelog' ? 'active' : ''}`} onClick={() => switchTab('changelog')}>
            Changelog
          </button>
          <button className={`tab ${activeTab === 'api' ? 'active' : ''}`} onClick={() => switchTab('api')}>
            API Status
          </button>
        </div>

        {/* Dashboard */}
        {activeTab === 'dashboard' && (
          <section className="section active">
            <div className="quick-stats">
              <div className="quick-stat">
                <div className="quick-stat-value">738</div>
                <div className="quick-stat-label">Claude Skills</div>
              </div>
              <div className="quick-stat">
                <div className="quick-stat-value">75</div>
                <div className="quick-stat-label">Agents</div>
              </div>
              <div className="quick-stat">
                <div className="quick-stat-value">102</div>
                <div className="quick-stat-label">Slash Commands</div>
              </div>
              <div className="quick-stat">
                <div className="quick-stat-value">7</div>
                <div className="quick-stat-label">AI Frameworks</div>
              </div>
            </div>

            <div className="section-header">
              <div>
                <h2>Popular AI Tools</h2>
                <p>Quick access to your most used tools</p>
              </div>
            </div>
            <div className="grid-3">
              <div className="card">
                <div className="card-icon cyan"><i className="ri-bard-fill" /></div>
                <h3>God Level Extension</h3>
                <p>Access all 9 AI frameworks with one click. Claude, Gemini, GPT-4, and more integrated.</p>
                <div className="card-meta">
                  <span className="badge cyan">VS Code</span>
                  <span className="badge purple">All Frameworks</span>
                </div>
                <button className="card-btn" onClick={() => window.open('../god-level-extension/index.html', '_blank')}>
                  <i className="ri-external-link-line" /> Open Extension
                </button>
              </div>

              <div className="card">
                <div className="card-icon purple"><i className="ri-message-3-fill" /></div>
                <h3>Prompt Builder Pro</h3>
                <p>Build structured prompts with role detection, templates, and AI converter. Hindi/English support.</p>
                <div className="card-meta">
                  <span className="badge cyan">10 Skills</span>
                  <span className="badge purple">8 Templates</span>
                </div>
                <button className="card-btn" onClick={() => window.open('../prompt-builder-vscode/index.html', '_blank')}>
                  <i className="ri-external-link-line" /> Open Builder
                </button>
              </div>

              <div className="card">
                <div className="card-icon green"><i className="ri-team-fill" /></div>
                <h3>Agno Multi-Agent</h3>
                <p>Deploy multi-agent AI systems with LangGraph, CrewAI, and AutoGen orchestration.</p>
                <div className="card-meta">
                  <span className="badge green">Multi-Agent</span>
                  <span className="badge purple">v2.5.17</span>
                </div>
                <button className="card-btn" onClick={() => window.open('../agno-multiagent/index.html', '_blank')}>
                  <i className="ri-external-link-line" /> Open Agent
                </button>
              </div>

              <div className="card">
                <div className="card-icon orange"><i className="ri-palette-fill" /></div>
                <h3>Design Tool</h3>
                <p>AI-powered design automation with Figma integration and template generation.</p>
                <div className="card-meta">
                  <span className="badge orange">Design</span>
                  <span className="badge cyan">Automation</span>
                </div>
                <button className="card-btn" onClick={() => window.open('../design-tool/index.html', '_blank')}>
                  <i className="ri-external-link-line" /> Open Tool
                </button>
              </div>

              <div className="card">
                <div className="card-icon red"><i className="ri-share-circle-fill" /></div>
                <h3>Agentfy</h3>
                <p>Social media automation agents for Twitter, Instagram, and LinkedIn content creation.</p>
                <div className="card-meta">
                  <span className="badge red">Social</span>
                  <span className="badge green">Automation</span>
                </div>
                <button className="card-btn" onClick={() => window.open('../Agentfy/index.html', '_blank')}>
                  <i className="ri-external-link-line" /> Open Agentfy
                </button>
              </div>

              <div className="card">
                <div className="card-icon cyan"><i className="ri-brain-fill" /></div>
                <h3>Hermes AI Hub</h3>
                <p>Central AI hub with intelligent agent coordination and workflow automation.</p>
                <div className="card-meta">
                  <span className="badge cyan">Central Hub</span>
                  <span className="badge purple">Smart</span>
                </div>
                <button className="card-btn" onClick={() => window.open('../sai-rolotech-ai-hub/index.html', '_blank')}>
                  <i className="ri-external-link-line" /> Open Hub
                </button>
              </div>
            </div>
          </section>
        )}

        {/* AI Tools */}
        {activeTab === 'tools' && (
          <section className="section">
            <div className="section-header">
              <div>
                <h2>All AI Tools</h2>
                <p>Complete collection of AI development tools</p>
              </div>
            </div>
            <div className="grid-4">
              <div className="card"><div className="card-icon cyan"><i className="ri-bard-fill" /></div><h3>God Level Extension</h3><p>9 AI frameworks in one extension</p><div className="card-meta"><span className="badge cyan">VS Code</span></div></div>
              <div className="card"><div className="card-icon purple"><i className="ri-message-3-fill" /></div><h3>Prompt Builder</h3><p>Structured prompt generation</p><div className="card-meta"><span className="badge purple">10 Skills</span></div></div>
              <div className="card"><div className="card-icon green"><i className="ri-team-fill" /></div><h3>Agno Multi-Agent</h3><p>Multi-agent orchestration</p><div className="card-meta"><span className="badge green">v2.5.17</span></div></div>
              <div className="card"><div className="card-icon orange"><i className="ri-palette-fill" /></div><h3>Design Tool</h3><p>Design automation</p><div className="card-meta"><span className="badge orange">Design</span></div></div>
              <div className="card"><div className="card-icon red"><i className="ri-share-circle-fill" /></div><h3>Agentfy</h3><p>Social media agents</p><div className="card-meta"><span className="badge red">Social</span></div></div>
              <div className="card"><div className="card-icon cyan"><i className="ri-brain-fill" /></div><h3>Hermes AI Hub</h3><p>Central AI coordination</p><div className="card-meta"><span className="badge cyan">Central</span></div></div>
              <div className="card"><div className="card-icon purple"><i className="ri-file-chart-fill" /></div><h3>AutoCAD Bridge</h3><p>Natural language to AutoCAD</p><div className="card-meta"><span className="badge purple">Engineering</span></div></div>
              <div className="card"><div className="card-icon green"><i className="ri-customer-service-2-fill" /></div><h3>SAI Rolotech Engine</h3><p>Automation dashboard</p><div className="card-meta"><span className="badge green">Dashboard</span></div></div>
            </div>
          </section>
        )}

        {/* Frameworks */}
        {activeTab === 'frameworks' && (
          <section className="section">
            <div className="section-header">
              <div>
                <h2>AI Frameworks</h2>
                <p>All supported AI development frameworks</p>
              </div>
            </div>
            <div className="grid-4">
              <div className="framework-card"><div className="framework-header"><span className="framework-name">LangGraph</span><span className="framework-version">v1.1.8</span></div><p className="framework-desc">Build stateful multi-actor applications with LLM graphs</p><div className="framework-status"><span className="status-dot" /> Installed and Working</div></div>
              <div className="framework-card"><div className="framework-header"><span className="framework-name">CrewAI</span><span className="framework-version">v1.14.1</span></div><p className="framework-desc">Framework for building autonomous AI agents</p><div className="framework-status"><span className="status-dot" /> Installed and Working</div></div>
              <div className="framework-card"><div className="framework-header"><span className="framework-name">Agno</span><span className="framework-version">v2.5.17</span></div><p className="framework-desc">Build Agentic RAG and Multi-Agent systems</p><div className="framework-status"><span className="status-dot" /> Installed and Working</div></div>
              <div className="framework-card"><div className="framework-header"><span className="framework-name">AutoGen</span><span className="framework-version">v0.5.7</span></div><p className="framework-desc">Microsoft framework for LLM applications</p><div className="framework-status"><span className="status-dot" /> Installed and Working</div></div>
              <div className="framework-card"><div className="framework-header"><span className="framework-name">LlamaIndex</span><span className="framework-version">v0.14.20</span></div><p className="framework-desc">Data framework for LLM applications</p><div className="framework-status"><span className="status-dot" /> Installed and Working</div></div>
              <div className="framework-card"><div className="framework-header"><span className="framework-name">ChromaDB</span><span className="framework-version">Latest</span></div><p className="framework-desc">Vector database for AI applications</p><div className="framework-status"><span className="status-dot" /> Installed and Working</div></div>
              <div className="framework-card"><div className="framework-header"><span className="framework-name">DeepEval</span><span className="framework-version">Latest</span></div><p className="framework-desc">Evaluation framework for LLM outputs</p><div className="framework-status"><span className="status-dot" /> Installed and Working</div></div>
              <div className="framework-card"><div className="framework-header"><span className="framework-name">Arize Phoenix</span><span className="framework-version">Latest</span></div><p className="framework-desc">ML observability platform</p><div className="framework-status"><span className="status-dot" /> Available</div></div>
              <div className="framework-card"><div className="framework-header"><span className="framework-name">Weaviate</span><span className="framework-version">Latest</span></div><p className="framework-desc">Open source vector search engine</p><div className="framework-status"><span className="status-dot" /> Available</div></div>
            </div>
          </section>
        )}

        {/* Changelog */}
        {activeTab === 'changelog' && (
          <section className="section">
            <div className="section-header">
              <div>
                <h2>Changelog</h2>
                <p>Track all updates and changes</p>
              </div>
            </div>
            <div className="changelog-item">
              <div className="changelog-date"><div className="day">18</div><div className="month">APR 2026</div></div>
              <div className="changelog-content">
                <h4>AI Command Center Launched</h4>
                <p>Unified dashboard combining all AI coding tools with changelog tracking and API status monitoring.</p>
                <div className="changelog-badges"><span className="badge cyan">New</span><span className="badge green">Feature</span></div>
              </div>
            </div>
            <div className="changelog-item">
              <div className="changelog-date"><div className="day">17</div><div className="month">APR 2026</div></div>
              <div className="changelog-content">
                <h4>AutoCAD SCR Generator v2.0</h4>
                <p>Enhanced with roll assembly diagrams, bearing specs, and flower pattern generation.</p>
                <div className="changelog-badges"><span className="badge green">Feature</span></div>
              </div>
            </div>
            <div className="changelog-item">
              <div className="changelog-date"><div className="day">16</div><div className="month">APR 2026</div></div>
              <div className="changelog-content">
                <h4>God Level Extension Updated</h4>
                <p>All 9 AI frameworks integrated with version tracking and run demo functionality.</p>
                <div className="changelog-badges"><span className="badge purple">Update</span></div>
              </div>
            </div>
            <div className="changelog-item">
              <div className="changelog-date"><div className="day">15</div><div className="month">APR 2026</div></div>
              <div className="changelog-content">
                <h4>Prompt Builder Pro Released</h4>
                <p>10 skill chips, 8 templates, AI converter with tone/format options.</p>
                <div className="changelog-badges"><span className="badge cyan">New</span></div>
              </div>
            </div>
            <div className="changelog-item">
              <div className="changelog-date"><div className="day">14</div><div className="month">APR 2026</div></div>
              <div className="changelog-content">
                <h4>OpenClaw Gateway Updated</h4>
                <p>Version 2026.4.15 with 32/74 skills ready, Telegram integration.</p>
                <div className="changelog-badges"><span className="badge purple">Update</span></div>
              </div>
            </div>
          </section>
        )}

        {/* API Status */}
        {activeTab === 'api' && (
          <section className="section">
            <div className="section-header">
              <div>
                <h2>API Status</h2>
                <p>Real-time status of all connected APIs</p>
              </div>
            </div>
            <div className="api-item">
              <div className="api-info">
                <span className="api-icon">G</span>
                <div><div className="api-name">Gemini API</div><div className="api-endpoint">generativelanguage.googleapis.com</div></div>
              </div>
              <span className="api-status-badge working"><span className="status-dot" /> Working - 13 Keys</span>
            </div>
            <div className="api-item">
              <div className="api-info">
                <span className="api-icon">C</span>
                <div><div className="api-name">Claude (OpusMax)</div><div className="api-endpoint">api.opusmax.pro</div></div>
              </div>
              <span className="api-status-badge working"><span className="status-dot" /> Working</span>
            </div>
            <div className="api-item">
              <div className="api-info">
                <span className="api-icon">OR</span>
                <div><div className="api-name">OpenRouter</div><div className="api-endpoint">openrouter.ai</div></div>
              </div>
              <span className="api-status-badge working"><span className="status-dot" /> Working</span>
            </div>
            <div className="api-item">
              <div className="api-info">
                <span className="api-icon">GQ</span>
                <div><div className="api-name">Groq</div><div className="api-endpoint">api.groq.com</div></div>
              </div>
              <span className="api-status-badge working"><span className="status-dot" /> Working</span>
            </div>
            <div className="api-item">
              <div className="api-info">
                <span className="api-icon">NV</span>
                <div><div className="api-name">NVIDIA</div><div className="api-endpoint">integrate.api.nvidia.com</div></div>
              </div>
              <span className="api-status-badge working"><span className="status-dot" /> Working</span>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export default App;
