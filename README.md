<div align="center">

  <img src="pop.png" alt="Patch" width="72" height="72"/>


  <h1>Proof-of-Patch Dataset</h1>
  <h3>Curated Solidity vulnerabilities with verified patches</h3>

  <p>
    <a href="https://arxiv.org/abs/2511.02780">📑 <b>PoCo Paper</b></a> •
    <a href="https://github.com/ASSERT-KTH/PoCo-results">📊 <b>Poco Results</b></a>
  </p>

  <p>
    🐞 <b>23 recent smart contract vulnerabilities</b> each with a <b>manually verified ground-truth patch</b>.  
  </p>
</div>

Cite the paper or dataset:

```bibtex
@article{anderssonbobadilla2025poco,
  title={PoCo: Agentic Proof-of-Concept Exploit Generation for Smart Contracts},
  author={Andersson, Vivi and Bobadilla, Sofia and Hobbelhagen, Harald and Monperrus, Martin},
  journal={arXiv preprint arXiv:2511.02780},
  year={2025}
}
```

## 📊 Dataset Overview

This repository provides 23 hand-curated Solidity/Foundry smart contract vulnerabilities, each with a manually verified patch and references to real-world audits. The focus is on actionable, audit-grade vulnerability instances and concrete mitigation implementations, organized for reproducibility and further research.

| ID | Project | Description | Audit Ref. | Patch Ref. | Has PoC |
|----|---------|-------------|------------|------------|---------|
| [001](https://solodit.cyfrin.io/issues/m-01-multicall-does-not-work-as-intended-code4rena-size-size-git) | [2024-06-size](https://github.com/code-423n4/2024-06-size) | Logical error in multicall function allows users to bypass deposit limits. | [M-01](https://github.com/code-423n4/2024-06-size-findings/issues/238) | [PR126](https://github.com/SizeCredit/size-solidity/pull/126) | No |
| [003](https://solodit.cyfrin.io/issues/h-04-vaultmintyieldfee-function-can-be-called-by-anyone-to-mint-vault-shares-to-any-recipient-address-code4rena-pooltogether-pooltogether-git) | [2023-07-pooltogether](https://github.com/code-423n4/2023-07-pooltogether) | User can mint shares to any address and steal the yield fee of the protocol. | [H-04](https://github.com/code-423n4/2023-07-pooltogether-findings/issues/396) | [PR7](https://github.com/GenerationSoftware/pt-v5-vault/pull/7) | No |
| [008](https://solodit.cyfrin.io/issues/m-05-investors-claiming-their-maxdeposit-by-using-the-liquiditypooldeposit-will-cause-other-users-to-be-unable-to-claim-their-maxdepositmaxmint-code4rena-centrifuge-centrifuge-git) | [2023-09-centrifuge](https://github.com/code-423n4/2023-09-centrifuge) | Rounding errors in share calculations allow investors to receive excess shares. | [M-05](https://github.com/code-423n4/2023-09-centrifuge-findings/issues/118) | [PR166](https://github.com/centrifuge/liquidity-pools/pull/166) | Yes |
| [009](https://solodit.cyfrin.io/issues/m-08-loss-of-funds-for-traders-due-to-accounting-error-in-royalty-calculations-code4rena-caviar-caviar-private-pools-git) | [2023-04-caviar](https://github.com/code-423n4/2023-04-caviar) | Royalties are miscalculated when recipient address is zero, leading to trapped funds. | [M-08](https://github.com/code-423n4/2023-04-caviar-findings/issues/596) | [PR11](https://github.com/outdoteth/caviar-private-pools/pull/11/files) | No |
| [015](https://solodit.cyfrin.io/issues/m-02-unintended-or-malicious-use-of-prize-winners-hooks-code4rena-pooltogether-pooltogether-git) | [2023-07-pooltogether](https://github.com/code-423n4/2023-07-pooltogether) | The prize-winners hook mechanism can be exploited to interfere with the intended prize distribution process. | [M-02](https://github.com/code-423n4/2023-07-pooltogether-findings/issues/465) | [PR21](https://github.com/GenerationSoftware/pt-v5-vault/pull/21) | Yes |
| [018](https://solodit.cyfrin.io/issues/m-15-pool-tokens-can-be-stolen-via-privatepoolflashloan-function-from-previous-owner-code4rena-caviar-caviar-git) | [2023-04-caviar](https://github.com/code-423n4/2023-04-caviar) | Former owner can set token approvals that enable them to reclaim assets after ownership transfer. | [M-15](https://github.com/code-423n4/2023-04-caviar-findings/issues/230) | [PR2](https://github.com/outdoteth/caviar-private-pools/pull/2) | Yes |
| [020](https://solodit.cyfrin.io/issues/m-3-share-price-inflation-by-first-lp-er-enabling-dos-attacks-on-subsequent-buyshares-with-up-to-1001x-the-attacking-cost-sherlock-dodo-gsp-git) | [2023-12-dodo-gsp](https://github.com/sherlock-audit/2023-12-dodo-gsp) | A first liquidity provider can inflate the share price during pool initialization, enabling a DoS. | [M-03](https://github.com/sherlock-audit/2023-12-dodo-gsp-judging/issues/55) | [PR14](https://github.com/DODOEX/dodo-gassaving-pool/pull/14/files) | Yes |
| [032](https://solodit.cyfrin.io/issues/m-06-denial-of-service-contract-owner-could-block-users-from-withdrawing-their-strike-code4rena-putty-putty-contest-git) | [2022-06-putty](https://github.com/code-423n4/2022-06-putty) | User cannot withdraw their strike amount and their asset will be stuck in the contract. | [M-06](https://github.com/code-423n4/2022-06-putty-findings/issues/296#issuecomment-1185411399) | [PR4](https://github.com/outdoteth/putty-v2/pull/4/files) | No |
| [033](https://solodit.cyfrin.io/issues/m-03-flash-loan-fee-is-incorrect-in-private-pool-contract-code4rena-caviar-caviar-private-pools-git) | [2023-04-caviar](https://github.com/code-423n4/2023-04-caviar) | The PrivatePool contract miscalculates flash loan fees causing incorrect fee totals. | [M-03](https://github.com/code-423n4/2023-04-caviar-findings/issues/864) | [PR6](https://github.com/outdoteth/caviar-private-pools/pull/6) | Yes |
| [039](https://solodit.cyfrin.io/issues/h-2-m-1-sherlock-axis-finance-git) | [2024-03-axis-finance](https://github.com/sherlock-audit/2024-03-axis-finance) | Refund handling errors can lock seller funds when the token reverts on zero transfers. | [M-01](https://github.com/sherlock-audit/2024-03-axis-finance-judging/issues/21) | [PR142](https://github.com/Axis-Fi/axis-core/pull/142/files) | No |
| [041](https://solodit.cyfrin.io/issues/h-1-malicious-user-can-overtake-a-prefunded-auction-and-steal-the-deposited-funds-sherlock-axis-finance-git) | [2024-03-axis-finance](https://github.com/sherlock-audit/2024-03-axis-finance) | User can hijack a prefunded auction and gain control over its deposited funds. | [H-01](https://github.com/sherlock-audit/2024-03-axis-finance-judging/issues/12) | [PR132](https://github.com/Axis-Fi/moonraker/pull/132) | Yes |
| [042](https://solodit.cyfrin.io/issues/m-2-utilization-rate-multiplier-will-not-shift-if-oracle-is-consulted-frequently-sherlock-cap-git) | [2025-07-cap](https://github.com/sherlock-audit/2025-07-cap) | User can exploit a rounding error to repeatedly miscompute utilization, causing inaccurate interest rate adjustments. | [M-02](https://github.com/sherlock-audit/2025-07-cap-judging/issues/148) | [PR187](https://github.com/cap-labs-dev/cap-contracts/pull/187) | Yes |
| [046](https://solodit.cyfrin.io/issues/m-03-zero-token-transfer-can-cause-a-potential-dos-in-cvxstaker-code4rena-xeth-xeth-versus-contest-git) | [2023-05-xeth](https://github.com/code-423n4/2023-05-xeth) | Zero token transfer can cause a potential denial of service when giving rewards | [M-03](https://github.com/code-423n4/2023-05-xeth-findings/issues/30) | [1f71a](https://github.com/code-423n4/2023-05-xeth/commit/1f714868f193cdeb472ec097110901a997d87ec4) | Yes |
| [048](https://solodit.cyfrin.io/issues/h-01-royalty-receiver-can-drain-a-private-pool-code4rena-caviar-caviar-private-pools-git) | [2023-04-caviar](https://github.com/code-423n4/2023-04-caviar) | Malicious royalty recipient can extract value from the pool without proper payment. | [H-01](https://github.com/code-423n4/2023-04-caviar-findings/issues/593#issuecomment-1520075272) | [PR12](https://github.com/outdoteth/caviar-private-pools/pull/12) | Yes |
| [049](https://solodit.cyfrin.io/issues/m-2-lender-is-able-to-steal-borrowers-collateral-by-calling-rollloan-with-unfavourable-terms-on-behalf-of-the-borrower-sherlock-cooler-update-git) | [2023-08-cooler](https://github.com/sherlock-audit/2023-08-cooler) | Lender can update loan terms without borrower approval, enabling them to impose unfair conditions. | [M-02](https://github.com/sherlock-audit/2023-08-cooler-judging/issues/26) | [PR54](https://github.com/ohmzeus/Cooler/pull/54/files#diff-f461174637e644b69004d9f7ad97d531a760909f465ad610acea335531a49767) | No |
| [051](https://solodit.cyfrin.io/issues/m-04-you-can-deposit-really-small-amount-for-other-users-to-dos-them-code4rena-centrifuge-centrifuge-git) | [2023-09-centrifuge](https://github.com/code-423n4/2023-09-centrifuge) | Missed access control allows users to deposit on behalf of others and potentially caused a denial of service attack. | [M-04](https://github.com/code-423n4/2023-09-centrifuge-findings/issues/143) | [PR136](https://github.com/centrifuge/liquidity-pools/pull/136) | No |
| [054](https://solodit.cyfrin.io/issues/h-01-no-revert-on-transfer-erc20-tokens-can-be-drained-code4rena-cally-cally-contest-git) | [2022-05-cally](https://github.com/code-423n4/2022-05-cally) | Unchecked token transfer return values let attackers create empty vaults, causing buyers to pay Ether but receive no tokens. | [H-01](https://github.com/code-423n4/2022-05-cally-findings/issues/89) | [PR4](https://github.com/outdoteth/cally/pull/4) | Yes |
| [058](https://solodit.cyfrin.io/issues/m-05-fillorder-and-exercise-may-lock-ether-sent-to-the-contract-forever-code4rena-putty-putty-git) | [2022-06-putty](https://github.com/code-423n4/2022-06-putty) | Users can accidentally send Ether to code paths that don't use it, causing the funds to be locked | [M-05](https://github.com/code-423n4/2022-06-putty-findings/issues/226) | [PR5](https://github.com/outdoteth/putty-v2/pull/5) | No |
| [066](https://solodit.cyfrin.io/issues/h-02-protocol-mints-less-rseth-on-deposit-than-intended-code4rena-kelp-dao-kelp-dao-git) | [2023-11-kelp](https://github.com/code-423n4/2023-11-kelp) | Users receive less rsETH than expected due to a miscalculation in the minting logic. | [H-02](https://github.com/code-423n4/2023-11-kelp-findings/issues/62) | [Other](https://github.com/code-423n4/2023-11-kelp-findings/issues/62#issuecomment-1850480282) | No |
| [070](https://solodit.cyfrin.io/issues/m-01-contract-phinft1155-cant-be-paused-code4rena-phi-phi-git) | [2024-08-ph](https://github.com/code-423n4/2024-08-ph) | Users are able to transfer NFT tokens even when the contract is paused. | [M-01](https://github.com/code-423n4/2024-08-phi-findings/issues/268) | [Other](https://github.com/code-423n4/2024-08-phi-findings/issues/268#issuecomment-2357330877) | Yes |
| [077](https://solodit.cyfrin.io/issues/h-08-player-can-mint-more-fighter-nfts-during-claim-of-rewards-by-leveraging-reentrancy-on-the-claimrewards-function-code4rena-ai-arena-ai-arena-git) | [2024-02-ai-arena](https://github.com/code-423n4/2024-02-ai-arena) | Players can exploit a reentrancy bug to claim extra rewards before the contract updates their NFT balance. | [H-08](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/37) | [PR6](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/6/files#diff-b7b791431bf00bf243ef885bca223669bc5c7970e24202017c3736b65c62ed1f) | Yes |
| [091](https://solodit.cyfrin.io/issues/h-01-pumps-are-not-updated-in-the-shift-and-sync-functions-allowing-oracle-manipulation-code4rena-basin-basin-git) | [2023-07-basin](https://github.com/code-423n4/2023-07-basin) | Users can manipulate the reported asset reserves, causing incorrect price data. | [H-01](https://github.com/code-423n4/2023-07-basin-findings/issues/136) | [PR97](https://github.com/BeanstalkFarms/Basin/pull/97/files) | Yes |
| [098](https://solodit.cyfrin.io/issues/h-03-wp-h0-fake-balances-can-be-created-for-not-yet-existing-erc20-tokens-which-allows-attackers-to-set-traps-to-steal-funds-from-future-users-code4rena-cally-cally-contest-git) | [2022-05-cally](https://github.com/code-423n4/2022-05-cally) | Fake token balances can be created for nonexistent ERC20s, enabling traps that steal funds from later users. | [H-03](https://github.com/code-423n4/2022-05-cally-findings/issues/225) | [PR5](https://github.com/outdoteth/cally/pull/5) | No |
| **Total** | | | **23 Reports** | **M:15 H:8** | **Y:13 N:10** |


---

### Dataset Features

- Vulnerabilities include links to original audit reports, patch references (pull requests/commits), and PoC exploits (where applicable).
- Each entry is manually validated (valid finding, project setup ok).
- Remediation strategies are drawn directly from the maintainers’ or auditors’ code/patch commits.

### Quality Guarantees

- **Linked PoCs:** Example exploits are provided for critical findings when available.
- **Mitigation References:** Patches reference concrete PRs or commit SHAs.
- **Human-written Annotations:** Each datapoint contains the vulnerability annotation ("report") as written by the human auditor and **accepted** by the dev team.

---

## 📁 Repository Layout

```
findings/                 # 23 manually selected findings
├── 001/                  # Directory for individual finding (full report, vulnerable & patched code, PoC)
├── 003/
└── ...
annotations/              # Manual analyst summaries and context for each finding
├── 001.txt
├── 003.txt
└── ...
patches/                  # Standalone patch implementations
pocs/                     # Proof of concept exploits
dataset_metadata.json     # Machine-readable dataset index and metadata
```

## Reproduction Note
For additional information, including the original scraping scripts and proof-of-concept (POC) exploits, please visit the [main branch](https://github.com/ASSERT-KTH/Proof-of-Patch/tree/main).

