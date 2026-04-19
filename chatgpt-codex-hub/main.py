"""
ChatGPT + Codex Hub - Main Entry Point with Multi-Provider Support
SAI ROLO TECH

Supports:
- OpenAI (GPT-4)
- Ollama (Local Llama 3.1/3.2)
- Demo Mode
"""

import argparse
import sys
import json
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, str(Path(__file__).parent.parent))

from chatgpt_codex_loop import ChatGPTCodexLoop
from scenarios.demo_scenario import DEMO_SCENARIOS


class APIHandler(SimpleHTTPRequestHandler):
    """HTTP API handler for frontend communication."""

    loop = None

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(body) if body else {}

        # Route based on path
        if self.path.startswith('/api/openai/'):
            self.handle_openai(self.path.replace('/api/openai/', ''), data)
        elif self.path.startswith('/api/ollama/'):
            self.handle_ollama(self.path.replace('/api/ollama/', ''), data)
        elif self.path == '/api/analyze':
            self.handle_demo_analyze(data)
        elif self.path == '/api/generate':
            self.handle_demo_generate(data)
        elif self.path == '/api/verify':
            self.handle_demo_verify(data)
        elif self.path == '/api/github/repos':
            self.handle_github_repos()
        else:
            self.send_error(404, 'Not Found')

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
        else:
            super().do_GET()

    def handle_openai(self, action: str, data: Dict):
        """Handle OpenAI API calls."""
        try:
            api_key = data.get('api_key')
            if not api_key:
                self.send_json({'error': 'API key required'}, 400)
                return

            from models.chatgpt_client import ChatGPTClient
            from models.codex_client import CodexClient

            if action == 'analyze':
                client = ChatGPTClient(api_key=api_key)
                result = client.analyze(data['request'], data.get('task_type', 'generate_feature'))
                self.send_json({
                    'plan': result.get('plan', ''),
                    'components': result.get('components', []),
                    'dependencies': result.get('dependencies', [])
                })
                client.close()

            elif action == 'generate':
                client = CodexClient(api_key=api_key)
                result = client.generate(
                    plan=data['plan'],
                    context=data.get('context', ''),
                    feedback=data.get('feedback', [])
                )
                self.send_json({
                    'code': result.get('code', ''),
                    'files': result.get('files', []),
                    'language': result.get('language', 'python')
                })
                client.close()

            elif action == 'verify':
                client = ChatGPTClient(api_key=api_key)
                result = client.verify(data['code'], data['original_request'])
                self.send_json({
                    'status': result.get('status', 'PASS'),
                    'score': result.get('score', 100),
                    'issues': result.get('issues', []),
                    'summary': result.get('summary', '')
                })
                client.close()

        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_ollama(self, action: str, data: Dict):
        """Handle Ollama API calls."""
        try:
            url = data.get('ollama_url', 'http://localhost:11434')
            model = data.get('model', 'llama3.1:8b')

            from models.ollama_client import OllamaClient
            client = OllamaClient(base_url=url, model=model)

            if action == 'analyze':
                result = client.analyze(data['request'], data.get('task_type', 'generate_feature'))
                self.send_json({
                    'plan': result.get('plan', ''),
                    'components': result.get('components', []),
                    'response': result.get('response', '')
                })

            elif action == 'generate':
                result = client.generate(
                    plan=data['plan'],
                    context=data.get('context', ''),
                    feedback=data.get('feedback', [])
                )
                self.send_json({
                    'code': result.get('code', ''),
                    'response': result.get('response', ''),
                    'files': result.get('files', [])
                })

            elif action == 'verify':
                result = client.verify(data['code'], data['original_request'])
                self.send_json({
                    'status': result.get('status', 'PASS'),
                    'score': result.get('score', 100),
                    'issues': result.get('issues', []),
                    'summary': result.get('summary', '')
                })

            client.close()

        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_demo_analyze(self, data: Dict):
        """Handle demo analyze."""
        self.send_json({
            'plan': f"## Plan for: {data.get('request', '')}\n\n1. Analyze requirements\n2. Create implementation\n3. Test",
            'components': ['main.py', 'utils.py']
        })

    def handle_demo_generate(self, data: Dict):
        """Handle demo generate."""
        self.send_json({
            'code': '# Demo code\nprint("Hello, World!")',
            'files': ['demo.py']
        })

    def handle_demo_verify(self, data: Dict):
        """Handle demo verify."""
        self.send_json({
            'status': 'PASS',
            'score': 85,
            'issues': [],
            'summary': 'Demo mode - simulated verification'
        })

    def handle_github_repos(self):
        """Fetch GitHub repos for Hunting Mode."""
        try:
            token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
            if not token:
                # Try using gh CLI
                import subprocess
                result = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True)
                token = result.stdout.strip()

            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }

            import urllib.request
            req = urllib.request.Request(
                'https://api.github.com/user/repos?per_page=100&sort=updated',
                headers=headers
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                repos = json.loads(response.read().decode())

            repo_list = [{
                'name': r['name'],
                'full_name': r['full_name'],
                'url': r['html_url'],
                'description': r['description'] or '',
                'language': r['language'] or '',
                'stars': r['stargazers_count'],
                'forks': r['fork']
            } for r in repos]

            self.send_json({'repos': repo_list})

        except Exception as e:
            self.send_json({'error': str(e), 'repos': []}, 500)

    def send_json(self, data: Dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def run_server(port: int = 8080):
    """Run the API server."""
    handler = APIHandler
    handler.loop = ChatGPTCodexLoop()

    server = HTTPServer(('localhost', port), handler)

    print(f"""
{'='*60}
ChatGPT + Codex Hub Server
{'='*60}
Server:    http://localhost:{port}
UI:        http://localhost:{port}/index.html

Providers:
- OpenAI:  Enter API key in UI
- Ollama:  Run 'ollama serve' first
- Demo:    No setup needed

Press Ctrl+C to stop
{'='*60}
""")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.shutdown()


def main():
    parser = argparse.ArgumentParser(
        description="ChatGPT + Codex Hub - Collaborative Coding Loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py serve        # Start API server (for UI)
  python main.py serve --port 3000  # Custom port
  python main.py list          # List scenarios
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start API server")
    serve_parser.add_argument("--port", "-p", type=int, default=8080, help="Port number")

    # List scenarios
    subparsers.add_parser("list", help="List available scenarios")

    args = parser.parse_args()

    if not args.command or args.command == "serve":
        port = args.port if args.command == "serve" else 8080
        run_server(port)
        return

    if args.command == "list":
        print("\nAvailable Scenarios:")
        print("=" * 50)
        for key, scenario in DEMO_SCENARIOS.items():
            print(f"\n{key}:")
            print(f"  Name: {scenario['name']}")
            print(f"  Type: {scenario['task_type']}")
            print(f"  {scenario['description']}")
        return


if __name__ == "__main__":
    main()
