# Contributing to MuryaAI (N-VoiceCare)

Thank you for your interest in contributing to **MuryaAI**, the open-source voice-first citizen resolution infrastructure powered by Nigeria's national foundational model, **N-ATLAS** (NCAIR / NITDA).

## Our Mission
To bridge the digital inclusion divide for over 100 million Nigerians who communicate primarily in **Hausa, Yoruba, Igbo, and Nigerian Pidgin / accented English**, enabling seamless dispute resolution across financial inclusion (POS/NIBSS) and public utilities (DisCos/electricity).

## How You Can Contribute

1. **Acoustic & Dialect Benchmarks**: Add localized audio recordings and text transcripts for specific regional dialects (e.g., Kanuri-Hausa, Ekiti-Yoruba, Owerri-Igbo, Warri Pidgin).
2. **Domain Connectors**: Build additional resolution adapters (e.g., healthcare primary triage, agricultural input subsidies, NIN/BVN status queries).
3. **Telephony Adapters**: Expand open-source connectors for local Nigerian telecommunications trunks (e.g., USSD gateway adapters, Asterisk PBX, FreeSWITCH).

## Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/naic-natlas-ai.git
cd naic-natlas-ai

# Install dependencies
pip install -r requirements.txt

# Run the test suite
python -m backend.test_pipeline

# Run the empirical benchmark suite
python -m backend.benchmark_suite

# Start the interactive local server
python -m backend.main
```

Visit `http://localhost:8000` in your browser.

## Code of Conduct & Standards
- Maintain clean, typed Python code (PEP 8, Pydantic models).
- Ensure all new domain modules include unit tests and benchmark test items.
- Respect local linguistic cultural sensitivities in conversational agent prompts.

## License
By contributing to MuryaAI, you agree that your contributions will be licensed under its MIT License.
