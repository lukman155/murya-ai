"""Domain Services for Nigerian Financial Disputes and Electricity/DisCo Grievances.
Simulates real-world Nigerian banking core (NIBSS Instant Payments) and DisCo STS Token services.
"""
import uuid
import random
from datetime import datetime, timedelta
from typing import Any

# In-memory mock databases pre-seeded with representative Nigerian transaction records
MOCK_BANK_TRANSACTIONS = {
    "08031234567": [
        {
            "rrn": "902184918231",
            "amount": 15000.0,
            "type": "pos_cash_out",
            "terminal_id": "2031PO09",
            "bank": "FirstBank / Moniepoint Agent",
            "status": "FAILED_DEBIT_UNSETTLED",
            "timestamp": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "resolution_action": "auto_reversal_initiated",
            "reversal_eta_hours": 12
        },
        {
            "rrn": "882190123910",
            "amount": 5000.0,
            "type": "interbank_transfer",
            "bank": "Zenith Bank to OPay",
            "status": "PENDING_BENEFICIARY_CREDIT",
            "timestamp": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "resolution_action": "nibss_session_queried",
            "reversal_eta_hours": 24
        }
    ],
    "default": [
        {
            "rrn": "771928374619",
            "amount": 20000.0,
            "type": "pos_withdrawal",
            "terminal_id": "2019OP01",
            "bank": "Access Bank / OPay Agent",
            "status": "FAILED_DEBIT_UNSETTLED",
            "timestamp": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "resolution_action": "auto_reversal_initiated",
            "reversal_eta_hours": 24
        }
    ]
}

MOCK_DISCO_METERS = {
    "01482910394": {
        "disco": "IBEDC (Ibadan Electricity Distribution Company)",
        "customer_name": "Adeyemi Babatunde",
        "last_payment_amount": 5000.0,
        "last_token": "4819-2041-8921-0021-9312",
        "units_kwh": 68.4,
        "token_status": "GENERATED_UNCLAIMED",
        "feeder": "Ring Road 33kV Feeder",
        "grid_status": "SUPPLIED"
    },
    "45190283719": {
        "disco": "KEDCO (Kano Electricity Distribution Company)",
        "customer_name": "Malam Musa Abdullahi",
        "last_payment_amount": 3000.0,
        "last_token": "7712-4091-1182-3901-5521",
        "units_kwh": 41.2,
        "token_status": "GENERATED_UNCLAIMED",
        "feeder": "Fagge 11kV Substation",
        "grid_status": "SUPPLIED"
    },
    "04192837461": {
        "disco": "EEDC (Enugu Electricity Distribution Company)",
        "customer_name": "Chidi Okonkwo",
        "last_payment_amount": 10000.0,
        "last_token": "6619-3320-1920-4491-0182",
        "units_kwh": 136.8,
        "token_status": "GENERATED_UNCLAIMED",
        "feeder": "Ogui Road 33kV Feeder",
        "grid_status": "SUPPLIED"
    },
    "default": {
        "disco": "AEDC (Abuja Electricity Distribution Company)",
        "customer_name": "Citizen Subscriber",
        "last_payment_amount": 7500.0,
        "last_token": "5129-8472-1094-3382-7719",
        "units_kwh": 102.5,
        "token_status": "GENERATED_UNCLAIMED",
        "feeder": "Gwarinpa Central 33kV",
        "grid_status": "SUPPLIED"
    }
}

ACTIVE_TICKETS = []

def resolve_banking_dispute(
    caller_id: str,
    intent: str,
    amount: float | None = None,
    account_number: str | None = None,
    rrn: str | None = None
) -> dict[str, Any]:
    """Resolves banking / POS dispute according to CBN E-Payment Guidelines."""
    tx_list = MOCK_BANK_TRANSACTIONS.get(caller_id, MOCK_BANK_TRANSACTIONS["default"])
    target_tx = tx_list[0] if tx_list else None
    
    ticket_id = f"DIS-BNK-{datetime.now().strftime('%y%m%d')}-{random.randint(1000, 9999)}"
    
    if target_tx and target_tx["status"] == "FAILED_DEBIT_UNSETTLED":
        action_type = "instant_auto_reversal_initiated"
        status = "RESOLVED_REVERSAL_TRIGGERED"
        sla_hours = 12
        details = {
            "rrn": target_tx["rrn"],
            "amount": target_tx["amount"],
            "terminal": target_tx.get("terminal_id", "AGENT-POS"),
            "cbn_policy": "CBN 2020 Consumer Protection Framework Sec 4.1",
            "message": f"NIBSS instant check confirmed failed transaction (RRN: {target_tx['rrn']}). Reversal of ₦{target_tx['amount']:,.2f} initiated back to your account."
        }
    else:
        action_type = "formal_cbn_dispute_ticket_logged"
        status = "PENDING_SETTLEMENT"
        sla_hours = 48
        resolved_amount = amount if amount else 10000.0
        details = {
            "ticket_number": ticket_id,
            "dispute_type": intent,
            "amount": resolved_amount,
            "sla": "48 Hours max per CBN SLA",
            "message": f"Formal dispute logged under reference {ticket_id}. Notification dispatched to originating bank settlement desk."
        }
        
    ticket_record = {
        "ticket_id": ticket_id,
        "domain": "banking_pos",
        "caller_id": caller_id,
        "status": status,
        "created_at": datetime.now().isoformat(),
        "action_type": action_type,
        "details": details
    }
    ACTIVE_TICKETS.insert(0, ticket_record)
    
    return {
        "action_type": action_type,
        "ticket_id": ticket_id,
        "status": status,
        "details": details,
        "sla_hours": sla_hours
    }

def resolve_disco_complaint(
    caller_id: str,
    intent: str,
    meter_number: str | None = None,
    disco_name: str | None = None
) -> dict[str, Any]:
    """Resolves DisCo / Electricity prepaid meter token complaints."""
    meter_data = MOCK_DISCO_METERS.get(meter_number, MOCK_DISCO_METERS.get("default"))
    ticket_id = f"DIS-PWR-{datetime.now().strftime('%y%m%d')}-{random.randint(1000, 9999)}"
    
    if "token" in intent.lower() or intent == "missing_meter_token":
        token = meter_data["last_token"]
        action_type = "sts_token_retrieved_and_voiced"
        status = "RESOLVED_TOKEN_DELIVERED"
        sla_hours = 0  # Instant resolution!
        details = {
            "meter_number": meter_number or "01482910394",
            "disco": meter_data["disco"],
            "token": token,
            "units_kwh": meter_data["units_kwh"],
            "amount_paid": meter_data["last_payment_amount"],
            "message": f"Your 20-digit electricity recharge token for meter {meter_number or '01482910394'} is: {token}. Valid for {meter_data['units_kwh']} kWh."
        }
    elif "tamper" in intent.lower() or "error" in intent.lower():
        action_type = "tamper_reset_code_generated"
        status = "RESOLVED_TAMPER_CODE_ISSUED"
        sla_hours = 0
        details = {
            "meter_number": meter_number or "01482910394",
            "reset_code": f"{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
            "instruction": "Key in the 20-digit tamper reset token, then press the blue/red enter key.",
            "message": "Tamper reset token generated successfully. Key into meter keypad to restore power."
        }
    else:
        # Outage / Feeder fault
        action_type = "feeder_fault_ticket_logged"
        status = "IN_PROGRESS_ENGINEERING_DISPATCH"
        sla_hours = 4
        details = {
            "feeder": meter_data.get("feeder", "Central 33kV Feeder"),
            "disco": meter_data.get("disco", "AEDC"),
            "status": "Fault detected on 33kV line. DisCo technical crew dispatched.",
            "message": "Power outage acknowledged on your local feeder. DisCo technical team on site."
        }
        
    ticket_record = {
        "ticket_id": ticket_id,
        "domain": "electricity_disco",
        "caller_id": caller_id,
        "status": status,
        "created_at": datetime.now().isoformat(),
        "action_type": action_type,
        "details": details
    }
    ACTIVE_TICKETS.insert(0, ticket_record)
    
    return {
        "action_type": action_type,
        "ticket_id": ticket_id,
        "status": status,
        "details": details,
        "sla_hours": sla_hours
    }

def resolve_general_inquiry(caller_id: str = "08031234567", intent: str = "greeting_or_inquiry") -> dict[str, Any]:
    """Handles general conversational inquiries and greetings."""
    ticket_id = f"SUP-INQ-{datetime.now().strftime('%y%m%d')}-{random.randint(100, 999)}"
    return {
        "action_type": "CONVERSATIONAL_SUPPORT",
        "ticket_id": ticket_id,
        "status": "SESSION_ACTIVE",
        "details": {
            "channel": "voice",
            "message": "MuryaAI active and listening."
        },
        "sla_hours": 0
    }

def get_recent_tickets(limit: int = 15) -> list[dict[str, Any]]:
    """Returns recent resolved/in-progress tickets for the admin telemetry view."""
    return ACTIVE_TICKETS[:limit]
