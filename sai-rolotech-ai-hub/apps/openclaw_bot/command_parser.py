"""
OpenClaw Command Parser
Maps user commands to Hermes router
"""

import re
from typing import Dict, Optional


class CommandParser:
    """
    OpenClaw Command Parser
    Entry/Exit Layer for Telegram/WhatsApp
    """

    # Command patterns
    COMMANDS = {
        # CRM commands
        r"/lead\s+add\s+(.+)\s+(\d{10,})": "crm_add_lead",
        r"/lead\s+list": "crm_list_leads",
        r"/lead\s+(\d+)": "crm_get_lead",
        r"/leads": "crm_list_leads",

        # Desktop commands
        r"/open\s+(.+)": "desktop_open",
        r"/run\s+(.+)": "desktop_run",
        r"/click\s+(.+)": "desktop_click",

        # Task commands
        r"/task\s+create\s+(.+)": "schedule_task",
        r"/remind\s+(.+)": "schedule_reminder",
        r"/schedule\s+(.+)": "schedule_task",

        # General
        r"/help": "show_help",
        r"/stats": "show_stats",
        r"/report": "daily_report",
    }

    def __init__(self, master_router):
        self.router = master_router

    def parse(self, message: str, user_id: int) -> Dict:
        """
        Parse message and route to correct handler
        Returns: {command, params, response}
        """
        msg = message.strip()
        msg_lower = msg.lower()

        # Check command patterns
        for pattern, command in self.COMMANDS.items():
            match = re.search(pattern, msg_lower)
            if match:
                return self._execute_command(command, match.groups(), msg, user_id)

        # Natural language - route through Hermes
        return {
            "command": "chat",
            "params": {},
            "response": None,  # Will be handled by Hermes
            "raw_message": msg
        }

    def _execute_command(self, command: str, params: tuple, raw: str, user_id: int) -> Dict:
        """Execute specific command"""

        if command == "crm_add_lead":
            name = params[0].title()
            mobile = params[1]
            result = self.router.process(user_id, f"add lead {name} {mobile}")
            return {
                "command": "crm_add_lead",
                "params": {"name": name, "mobile": mobile},
                "response": f"✅ Lead added!\n\n📋 Name: {name}\n📱 Mobile: {mobile}",
                "needs_hermes": False
            }

        elif command == "crm_list_leads":
            return {
                "command": "crm_list_leads",
                "params": {},
                "response": "📋 Fetching leads...",
                "needs_hermes": False,
                "action": "fetch_leads"
            }

        elif command == "desktop_open":
            app = params[0]
            return {
                "command": "desktop_open",
                "params": {"app": app},
                "response": f"🌐 Opening {app}...",
                "needs_hermes": True,
                "action": "open_app"
            }

        elif command == "desktop_run":
            cmd = params[0]
            return {
                "command": "desktop_run",
                "params": {"command": cmd},
                "response": f"💻 Running: {cmd}",
                "needs_hermes": True,
                "action": "run_command"
            }

        elif command == "schedule_task":
            task = params[0]
            return {
                "command": "schedule_task",
                "params": {"task": task},
                "response": f"⏰ Scheduling: {task}",
                "needs_hermes": True,
                "action": "schedule"
            }

        elif command == "schedule_reminder":
            reminder = params[0]
            return {
                "command": "schedule_reminder",
                "params": {"reminder": reminder},
                "response": f"🔔 Reminder set: {reminder}",
                "needs_hermes": True,
                "action": "remind"
            }

        elif command == "show_help":
            return {
                "command": "show_help",
                "params": {},
                "response": self._get_help_text(),
                "needs_hermes": False
            }

        elif command == "show_stats":
            return {
                "command": "show_stats",
                "params": {},
                "response": "📊 Fetching stats...",
                "needs_hermes": False,
                "action": "fetch_stats"
            }

        elif command == "daily_report":
            return {
                "command": "daily_report",
                "params": {},
                "response": "📊 Generating daily report...",
                "needs_hermes": False,
                "action": "daily_report"
            }

        else:
            return {
                "command": "unknown",
                "params": {},
                "response": "Command not recognized. Type /help for options."
            }

    def _get_help_text(self) -> str:
        """Get help message"""
        return """
🤖 **SAI Rolotech AI Hub Commands**

**CRM Commands:**
`/lead add [Name] [Mobile]` - Add new lead
`/lead list` - List all leads
`/leads` - View leads

**Desktop Commands:**
`/open [app]` - Open application
`/run [command]` - Run command

**Task Commands:**
`/task create [task]` - Create scheduled task
`/remind [message]` - Set reminder
`/schedule [task]` - Schedule automation

**General:**
`/stats` - View business stats
`/report` - Daily report
`/help` - Show this help

💬 Or just chat naturally!
"""


# Singleton
command_parser = None
