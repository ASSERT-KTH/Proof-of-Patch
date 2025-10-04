# VeriSet

**A Smart Contract Audit Verification and Testing Pipeline**

VeriSet is a comprehensive pipeline developed as part of a master's thesis that focuses on collecting, processing, and creating reproducible verification environments for smart contract security audits. The project automates the process of scraping audit data from Solodit, analyzing it using AI, and creating containerized environments where the findings can be reproduced and verified.

## 🎯 Project Overview

This repository contains:
- **Smart Contract Audit Data Collection**: Automated scraping from Solodit with AI-powered analysis
- **Verified Audit Reproductions**: 100+ manually verified smart contract audits with reproduction environments (for some of them)
- **Containerized Testing Pipeline**: Docker-based environments for reproducing audit findings

## 📁 Project Structure

```
VeriSet/
├── solodit-scraper/           # Web scraper and analysis tools
│   ├── scraper.py            # Selenium-based Solodit scraper
│   ├── parser.py             # AI-powered audit content analysis
│   ├── priority.py           # Audit prioritization scoring
│   └── my_result/            # Scraped and processed data
├── verified_audits/          # Manually verified audit reproductions
│   ├── 0001/                # Each folder contains:
│   ├── 0002/                #   - Original audit files
│   ├── ...                  #   - Dockerfile or docker-compose setup
│   └── 0100/                #   - Proof of Concept (PoC) files
├── initial_work/             # Out-of-scope preliminary audit work
└── .env                     # Environment variables and API keys
```

## 🛠️ Components

### Solodit Scraper
The scraper component consists of three main tools:

- **`scraper.py`**: Selenium-based web scraper that collects audit data from [Solodit](https://solodit.cyfrin.io/)
  - Requires manual login to Cyfrin account
  - Generates `results.json` and `disregarded_links.json`
  - Collects audit content, metadata, vulnerabilities, and impact information

- **`parser.py`**: AI-powered analysis tool using OpenAI API
  - Analyzes audit content for proof-of-concept code presence
  - Evaluates reasoning quality and technical correctness
  - Generates `enriched_data.json` with analysis results

- **`priority.py`**: Scoring system for audit prioritization
  - Ranks audits based on multiple factors (PoC presence, reasoning quality, impact, etc.)
  - Generates `prioritized_data.csv` and `prioritized_data.json`

### Verified Audits
Each verified audit folder (numbered 0001-0100+) contains:
- **Original audit files**: README, scope, configuration files from the contest
- **Reproduction environment**: Dockerfile and/or docker-compose.yml
- **Proof of Concept**: Solidity, TypeScript, or JavaScript test files demonstrating the vulnerability
- **Discord exports**: Community discussions from audit contests (where applicable)

## 🚀 Setup and Usage

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Node.js (for some audits)
- Git

### Environment Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd VeriSet
   ```

2. **Set up environment variables**:
   The project uses a `.env` file in the root directory containing:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ETHEREUM_MAINNET=your_ethereum_rpc_url
   ARBITRUM_MAINNET=your_arbitrum_rpc_url
   ALCHEMY_API_KEY=your_alchemy_api_key
   METAMASK_PRIVATE_KEY=your_private_key_for_testing
   ```

### Running the Solodit Scraper

1. **Set up Python environment**:
   ```bash
   cd solodit-scraper
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the scraper**:
   ```bash
   python scraper.py
   ```
   Note: You'll need to manually log in to Cyfrin when prompted during scraping.

3. **Parse the results** (requires OpenAI API key):
   ```bash
   python parser.py
   ```

4. **Prioritize audits**:
   ```bash
   python priority.py
   ```

### Running Verified Audits

Each verified audit can be run using Docker. There are two patterns:

#### Pattern 1: Simple Dockerfile
```bash
cd verified_audits/XXXX/
docker build --no-cache --progress=plain -t your-image-name .
```

#### Pattern 2: Dockerfile + docker-compose.yml
```bash
cd verified_audits/XXXX/
ln -s ../../.env .env
docker compose build --no-cache --progress=plain
```

The docker-compose setup automatically uses environment variables from the symlinked `.env` file.

## 📊 Data Pipeline

1. **Collection**: Scraper collects raw audit data from Solodit
2. **Analysis**: AI parser evaluates content quality and PoC presence
3. **Prioritization**: Scoring system ranks audits by reproduction value
4. **Verification**: Manual review and Docker environment creation
5. **Reproduction**: Containerized environments for testing findings

## 🔍 Research Context

This project is part of a master's thesis studying:
- Smart contract vulnerability reproduction methodologies
- Automated audit quality assessment
- Containerized security testing environments
- Community-driven security research analysis

### Scope Notes
- **`initial_work/`**: Contains preliminary research and is out of scope for the main pipeline
- **Verified audits**: Represent a curated subset of high-quality, reproducible findings
- **Solodit data**: Current as of the scraping date (webpage structure dependent)

## 🤝 Contributing

This is primarily a research project for academic purposes. The scraper may need updates if Solodit's webpage structure changes.

## 📝 License

This project is developed for academic research purposes as part of a master's thesis.

## ⚠️ Important Notes

- The scraper requires a Cyfrin/Solodit account for access
- API keys are required for full functionality (OpenAI for parsing, RPC endpoints for testing)
- Some audit environments may require specific Node.js versions or additional dependencies
- Docker environments are designed for research and testing purposes

---

*This project represents a systematic approach to smart contract audit verification, combining automated data collection, AI analysis, and reproducible testing environments.*