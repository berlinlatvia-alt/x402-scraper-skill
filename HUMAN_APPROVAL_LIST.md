# 🛑 Human Approval & Mandatory Action List (Tier 4 Only)

> [!IMPORTANT]
> **Tier 4 Principle Enforcement:**  
> Before adding any task to this list, agents MUST test if the task can be completed autonomously. Only tasks requiring human cryptographic signatures, exchange UI confirmations, or fiat deposits belong on this list.

---

## 📋 Pending Human Actions

### Item 1: Binance USDC Seed Deposit for Strategy 2 (Optional)
- **Action Required:** Transfer **$10.00 to $20.00 USDC** to our Base/Polygon wallet:
  ```text
  Wallet Address: 0x29C814FA1b67c23ec614bFc96C80f2274301cEBc
  Network: Polygon Mainnet OR Base Mainnet
  ```
- **Why Human (Tier 4) is Required:** Binance withdrawal confirmation requires 2FA security (SMS/Email/Authenticator) which is strictly protected on your device.
- **Is Strategy 2 Safe?:** Yes, 100% spot trading with zero leverage.
- **Can Money Be Returned?:** Yes. Private key is saved in `.env` (`BASE_PRIVATE_KEY`), so funds can be withdrawn back to your personal wallet at any time.
- **Status:** **AWAITING USER DECISION**

---

### Item 2: ⏳ GM APPROVAL REQUIRED — Full Audit & KPI Tracking Skill

**GM (Opus 5) Verdict:** APPROVED with 6 conditions (C1-C6)
**GM (Kimi K3) Verdict:** APPROVED (via reasoning, provider blocked full output)

#### Your Decisions Required:

| # | Decision | Options |
|---|----------|---------|
| **1** | **Audience Lock** | Agents (AI bots) vs Humans (devs) — which do we sell to for the NEXT 30 DAYS? (locked per Opus 5 C2) |
| **2** | **First Channel** | Payhip (current listing) vs Gumroad (original plan) vs agentskill.sh (agent-native) |
| **3** | **First Product** | Prompt Templates ($9 — lowest friction) vs Never-Stop Skill ($29 — validated) vs Agent Memory System ($49 — highest price) |
| **4** | **Credential Rotation** | Approve rotating all exposed keys now? (P0 blocking per Opus 5) |
| **5** | **Skill Freeze (C1)** | Approve 30-day ban on new skill creation? (78 skills frozen) |
| **6** | **Ship Deadline (C3)** | Approve 7-day deadline from security purge completion? |
| **7** | **Kill Criteria (C6)** | Day 60 with $0 revenue = project shutdown or handoff. Accept? |

#### What's Already Done (Authorized by GM):
- ✅ Audit file written: `AUDIT-2026-07-30-DSL.json` — 5 bottlenecks, 5 hallucinations, 6 new biases
- ✅ KPI tracking skill deployed: `skills/kpi-tracking/SKILL.md` + `KPI_TRACKING_SKILL_2026-07-30.json`
- ✅ 6 new biases (BIAS-034 to BIAS-039) written to memory.db
- ✅ 6 new rules written to memory.db
- ✅ 25 previously-lost biases restored (total: 39 active)
- ✅ SK-013 kpi-tracking skill registered in memory.db
- ❌ Security purge NOT started (awaiting your approval — P0 blocking per Opus 5)
