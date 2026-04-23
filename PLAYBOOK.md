# A/B Testing Playbook

> Standard methodology for designing, running, and learning from controlled experiments across web, app, and lifecycle channels (email, push, landing pages).

**Audience:** Everyone running or contributing to an A/B test — Product Managers, Designers, Engineers, and Data Analysts.

**Goal:** Ship clean, decision-ready experiments with minimal complexity.

---

## What is A/B testing?

A/B testing is a way to compare two versions of something (A and B) to see which one works better for real users. You show Version A to some users and Version B to others, then measure which version leads to more of the result you care about — more signups, more clicks, more completed flows.

You can test many things: pages, forms, buttons, emails, messages, or full flows. Instead of guessing what users prefer and having endless opinion debates, you let real user behavior tell you which version is objectively better.

**When to use A/B testing:**
- You have sufficient traffic to reach statistical significance within 4 weeks
- You are optimizing an existing flow (signup, checkout, onboarding, landing page)
- The success metric is clearly measurable (clicks, conversions, retention)

**When NOT to use A/B testing:**
- Traffic is too low (tests would take months to reach significance)
- You're in discovery mode and don't know *why* users behave a certain way — use user research instead
- You're making a major pivot where the entire value proposition is changing

---

## Glossary

| Term | Definition |
|---|---|
| **Control (A)** | The current experience — the thing you're testing against |
| **Variant (B)** | The version being tested; what changes relative to Control |
| **Hypothesis** | A clear, testable statement: "If we [change X], then [metric Y] will [improve] because [reason]" |
| **Primary KPI** | The single metric that determines if the test wins or loses. One only. |
| **Secondary metrics** | Additional measures to help interpret results — not decision drivers |
| **Guardrails** | Critical metrics (error rate, load time, unsubscribes) that must NOT degrade. A guardrail breach kills the test immediately. |
| **MDE** | Minimum Detectable Effect — the smallest improvement worth the cost to implement and analyze. The "so what?" threshold. |
| **SRM** | Sample Ratio Mismatch — when your actual traffic split differs significantly from the intended split (e.g., 50/50 intended, but 10,000 vs. 8,500 actual). Indicates a technical bug. |
| **False positive** | You conclude the variant wins, but the difference was random chance. Controlled by your significance level (α). |
| **Unit of randomization** | The entity randomized into Control or Variant — prefer `user_id` over session or cookie for stability. |

---

## Roles & Ownership

Every experiment must have clear ownership to prevent zombie tests that confuse the whole team.

| Role | Responsibilities |
|---|---|
| **Experiment Owner** (PM / Designer) | Defines the hypothesis, MDE, and decision logic. Responsible for the final Ship / Kill decision and documenting results. |
| **Peer Reviewer** (PM, Designer, Engineer, or Analyst) | The sanity checker. Reviews the Pre-Test Checklist before launch to confirm the hypothesis is clear, KPIs are defined, and nothing obvious is missing. |
| **Implementer** (Engineer / PM / Data) | Instruments tracking, handles randomization, ensures feature flags are wired correctly. |
| **Analyst / QA** (Data / Peer PM) | Validates data quality (SRM checks), signs off on statistical interpretation. If the Experiment Owner also does the analysis, a third person must double-check the conclusion to prevent bias. |

---

## Product Guidance

**One variable at a time.** If you change copy *and* the image, and B wins — you won't know which drove it. Test one thing at a time.

**Small changes matter too.** Changing a button color or shortening a form label can move conversion. Don't only run big bets.

**Consider large variables.** Your test can be as small as button copy or as large as a completely redesigned page. Starting with bigger changes yields bigger signal before you optimize smaller details.

**Track beyond conversion rates.** A/B testing directly affects conversion, but track downstream metrics — leads, activation, retention — to see the full effect.

**Use two audiences of the same size and composition.** Randomize users into equal groups so the audiences are comparable. Don't manually select who sees which variant.

**Test at the same time.** Seasonality affects performance. If you run variant A in one period and variant B in another, you won't know if timing — not the change — drove the difference.

---

## The Experiment Lifecycle

### Phase 1 — Plan & Prioritize

**Prioritize with ICE scoring:**
- **Impact** — How much will this move the needle on business goals?
- **Confidence** — How sure are we this will work, based on data or research?
- **Ease** — How simple is it to implement?

Focus on tests that score high across all three. Avoid testing for the sake of testing.

**Check for test collisions.** Before launching, confirm your target audience doesn't overlap with other running experiments. Overlapping tests contaminate results and make interpretation impossible.

> **Tool:** Use [Step 0 — Idea Validator](https://ab-test-framework.streamlit.app/Idea_Validator) to route your idea and generate a structured brief if testing is warranted.

---

### Phase 2 — Design

**Decide what to test.** What specific element or flow are you changing?

**Define the objective.** Beyond conversion — what do you want to *learn* about how users interact with this?

**Write the hypothesis:**
> "If we [change X], then [metric Y] will [increase/decrease] because [reason]."

**Identify testable elements.** Landing pages, CTAs, email subject lines, form length, onboarding steps.

**Determine sample size and duration.** Use the calculator to find how many users you need per variant given your:
- Baseline conversion rate (pull the last 2–6 weeks of data for the same audience)
- Minimum Detectable Effect (MDE)
- Confidence level (95% standard; 90% for low-risk changes; 99% for high-stakes revenue flows)
- Power (80% standard; 90% for mission-critical tests)

**Setting MDE — three approaches:**
1. **Business impact threshold (best):** Ask "what's the smallest lift that justifies the dev time and analysis cost?" (e.g., +5% on signup rate)
2. **Time-boxed:** If you need results within 3 weeks, use the calculator to find the smallest MDE detectable in that window
3. **Benchmark-based:** For B2B SaaS, visitor-to-trial conversion typically runs 8–12%. A 5% relative MDE from a 10% baseline means looking for ≥10.5% — a 0.5pp absolute lift

**One-sided vs. two-sided test:**
- **Two-sided (default):** Detects improvement *and* harm. Use for any test where a negative result matters.
- **One-sided:** Only tests if the variant is better. Valid only if you pre-commit that you'll kill the test the moment it looks negative — and you stick to that rule.

Decide before you look at the data. Do not switch after.

> **Tool:** Use [Step 1 — Sample Size Calculator](https://ab-test-framework.streamlit.app/Sample_Size) to calculate required sample size and duration.

---

### Phase 3 — Approve & Implement

**Engineering implementation:**
- Set up feature flags and randomization logic
- Instrument tracking for all metrics: primary KPI, secondary metrics, guardrails
- Ensure proper user assignment to Control vs. Variant

**Peer review before launch:**
- Have another team member review the test configuration
- Verify tracking events fire correctly in both Control and Variant

**Pre-Test Checklist** (Experiment Owner must complete this before launch):

- [ ] Hypothesis written in "If [change], then [metric] will [improve] because [reason]" format
- [ ] Primary KPI defined — single metric that decides Ship vs. Kill
- [ ] Guardrail metrics listed (e.g., page load time, error rate, unsubscribe rate)
- [ ] MDE documented (e.g., "+5% relative improvement on signup rate")
- [ ] Test duration calculated — covers full business cycles including weekends
- [ ] Decision rule pre-committed — what result triggers Ship vs. Kill
- [ ] Target audience defined — confirmed NO collision with other running experiments
- [ ] Unit of randomization defined — prefer `user_id` over session ID

> **Tool:** Use [Step 3 — Workspace](https://ab-test-framework.streamlit.app/Workspace) to generate a shareable experiment brief and save to the registry.

---

### Phase 4 — Run & Monitor

**First 24–48 hours — essential data quality checks:**

**SRM Check:** If you split traffic 50/50, are actual assignments roughly 50/50?
- Green: 10,000 Control / 10,100 Variant (within ~2% tolerance)
- Red flag: 10,000 Control / 8,500 Variant → **STOP IMMEDIATELY** — indicates a technical bug

**Tracking validation:** Confirm primary KPI events fire in both variants. Check that conversion events are being logged. Confirm no broken tracking in either variant.

**Guardrail check:** Error rates, page load times, and other guardrails must remain stable.

**Visual QA:** Test the experience on mobile and desktop to confirm nothing is broken.

**Ongoing:**
- Monitor guardrail metrics daily
- Do **NOT** peek at primary results and make decisions before the planned duration ends

---

### Phase 5 — Stopping Rules & Decision

Stick to strict stopping rules to avoid p-hacking (stopping when results look favorable).

**Ship (Winner):**
- Minimum planned duration has been reached
- Result is statistically significant (≥95% confidence)
- All guardrail metrics are stable or improved
- Effect size meets or exceeds the pre-defined MDE

**Kill (Loser / Harm):**
- Immediate kill: guardrail breach detected (error rate spikes, revenue drops)
- After duration: test reached planned end date and result is negative or flat
- Futility: test has run long enough that reaching significance is impossible — don't extend "just to see"

**Kill (Inconclusive):**
- Planned duration ended but result is not statistically significant
- Do NOT ship — return to Control to maintain code cleanliness
- Document the learning and move on

**What NOT to do:**
- Do not stop early because you see a "win" on Day 3
- Do not extend the test indefinitely hoping for significance
- Do not change traffic allocation mid-test (e.g., 50% → 90%) — it breaks the statistical assumptions

> **Tool:** Use [Step 2 — Results Interpreter](https://ab-test-framework.streamlit.app/Results_Interpreter) for SRM check, frequentist analysis, Bayesian analysis, and a plain-English Ship / Kill verdict.

---

### Phase 6 — Document & Archive

A test is not complete until it is documented. This is your team's institutional memory — it stops you from re-testing old ideas and helps onboard new team members.

**Inconclusive results are not failures.** They mean you now know that hypothesis wasn't it, which is still progress. Kill the experiment, restore Control, and document the learning.

**Required documentation:**

| Field | What to include |
|---|---|
| Hypothesis | Original hypothesis statement |
| Visual evidence | Screenshots of Control (A) and Variant (B) |
| Result | Winner / Loser / Flat / Inconclusive |
| Metrics | Primary KPI result with confidence interval; secondary metrics; guardrails |
| Key learning | Why did it win/lose? What user behavior insight did we gain? |
| Decision | Shipped / Killed / No Action |
| Next steps | Follow-up tests or iterations planned |

Archive experiment summaries in your team's documentation system (Confluence, Notion, Linear, etc.).

> **Tool:** Use [Step 3 — Workspace](https://ab-test-framework.streamlit.app/Workspace) to generate a results one-pager and update the registry.

---

## Common Mistakes to Avoid

**Peeking at results and stopping early.** Looking at results on Day 2, seeing a "win," and stopping inflates false positive rates significantly. Wait for the full planned duration.

**Changing test parameters mid-flight.** Do not change traffic allocation, targeting rules, or variant designs during an active test. It invalidates the statistical assumptions.

**Ignoring seasonality.** Avoid running tests during atypical periods (holidays, major campaigns, end of quarter) unless you plan to always operate under those conditions.

**Not checking for SRM.** Failing to validate that your 50/50 split is actually 50/50 can mean you're analyzing a broken test. Always check SRM in the first 24 hours.

**Projecting your hypothesis onto results.** The results may not confirm your hypothesis, and that's fine. Don't reverse-engineer an interpretation to match what you expected.

**Looking only at quantitative data.** A/B tests give you the *what*. Pair with qualitative research (interviews, session recordings) to understand the *why*.

**Testing multiple variables at once.** If you change copy and images and the variant wins, you won't know which element drove the result.

---

## References

- [Futility Stopping Rules in A/B Testing](https://www.evanmiller.org/how-not-to-run-an-ab-test.html)
- [Don't Stop Your A/B Tests Partway Through](https://www.evanmiller.org/how-not-to-run-an-ab-test.html)
- [Sample Ratio Mismatch — What It Is and How to Fix It](https://monetate.com/resource/sample-ratio-mismatch-ab-testing/)
- [Are You Stopping Your A/B Tests Too Early?](https://www.kameleoon.com/blog/stopping-ab-tests-too-early)
- [SaaS Conversion Rate Benchmarks](https://www.eleken.co/blog-posts/saas-conversion-rates)
