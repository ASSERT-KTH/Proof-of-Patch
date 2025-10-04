# Proof-of-Patch Dataset

**A curated dataset of smart contract security audits with patch/mitigation indicators from Solodit**

## 🎯 Overview

This repository contains a specialized dataset of smart contract security audits that have been identified as containing **patch indicators** or **mitigation strategies**. Unlike general audit datasets, this collection focuses specifically on audits that provide actionable fixes, GitHub commits, pull requests, or other forms of remediation.

The dataset is built using enhanced scraping and AI analysis tools adapted from the [VeriSet](https://github.com/ASSERT-KTH/VeriSet) project, specifically modified to prioritize audits with patch/mitigation content.

## 📊 Dataset Statistics

- **Total Audits**: 3,814 curated audits
- **Patch Indicators**: Audits with GitHub commits, PRs, or mitigation code
- **Quality Metrics**: AI-analyzed for PoC presence, mitigation quality, and technical soundness

### **Vulnerability Category Breakdown**

| Category | Audits Found | Audits Added | Success Rate |
|----------|-------------|--------------|--------------|
| **Access Control** | 1,326 | 1,043 | 78.7% |
| **Reentrancy** | 1,083 | 760 | 70.2% |
| **Logic Error** | 940 | 770 | 81.9% |
| **Flash Loan** | 460 | 356 | 77.4% |
| **Denial of Service (DoS)** | 375 | 309 | 82.4% |
| **Lack of Input Validation** | 364 | 276 | 75.8% |
| **Price Oracle Manipulation** | 297 | 230 | 77.4% |
| **Unchecked External Calls** | 301 | 250 | 83.1% |
| **Integer Overflow** | 222 | 175 | 78.8% |
| **Integer Underflow** | 99 | 79 | 79.8% |
| **Insecure Randomness** | 13 | 8 | 61.5% |

**Total**: 5,480 audits found → 3,814 audits added (69.6% overall success rate)

*Data collected on October 3-4, 2025*

STARTING TIMESTAMP: 2025-10-03 15:30:55,954
FINISHED AT:        2025-10-04 07:38:23,078

## 🔍 What Makes This Dataset Special

### **Patch-Focused Collection**
- ✅ Audits with **GitHub commit references**
- ✅ Audits with **pull request links**
- ✅ Audits with **mitigation code examples**
- ✅ Audits with **clear remediation strategies**

### **Quality Assessment**
- **Proof of Concept (PoC)**: Code examples demonstrating vulnerabilities
- **Mitigation Proposals**: Clear recommendations and solutions
- **Patch References**: Links to actual implementations
- **Audit Quality**: Technical soundness and explanation quality

### **Comprehensive Metadata**
Each audit includes:
- Vulnerability type and impact level
- Publication date and authors
- Patch indicators and mitigation content
- AI-analyzed quality metrics
- Priority scores for research value

## 📁 Dataset Structure

```
results/
├── results.json              # Raw scraped audit data
├── enriched_data.json        # AI-analyzed audit data
├── prioritized_data.json     # Prioritized by patch value
├── prioritized_data.csv      # CSV export for analysis
├── cost_summary.json         # Processing cost breakdown
└── disregarded_links.json    # Audits without patches
```

## 🛠️ Tools & Pipeline

### **Enhanced Scraper** (`solodit-scraper/scraper.py`)
- Searches Solodit for audits with patch-related keywords
- Detects GitHub commits, PRs, and mitigation sections
- Maintains PoC detection alongside patch analysis
- Incremental saving with progress tracking

### **AI Parser** (`solodit-scraper/parser.py`)
- Uses GPT-4o to analyze audit content
- Evaluates PoC quality and mitigation strategies
- Tracks token usage and costs
- Generates quality metrics and patch scores

### **Priority Scorer** (`solodit-scraper/priority.py`)
- Ranks audits by patch/mitigation value
- Categorizes as "patch_and_poc", "patch_only", "poc_only"
- Generates CSV exports for analysis
- Provides detailed statistics

## 🚀 Usage

### **Setup**
```bash
# Clone repository
git clone https://github.com/sofiabobadilla/Proof-of-Patch.git
cd proof-of-patch

# Navigate to scraper directory
cd solodit-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key (for parser)
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### **Running the Pipeline**

1. **Scrape Audits** (requires Cyfrin login):
   ```bash
   cd solodit-scraper
   python scraper.py
   # Manual login required when prompted
   ```

2. **Analyze with AI**:
   ```bash
   python parser.py
   ```

3. **Prioritize Results**:
   ```bash
   python priority.py
   ```

### **Testing**
```bash
# Create test dataset (2 audits)
python create_test.py setup
python parser.py
```

## 📈 Key Metrics

### **Priority Scoring System**
- **Patch References**: 20 points (highest priority)
- **Mitigation Proposals**: 15 points
- **PoC Quality**: 12 points
- **Technical Indicators**: 8-12 points each
- **Impact Level**: 2-8 points

### **Cost Analysis**
- **Average cost per audit**: ~$0.007
- **Total processing cost**: ~$26.70 for full dataset
- **Token efficiency**: ~1,300 tokens per audit

## 🎯 Research Applications

This dataset is ideal for:
- **Vulnerability Research**: Studying how vulnerabilities are fixed
- **Patch Analysis**: Understanding mitigation strategies
- **Security Tool Development**: Training models on patch patterns
- **Academic Research**: Smart contract security studies
- **Developer Education**: Learning from real-world fixes

## 📋 Dataset Categories

### **By Patch Type**
- `patch_and_poc`: Both patch and proof-of-concept
- `patch_only`: Patch but no PoC
- `poc_only`: PoC but no patch
- `other`: Neither patch nor PoC

### **By Vulnerability Type**
- Access Control
- Reentrancy
- Price Oracle Manipulation
- Logic Errors
- Integer Overflow/Underflow
- Denial of Service (DoS)
- And more...

## 🔧 Technical Details

### **Dependencies**
- Python 3.8+
- Selenium (web scraping)
- OpenAI API (AI analysis)
- tiktoken (token counting)
- pandas (data processing)

### **Data Sources**
- **Primary**: [Solodit](https://solodit.cyfrin.io/) - Cyfrin's audit database
- **Enhancement**: AI analysis using GPT-4o
- **Validation**: Manual quality assessment

### **File Formats**
- **JSON**: Structured data with full metadata
- **CSV**: Tabular format for analysis
- **Logs**: Detailed processing information

## ⚠️ Important Notes

- **Webpage Dependency**: Scraper depends on Solodit's HTML structure (current as of October 2024)
- **API Costs**: AI analysis requires OpenAI API credits
- **Login Required**: Cyfrin account needed for scraping
- **Data Freshness**: Dataset reflects Solodit content at scraping time

## 📄 License & Citation

This dataset is provided for research purposes. When using this data, please cite:

```
Proof-of-Patch Dataset: Smart Contract Audits with Mitigation Indicators
[Your Name/Institution]
[Year]
```





---

*This dataset represents a systematic approach to identifying and analyzing smart contract security audits with actionable remediation strategies, supporting the development of more secure blockchain applications.*