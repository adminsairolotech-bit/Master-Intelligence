"""
PRO Version Automation System
============================
n8n workflow triggers and integrations
Handles automated actions based on AI responses
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

# Optional: requests for HTTP calls
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WHATSAPP_API = os.getenv("WHATSAPP_API", "")

class ActionType(Enum):
    """Types of automation actions"""
    CREATE_LEAD = "create_lead"
    SEND_NOTIFICATION = "send_notification"
    SCHEDULE_TASK = "schedule_task"
    SEND_EMAIL = "send_email"
    WHATSAPP_MESSAGE = "whatsapp_message"
    TELEGRAM_MESSAGE = "telegram_message"
    CUSTOM_WEBHOOK = "custom_webhook"
    GENERATE_QUOTE = "generate_quote"
    CREATE_TASK = "create_task"
    UPDATE_CRM = "update_crm"

@dataclass
class AutomationAction:
    """An automation action to be executed"""
    action_type: ActionType
    data: Dict[str, Any]
    priority: int = 1
    retry_count: int = 0
    max_retries: int = 3
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class TriggerResult:
    """Result of an automation trigger"""
    action: AutomationAction
    success: bool
    response: Optional[Dict] = None
    error: Optional[str] = None
    execution_time_ms: int = 0


class AutomationTrigger:
    """
    Automation Trigger System
    ========================

    Detects automation opportunities in AI responses
    and executes appropriate workflows via n8n
    """

    def __init__(self, webhook_url: str = N8N_WEBHOOK_URL):
        self.webhook_url = webhook_url
        self.action_queue: List[AutomationAction] = []
        self.execution_history: List[TriggerResult] = []

        # Keyword mappings for action detection
        self.action_patterns = {
            ActionType.CREATE_LEAD: [
                "new lead", "add customer", "create contact",
                "lead from", "prospect identified"
            ],
            ActionType.SEND_NOTIFICATION: [
                "notify", "alert", "inform", "send update",
                "let them know"
            ],
            ActionType.SCHEDULE_TASK: [
                "schedule", "remind", "follow up",
                "set a reminder", "calendar"
            ],
            ActionType.SEND_EMAIL: [
                "send email", "email to", "compose email",
                "mail them"
            ],
            ActionType.WHATSAPP_MESSAGE: [
                "whatsapp", "send message", "text message"
            ],
            ActionType.TELEGRAM_MESSAGE: [
                "telegram", "bot message"
            ],
            ActionType.GENERATE_QUOTE: [
                "quote", "quotation", "price estimate",
                "pricing for"
            ],
            ActionType.CREATE_TASK: [
                "create task", "add to todo", "task for",
                "assign task"
            ],
            ActionType.UPDATE_CRM: [
                "update crm", "crm entry", "log activity"
            ]
        }

    def detect_action(self, response: str, command: str) -> List[AutomationAction]:
        """
        Analyze AI response and detect automation opportunities

        Returns list of actions to execute
        """

        actions = []
        response_lower = response.lower()
        command_lower = command.lower()
        combined = f"{command_lower} {response_lower}"

        for action_type, patterns in self.action_patterns.items():
            for pattern in patterns:
                if pattern in combined:
                    # Extract relevant data from response
                    data = self._extract_action_data(
                        action_type,
                        command,
                        response
                    )

                    actions.append(AutomationAction(
                        action_type=action_type,
                        data=data
                    ))
                    break  # Only one action per type

        return actions

    def _extract_action_data(self, action_type: ActionType,
                            command: str, response: str) -> Dict[str, Any]:
        """Extract relevant data for the action type"""

        data = {
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "source": "pro_engine"
        }

        if action_type == ActionType.CREATE_LEAD:
            # Try to extract lead info from command/response
            data.update({
                "trigger": "ai_suggestion",
                "status": "pending_review"
            })

        elif action_type == ActionType.GENERATE_QUOTE:
            # Check for product/quantity mentions
            data.update({
                "trigger": "pricing_request",
                "status": "draft"
            })

        elif action_type == ActionType.SCHEDULE_TASK:
            data.update({
                "trigger": "ai_task_creation",
                "status": "scheduled"
            })

        return data

    def execute_action(self, action: AutomationAction) -> TriggerResult:
        """Execute a single automation action"""

        start_time = time.time()

        try:
            # Route to appropriate handler
            if action.action_type == ActionType.CREATE_LEAD:
                result = self._create_lead(action.data)
            elif action.action_type == ActionType.SEND_NOTIFICATION:
                result = self._send_notification(action.data)
            elif action.action_type == ActionType.SCHEDULE_TASK:
                result = self._schedule_task(action.data)
            elif action.action_type == ActionType.SEND_EMAIL:
                result = self._send_email(action.data)
            elif action.action_type == ActionType.WHATSAPP_MESSAGE:
                result = self._send_whatsapp(action.data)
            elif action.action_type == ActionType.TELEGRAM_MESSAGE:
                result = self._send_telegram(action.data)
            elif action.action_type == ActionType.CUSTOM_WEBHOOK:
                result = self._call_webhook(action.data)
            elif action.action_type == ActionType.GENERATE_QUOTE:
                result = self._generate_quote(action.data)
            elif action.action_type == ActionType.CREATE_TASK:
                result = self._create_task(action.data)
            elif action.action_type == ActionType.UPDATE_CRM:
                result = self._update_crm(action.data)
            else:
                result = {"error": f"Unknown action type: {action.action_type}"}

            exec_time = int((time.time() - start_time) * 1000)

            trigger_result = TriggerResult(
                action=action,
                success=True,
                response=result,
                execution_time_ms=exec_time
            )

        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            exec_time = int((time.time() - start_time) * 1000)
            trigger_result = TriggerResult(
                action=action,
                success=False,
                error=str(e),
                execution_time_ms=exec_time
            )

        self.execution_history.append(trigger_result)
        return trigger_result

    def _call_webhook(self, data: Dict) -> Dict:
        """Call n8n webhook with data"""

        if not HAS_REQUESTS:
            return {"error": "requests library not available"}

        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=30
            )

            if response.status_code in [200, 201]:
                return {"status": "success", "response": response.json()}
            else:
                return {"status": "error", "code": response.status_code}

        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "n8n not reachable"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _create_lead(self, data: Dict) -> Dict:
        """Create a lead via n8n webhook"""

        return self._call_webhook({
            "type": "create_lead",
            **data
        })

    def _send_notification(self, data: Dict) -> Dict:
        """Send notification"""

        return self._call_webhook({
            "type": "notification",
            **data
        })

    def _schedule_task(self, data: Dict) -> Dict:
        """Schedule a task"""

        return self._call_webhook({
            "type": "schedule_task",
            **data
        })

    def _send_email(self, data: Dict) -> Dict:
        """Send email via n8n"""

        return self._call_webhook({
            "type": "send_email",
            **data
        })

    def _send_whatsapp(self, data: Dict) -> Dict:
        """Send WhatsApp message"""

        return self._call_webhook({
            "type": "whatsapp_message",
            **data
        })

    def _send_telegram(self, data: Dict) -> Dict:
        """Send Telegram message"""

        return self._call_webhook({
            "type": "telegram_message",
            **data
        })

    def _generate_quote(self, data: Dict) -> Dict:
        """Generate quotation"""

        return self._call_webhook({
            "type": "generate_quote",
            **data
        })

    def _create_task(self, data: Dict) -> Dict:
        """Create task"""

        return self._call_webhook({
            "type": "create_task",
            **data
        })

    def _update_crm(self, data: Dict) -> Dict:
        """Update CRM"""

        return self._call_webhook({
            "type": "update_crm",
            **data
        })

    def process_response(self, command: str, response: str,
                        auto_execute: bool = True) -> List[TriggerResult]:
        """
        Main entry point: Process AI response for automation

        Args:
            command: Original user command
            response: AI response text
            auto_execute: Whether to automatically execute detected actions

        Returns:
            List of trigger results
        """

        # Detect automation opportunities
        actions = self.detect_action(response, command)

        results = []

        for action in actions:
            logger.info(f"Detected action: {action.action_type.value}")

            if auto_execute:
                result = self.execute_action(action)
                results.append(result)
            else:
                # Just queue the action
                self.action_queue.append(action)
                results.append(TriggerResult(
                    action=action,
                    success=True,
                    response={"status": "queued"}
                ))

        return results

    def get_queue(self) -> List[Dict]:
        """Get pending actions in queue"""

        return [
            {
                "action_type": a.action_type.value,
                "data": a.data,
                "priority": a.priority,
                "created_at": a.created_at
            }
            for a in self.action_queue
        ]

    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get execution history"""

        return [
            {
                "action_type": r.action.action_type.value,
                "success": r.success,
                "error": r.error,
                "execution_time_ms": r.execution_time_ms,
                "timestamp": r.action.created_at
            }
            for r in self.execution_history[-limit:]
        ]

    def get_stats(self) -> Dict:
        """Get automation statistics"""

        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.success)
        failed = total - successful

        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "pending_in_queue": len(self.action_queue),
            "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "N/A"
        }


# Singleton instance
automation = AutomationTrigger()


# Convenience functions
def trigger_automation(command: str, response: str,
                       auto_execute: bool = True) -> List[TriggerResult]:
    """Process AI response for automation triggers"""
    return automation.process_response(command, response, auto_execute)

def queue_action(action_type: ActionType, data: Dict) -> None:
    """Queue an action for later execution"""
    automation.action_queue.append(
        AutomationAction(action_type=action_type, data=data)
    )

def execute_queue() -> List[TriggerResult]:
    """Execute all queued actions"""
    results = []
    while automation.action_queue:
        action = automation.action_queue.pop(0)
        result = automation.execute_action(action)
        results.append(result)
    return results


if __name__ == "__main__":
    print("⚡ PRO Automation System Test\n")
    print("=" * 60)

    # Test action detection
    print("\n📋 Action Detection Test:")

    test_cases = [
        ("Add this customer to CRM", "I'll create a new lead for John from ABC Corp"),
        ("Generate quote for 100 units", "Based on your requirements, the quote is ready"),
        ("Remind me to follow up", "I've scheduled a reminder for tomorrow at 9 AM"),
        ("Send email to client", "Email has been composed and queued for sending"),
    ]

    for command, response in test_cases:
        actions = automation.detect_action(response, command)
        print(f"\nCommand: {command}")
        print(f"Response: {response}")
        print(f"Detected Actions: {[a.action_type.value for a in actions]}")

    # Test stats
    print("\n" + "=" * 60)
    print("\n📊 Automation Stats:")
    stats = automation.get_stats()
    print(json.dumps(stats, indent=2))
