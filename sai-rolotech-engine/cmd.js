/**
 * SAI Rolotech Engine - Gemini API Integration
 * Direct API calls without server
 */

const GEMINI_API_KEYS = [
  'AIzaSyD_placeholder_key_1',
  'AIzaSyD_placeholder_key_2',
  'AIzaSyD_placeholder_key_3'
];

let currentKeyIndex = 0;

function getApiKey() {
  return GEMINI_API_KEYS[currentKeyIndex % GEMINI_API_KEYS.length];
}

function rotateKey() {
  currentKeyIndex++;
  console.log(`Rotated to key ${currentKeyIndex % GEMINI_API_KEYS.length + 1}`);
}

async function callGemini(prompt, options = {}) {
  const apiKey = getApiKey();
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: {
          temperature: options.temperature || 0.9,
          maxOutputTokens: options.maxTokens || 2048,
          topP: 0.95,
          topK: 40
        }
      })
    });

    if (!response.ok) {
      rotateKey();
      throw new Error(`API Error: ${response.status}`);
    }

    const data = await response.json();
    return data.candidates?.[0]?.content?.parts?.[0]?.text || 'No response';
  } catch (error) {
    console.error('Gemini API Error:', error);
    return `Error: ${error.message}`;
  }
}

// CLI Interface
if (typeof require !== 'undefined' && require.main === module) {
  const readline = require('readline');
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

  console.log('🤖 SAI Rolotech Gemini CLI');
  console.log('Type your message or "exit" to quit\n');

  const ask = () => {
    rl.question('You: ', async (input) => {
      if (input.toLowerCase() === 'exit') {
        rl.close();
        return;
      }
      console.log('AI: Thinking...');
      const response = await callGemini(input);
      console.log('AI:', response, '\n');
      ask();
    });
  };

  ask();
}

// Export for browser
if (typeof window !== 'undefined') {
  window.callGemini = callGemini;
  window.GeminiCLI = { callGemini, rotateKey };
}
