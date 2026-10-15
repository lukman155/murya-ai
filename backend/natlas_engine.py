"""N-ATLAS Language Reasoning Engine.
Connects with NCAIR1/N-ATLaS (Llama-3 8B Nigerian multilingual model) via HF Inference API,
local weights server, and high-fidelity deterministic fallback.
"""
import re
import json
import logging
import requests
from typing import Any
from backend.config import settings

logger = logging.getLogger(__name__)

# Language detection keywords and regex patterns
HAUSA_INDICATORS = [
    "kudi", "kudina", "kudin", "cire", "ba a", "banyi", "wutar", "wuta", "lantarki",
    "na tura", "amma", "ban samu", "sanadi", "na gode", "ina son", "don allah", "na biya",
    "token", "mitar", "mitarmu", "na pos", "katin", "banki", "mita", "gaba daya", "yau",
    "kuskure", "gyara", "danna", "asusu", "ungwarmu", "ban ga"
]

YORUBA_INDICATORS = [
    "owo", "owomi", "won fa", "yo", "sugbon", "mi o", "ina", "monamona", "ina wa",
    "mo san", "o wo", "token mi", "mo ra", "e jowo", "bawo ni", "ko wole", "pos",
    "ero", "banki", "eka", "ti baje", "fun mi", "dakun", "mo fe", "lana", "lo si",
    "adugbo", "akanti", "egberun", "meedogun", "mewaa", "gbigbe"
]

IGBO_INDICATORS = [
    "ego", "egom", "e weputara", "mana", "anaraghi", "m ya", "oku", "nepa", "electric",
    "kwụrụ", "chọrọ", "biko", "token m", "igwe", "pos", "enyemaka", "nke a", "akwụrụ",
    "ụgwọ", "eletrik", "ahụghị", "na-ada", "ụda", "dozie", "kemgbe", "ụnyaahụ",
    "banye", "kwuru", "onye", "kachifo", "kedụ", "anyi", "nwanne", "ezitere", "agara",
    "iwepu", "akauntu", "akaụntụ", "ebee", "nweta", "mita", "puku", "kụrụ afọ"
]

NIGERIAN_ENGLISH_INDICATORS = [
    "dey", "na", "wetin", "no enter", "dem debit", "my money", "pos", "token", "meter",
    "recharge", "disco", "abeg", "oya", "commot", "alert", "firstbank", "opay",
    "moniepoint", "light", "cut", "enter", "since", "yesterday", "token no drop",
    "hang", "machine", "balance", "don reduce", "spark", "whole street"
]

SYSTEM_PROMPTS = {
    "hausa": (
        "Kai ne mai taimaka wa jama'a a Najeriya mai amfani da N-ATLAS. "
        "Aikinka shine fahimtar koken kudi (POS, canja kudi) ko wutar lantarki (token na mita, matsalar wuta) "
        "sannan ka bayar da amsa cikin sauki da girmamawa a harshen Hausa."
    ),
    "yoruba": (
        "Iwo ni oluranlowo gbogbo gboo lori eto N-ATLAS fun awon omo orile-ede Naijiria. "
        "Ise re ni lati gbo awon ategun lori owo (POS, gbigbe owo) ati ina monamona (token mita, ina to ku) "
        "ki o si dahun pelu iwa rere ati imo to daju ni ede Yoruba."
    ),
    "igbo": (
        "Ị bụ onye enyemaka N-ATLAS maka ụmụ amaala Naịjirịa. "
        "Ọrụ gị bụ ịghọta mkpesa gbasara ego (POS, mbufe ego) na ọkụ eletrik (token mita, nsogbu ọkụ) "
        "ma zaa ajụjụ nke ọma n'asụsụ Igbo dị mfe ma dị nkwanye ùgwù."
    ),
    "nigerian_english": (
        "You be N-ATLAS citizen resolution assistant for Nigeria. "
        "Your work na to listen to complaints about money issues (POS debit without cash, transfer delay) "
        "or light matters (prepaid meter token not received, light cut) and give quick, respectful solution in natural Nigerian English / Pidgin."
    )
}

def contains_word_or_phrase(pattern: str, text: str) -> bool:
    if " " in pattern:
        return pattern in text
    return bool(re.search(rf"\b{re.escape(pattern)}\b", text))

def detect_language(text: str) -> tuple[str, float]:
    """Detects whether text is Hausa, Yoruba, Igbo, or Nigerian-accented English."""
    text_lower = text.lower()
    
    counts = {
        "hausa": sum(1 for kw in HAUSA_INDICATORS if contains_word_or_phrase(kw, text_lower)),
        "yoruba": sum(1 for kw in YORUBA_INDICATORS if contains_word_or_phrase(kw, text_lower)),
        "igbo": sum(1 for kw in IGBO_INDICATORS if contains_word_or_phrase(kw, text_lower)),
        "nigerian_english": sum(1 for kw in NIGERIAN_ENGLISH_INDICATORS if contains_word_or_phrase(kw, text_lower))
    }
    
    total = sum(counts.values())
    if total == 0:
        return ("nigerian_english", 0.75)
    
    best_lang = max(counts, key=counts.get)
    confidence = min(0.99, max(0.70, counts[best_lang] / total))
    return (best_lang, confidence)

def extract_entities_and_intent(text: str, language: str) -> dict[str, Any]:
    """Extracts domain, intent, meter numbers, amounts, RRNs from localized utterance."""
    text_lower = text.lower()
    
    # Check for amount in Naira (e.g., 5000, 15,000, 20k)
    amount = None
    amount_match = re.search(r'(?:₦|naira|n)?\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{3,7})(?:\s*k)?', text_lower)
    if amount_match:
        val_str = amount_match.group(1).replace(',', '')
        try:
            amount = float(val_str)
            if "k" in text_lower[amount_match.end():amount_match.end()+2]:
                amount *= 1000
        except ValueError:
            amount = None

    # Check for 11-digit meter number
    meter_match = re.search(r'\b([0-9]{11})\b', text)
    meter_number = meter_match.group(1) if meter_match else None
    
    # Check for RRN (12 digits)
    rrn_match = re.search(r'\b([0-9]{12})\b', text)
    rrn = rrn_match.group(1) if rrn_match else None

    # Check power tokens with word boundaries
    power_keywords = [
        "token", "meter", "mita", "mitar", "mitarmu", "wuta", "wutar", "ina", "monamona",
        "oku", "nepa", "disco", "ibedc", "kedco", "eedc", "aedc", "ekedc", "ikedc",
        "light", "transformer", "feeder", "units"
    ]
    is_power = any(contains_word_or_phrase(kw, text_lower) for kw in power_keywords) or (meter_number is not None)
    
    # Banking explicit overrides
    banking_strong = ["pos", "transfer", "tura", "gbigbe", "mbufe", "debit", "reversal", "alert", "asusu", "akanti", "akaụntụ"]
    if any(contains_word_or_phrase(b, text_lower) for b in banking_strong) and not any(contains_word_or_phrase(k, text_lower) for k in ["token", "meter", "mita", "feeder"]):
        is_power = False

    domain = "electricity_disco" if is_power else "banking_pos"
    
    # Determine intent
    if domain == "electricity_disco":
        if any(contains_word_or_phrase(w, text_lower) for w in ["tamper", "error", "kuskure", "koodu", "baje", "beeping", "reset"]):
            intent = "meter_tamper_error"
        elif any(contains_word_or_phrase(w, text_lower) for w in ["outage", "spark", "adugbo", "ungwarmu", "feeder", "transformer", "babu wuta", "ina ti ku", "kemgbe ụnyaahụ"]):
            intent = "power_outage_report"
        else:
            intent = "missing_meter_token"
    else:
        if any(contains_word_or_phrase(w, text_lower) for w in ["transfer", "tura", "gbigbe", "mbufe", "sent", "receive", "abokina", "nwanne", "alert"]):
            intent = "uncredited_transfer"
        elif any(contains_word_or_phrase(w, text_lower) for w in ["pos", "cire", "debit", "yo", "wepu", "dispense", "cash", "withdraw", "hang", "decline"]):
            intent = "failed_pos_debit"
        else:
            intent = "general_transaction_dispute"

    # Identify DisCo if present
    disco = "IBEDC"
    for d in ["aedc", "ibedc", "kedco", "ekedc", "ikedc", "eedc", "phed", "kaedco"]:
        if d in text_lower:
            disco = d.upper()
            break

    return {
        "domain": domain,
        "intent": intent,
        "amount": amount,
        "meter_number": meter_number,
        "rrn": rrn,
        "disco": disco,
        "urgency": "high" if (amount and amount >= 20000) or "token" in intent else "medium"
    }

def generate_local_response(
    language: str,
    domain: str,
    intent: str,
    resolution_data: dict[str, Any],
    caller_name: str = "Mallam / Madam"
) -> tuple[str, str]:
    """Generates localized spoken response in Yoruba, Hausa, Igbo, or Nigerian English,
    plus standard English translation for panel evaluation.
    """
    details = resolution_data.get("details", {})
    action_type = resolution_data.get("action_type", "")
    ticket_id = resolution_data.get("ticket_id", "REF-001")
    
    if domain == "electricity_disco":
        token = details.get("token", "5129-8472-1094-3382-7719")
        meter = details.get("meter_number", "01482910394")
        units = details.get("units_kwh", 68.4)
        
        if "token" in intent:
            if language == "hausa":
                resp_local = (
                    f"Sannu! Mun duba tsarin wutar lantarki na N-ATLAS. Lambar token din mitarku ({meter}) "
                    f"ita ce: {token}. Wannan zai ba ku raka'a {units} na wuta. "
                    f"Kuna iya danna wannan lambar a mitarku nan take. An aike muku da sakon SMS ma."
                )
            elif language == "yoruba":
                resp_local = (
                    f"E kaasan! A ti ye e wo lori ero N-ATLAS. Nomba token mita yin ({meter}) "
                    f"ni: {token}. Eleyi yoo fun yin ni yuniti {units} ina. "
                    f"E te nomba yi sinu mita yin bayi, ina yin yoo si tan. A ti fi SMS ranse si yin pelu."
                )
            elif language == "igbo":
                resp_local = (
                    f"Nnoo! Anyi elelela na N-ATLAS. Nọmba token mita gi ({meter}) "
                    f"bu: {token}. Nke a ga-enye gi unit {units} oku. "
                    f"Pịa nọmba a na mita gị ugbu a ka ọkụ bata. Anyị zitekwara gị ya na SMS."
                )
            else: # Nigerian English
                resp_local = (
                    f"Well done! We don check your meter record on N-ATLAS. Your 20-digit recharge token for meter ({meter}) "
                    f"na: {token}. E go give you {units} units of light. "
                    f"Make you punch am enter your meter keypad now. We don also send the token to your phone via SMS."
                )
            resp_en = f"Electricity token retrieved successfully for meter {meter}: {token} ({units} kWh). SMS confirmation dispatched."
            
        elif "tamper" in intent:
            code = details.get("reset_code", "4820-1928-3301-4491-0021")
            if language == "hausa":
                resp_local = f"Mun gano mitarku ta kulle kanta (tamper). Ga lambar bude mitar: {code}. Shigar da ita a jikin mita."
            elif language == "yoruba":
                resp_local = f"Mita yin ti tii pa. Eyi ni koodu lati tun se e: {code}. E te e sinu bọtini mita yin."
            elif language == "igbo":
                resp_local = f"Mita gi kpochiri onwe ya. Nke a bụ koodu iji mepee ya: {code}. Tinye ya na mita gị."
            else:
                resp_local = f"Your meter don lock (tamper error). Here is your reset code: {code}. Punch am into your keypad to clear the lock."
            resp_en = f"Meter tamper lock reset code issued: {code}. Enter into keypad to restore functionality."
        else:
            resp_local = f"Mun shigar da koken daukewar wutar lantarki. Lambar kokenku ita ce {ticket_id}. Ma'aikatan DisCo na kan aiki."
            resp_en = f"Power outage report logged under reference {ticket_id}. Local feeder maintenance crew dispatched."

    else:
        # Banking / POS dispute
        amount = details.get("amount", 15000.0)
        rrn = details.get("rrn", "902184918231")
        sla = resolution_data.get("sla_hours", 12)
        
        if "reversal" in action_type:
            if language == "hausa":
                resp_local = (
                    f"Mun duba tsarin NIBSS. Tabbatar da cewa an cire ₦{amount:,.0f} daga asusunku amma POS bai bayar da kudi ba. "
                    f"An riga an fara mayar da kudin (Auto-Reversal) karkashin lambar {ticket_id}. "
                    f"Za ku ga kudin a asusunku cikin sa'o'i {sla} kamar yadda dokar CBN ta tanada."
                )
            elif language == "yoruba":
                resp_local = (
                    f"A ti se iwadi lori NIBSS. O daju wipe a fa ₦{amount:,.0f} yo ninu akanti yin sugbon ero POS ko fun yin lowo. "
                    f"A ti bere eto idapada owo yin (Auto-Reversal) pelu nomba {ticket_id}. "
                    f"Owo yin yoo pada sinu akanti yin laarin wakati {sla} gege bi ofin CBN se so."
                )
            elif language == "igbo":
                resp_local = (
                    f"Anyi elelela na NIBSS. O doro anya na e weputara ₦{amount:,.0f} na akaụntụ gị mana POS enyeghị gị ego. "
                    f"Anyị ebidola nkwụghachi ego gị (Auto-Reversal) n'okpuru tiketi {ticket_id}. "
                    f"Ego gị ga-alaghachi n'ime awa {sla} dika iwu CBN siri kwuo."
                )
            else: # Nigerian English
                resp_local = (
                    f"We don check NIBSS network. E clear say dem debit you ₦{amount:,.0f} but the POS machine no drop cash. "
                    f"We don already trigger instant auto-reversal with reference {ticket_id}. "
                    f"Your money go enter your account back within {sla} hours strictly based on CBN policy."
                )
            resp_en = f"NIBSS verification confirmed failed POS debit of ₦{amount:,.2f}. Instant auto-reversal triggered under ticket {ticket_id} (SLA: {sla} hrs per CBN guidelines)."
        else:
            resp_local = (
                f"An rubuta kokenku na kudi (Ticket: {ticket_id}). Za a warware matsalar cikin sa'o'i {sla}."
            )
            resp_en = f"Formal banking dispute logged under reference {ticket_id}. Dispatched to settlement desk."

    return resp_local, resp_en

def query_natlas_llm(prompt: str, language: str) -> str | None:
    """Invokes live N-ATLAS model on Kaggle/vLLM (OpenAI-compatible) or Hugging Face."""
    api_url = settings.NATLAS_API_URL.strip()
    if not api_url:
        return None

    system_instruction = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["nigerian_english"])
    
    # 1. Handle OpenAI-compatible endpoints (Kaggle ngrok, vLLM, FastChat)
    if "chat/completions" in api_url or "ngrok" in api_url or "localhost" in api_url:
        target_url = api_url if "chat/completions" in api_url else f"{api_url.rstrip('/')}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "1",
            "User-Agent": "MuryaAI/1.0.0"
        }
        if settings.NATLAS_API_KEY:
            headers["Authorization"] = f"Bearer {settings.NATLAS_API_KEY}"
            
        payload = {
            "model": "NCAIR1/N-ATLaS",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 256,
            "temperature": 0.2
        }
        try:
            resp = requests.post(target_url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    logger.info(f"N-ATLAS GPU Live Inference Success from {target_url}")
                    return content.strip()
            logger.warning(f"Kaggle/OpenAI endpoint returned {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"Live GPU endpoint connection note: {e}")
            return None

    # 2. Handle Hugging Face Inference API
    elif "huggingface.co" in api_url and settings.NATLAS_API_KEY:
        headers = {"Authorization": f"Bearer {settings.NATLAS_API_KEY}"}
        payload = {
            "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{system_instruction}<|eot_id|><|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n",
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.3,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        try:
            resp = requests.post(api_url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                result = resp.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
        except Exception as e:
            logger.warning(f"HuggingFace inference note: {e}")

    return None

def test_endpoint_connection(api_url: str, api_key: str = "") -> dict[str, Any]:
    """Tests connectivity to a live N-ATLAS endpoint (ngrok, vLLM, or HuggingFace)."""
    import time
    t0 = time.time()
    api_url = (api_url or "").strip()
    if not api_url:
        return {"status": "offline", "message": "No GPU endpoint configured. Using local fallback."}
    
    target_url = api_url
    if "chat/completions" not in target_url and ("ngrok" in target_url or "localhost" in target_url or ("http" in target_url and "huggingface" not in target_url)):
        target_url = f"{target_url.rstrip('/')}/v1/chat/completions"
        
    headers = {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "1",
        "User-Agent": "MuryaAI/1.0.0"
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        
    payload = {
        "model": "NCAIR1/N-ATLaS",
        "messages": [
            {"role": "user", "content": "Sannu"}
        ],
        "max_tokens": 15
    }
    
    try:
        resp = requests.post(target_url, headers=headers, json=payload, timeout=8)
        latency_ms = round((time.time() - t0) * 1000, 1)
        if resp.status_code == 200:
            data = resp.json()
            reply = ""
            if "choices" in data and len(data["choices"]) > 0:
                reply = data["choices"][0]["message"].get("content", "")
            return {
                "status": "online",
                "target_url": target_url,
                "latency_ms": latency_ms,
                "message": f"Connected to live GPU! Latency: {latency_ms}ms",
                "sample_reply": reply.strip()
            }
        elif resp.status_code == 404:
            return {
                "status": "offline",
                "target_url": target_url,
                "message": "ngrok tunnel is offline or expired (ERR_NGROK_3200 / 404). Check Kaggle notebook."
            }
        else:
            return {
                "status": "error",
                "status_code": resp.status_code,
                "target_url": target_url,
                "message": f"Endpoint returned HTTP {resp.status_code}: {resp.text[:120]}"
            }
    except Exception as e:
        return {
            "status": "offline",
            "target_url": target_url,
            "message": f"Connection unreachable ({type(e).__name__}). Using local fallback."
        }
