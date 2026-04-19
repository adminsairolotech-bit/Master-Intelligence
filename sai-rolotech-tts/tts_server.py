#!/usr/bin/env python3
"""
SAI ROLOTECH TTS SERVER - API Server
REST API for TTS with Hindi/English support
Similar to ElevenLabs API
"""

import asyncio
import edge_tts
import json
import os
from pathlib import Path
from aiohttp import web

PORT = 8888

class TTSServer:
    def __init__(self):
        self.output_dir = Path("output/tts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.voices_cache = None

    async def get_voices(self):
        if self.voices_cache is None:
            self.voices_cache = await edge_tts.list_voices()
        return self.voices_cache

    async def handle_health(self, request):
        return web.json_response({
            "status": "ok",
            "service": "SAI ROLOTECH TTS",
            "version": "1.0.0",
            "voices_available": len(await self.get_voices())
        })

    async def handle_voices(self, request):
        lang = request.query.get("lang")
        voices = await self.get_voices()

        result = []
        for v in voices:
            if lang and not v["Locale"].startswith(lang.lower()):
                continue
            result.append({
                "name": v["Name"],
                "locale": v["Locale"],
                "gender": v.get("Gender", "Unknown"),
                "style": v.get("Style", [])
            })

        return web.json_response({"voices": result, "count": len(result)})

    async def handle_speak(self, request):
        try:
            data = await request.json()

            text = data.get("text")
            if not text:
                return web.json_response({"error": "text is required"}, status=400)

            voice = data.get("voice", "hi-IN-SwaraNeural")
            speed = float(data.get("speed", 1.0))

            # Generate filename
            filename = f"{Path(text[:20].replace(' ', '_').replace(',', '').replace('?', '').replace('!', ''))}_{os.urandom(4).hex()}.mp3"
            output_path = self.output_dir / filename

            # Generate
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))

            file_size = os.path.getsize(output_path)

            return web.json_response({
                "success": True,
                "file": str(output_path),
                "size": file_size,
                "voice": voice,
                "text_length": len(text)
            })

        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_stream(self, request):
        """Stream audio response - like ElevenLabs"""
        try:
            data = await request.json()

            text = data.get("text")
            if not text:
                return web.json_response({"error": "text is required"}, status=400)

            voice = data.get("voice", "hi-IN-SwaraNeural")

            # Generate to temp file
            temp_file = self.output_dir / f"stream_{os.urandom(8).hex()}.mp3"
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(temp_file))

            # Read and return
            with open(temp_file, "rb") as f:
                audio_data = f.read()

            os.remove(temp_file)

            return web.Response(
                body=audio_data,
                content_type="audio/mpeg",
                headers={"Content-Disposition": "inline"}
            )

        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_batch(self, request):
        """Batch TTS - like ElevenLabs batch API"""
        try:
            data = await request.json()

            texts = data.get("texts", [])
            if not texts:
                return web.json_response({"error": "texts array is required"}, status=400)

            voice = data.get("voice", "hi-IN-SwaraNeural")
            batch_id = os.urandom(8).hex()

            results = []
            for i, text in enumerate(texts):
                filename = f"batch_{batch_id}_{i:03d}.mp3"
                output_path = self.output_dir / filename

                try:
                    communicate = edge_tts.Communicate(text, voice)
                    await communicate.save(str(output_path))

                    results.append({
                        "index": i,
                        "success": True,
                        "file": str(output_path),
                        "size": os.path.getsize(output_path)
                    })
                except Exception as e:
                    results.append({
                        "index": i,
                        "success": False,
                        "error": str(e)
                    })

            return web.json_response({
                "batch_id": batch_id,
                "results": results,
                "success_count": sum(1 for r in results if r["success"]),
                "total": len(results)
            })

        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

async def main():
    app = web.Application()
    tts = TTSServer()

    # Routes
    app.router.add_get("/health", tts.handle_health)
    app.router.add_get("/voices", tts.handle_voices)
    app.router.add_post("/speak", tts.handle_speak)
    app.router.add_post("/stream", tts.handle_stream)
    app.router.add_post("/batch", tts.handle_batch)

    print(f"""
╔════════════════════════════════════════════════════════╗
║        SAI ROLOTECH TTS SERVER - ELEVENLABS STYLE       ║
╠════════════════════════════════════════════════════════╣
║                                                         ║
║  API Endpoints:                                        ║
║                                                         ║
║  GET  /health              - Health check             ║
║  GET  /voices              - List all voices          ║
║  GET  /voices?lang=hi-IN   - Filter by language      ║
║                                                         ║
║  POST /speak                - Generate speech          ║
║       {{"text": "...", "voice": "hi-IN-SwaraNeural"}} ║
║                                                         ║
║  POST /stream               - Stream audio response   ║
║       {{"text": "...", "voice": "hi-IN-SwaraNeural"}} ║
║                                                         ║
║  POST /batch                - Batch TTS               ║
║       {{"texts": ["...", "..."], "voice": "..."}}    ║
║                                                         ║
║  Port: {PORT}                                             ║
║                                                         ║
╚════════════════════════════════════════════════════════╝
    """)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", PORT)
    await site.start()

    print(f"\n🚀 Server running at http://localhost:{PORT}")
    print(f"📁 Output directory: {tts.output_dir}\n")

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())