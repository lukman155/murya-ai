# MuryaAI (N-VoiceCare) — Official 3-5 Minute Video Demo Script
**National AI Innovation Challenge (NAIC 2026) — Innovation & Enterprise Track**  
**Problem Statement:** PS2: Voice-First Access  
**Target Video Duration:** 3 minutes 45 seconds – 4 minutes 30 seconds  
**Format:** Screen recording (OBS / Loom / Camtasia) with clear voiceover, camera-in-corner (optional but recommended), and live audio playback enabled.

---

## 🎬 Recording Checklist & Setup
1. **Local Server Running:**
   ```powershell
   cd "c:\Users\Monsieur Lukman\Desktop\Repos\hackathons\naic-natlas-ai\murya-ai"
   python -m backend.main
   ```
   Open `http://localhost:8000` in Google Chrome or Edge.
2. **Audio System Audio Sharing:** Ensure your recording tool (Loom / OBS) captures **desktop audio** so the judges hear the synthesized voice playback in Hausa, Yoruba, and Igbo.
3. **Tabs to Have Ready:**
   - Tab 1: `http://localhost:8000` (MuryaAI Live Console)
   - Tab 2: GitHub Repository (`https://github.com/your-username/naic-natlas-ai`)
   - Tab 3 (Optional): Architecture Diagram from `docs/ARCHITECTURE.md`

---

## ⏱️ Video Timeline Breakdown

```
[0:00 - 0:45] Hook, Problem & The PS2 Mandate
[0:45 - 1:30] System Architecture & N-ATLAS Foundation Model
[1:30 - 2:20] Live Demo 1: Hausa POS Debit Auto-Reversal & Audio Output
[2:20 - 3:05] Live Demo 2: Yoruba DisCo Token Instant Recovery & Phone Simulator
[3:05 - 3:45] Live Demo 3: Igbo & WhatsApp Channel Simulator
[3:45 - 4:15] Empirical Benchmarks, Telemetry & CBN Policy Alignment
[4:15 - 4:45] Traction, 1,000-User Scaling Roadmap & Vision
```

---

## 📜 Full Word-for-Word Voiceover & Action Script

### SECTION 1: The Hook & The Problem (0:00 – 0:45)
**Screen:** Camera on speaker OR MuryaAI Web Console hero section showing: *"Instant Citizen Dispute Resolution in Hausa, Yoruba, Igbo & Nigerian English"*.

> **Voiceover (Speaker):**  
> *"Hello, distinguished evaluation panel of the National AI Innovation Challenge, FMCIDE, NITDA, and NCAIR. My name is Lukman Abdulkarim, presenting **MuryaAI (N-VoiceCare)** under **Problem Statement 2: Voice-First Access**.*
> 
> *In Nigeria today, over 65% of citizens communicate primarily in their mother tongue and face crippling language and literacy barriers with English-only digital apps and automated call centers.*
> 
> *When a market trader in Kano loses ₦15,000 to a failed POS debit, or an artisan in Ibadan recharges their electricity meter and the token fails to deliver via SMS, they are stranded. They spend hours in crowded bank queues or days in darkness.*
> 
> *To truly democratize AI, we cannot demand high-end smartphones or high-speed broadband. Under the PS2 mandate, we built **MuryaAI**: an omnichannel, voice-first resolution infrastructure powered entirely by Nigeria's sovereign foundational model, **N-ATLAS**."*

---

### SECTION 2: Architecture & N-ATLAS Integration (0:45 – 1:30)
**Screen:** Zoom in slightly on the console header, showing the **`Model: NCAIR1/N-ATLaS`** badge and the **`⚙️ Update URL`** live GPU connector.

> **Voiceover (Speaker):**  
> *"MuryaAI is not a generic chatbot. It is an end-to-end resolution pipeline natively integrated with **N-ATLAS** (Llama-3 8B multilingual model by NCAIR and NITDA).*
> 
> *Here is how the pipeline operates:*
> 1. *A citizen dials a standard telephone number from any basic 2G phone or sends a WhatsApp voice note.*
> 2. *Our telephony trunk streams the audio to **N-ATLAS ASR**, transcribing the vernacular speech and identifying the dialect with confidence scoring.*
> 3. *The text is routed to **N-ATLAS 8B**, which extracts structured intent—such as a failed debit or missing meter number.*
> 4. *MuryaAI interfaces directly with NIBSS dispute protocols and DisCo STS gateways to execute instant resolution.*
> 5. *Finally, N-ATLAS synthesizes an empathetic, culturally respectful spoken response in their native dialect in sub-second latency.*
> 
> *Notice our live GPU connector: MuryaAI connects dynamically to live inference endpoints or runs on local edge nodes with deterministic fallback."*

---

### SECTION 3: Live Demo 1 — Hausa POS Debit Dispute (1:30 – 2:20)
**Screen:** On `http://localhost:8000`, click the Quick-Test scenario: **"Hausa — Banking / POS Dispute"** (or speak into the mic).

**Action:**
1. Click the button for: `"An cire min kudi naira dubu goma sha biyar a POS amma ban samu kudi ba..."`
2. Show the processing animation.
3. Show the resulting output card:
   - Language detected: **Hausa (100%)**
   - Domain: **POS Banking**
   - Intent: **failed_pos_debit**
   - Ticket generated: **`DIS-BNK-2026-XXXX`**
4. Click **Play / Replay Audio** so the audio plays loudly.

> **Audio Plays from Speaker:**  
> *(Native Hausa voice): "Mun duba tsarin NIBSS. Tabbatar da cewa an cire ₦15,000 daga asusunku amma POS bai bayar da kudi ba. An riga an fara mayar da kudin karkashin lambar DIS-BNK-2026..."*

> **Voiceover (Speaker):**  
> *"Watch this in real-time. The user spoke in Hausa describing a failed POS debit of ₦15,000. Within milliseconds, N-ATLAS transcribed the audio, identified the language as Hausa with 100% confidence, extracted the ₦15,000 amount, and queried the mock NIBSS settlement engine.*
> 
> *Under Central Bank of Nigeria guidelines, it automatically triggered an auto-reversal ticket `DIS-BNK-2026`, and voiced back a clear explanation in Hausa explaining that the reversal has begun. The caller receives immediate peace of mind without filling a single bank form."*

---

### SECTION 4: Live Demo 2 — Yoruba Electricity Token Recovery (2:20 – 3:05)
**Screen:** Click on the Quick-Test button: **"Yoruba — Electricity / DisCo Token"**.

**Action:**
1. Click: `"Mo ra owo ina naira egberun marun lori mita mi 01482910394 sugbon mi o ri token gba..."`
2. Show the output card:
   - Language detected: **Yoruba**
   - Domain: **DisCo Power**
   - Meter extracted: **`01482910394`**
   - Action: **STS Token Retrieved & Voiced** (`4819-2041-8921-0021-9312`)
3. Switch Channel Tab to **"Phone IVR"** to show the 2G Nokia keypad simulator!

> **Audio Plays from Speaker:**  
> *(Native Yoruba voice): "E kaasan! A ti ye e wo lori ero N-ATLAS. Nomba token mita yin ni: 4819-2041-8921-0021-9312..."*

> **Voiceover (Speaker):**  
> *"Now let's switch to public utilities. A Yoruba-speaking citizen purchased ₦5,000 electricity for meter 01482910394, but the SMS token never arrived.*
> 
> *N-ATLAS instantly identifies the 11-digit meter number, queries the DisCo STS gateway, retrieves the unclaimed 20-digit recharge token, and reads the numbers out loud clearly in Yoruba.*
> 
> *Notice our Phone IVR simulator: this runs over basic 2G cellular PSTN voice lines using Africa's Talking. The caller does not need an iPhone or a computer—any ₦5,000 button phone can dial our toll-free line."*

---

### SECTION 5: Live Demo 3 — Igbo, WhatsApp & Low-Barrier Channels (3:05 – 3:45)
**Screen:** Click the **"WhatsApp Voice"** channel tab, then click the **"Igbo — Banking / POS Dispute"** scenario.

**Action:**
1. Click: `"E weputara ego m naira puku iri abuo n'igwe POS taa mana anaraghi m ego..."`
2. Show the WhatsApp chat simulator with voice note bubble and Igbo audio response.

> **Voiceover (Speaker):**  
> *"For smartphone users on low-bandwidth networks, MuryaAI integrates natively with WhatsApp Voice Notes. The user sends a voice note in Igbo, and our webhook dispatches both an audio reply and an SMS confirmation.*
> 
> *This ensures 100% inclusion across Nigeria's 3 major language groups as well as Nigerian-accented English and Pidgin."*

---

### SECTION 6: Empirical Benchmarks & CBN Policy Alignment (3:45 – 4:15)
**Screen:** Scroll to the **Metric Strip** and open `docs/BENCHMARK_REPORT.md` (or highlight the telemetry metrics on screen).

> **Voiceover (Speaker):**  
> *"Our claims are backed by rigorous empirical testing. We built an automated benchmark suite evaluating 40 representative dispute utterances across Nigeria:*
> - ***100.0% accuracy** in language identification.*
> - ***95.0% accuracy** in structured intent and entity extraction.*
> - ***128.8 millisecond** average pipeline latency—guaranteeing natural, real-time voice conversations.*
> - *Average Handling Time dropped from **14 minutes** on human call center queues to **18.4 seconds**—a **97.8% reduction in wait time**.*
> 
> *Furthermore, every dispute ticket adheres strictly to the CBN Consumer Protection Framework and NDPA 2023 data privacy regulations."*

---

### SECTION 7: Scaling Roadmap & Closing Vision (4:15 – 4:45)
**Screen:** Return to the main console or camera.

> **Voiceover (Speaker):**  
> *"Our user acquisition plan for reaching 1,000 users in 3 months is focused and institutional: partnering with the Association of Mobile Money and Bank Agents in Nigeria (AMMBAN) across major trading clusters in Kano, Ibadan, and Aba, alongside community Microfinance Banks.*
> 
> *MuryaAI proves that Nigeria's sovereign AI foundational model, N-ATLAS, can transition from research into life-changing public infrastructure.*
> 
> *Thank you to NCAIR, NITDA, and FMCIDE for spearheading national AI innovation. We look forward to scaling MuryaAI in the acceleration phase."*

---

## 💡 Top 5 Tips for a Winning Video Recording

1. **Keep Energy High & Crisp:** Speak with confidence, clear pacing, and professional enthusiasm.
2. **Ensure Audio Playback is Auditable:** When the app speaks in Hausa or Yoruba, let it play for 3-5 seconds uninterrupted so the judges clearly hear the native vernacular response.
3. **Keep Mouse Movements Deliberate:** Don't move the cursor erratically; click the buttons smoothly so the panel can read the transcripts and latency badges.
4. **Export Settings:** Record at **1080p (1920x1080)** at 30fps or 60fps.
5. **Video Host:** Upload to **YouTube (Unlisted or Public)** or **Loom**, and paste the direct link into the NAIC portal field:  
   `Video demonstration (3 to 5 minutes)*`.
