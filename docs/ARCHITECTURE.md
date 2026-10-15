# MuryaAI System Architecture & N-ATLAS Integration

**Project Name:** MuryaAI (N-VoiceCare)  
**Track:** National AI Innovation Challenge (NAIC) 2026 – Innovation & Enterprise Track  
**Problem Statement:** PS2: Voice-First Access  
**Foundational Model:** N-ATLAS (`NCAIR1/N-ATLaS`, Llama-3 8B Multilingual Nigerian LLM + ASR)  

---

## 1. Executive Summary

MuryaAI is an omnichannel, voice-first citizen resolution infrastructure engineered to eliminate the severe language and digital literacy barrier for over 100 million Nigerians. By interfacing with **N-ATLAS** (Nigeria's foundational multilingual language model), MuryaAI allows ordinary citizens—ranging from market traders in Kano and Onitsha to rural artisans in Oyo—to resolve **failed POS banking transactions** and **missing electricity prepaid meter tokens** by simply speaking in **Hausa, Yoruba, Igbo, or Nigerian English/Pidgin** over standard 2G phone calls (IVR) or WhatsApp voice notes.

---

## 2. End-to-End System Architecture

```mermaid
flowchart TD
    subgraph Channels["Low-Barrier Ingress Channels (Zero Smartphone Required)"]
        PSTN["Basic 2G Feature Phone (PSTN / Telco Voice)"] --> AT["Africa's Talking / Twilio SIP Voice Trunk"]
        WAPP["WhatsApp Audio Voice Note (.ogg)"] --> WA_API["WhatsApp Cloud API Webhook"]
        WEB["Browser Audio / Feature Web App"] --> WEB_API["FastAPI Web Audio Ingestion"]
    end

    subgraph AudioPipeline["Audio Ingestion & Normalization"]
        AT --> STREAM["Audio Stream Ingest (16kHz PCM / WAV / OGG)"]
        WA_API --> STREAM
        WEB_API --> STREAM
    end

    subgraph NATLAS_Core["N-ATLAS Multilingual Engine (NCAIR / NITDA)"]
        STREAM --> ASR["N-ATLAS ASR (Speech-to-Text)"]
        ASR --> DIALECT["Dialect Identification & Confidence Normalizer"]
        DIALECT --> LLM["N-ATLAS Multilingual Model (NCAIR1/N-ATLaS)"]
        LLM --> INTENT["Entity & Intent Extractor (JSON Structured Output)"]
    end

    subgraph DomainServices["National Infrastructure Connectors"]
        INTENT --> ROUTE{Domain Router}
        ROUTE -->|"Banking / POS Dispute"| NIBSS["NIBSS Instant Payment & CBN Dispute Core"]
        ROUTE -->|"DisCo / Prepaid Token"| DISCO["DisCo STS Token Gateway (AEDC, IBEDC, KEDCO, EEDC)"]
    end

    subgraph Resolution["Resolution Synthesis & Vocal Delivery"]
        NIBSS --> ACTION["Auto-Reversal / Ticket Generation"]
        DISCO --> TOKEN["20-Digit STS Token Recovery / Reset Code"]
        ACTION --> LOCAL_NLG["N-ATLAS Vernacular NLG (Hausa / Yoruba / Igbo / Pidgin)"]
        TOKEN --> LOCAL_NLG
        LOCAL_NLG --> TTS["Multilingual TTS Voice Synthesizer"]
        TTS --> AUDIO_OUT["Audio Stream Returned to Caller"]
        AUDIO_OUT --> PSTN
        AUDIO_OUT --> WAPP
        AUDIO_OUT --> WEB
    end
```

---

## 3. Strict Compliance with PS2 Delivery Channel Mandate

> **Evaluation Requirement:** *"Delivery channel must not require a high-end smartphone or laptop."*

MuryaAI directly satisfies this requirement across two primary public-facing channels:
1. **Interactive Voice Response (IVR) via PSTN / 2G Telephony Trunks:**
   - A citizen dials a dedicated local hotline (e.g. `0800-MURYAAI` or a standard MTN/Airtel/Glo number).
   - Operable on basic feature phones (Nokia 105, Itel, Tecno button phones).
   - Audio is streamed in real-time through SIP trunks powered by Africa's Talking / Twilio voice webhooks.
2. **WhatsApp Voice Notes:**
   - WhatsApp is the default communication utility across emerging markets in Nigeria even on low-cost ₦15,000 Android devices with 3G connections.
   - The user holds the microphone icon, speaks in their mother tongue, and receives a spoken audio reply and SMS text receipt.

---

## 4. Sequence Flow: Failed POS Debit Auto-Reversal

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Caller (Hausa / Yoruba / Igbo)
    participant IVR as Africa's Talking / Twilio IVR
    participant NATLAS_ASR as N-ATLAS ASR
    participant NATLAS_LLM as N-ATLAS Reasoning Engine
    participant NIBSS as Core Banking / NIBSS Gateway
    participant TTS as Vernacular TTS

    Citizen->>IVR: Dials 0800-MURYAAI and speaks: "An cire min kudi naira dubu goma sha biyar a POS amma ban samu kudi ba"
    IVR->>NATLAS_ASR: Transmits audio payload (16kHz PCM)
    NATLAS_ASR-->>NATLAS_LLM: Transcribed Text: "An cire min kudi naira dubu goma sha biyar..."
    NATLAS_LLM->>NATLAS_LLM: Detects Language (Hausa 99%), extracts Intent: failed_pos_debit, Amount: ₦15,000
    NATLAS_LLM->>NIBSS: Queries terminal RRN & unsettled debit status for caller ID
    NIBSS-->>NATLAS_LLM: Status: FAILED_DEBIT_UNSETTLED. Auto-reversal approved under Ticket DIS-BNK-2026-6077 (SLA: 12 hrs)
    NATLAS_LLM->>NATLAS_LLM: Generates localized spoken response in native Hausa
    NATLAS_LLM->>TTS: Synthesizes Hausa speech
    TTS-->>IVR: Streams vocal response: "Mun duba tsarin NIBSS. Tabbatar da cewa an cire ₦15,000... An riga an fara mayar da kudin..."
    IVR-->>Citizen: Caller hears natural Hausa spoken resolution and receives SMS confirmation
```

---

## 5. Sequence Flow: DisCo Electricity Token Recovery

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Caller (Yoruba Speaker)
    participant Ingress as WhatsApp / Voice Webhook
    participant NATLAS as N-ATLAS Pipeline
    participant DisCo as DisCo STS Gateway (IBEDC)
    participant TTS as Vernacular TTS

    Citizen->>Ingress: Speaks: "Mo ra owo ina naira egberun marun lori mita mi 01482910394 sugbon mi o ri token gba"
    Ingress->>NATLAS: Audio Stream
    NATLAS->>NATLAS: ASR Transcription -> Yoruba detected (99%) -> Intent: missing_meter_token -> Meter: 01482910394
    NATLAS->>DisCo: Query STS token for meter 01482910394
    DisCo-->>NATLAS: Token Found: 4819-2041-8921-0021-9312 (68.4 kWh units)
    NATLAS->>TTS: Synthesizes Yoruba speech with clear digit pacing
    TTS-->>Ingress: Audio Stream: "E kaasan! Nomba token mita yin ni: 4819-2041-8921-0021-9312..."
    Ingress-->>Citizen: Caller hears their 20-digit token voiced slowly in Yoruba + SMS receipt
```

---

## 6. Regulatory & Security Architecture

1. **Central Bank of Nigeria (CBN) Consumer Protection Framework:**
   - Adheres to CBN circulars on failed electronic payment transactions (instant reversal SLA).
   - Generates deterministic audit reference logs (`DIS-BNK-YYMMDD-XXXX`).
2. **Nigeria Data Protection Act (NDPA) 2023 Compliance:**
   - Caller phone numbers are pseudonymized in public logs.
   - Zero retention of raw biometric voiceprints beyond the active resolution session.
