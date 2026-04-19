"""
Laptop Optimizer Pro - SAI ROLO TECH
Full System Control with AI (Offline + Online)
========================================
Features:
- CPU/RAM/GPU/CPU Temperature Full Monitoring
- Process Manager with Kill/Optimize
- Disk Cleanup & Analysis
- Network Monitor & Stats
- Battery Optimization
- Ollama AI (Offline)
- OPUS 4.7 AI (Online with Private Key)
"""

import json
import psutil
import platform
import subprocess
import os
import asyncio
import httpx
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


class SystemOptimizerPro:
    """Full system optimization engine."""

    def __init__(self):
        self.boot_time = datetime.fromtimestamp(psutil.boot_time())
        self.start_time = datetime.now()
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.opus_api_key = os.getenv('OPUS_API_KEY', '')
        self.opus_api_url = os.getenv('OPUS_API_URL', 'https://api.opusmax.pro/v1/chat/completions')

    # ==================== SYSTEM INFO ====================
    def get_system_info(self):
        """Complete system information."""
        info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor()[:50] if platform.processor() else "Unknown",
            "hostname": platform.node(),
            "boot_time": self.boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            "uptime_seconds": int((datetime.now() - self.boot_time).total_seconds()),
            "uptime_str": self._format_uptime(int((datetime.now() - self.boot_time).total_seconds())),
            "cpu_count": psutil.cpu_count(logical=False),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "python_version": platform.python_version(),
        }
        return info

    def _format_uptime(self, seconds):
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        mins = (seconds % 3600) // 60
        if days > 0: return f"{days}d {hours}h"
        if hours > 0: return f"{hours}h {mins}m"
        return f"{mins}m"

    # ==================== CPU ====================
    def get_cpu_stats(self):
        """Detailed CPU stats."""
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        freq = psutil.cpu_freq()
        cpu_times = psutil.cpu_times()

        return {
            "per_cpu": [{"core": i, "usage": round(c, 1)} for i, c in enumerate(cpu_percent)],
            "average": round(sum(cpu_percent) / len(cpu_percent), 1),
            "freq_current": round(freq.current, 0) if freq else 0,
            "freq_min": round(freq.min, 0) if freq else 0,
            "freq_max": round(freq.max, 0) if freq else 0,
            "user": round(cpu_times.user, 1),
            "system": round(cpu_times.system, 1),
            "idle": round(cpu_times.idle, 1),
        }

    # ==================== MEMORY ====================
    def get_memory_stats(self):
        """Detailed memory stats."""
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total_gb": round(vm.total / (1024**3), 2),
            "available_gb": round(vm.available / (1024**3), 2),
            "used_gb": round(vm.used / (1024**3), 2),
            "percent": vm.percent,
            "swap_total_gb": round(swap.total / (1024**3), 2),
            "swap_used_gb": round(swap.used / (1024**3), 2),
            "swap_percent": swap.percent,
        }

    # ==================== DISK ====================
    def get_disk_stats(self):
        """Complete disk analysis."""
        partitions = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024**3), 1),
                    "used_gb": round(usage.used / (1024**3), 1),
                    "free_gb": round(usage.free / (1024**3), 1),
                    "percent": usage.percent,
                })
            except:
                pass
        return partitions

    # ==================== BATTERY ====================
    def get_battery_stats(self):
        """Battery status and optimization."""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "plugged_in": battery.power_plugged,
                    "charging": battery.percent < 100 and battery.power_plugged,
                    "time_left_minutes": int(battery.secsleft / 60) if battery.secsleft >= 0 else -1,
                    "status": "Charging" if battery.power_plugged else f"{battery.percent}%",
                }
            return {"percent": -1, "plugged_in": True, "status": "No Battery"}
        except:
            return {"percent": -1, "plugged_in": True, "status": "Unknown"}

    # ==================== NETWORK ====================
    def get_network_stats(self):
        """Network IO and connections."""
        net_io = psutil.net_io_counters()
        connections = len(psutil.net_connections())
        return {
            "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errin": net_io.errin,
            "errout": net_io.errout,
            "connections": connections,
        }

    def get_network_interfaces(self):
        """Network interface details."""
        interfaces = {}
        try:
            for iface, addrs in psutil.net_if_addrs().items():
                interfaces[iface] = {
                    "mac": next((a.address for a in addrs if a.family == psutil.AF_LINK), None),
                    "ipv4": next((a.address for a in addrs if a.family == 2), None),
                    "ipv6": next((a.address for a in addrs if a.family == 10), None),
                }
        except:
            pass
        return interfaces

    # ==================== GPU ====================
    def get_gpu_info(self):
        """GPU information."""
        gpu = {"available": False, "name": "Unknown", "memory_used": 0, "memory_total": 0}

        if platform.system() == "Windows":
            try:
                result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name', '/format:json'],
                                       capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    if data and len(data) > 0:
                        gpu["name"] = data[0].get("Name", "Unknown")
                        gpu["available"] = True
            except:
                pass

        return gpu

    # ==================== TEMPERATURE ====================
    def get_temperature(self):
        """Temperature sensors."""
        temps = {}
        try:
            for name, entries in psutil.sensors_temperatures().items():
                temps[name] = [{
                    "label": e.label or name,
                    "current": round(e.current, 1),
                    "high": e.high,
                    "critical": e.critical
                } for e in entries]
        except:
            pass
        return temps

    # ==================== PROCESSES ====================
    def get_processes(self, sort_by="cpu", limit=30):
        """Top processes sorted by CPU or memory."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username']):
            try:
                pinfo = proc.info
                pinfo['memory_mb'] = round(proc.memory_info().rss / (1024**2), 1)
                pinfo['cpu_percent'] = pinfo.get('cpu_percent') or 0
                pinfo['memory_percent'] = pinfo.get('memory_percent') or 0
                processes.append(pinfo)
            except:
                pass

        if sort_by == "cpu":
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        else:
            processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)

        return processes[:limit]

    def kill_process(self, pid):
        """Kill process by PID."""
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            proc.kill()
            return {"success": True, "name": name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_high_cpu_processes(self, threshold=10):
        """Get processes using high CPU."""
        return [p for p in self.get_processes("cpu", 50) if p['cpu_percent'] > threshold]

    # ==================== STARTUP ====================
    def get_startup_programs(self):
        """Startup programs (Windows)."""
        startup = []
        if platform.system() == "Windows":
            try:
                startup_folder = Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
                if startup_folder.exists():
                    for f in startup_folder.iterdir():
                        if f.suffix in ['.lnk', '.exe', '.bat', '.cmd']:
                            startup.append({"name": f.stem, "path": str(f), "source": "Startup Folder"})

                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        startup.append({"name": name, "path": value, "source": "Registry"})
                        i += 1
                    except:
                        break
                winreg.CloseKey(key)
            except:
                pass
        return startup

    # ==================== OPTIMIZATION ====================
    def get_optimization_suggestions(self):
        """Get optimization suggestions."""
        suggestions = []
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)

        if mem.percent > 90:
            suggestions.append({"type": "danger", "msg": "Memory critical! Close unused apps.", "action": "memory"})
        elif mem.percent > 80:
            suggestions.append({"type": "warning", "msg": "Memory usage high.", "action": "memory"})

        if cpu > 90:
            suggestions.append({"type": "danger", "msg": f"CPU at {cpu}%!", "action": "cpu"})
        elif cpu > 70:
            suggestions.append({"type": "warning", "msg": f"CPU usage elevated ({cpu}%).", "action": "cpu"})

        # Check disk space
        for disk in self.get_disk_stats():
            if disk['percent'] > 95:
                suggestions.append({"type": "danger", "msg": f"{disk['mountpoint']} almost full!", "action": "disk"})
            elif disk['percent'] > 85:
                suggestions.append({"type": "warning", "msg": f"{disk['mountpoint']} needs cleanup.", "action": "disk"})

        if len(suggestions) == 0:
            suggestions.append({"type": "success", "msg": "System is running optimally!", "action": None})

        return suggestions

    # ==================== AI - OLLAMA (OFFLINE) ====================
    async def ollama_chat(self, message, model="llama3:8b"):
        """Chat with local Ollama AI."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": message}],
                        "stream": False
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return {"success": True, "response": data.get('message', {}).get('content', '')}
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_ollama_status(self):
        """Check if Ollama is running."""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 11434))
            sock.close()
            return {"running": result == 0}
        except:
            return {"running": False}

    # ==================== AI - OPUS 4.7 (ONLINE) ====================
    async def opus_chat(self, message):
        """Chat with OPUS 4.7 via API."""
        # Try multiple key sources (safe fallback chain)
        api_key = (
            os.getenv('OPUS_API_KEY') or
            os.getenv('OPENROUTER_API_KEY') or  # Fallback to OpenRouter
            os.getenv('sk_or_v1') or
            self.opus_api_key
        )

        if not api_key:
            return {"success": False, "error": "API key not found. Check .env file."}

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    self.opus_api_url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "claude-opus-4-7",
                        "messages": [{"role": "user", "content": message}]
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return {"success": True, "response": data['choices'][0]['message']['content']}
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text[:100]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== FULL STATUS ====================
    def get_full_status(self):
        """Get all system stats in one call."""
        return {
            "system": self.get_system_info(),
            "cpu": self.get_cpu_stats(),
            "memory": self.get_memory_stats(),
            "disk": self.get_disk_stats(),
            "battery": self.get_battery_stats(),
            "network": self.get_network_stats(),
            "gpu": self.get_gpu_info(),
            "temperature": self.get_temperature(),
            "ollama": self.check_ollama_status(),
        }


class APIHandler(SimpleHTTPRequestHandler):
    """HTTP API Handler."""

    optimizer = SystemOptimizerPro()

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/api/system': self.send_json(self.optimizer.get_system_info())
        elif self.path == '/api/cpu': self.send_json(self.optimizer.get_cpu_stats())
        elif self.path == '/api/memory': self.send_json(self.optimizer.get_memory_stats())
        elif self.path == '/api/disk': self.send_json(self.optimizer.get_disk_stats())
        elif self.path == '/api/battery': self.send_json(self.optimizer.get_battery_stats())
        elif self.path == '/api/network': self.send_json(self.optimizer.get_network_stats())
        elif self.path == '/api/network/interfaces': self.send_json(self.optimizer.get_network_interfaces())
        elif self.path == '/api/gpu': self.send_json(self.optimizer.get_gpu_info())
        elif self.path == '/api/temperature': self.send_json(self.optimizer.get_temperature())
        elif self.path == '/api/processes/cpu': self.send_json({"processes": self.optimizer.get_processes("cpu")})
        elif self.path == '/api/processes/memory': self.send_json({"processes": self.optimizer.get_processes("memory")})
        elif self.path == '/api/startup': self.send_json({"programs": self.optimizer.get_startup_programs()})
        elif self.path == '/api/optimize': self.send_json({"suggestions": self.optimizer.get_optimization_suggestions()})
        elif self.path == '/api/all': self.send_json(self.optimizer.get_full_status())
        elif self.path == '/health': self.send_json({"status": "ok"})
        elif self.path.startswith('/index'): super().do_GET()
        else: super().do_GET()

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(body) if body else {}

        if self.path == '/api/kill':
            result = self.optimizer.kill_process(data.get('pid'))
            self.send_json(result)
        elif self.path == '/api/ai/ollama':
            asyncio.run(self._handle_ollama(data))
        elif self.path == '/api/ai/opus':
            asyncio.run(self._handle_opus(data))
        else:
            self.send_error(404, 'Not Found')

    async def _handle_ollama(self, data):
        """Handle Ollama AI chat."""
        message = data.get('message', '')
        model = data.get('model', 'llama3:8b')
        result = await self.optimizer.ollama_chat(message, model)
        self.send_json(result)

    async def _handle_opus(self, data):
        """Handle OPUS 4.7 AI chat."""
        message = data.get('message', '')
        result = await self.optimizer.opus_chat(message)
        self.send_json(result)

    def send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def run_server(port=3848):
    """Run the optimizer server."""
    # Change to app directory for serving static files
    os.chdir(Path(__file__).parent)

    server = HTTPServer(('0.0.0.0', port), APIHandler)

    print("""
+============================================================+
|           LAPTOP OPTIMIZER PRO - SAI ROLO TECH            |
+============================================================+
|  Dashboard:  http://localhost:{}                           |
|  API:        http://localhost:{}/api/all                   |
+============================================================+
|  FEATURES:                                                |
|  [X] CPU/RAM/GPU Monitoring                              |
|  [X] Process Manager                                       |
|  [X] Disk Analysis                                        |
|  [X] Battery Status                                       |
|  [X] Network Monitor                                     |
|  [X] Temperature Sensors                                  |
|  [X] Ollama AI (Offline)                                 |
|  [X] OPUS 4.7 AI (Online)                                |
+============================================================+
""".format(port, port))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    run_server()
