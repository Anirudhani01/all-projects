
---

## 🔄 Acceptance Criteria–Driven Refinement Loop

### Step 1. Input

* *Fixed*: User Story + Acceptance Criteria
* *Variable*: Generated Test Cases (initial draft)

---

### Step 2. Validation

Run validation:


Validation completed: 50% satisfaction rate


* If ≥ 90% → ✅ Done
* If < 90% → Go to Step 3

---

### Step 3. Gap Analysis (Reflection)

Ask LLM:

* Which acceptance criteria are *not satisfied*?
* Why are they not covered by test cases?
* What kind of test case is missing (happy, negative, edge)?

---

### Step 4. Targeted Test Case Generation (Action)

* Generate *only missing/weak test cases*.
* Don’t regenerate everything — focus on uncovered criteria.
* Example:

  * Thought: "Criterion requires invalid email check, no test case exists."
  * Action: Generate test case for invalid email input.

---

### Step 5. Re-Validation (Observation)

Re-run validation with updated test cases.

* Get new satisfaction rate.
* If still < 90%, go back to Step 3.

---

### Step 6. Exit Conditions

* Stop when satisfaction ≥ 90%.
* Or when max iterations (say 3–5 loops) are reached → escalate to human review.

---

## 🖼 Flow Diagram (Text Form)


 User Story + Acceptance Criteria (fixed)
                   │
                   ▼
         Initial Test Case Generation
                   │
                   ▼
            Validation Engine
                   │
       ┌───────────┴────────────┐
       │ Satisfaction ≥ 90% ?   │
       └───────┬───────┬────────┘
               │       │
             Yes       No
               │       │
               ▼       ▼
           ✅ Done   Gap Analysis
                        │
                        ▼
           Targeted Test Case Generation
                        │
                        ▼
                  Re-Validation
                        │
                        └─── Loop back


---

👉 So the loop is basically a *ReAct cycle*:

* *Thought (Reflection):* Identify uncovered criteria.
* *Action:* Generate missing test cases.
* *Observation:* Re-check validation.
* *Repeat* until ≥ 90%.