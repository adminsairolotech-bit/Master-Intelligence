"""
ChatGPT + Codex Hub - Main Entry Point with Real API Support
SAI ROLO TECH
"""

import argparse
import sys
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from chatgpt_codex_loop import ChatGPTCodexLoop, TaskType
from scenarios.demo_scenario import DEMO_SCENARIOS, run_demo_scenario


class APIHandler(SimpleHTTPRequestHandler):
    """HTTP API handler for frontend communication."""

    loop = None

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(body) if body else {}

        if self.path == '/api/analyze':
            self.handle_analyze(data)
        elif self.path == '/api/generate':
            self.handle_generate(data)
        elif self.path == '/api/verify':
            self.handle_verify(data)
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

    def handle_analyze(self, data):
        """Handle analyze endpoint."""
        try:
            api_key = data.get('api_key')
            if not api_key:
                self.send_json({'error': 'API key required'}, 400)
                return

            client = self.loop.chatgpt if self.loop else None
            if not client:
                from models.chatgpt_client import ChatGPTClient
                client = ChatGPTClient(api_key=api_key)

            result = client.analyze(data['request'], data.get('task_type', 'generate_feature'))

            self.send_json({
                'plan': result.get('plan', ''),
                'components': result.get('components', []),
                'dependencies': result.get('dependencies', []),
                'verification_criteria': result.get('verification_criteria', [])
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_generate(self, data):
        """Handle generate endpoint."""
        try:
            api_key = data.get('api_key')
            if not api_key:
                self.send_json({'error': 'API key required'}, 400)
                return

            client = self.loop.codex if self.loop else None
            if not client:
                from models.codex_client import CodexClient
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
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_verify(self, data):
        """Handle verify endpoint."""
        try:
            api_key = data.get('api_key')
            if not api_key:
                self.send_json({'error': 'API key required'}, 400)
                return

            client = self.loop.chatgpt if self.loop else None
            if not client:
                from models.chatgpt_client import ChatGPTClient
                client = ChatGPTClient(api_key=api_key)

            result = client.verify(data['code'], data['original_request'])

            self.send_json({
                'status': result.get('status', 'PASS'),
                'score': result.get('score', 100),
                'issues': result.get('issues', []),
                'verified_aspects': result.get('verified_aspects', []),
                'summary': result.get('summary', '')
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def run_server(port=8080):
    """Run the API server."""
    handler = APIHandler
    handler.loop = ChatGPTCodexLoop()

    server = HTTPServer(('localhost', port), handler)
    print(f"\n{'='*60}")
    print(f"API Server running at http://localhost:{port}")
    print(f"Open http://localhost:{port}/index.html in browser")
    print(f"{'='*60}\n")

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
  python main.py run "Create a calculator"
  python main.py demo calculator
  python main.py list
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Serve command (for UI)
    subparsers.add_parser("serve", help="Start API server for UI")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a task")
    run_parser.add_argument("request", help="The task/request description")
    run_parser.add_argument("--type", "-t", choices=["generate", "fix", "refactor"],
                           default="generate", help="Task type")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run a demo scenario")
    demo_parser.add_argument("scenario", nargs="?", help="Demo scenario name")

    # List scenarios
    subparsers.add_parser("list", help="List available scenarios")

    # Interactive mode
    subparsers.add_parser("interactive", help="Start interactive mode")

    args = parser.parse_args()

    if not args.command or args.command == "serve":
        run_server()
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

    if args.command == "demo":
        run_demo_scenario(args.scenario)
        return

    if args.command == "run":
        loop = ChatGPTCodexLoop()

        task_map = {
            "generate": TaskType.GENERATE_FEATURE,
            "fix": TaskType.FIX_BUG,
            "refactor": TaskType.REFACTOR
        }

        print(f"\n{'='*60}")
        print(f"CHATGPT + CODEX LOOP")
        print(f"{'='*60}")
        print(f"\nRequest: {args.request}")
        print(f"Type: {args.type}")

        result = loop.run(args.request, task_map[args.type])

        print(f"\n{'='*60}")
        print("RESULT")
        print(f"{'='*60}")
        print(f"Status: {result['status'].upper()}")
        print(f"Iterations: {result['iterations']}")

        if result.get('code'):
            print(f"\nGenerated code:")
            print("-" * 40)
            print(result['code'][:500] + "..." if len(result.get('code', '')) > 500 else result.get('code', ''))
        return

    if args.command == "interactive":
        print("\n" + "="*60)
        print("INTERACTIVE MODE - ChatGPT + Codex Loop")
        print("="*60)
        print("\nType your request and press Enter.")
        print("Type 'quit' or 'exit' to stop.")
        print("-" * 60)

        loop = ChatGPTCodexLoop()

        while True:
            try:
                request = input("\n>>> ").strip()

                if request.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break

                if not request:
                    continue

                result = loop.run(request)
                print(f"\nResult: {result['status']}")
                print(f"Iterations: {result['iterations']}")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
