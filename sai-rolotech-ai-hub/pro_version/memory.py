"""
PRO Version Memory System
========================
Persistent memory storage with SQLite backend
Stores command history, results, and context
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")

@dataclass
class MemoryEntry:
    """Memory entry structure"""
    id: Optional[int] = None
    user_id: int = 1
    command: str = ""
    result: str = ""
    context: Dict[str, Any] = None
    timestamp: str = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class MemoryStore:
    """
    PRO Memory System with SQLite persistence
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    command TEXT NOT NULL,
                    result TEXT,
                    context TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id
                ON memories(user_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON memories(timestamp)
            """)
            conn.commit()

    def save(self, user_id: int, command: str, result: str = "",
             context: Optional[Dict] = None) -> int:
        """
        Save a memory entry

        Returns: entry ID
        """
        entry = MemoryEntry(
            user_id=user_id,
            command=command,
            result=result,
            context=context or {}
        )

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO memories (user_id, command, result, context, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                entry.user_id,
                entry.command,
                entry.result,
                json.dumps(entry.context),
                entry.timestamp
            ))
            conn.commit()
            return cursor.lastrowid

    def get_recent(self, user_id: int = 1, limit: int = 10) -> List[Dict]:
        """Get recent memory entries"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM memories
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_by_command(self, user_id: int, command: str) -> Optional[Dict]:
        """Find memory by command (fuzzy match)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM memories
                WHERE user_id = ? AND command LIKE ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (user_id, f"%{command}%"))

            row = cursor.fetchone()
            return dict(row) if row else None

    def search(self, user_id: int, query: str, limit: int = 10) -> List[Dict]:
        """Search memories by command or result"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM memories
                WHERE user_id = ?
                AND (command LIKE ? OR result LIKE ?)
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, f"%{query}%", f"%{query}%", limit))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_context(self, user_id: int = 1, limit: int = 5) -> str:
        """
        Get context string from recent memories
        Useful for AI prompts
        """
        memories = self.get_recent(user_id, limit)

        if not memories:
            return "No previous context available."

        context_parts = []
        for i, mem in enumerate(memories, 1):
            context_parts.append(
                f"[{i}] Command: {mem['command']}\n"
                f"    Result: {mem['result'][:200]}..."
            )

        return "\n".join(context_parts)

    def delete_old(self, days: int = 30) -> int:
        """Delete memories older than specified days"""
        cutoff = datetime.now().timestamp() - (days * 86400)
        cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM memories WHERE timestamp < ?
            """, (cutoff_iso,))
            conn.commit()
            return cursor.rowcount

    def get_stats(self, user_id: int = 1) -> Dict:
        """Get memory statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    MIN(timestamp) as oldest,
                    MAX(timestamp) as newest
                FROM memories
                WHERE user_id = ?
            """, (user_id,))

            row = cursor.fetchone()
            return {
                "total_memories": row[0] or 0,
                "oldest": row[1],
                "newest": row[2]
            }


# Singleton instance
memory_store = MemoryStore()


# Convenience functions
def save_memory(cmd: str, result: str = "", context: Dict = None) -> int:
    """Save a memory entry"""
    return memory_store.save(1, cmd, result, context)

def get_memory(limit: int = 10) -> List[Dict]:
    """Get recent memories"""
    return memory_store.get_recent(1, limit)

def get_context(limit: int = 5) -> str:
    """Get context string for AI"""
    return memory_store.get_context(1, limit)


if __name__ == "__main__":
    # Test
    print("🧠 PRO Memory System Test")

    # Save some test memories
    save_memory("client query", "Need C-channel quotes", {"client": "ABC Corp"})
    save_memory("design request", "Machine specs sent", {"machine": "C-150"})

    # Get context
    context = get_context()
    print("\n📝 Recent Context:")
    print(context)

    # Stats
    stats = memory_store.get_stats()
    print(f"\n📊 Stats: {stats}")
