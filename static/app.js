/**
 * MuryaAI Frontend Client Logic
 * Powers live microphone recording, sample test dispatch,
 * channel simulation (Phone IVR & WhatsApp), and N-ATLAS inspection.
 */

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let currentChannel = "web";

document.addEventListener("DOMContentLoaded", () => {
    initSampleButtons();
    initTelemetry();
    initEventListeners();
    initEndpointConfig();
});

// Load quick test scenarios from backend
async function initSampleButtons() {
    const container = document.getElementById("sample-buttons-container");
    try {
        const res = await fetch("/api/samples");
        const samples = await res.json();
        container.innerHTML = "";
        
        samples.forEach(s => {
            const btn = document.createElement("button");
            btn.className = "text-left p-2.5 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-emerald-600/50 hover:bg-slate-900 transition flex flex-col justify-between group";
            btn.innerHTML = `
                <div class="flex items-center justify-between w-full mb-1">
                    <span class="text-xs font-bold text-emerald-400 group-hover:text-emerald-300">${s.language}</span>
                    <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">${s.domain.split('/')[0].trim()}</span>
                </div>
                <p class="text-xs text-slate-300 font-medium line-clamp-1">"${s.prompt}"</p>
                <span class="text-[10px] text-slate-500 mt-1 line-clamp-1 italic">${s.english}</span>
            `;
            btn.onclick = () => runSampleTest(s);
            container.appendChild(btn);
        });
    } catch (e) {
        console.error("Failed to load benchmark samples:", e);
    }
}

// Fetch live telemetry metrics and tickets
async function initTelemetry() {
    try {
        const res = await fetch("/api/telemetry");
        const data = await res.json();
        
        document.getElementById("stat-aht").innerText = `${data.average_handling_time_sec}s`;
        document.getElementById("stat-rate").innerText = `${data.resolution_rate_percent}%`;
        
        // Render recent tickets list
        const ticketsList = document.getElementById("recent-tickets-list");
        ticketsList.innerHTML = "";
        
        (data.recent_tickets || []).slice(0, 6).forEach(t => {
            const row = document.createElement("div");
            row.className = "p-2 rounded-lg bg-slate-950/70 border border-slate-800/80 flex items-center justify-between";
            const domainBadge = t.domain === "banking_pos" ? "POS / Bank" : "DisCo Power";
            row.innerHTML = `
                <div class="flex items-center space-x-2">
                    <span class="w-1.5 h-1.5 rounded-full ${t.status.includes('RESOLVED') ? 'bg-emerald-400' : 'bg-amber-400'}"></span>
                    <span class="font-mono text-emerald-300 font-bold">${t.ticket_id}</span>
                    <span class="text-slate-400 text-[11px]">${domainBadge}</span>
                </div>
                <span class="text-[11px] text-slate-400">${t.status.split('_')[0]}</span>
            `;
            ticketsList.appendChild(row);
        });
    } catch (e) {
        console.error("Telemetry fetch error:", e);
    }
}

function initEventListeners() {
    const btnRecord = document.getElementById("btn-record");
    btnRecord.addEventListener("click", toggleRecording);
    
    document.getElementById("btn-submit-text").addEventListener("click", () => {
        const text = document.getElementById("manual-text-input").value.trim();
        if (text) submitTextQuery(text);
    });

    document.getElementById("manual-text-input").addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            const text = e.target.value.trim();
            if (text) submitTextQuery(text);
        }
    });

    // Channel Switching Tabs
    const tabs = {
        "tab-web": "web",
        "tab-ivr": "ivr_phone",
        "tab-wa": "whatsapp_voice"
    };

    Object.keys(tabs).forEach(tabId => {
        document.getElementById(tabId).addEventListener("click", (e) => {
            document.querySelectorAll(".channel-tab").forEach(t => {
                t.classList.remove("active", "text-emerald-400", "bg-slate-800");
                t.classList.add("text-slate-400");
            });
            e.target.classList.add("active", "text-emerald-400", "bg-slate-800");
            e.target.classList.remove("text-slate-400");
            currentChannel = tabs[tabId];
            updateChannelSimulator(currentChannel);
        });
    });

    document.getElementById("btn-replay-audio").addEventListener("click", () => {
        const audio = document.getElementById("audio-player");
        if (audio && audio.src) {
            audio.currentTime = 0;
            audio.play();
        }
    });

    // Endpoint Configuration Modal Listeners
    document.getElementById("btn-open-endpoint-modal").addEventListener("click", openEndpointModal);
    document.getElementById("btn-close-modal").addEventListener("click", closeEndpointModal);
    document.getElementById("btn-cancel-modal").addEventListener("click", closeEndpointModal);
    document.getElementById("btn-test-connection").addEventListener("click", testEndpointConnection);
    document.getElementById("btn-save-endpoint").addEventListener("click", saveEndpointConfig);
}

function updateChannelSimulator(channel) {
    const simContainer = document.getElementById("sim-container");
    const simTitle = document.getElementById("sim-title");
    const simContent = document.getElementById("sim-content");

    if (channel === "web") {
        simContainer.classList.add("hidden");
        return;
    }

    simContainer.classList.remove("hidden");
    if (channel === "ivr_phone") {
        simTitle.innerText = "Phone IVR Simulator (Africa's Talking / Twilio 2G Trunk)";
        simContent.innerHTML = `
            <div class="feature-phone-body">
                <div class="feature-phone-screen space-y-2">
                    <div class="flex justify-between text-[10px] text-emerald-300 border-b border-emerald-700/60 pb-1">
                        <span>CALLING: 0800-MURYAAI</span>
                        <span>00:18</span>
                    </div>
                    <div class="text-[11px] text-emerald-200">
                        &gt; N-ATLAS IVR Bot: "Sannu! E kaasan! Nnoo! Please speak your complaint..."
                    </div>
                    <div class="text-[10px] text-emerald-400/80 animate-pulse">
                        ● Audio stream connected via SIP / PSTN
                    </div>
                </div>
                <div class="text-center text-[10px] text-slate-400 mt-2">
                    Zero smartphone needed. Tested on basic Nokia 105 & Itel phones.
                </div>
            </div>
        `;
    } else if (channel === "whatsapp_voice") {
        simTitle.innerText = "WhatsApp Voice Notes Simulator (Cloud API)";
        simContent.innerHTML = `
            <div class="max-w-sm mx-auto space-y-3 p-3 bg-slate-900 rounded-xl border border-slate-800">
                <div class="wa-bubble-incoming space-y-1">
                    <div class="text-[10px] text-teal-400 font-bold">Caller (0803***567)</div>
                    <div class="flex items-center space-x-2 text-xs">
                        <span class="w-6 h-6 rounded-full bg-slate-700 flex items-center justify-center">▶</span>
                        <span>Voice Message (0:07)</span>
                    </div>
                </div>
                <div class="wa-bubble-outgoing space-y-1">
                    <div class="text-[10px] text-emerald-300 font-bold">MuryaAI N-ATLAS Agent</div>
                    <div class="flex items-center space-x-2 text-xs">
                        <span class="w-6 h-6 rounded-full bg-emerald-600 flex items-center justify-center">▶</span>
                        <span>Localized Voice Resolution (0:09)</span>
                    </div>
                </div>
            </div>
        `;
    }
}

// Toggle browser audio recording
async function toggleRecording() {
    const btn = document.getElementById("btn-record");
    const statusText = document.getElementById("record-status");
    const wave = document.getElementById("mic-wave");

    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) audioChunks.push(e.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = () => {
                    const base64Audio = reader.result;
                    submitVoiceQuery(base64Audio);
                };
            };

            mediaRecorder.start();
            isRecording = true;
            btn.classList.add("ring-red-500/50", "from-red-600", "to-rose-500");
            btn.classList.remove("from-emerald-600", "to-teal-500");
            statusText.innerText = "Listening... Speak your complaint now (Click to stop)";
            wave.classList.add("recording-active");
            wave.style.opacity = "1";
        } catch (err) {
            console.warn("Microphone not permitted or unavailable, falling back to Web Speech or simulation:", err);
            statusText.innerText = "Mic blocked. Click any test scenario button below to test!";
        }
    } else {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
        }
        isRecording = false;
        btn.classList.remove("ring-red-500/50", "from-red-600", "to-rose-500");
        btn.classList.add("from-emerald-600", "to-teal-500");
        statusText.innerText = "Processing with N-ATLAS pipeline...";
        wave.classList.remove("recording-active");
        wave.style.opacity = "0.4";
    }
}

// Execute sample test
async function runSampleTest(sample) {
    document.getElementById("manual-text-input").value = sample.prompt;
    submitTextQuery(sample.prompt, sample.id);
}

// Send text query to API
async function submitTextQuery(text, sampleHint = null) {
    setLoadingState(true);
    const selectedLang = document.getElementById("lang-select").value;
    
    try {
        const payload = {
            text: text,
            language: selectedLang === "auto" ? null : selectedLang,
            channel: currentChannel,
            caller_id: "08031234567"
        };
        
        const res = await fetch("/api/resolve/text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        renderResolutionOutput(data);
    } catch (err) {
        console.error("Resolution error:", err);
    } finally {
        setLoadingState(false);
    }
}

// Send voice query to API
async function submitVoiceQuery(base64Audio) {
    setLoadingState(true);
    const selectedLang = document.getElementById("lang-select").value;

    try {
        const payload = {
            audio_base64: base64Audio,
            audio_format: "audio/webm",
            language: selectedLang === "auto" ? null : selectedLang,
            channel: currentChannel,
            caller_id: "08031234567"
        };

        const res = await fetch("/api/resolve/voice", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        renderResolutionOutput(data);
    } catch (err) {
        console.error("Voice resolution error:", err);
    } finally {
        setLoadingState(false);
    }
}

function renderResolutionOutput(data) {
    // 1. Badges
    const badgeLang = document.getElementById("badge-lang");
    badgeLang.innerText = `${data.detected_language} (${Math.round(data.language_confidence * 100)}%)`;
    
    const badgeDomain = document.getElementById("badge-domain");
    badgeDomain.innerText = data.entities.domain === "banking_pos" ? "POS Banking" : "DisCo Power";

    const badgeIntent = document.getElementById("badge-intent");
    badgeIntent.innerText = data.entities.intent.replace(/_/g, " ");

    // 2. Latency
    document.getElementById("out-latency").innerText = `${data.latency_ms.total_ms}ms (${data.natlas_engine_used})`;

    // 3. Transcript
    document.getElementById("out-transcript").innerText = `"${data.transcription}"`;

    // 4. Localized Response
    document.getElementById("out-response-local").innerText = data.response_text_local;

    // 5. English Translation
    document.getElementById("out-response-en").innerText = data.response_text_en;

    // 6. Action and Ticket
    document.getElementById("ticket-id").innerText = data.resolution_action.ticket_id;
    document.getElementById("ticket-status").innerText = data.resolution_action.status;
    document.getElementById("ticket-action").innerText = data.resolution_action.action_type;

    // 7. Audio Playback
    const audioPlayer = document.getElementById("audio-player");
    const btnReplay = document.getElementById("btn-replay-audio");

    if (data.audio_base64) {
        audioPlayer.src = data.audio_base64;
        audioPlayer.classList.remove("hidden");
        btnReplay.classList.remove("hidden");
        audioPlayer.play().catch(e => console.log("Autoplay note:", e));
    }

    // Refresh telemetry
    initTelemetry();
}

function setLoadingState(loading) {
    const statusText = document.getElementById("record-status");
    if (loading) {
        statusText.innerText = "Analyzing with N-ATLAS (ASR -> Reasoning -> NIBSS/DisCo)...";
    } else {
        statusText.innerText = "Click to Speak in Hausa, Yoruba, Igbo, or Pidgin";
    }
}

// -----------------------------------------------------------------------------
// N-ATLAS GPU Endpoint Configuration Modal & Live Connectivity
// -----------------------------------------------------------------------------

async function initEndpointConfig() {
    try {
        const res = await fetch("/api/config/endpoint");
        const data = await res.json();
        updateEndpointBadge(data);
        const urlInput = document.getElementById("modal-input-url");
        if (urlInput && data.active_api_url) {
            urlInput.value = data.active_api_url;
        }
    } catch (e) {
        console.warn("Could not fetch endpoint config:", e);
        updateEndpointBadge({ status: "offline", message: "Local fallback mode active" });
    }
}

function updateEndpointBadge(data) {
    const dot = document.getElementById("endpoint-status-dot");
    const label = document.getElementById("endpoint-status-label");
    if (!dot || !label) return;

    if (data.status === "online") {
        dot.className = "w-2 h-2 rounded-full bg-emerald-400 animate-pulse";
        label.className = "font-medium text-emerald-300";
        label.innerText = `GPU: Live (${data.latency_ms || 0}ms)`;
    } else if (data.status === "offline") {
        dot.className = "w-2 h-2 rounded-full bg-amber-400";
        label.className = "font-medium text-amber-300";
        label.innerText = "GPU: Local Fallback";
    } else {
        dot.className = "w-2 h-2 rounded-full bg-rose-400";
        label.className = "font-medium text-rose-300";
        label.innerText = "GPU: Connection Error";
    }

    const badge = document.getElementById("modal-status-badge");
    const msg = document.getElementById("modal-status-msg");
    if (badge && msg) {
        badge.innerText = data.status.toUpperCase();
        badge.className = data.status === "online" ? "font-bold text-emerald-400" : (data.status === "offline" ? "font-bold text-amber-400" : "font-bold text-rose-400");
        msg.innerText = data.message || "Active";
    }
}

function openEndpointModal() {
    const modal = document.getElementById("endpoint-modal");
    modal.classList.remove("hidden");
    // Trigger live check on open
    initEndpointConfig();
}

function closeEndpointModal() {
    const modal = document.getElementById("endpoint-modal");
    modal.classList.add("hidden");
}

async function testEndpointConnection() {
    const url = document.getElementById("modal-input-url").value.trim();
    const key = document.getElementById("modal-input-key").value.trim();
    const badge = document.getElementById("modal-status-badge");
    const msg = document.getElementById("modal-status-msg");
    const btn = document.getElementById("btn-test-connection");

    if (!url) {
        badge.innerText = "URL REQUIRED";
        badge.className = "font-bold text-rose-400";
        msg.innerText = "Please paste a valid ngrok or HTTP endpoint.";
        return;
    }

    btn.disabled = true;
    badge.innerText = "TESTING...";
    badge.className = "font-bold text-slate-300 animate-pulse";
    msg.innerText = "Sending ping to endpoint...";

    try {
        const res = await fetch("/api/config/test", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ api_url: url, api_key: key })
        });
        const result = await res.json();
        badge.innerText = (result.status || "UNKNOWN").toUpperCase();
        badge.className = result.status === "online" ? "font-bold text-emerald-400" : "font-bold text-rose-400";
        msg.innerText = result.message || "";
    } catch (e) {
        badge.innerText = "FAILED";
        badge.className = "font-bold text-rose-400";
        msg.innerText = "Network call error: " + e.message;
    } finally {
        btn.disabled = false;
    }
}

async function saveEndpointConfig() {
    const url = document.getElementById("modal-input-url").value.trim();
    const key = document.getElementById("modal-input-key").value.trim();
    const badge = document.getElementById("modal-status-badge");
    const msg = document.getElementById("modal-status-msg");
    const btnSave = document.getElementById("btn-save-endpoint");

    if (!url) {
        alert("Please provide an endpoint URL");
        return;
    }

    btnSave.disabled = true;
    btnSave.innerText = "Saving...";

    try {
        const res = await fetch("/api/config/endpoint", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ api_url: url, api_key: key })
        });
        const data = await res.json();
        const testRes = data.connection_test || {};
        updateEndpointBadge(testRes);
        
        btnSave.innerText = "Saved!";
        setTimeout(() => {
            btnSave.innerText = "Save & Connect";
            btnSave.disabled = false;
            closeEndpointModal();
        }, 1200);
    } catch (e) {
        alert("Failed to save endpoint: " + e.message);
        btnSave.disabled = false;
        btnSave.innerText = "Save & Connect";
    }
}
