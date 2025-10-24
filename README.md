# Proof-of-Patch Dataset

**A curated dataset of smart contract security audits with patch/mitigation indicators from Solodit**

## 🎯 Overview

This repository contains two distinct datasets:

1. **Raw Dataset** (`raw_dataset/`): Contains links and data scraped directly from [Solodit](https://solodit.cyfrin.io/), including 3,814+ audit findings with patch indicators, GitHub commits, pull requests, and mitigation strategies.

2. **Curated Dataset** (`dataset/`): A manually verified collection of the **100 most promising audits** from the raw dataset, carefully reviewed for their research value, patch quality, and educational potential.

The dataset is built using enhanced scraping and AI analysis tools adapted from the [VeriSet](https://github.com/ASSERT-KTH/VeriSet) project, specifically modified to prioritize audits with patch/mitigation content.

## 📊 Dataset Statistics

### **Raw Dataset**
- **Total Audits**: 3,814+ audits with patch indicators
- **Source**: Scraped from Solodit with AI analysis
- **Patch Indicators**: Audits with GitHub commits, PRs, or mitigation code
- **Quality Metrics**: AI-analyzed for PoC presence, mitigation quality, and technical soundness

### **Curated Dataset**
- **Total Findings**: 23 manually verified findings
- **Verification Process**: Most promising audits reviewed for research and education value
- **Manual Review**: Each finding includes detailed annotations and summaries
- **Patch References**: Direct links to implemented fixes

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

## 📋 Curated Findings Table

The following table presents the 23 most promising findings from our curated dataset, each manually verified and reviewed for their research value and educational potential.

| ID | Repository | Vulnerability Type | Difficulty | Has PoC | Summary |
|----|------------|-------------------|------------|---------|---------|
| 001 | [2024-06-size](https://github.com/code-423n4/2024-06-size) | Access Control | Medium | No | Multicall function bypasses deposit limits, allowing users to deposit more borrowATokens than intended, breaking the invariant that restricts borrowAToken supply increase to be less than or equal to debtToken supply decrease. |
| 003 | [2023-07-pooltogether](https://github.com/code-423n4/2023-07-pooltogether) | Access Control | High | No | Vault.mintYieldFee function lacks access control, allowing anyone to steal available yield fees by minting shares to any address instead of using the designated yield fee recipient. |
| 008 | [2023-09-centrifuge](https://github.com/code-423n4/2023-09-centrifuge) | Logic Error | Medium | Yes | Investors claiming deposits using LiquidityPool.deposit() cause rounding errors that result in the Escrow contract transferring slightly more shares than intended, preventing other investors from claiming their entitled shares. |
| 009 | [2023-04-caviar](https://github.com/code-423n4/2023-04-caviar) | Logic Error | Medium | No | Accounting error in royalty calculations causes loss of funds for traders due to incorrect fee computation in the PrivatePool contract. |
| 015 | [2023-07-pooltogether](https://github.com/code-423n4/2023-07-pooltogether) | Denial of Service | High | Yes | setHooks function allows users to set arbitrary hooks, potentially enabling unauthorized side transactions, reentrant calls, or denial-of-service attacks on claiming transactions. |
| 018 | [2023-04-caviar](https://github.com/code-423n4/2023-04-caviar) | Flash Loan | High | Yes | PrivatePool tokens can be stolen by previous owners via execute and flashLoan functions, as ownership changes don't revoke previous approvals, allowing attackers to drain funds after selling pool ownership. |
| 020 | [2023-12-dodo-gsp](https://github.com/sherlock-audit/2023-12-dodo-gsp) | Denial of Service | Medium | Yes | First liquidity provider can inflate share prices by depositing minimal amounts, enabling DoS attacks on subsequent buyShares with up to 1001x the attacking cost. |
| 032 | [2022-06-putty](https://github.com/code-423n4/2022-06-putty) | Logic Error | Medium | No | Contract owner can block users from withdrawing their strike by manipulating the withdrawal mechanism, causing denial of service for legitimate users. |
| 033 | [2023-04-caviar](https://github.com/code-423n4/2023-04-caviar) | Logic Error | Medium | Yes | Flash loan fee calculation is incorrect in the PrivatePool contract, leading to improper fee collection and potential loss of protocol revenue. |
| 039 | [2024-03-axis-finance](https://github.com/sherlock-audit/2024-03-axis-finance) | Unchecked External Calls | High | No | Auction house routing details are recorded at index 0, allowing attackers to create auctions right after honest users and take over their prefunded auctions to steal funds. |
| 041 | [2024-03-axis-finance](https://github.com/sherlock-audit/2024-03-axis-finance) | Reentrancy | High | Yes | Malicious users can overtake prefunded auctions and steal deposited funds by exploiting the auction creation mechanism and routing storage. |
| 042 | [2025-07-cap](https://github.com/sherlock-audit/2025-07-cap) | Access Control | Medium | Yes | Utilization rate multiplier fails to shift when oracle is consulted frequently, leading to incorrect interest rate calculations and potential economic exploitation. |
| 046 | [2023-05-xeth](https://github.com/code-423n4/2023-05-xeth) | Denial of Service | Medium | Yes | Zero token transfers can cause potential DoS in CVXStaker contract due to improper handling of zero-value transfers in the staking mechanism. |
| 048 | [2023-04-caviar](https://github.com/code-423n4/2023-04-caviar) | Reentrancy | High | Yes | Reentrancy vulnerability in PrivatePool contract allows attackers to manipulate state during external calls, potentially draining funds or causing unexpected behavior. |
| 049 | [2023-08-cooler](https://github.com/sherlock-audit/2023-08-cooler) | Access Control | Medium | No | Lender can steal borrower's collateral by calling rollLoan with unfavorable terms on behalf of the borrower, exploiting insufficient access controls. |
| 051 | [2023-09-centrifuge](https://github.com/code-423n4/2023-09-centrifuge) | Access Control | Medium | No | Users can deposit really small amounts for other users to DoS them, preventing legitimate users from claiming their deposits due to malicious micro-deposits. |
| 054 | [2022-05-cally](https://github.com/code-423n4/2022-05-cally) | Reentrancy | High | No | No revert on transfer of ERC20 tokens can lead to token drainage due to improper handling of failed token transfers in the contract logic. |
| 058 | [2022-06-putty](https://github.com/code-423n4/2022-06-putty) | Logic Error | Medium | No | fillOrder and exercise functions may lock ether sent to the contract forever due to improper handling of ETH transfers and order fulfillment logic. |
| 066 | [2023-11-kelp](https://github.com/code-423n4/2023-11-kelp) | Unchecked External Calls | High | No | Protocol mints less rsETH on deposit than intended due to unchecked external calls and improper calculation of minted tokens in the deposit process. |
| 070 | [2024-08-phi](https://github.com/code-423n4/2024-08-phi) | Reentrancy | Medium | Yes | Contract PhiNFT1155 cannot be paused due to reentrancy vulnerabilities that prevent proper emergency pause functionality. |
| 077 | [2024-02-ai-arena](https://github.com/code-423n4/2024-02-ai-arena) | Reentrancy | High | Yes | Players can mint more fighter NFTs during claim of rewards by leveraging reentrancy on the claimRewards function, allowing unlimited NFT minting. |
| 091 | [2023-07-basin](https://github.com/code-423n4/2023-07-basin) | Price Oracle Manipulation | High | Yes | Pumps (oracles) are not updated in shift() and sync() functions, allowing users to manipulate reserves in the current block and override previous block's reserves for oracle manipulation. |
| 098 | [2022-05-cally](https://github.com/code-423n4/2022-05-cally) | Reentrancy | High | No | Fake balances can be created for not-yet-existing ERC20 tokens, allowing attackers to set traps to steal funds from future users through reentrancy exploitation. |

## 🔍 What Makes This Dataset Special

### **Two-Tier Approach**
- **Raw Dataset**: Comprehensive collection of 3,814+ audits with patch indicators
- **Curated Dataset**: 23 manually verified findings for maximum research and educational value

### **Patch-Focused Collection**
- ✅ Audits with **GitHub commit references**
- ✅ Audits with **pull request links**
- ✅ Audits with **mitigation code examples**
- ✅ Audits with **clear remediation strategies**

### **Quality Assessment**
- **Proof of Concept (PoC)**: Code examples demonstrating vulnerabilities
- **Mitigation Proposals**: Clear recommendations and solutions
- **Patch References**: Links to actual implementations
- **Manual Annotations**: Detailed summaries and analysis for curated findings

### **Comprehensive Metadata**
Each finding includes:
- Vulnerability type and difficulty level
- Repository links and main contracts
- Patch references and test commands
- Manual annotations with detailed summaries
- Proof of concept implementations

## 📁 Dataset Structure

### **Raw Dataset** (`raw_dataset/`)
```
raw_dataset/
├── results.json              # Raw scraped audit data from Solodit
├── enriched_data.json        # AI-analyzed audit data
├── prioritized_data.json     # Prioritized by patch value
├── prioritized_data.csv      # CSV export for analysis
├── cost_summary.json         # Processing cost breakdown
└── disregarded_links.json    # Audits without patches
```

### **Curated Dataset** (`dataset/`)
```
dataset/
├── findings/                 # 23 manually selected findings
│   ├── 001/                 # Individual finding directories
│   ├── 003/
│   └── ...
├── annotations/             # Security Researcher annotations and summaries
│   ├── 001.txt
│   ├── 003.txt
│   └── ...
├── patches/                 # Implemented patches
├── pocs/                    # Proof of concept exploits obtained from original finding
└── dataset_metadata.json    # Curated dataset metadata
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

### **Using the Curated Dataset**
The curated dataset is ready to use immediately:

```bash
# Clone repository
git clone https://github.com/sofiabobadilla/Proof-of-Patch.git
cd proof-of-patch

# Execute the automated configuration file
./dataset_config.sh --help

# Explore curated findings
ls dataset/findings/

# Read annotations for specific findings
cat dataset/annotations/001.txt

# Examine patches
ls dataset/patches/

# View proof of concepts
ls dataset/pocs/
```

### **Reproducing the Raw Dataset**
To recreate the raw dataset from Solodit:

```bash
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

# Run the pipeline
python scraper.py    # Scrape audits (requires Cyfrin login)
python parser.py     # Analyze with AI
python priority.py   # Prioritize results
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

### **Raw Dataset Applications**
- **Large-scale Analysis**: Study patterns across 3,814+ audits
- **AI/ML Training**: Train models on patch patterns and vulnerability types
- **Trend Analysis**: Understand evolution of smart contract security
- **Automated Tools**: Develop security analysis tools

### **Curated Dataset Applications**
- **Case Studies**: Deep dive into specific vulnerability patterns
- **Research Benchmarks**: Use as ground truth for security research
- **Developer Training**: Understand real-world vulnerability fixes

## 📊 Dataset Categories

### **Curated Findings by Vulnerability Type**
- **Access Control** (5 findings): Improper access controls and authorization issues
- **Logic Error** (5 findings): Flawed business logic and calculation errors
- **Reentrancy** (5 findings): Classic reentrancy vulnerabilities
- **Denial of Service** (3 findings): DoS attacks and blocking mechanisms
- **Flash Loan** (1 finding): Flash loan attack vectors
- **Price Oracle Manipulation** (1 finding): Oracle manipulation techniques
- **Unchecked External Calls** (2 findings): Unsafe external contract interactions

### **Raw Dataset by Patch Type**
- `patch_and_poc`: Both patch and proof-of-concept
- `patch_only`: Patch but no PoC
- `poc_only`: PoC but no patch
- `other`: Neither patch nor PoC



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


## ⚠️ Important Notes

- **Webpage Dependency**: Scraper depends on Solodit's HTML structure (current as of October 2025)
- **API Costs**: AI analysis requires OpenAI API credits
- **Login Required**: Cyfrin account needed for scraping
- **Data Freshness**: Dataset reflects Solodit content at scraping time
- **⚠️ Storage Warning**: When all submodules are downloaded, the project can reach a size of **10 GB** due to the large number of audit repositories included

## 📄 License & Citation

This dataset is provided for research purposes. When using this data, please cite:

```
TODO
```





---

*This dataset represents a systematic approach to identifying and analyzing smart contract security audits with actionable remediation strategies, supporting the development of more secure blockchain applications.*
