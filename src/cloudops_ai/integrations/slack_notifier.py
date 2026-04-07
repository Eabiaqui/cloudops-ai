"""Slack notification integration for CloudOps AI."""

import os
import httpx
import json
from typing import Optional
from cloudops_ai.models.alert import ClassifiedAlert
from cloudops_ai.models.orm import Diagnosis

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


async def send_alert_to_slack(
    classified: ClassifiedAlert,
    diagnosis: Optional[Diagnosis] = None,
    dashboard_url: str = "https://app.qhunu.com",
) -> bool:
    """
    Send alert notification to Slack with diagnosis.
    
    Returns True if successful, False otherwise.
    """
    if not SLACK_WEBHOOK_URL:
        print("⚠️  SLACK_WEBHOOK_URL not configured, skipping Slack notification")
        return False
    
    try:
        # Build Slack message
        severity_emoji = {
            "critical": "🔴",
            "error": "🟠",
            "warning": "🟡",
            "info": "🔵",
            "unknown": "⚪",
        }
        
        emoji = severity_emoji.get(classified.severity_normalized, "⚪")
        
        # Extract key info
        alert_name = classified.essentials.alert_rule or "Unknown Alert"
        alert_id = classified.essentials.alert_id
        resource = classified.raw_payload.resource if hasattr(classified.raw_payload, 'resource') else "unknown"
        
        # Build blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {classified.category.upper()} - {classified.severity_normalized.upper()}",
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Alert:*\n{alert_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Resource:*\n{resource}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Category:*\n{classified.category}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Confidence:*\n{int(classified.confidence * 100)}%"
                    },
                ]
            },
        ]
        
        # Add diagnosis if available
        if diagnosis:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔍 AI Diagnosis:*\n{diagnosis.diagnosis}"
                }
            })
            
            if diagnosis.evidence:
                evidence_text = "\n".join([f"• {e}" for e in diagnosis.evidence[:3]])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Evidence:*\n{evidence_text}"
                    }
                })
            
            if diagnosis.suggested_action:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Suggested Action:*\n```{diagnosis.suggested_action}```"
                    }
                })
        
        # Add action buttons
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View in Dashboard"
                    },
                    "url": f"{dashboard_url}?alert={alert_id}",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Full Details"
                    },
                    "url": f"{dashboard_url}/alerts/{alert_id}",
                }
            ]
        })
        
        # Send to Slack
        payload = {
            "blocks": blocks,
            "text": f"{emoji} CloudOps AI Alert: {alert_name}"  # Fallback text
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(SLACK_WEBHOOK_URL, json=payload)
            
            if response.status_code == 200:
                print(f"✅ Slack notification sent for alert {alert_id}")
                return True
            else:
                print(f"❌ Slack notification failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error sending Slack notification: {e}")
        return False


async def send_test_message(channel: str = "#cloudops-alerts") -> bool:
    """Send a test message to Slack."""
    if not SLACK_WEBHOOK_URL:
        print("❌ SLACK_WEBHOOK_URL not configured")
        return False
    
    try:
        payload = {
            "text": "🧪 CloudOps AI - Test Message",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🧪 CloudOps AI Integration Test"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ Slack integration is working correctly!\n\nAlerts will appear here when they arrive from Azure Monitor."
                    }
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(SLACK_WEBHOOK_URL, json=payload)
            
            if response.status_code == 200:
                print(f"✅ Test message sent to Slack")
                return True
            else:
                print(f"❌ Test failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        return False
