# Response Evaluation Rubric

**Purpose:** Define how to evaluate the quality of AmazonHelp's responses.

**Scope:** This rubric will be used by both humans and LLM-as-judge in Phase 4.

---

## Overview

Each brand response is evaluated on multiple independent dimensions:
1. **Correctness** — Is the answer accurate?
2. **Relevance** — Does it address the customer's actual problem?
3. **Completeness** — Are all necessary steps provided?
4. **Groundedness** — Is it based on what the brand actually said?
5. **Clarity** — Is the response understandable?
6. **Actionability** — Can the customer actually act on it?
7. **Tone** — Is it appropriately professional and empathetic?
8. **Safety** — Does it avoid harm or policy violations?

---

## Evaluation Scale

Use a **4-point scale** for each dimension:

| Score | Definition |
|-------|-----------|
| 4 | **Excellent** — Exemplary in this dimension; sets the standard |
| 3 | **Good** — Meets expectations; solid response |
| 2 | **Fair** — Has issues but partially acceptable |
| 1 | **Poor** — Significant problems; below acceptable |

---

## Dimension Definitions

### 1. CORRECTNESS

**Definition:** The information provided is accurate and factually correct.

**Score 4 — Excellent:**
- All facts are verified and accurate
- References correct policies, procedures, or troubleshooting
- Numbers, dates, links all correct
- No misinformation

**Score 3 — Good:**
- Information is generally accurate
- Minor imprecision that doesn't mislead
- Appropriate level of detail

**Score 2 — Fair:**
- Some factual errors or outdated information
- Partially misleading but contains truth
- Could confuse the customer

**Score 1 — Poor:**
- Significantly inaccurate or wrong
- Provides false information
- Contradicts brand's own policies
- Harmful misinformation

**Examples:**
```
Customer: "Where is my order?"
❌ POOR: "Your package is in Denver" (guessing, no tracking given)
✓ GOOD: "Your tracking shows in transit, ETA Dec 3rd"
```

---

### 2. RELEVANCE

**Definition:** The response directly addresses the customer's stated problem.

**Score 4 — Excellent:**
- Directly solves the stated issue
- No irrelevant tangents
- Clearly relates to customer's problem

**Score 3 — Good:**
- Addresses main problem plus relevant context
- Minor tangents OK
- Stays on topic

**Score 2 — Fair:**
- Partially relevant; misses some aspects
- Answers related question instead
- Customer may feel unheard

**Score 1 — Poor:**
- Completely off-topic or irrelevant
- Addresses different problem
- Makes customer feel ignored

**Examples:**
```
Customer: "My order is late. Where is it?"

❌ POOR: "Did you know we have a sale on similar items?"
✓ GOOD: "I understand you're concerned. Your tracking shows..."
```

---

### 3. COMPLETENESS

**Definition:** All necessary information or steps to resolve the issue are provided.

**Score 4 — Excellent:**
- All steps to resolve provided
- Customer can act immediately
- Covers edge cases or next steps

**Score 3 — Good:**
- Main steps provided
- Customer can act on it
- Minor gaps don't prevent resolution

**Score 2 — Fair:**
- Some steps missing
- Customer might need follow-up
- Incomplete but partially useful

**Score 1 — Poor:**
- Critical steps missing
- Customer cannot act without more info
- Leaves problem unresolved

**Examples:**
```
Customer: "How do I return this?"

❌ POOR: "Returns are accepted."
✓ GOOD: "Go to [link], print label, drop at [locations], refund processes in 5-7 days"
```

---

### 4. GROUNDEDNESS

**Definition:** The response is grounded in what the brand actually said/did, not hallucinated.

**Score 4 — Excellent:**
- Cites actual policies, links, procedures
- Quotes or references real brand information
- Verifiable claims

**Score 3 — Good:**
- Based on real brand policies
- General statements that are accurate
- Reasonable inference from known facts

**Score 2 — Fair:**
- Some grounded info mixed with vague statements
- Generic info that may not apply
- Educated guess that could be wrong

**Score 1 — Poor:**
- Contains made-up information
- Fabricated policies or procedures
- Hallucinated links or details

**Examples:**
```
Customer: "What's your return policy?"

❌ POOR: "We accept returns up to 60 days" (if actual policy is 30)
✓ GOOD: "Per our policy, most items can be returned within 30 days..."
```

---

### 5. CLARITY

**Definition:** The response is easy to understand and unambiguous.

**Score 4 — Excellent:**
- Crystal clear and unambiguous
- Well-structured and easy to follow
- Jargon explained if used

**Score 3 — Good:**
- Clear enough to understand
- Minor unclear phrases
- Generally well-organized

**Score 2 — Fair:**
- Some confusion possible
- Requires re-reading to understand
- Organization could be better

**Score 1 — Poor:**
- Confusing or hard to parse
- Ambiguous or contradictory
- Customer is likely confused

**Examples:**
```
Customer: "How long will refund take?"

❌ POOR: "It depends on various circumstances and the modality of processing..."
✓ GOOD: "Refunds typically process in 5-7 business days after we receive the return."
```

---

### 6. ACTIONABILITY

**Definition:** The customer can actually take action based on the response.

**Score 4 — Excellent:**
- Clear next steps the customer can take
- Links, buttons, or specific instructions
- Customer knows exactly what to do

**Score 3 — Good:**
- Customer can figure out what to do
- Steps are reasonably clear
- May require minor effort to interpret

**Score 2 — Fair:**
- Customer can probably act, but it's not obvious
- Requires some inference or additional searching
- Might need follow-up

**Score 1 — Poor:**
- No clear action for customer to take
- Response doesn't enable resolution
- Customer is stuck

**Examples:**
```
Customer: "I need to reset my password."

❌ POOR: "You can reset your password if needed."
✓ GOOD: "Click 'Forgot Password' at [link], enter your email, check for reset link."
```

---

### 7. TONE

**Definition:** The response is appropriately professional, empathetic, and respectful.

**Score 4 — Excellent:**
- Empathetic and understanding
- Professional without being cold
- Acknowledges customer's frustration
- Respectful and helpful

**Score 3 — Good:**
- Neutral professional tone
- Not cold or dismissive
- Acceptable customer service tone

**Score 2 — Fair:**
- Slightly cold or dismissive
- Missing empathy
- Could offend sensitive customers

**Score 1 — Poor:**
- Rude, sarcastic, or condescending
- Dismissive of customer's concern
- Unprofessional or hostile

**Examples:**
```
Customer: "This is really frustrating!"

❌ POOR: "If you'd read the instructions, you wouldn't have this problem."
✓ GOOD: "I understand this is frustrating. Let me help you get this resolved."
```

---

### 8. SAFETY & POLICY

**Definition:** The response follows brand policy and avoids harm or inappropriate content.

**Score 4 — Excellent:**
- Follows all policies exactly
- Safe and appropriate
- No risky recommendations
- Respects privacy/security

**Score 3 — Good:**
- Follows policy
- No safety concerns
- Appropriate content

**Score 2 — Fair:**
- Minor policy deviation
- Slight risk or boundary issue
- Could be problematic

**Score 1 — Poor:**
- Violates policy
- Unsafe recommendation
- Inappropriate content
- Privacy/security violation

**Examples:**
```
Customer asks for another customer's order details.

❌ POOR: "Sure, here's customer XYZ's address and order history."
✓ GOOD: "I can't share another customer's information for privacy reasons."
```

---

## Overall Quality Score

After evaluating all 8 dimensions:

**Excellent Response (28-32 points):**
- All dimensions 3 or higher
- No score of 1
- Exemplary service

**Good Response (22-27 points):**
- Most dimensions 3 or higher
- At most one dimension is 2
- Acceptable service

**Fair Response (16-21 points):**
- Mixed results
- Multiple dimensions at 2
- Some significant issues
- Could be improved

**Poor Response (8-15 points):**
- Multiple dimensions at 1 or 2
- Significant problems
- Below acceptable standard

---

## Evaluation Process

### For Each Brand Response:

1. **Read the customer's problem** — Understand what they're asking
2. **Read the brand's response** — Full response in context
3. **Score each dimension** — Use 4-point scale
4. **Calculate total** — Sum of 8 dimensions (max 32)
5. **Add notes** — Explain your scores
6. **Classify overall** — Excellent/Good/Fair/Poor

### Notes to Include:

- Why you gave certain scores
- Specific strengths of the response
- Specific weaknesses
- What would improve it

---

## Common Scenarios

### Scenario: Customer gets helpful tracking info

```
Correctness: 4 (tracking number accurate)
Relevance: 4 (directly answers question)
Completeness: 3 (has tracking, but no next steps)
Groundedness: 4 (real tracking link)
Clarity: 4 (clear and simple)
Actionability: 4 (customer can click link)
Tone: 3 (neutral, slightly formulaic)
Safety: 4 (no issues)

Total: 30/32 = Excellent
```

### Scenario: Vague troubleshooting advice

```
Correctness: 2 (generic, may not apply)
Relevance: 2 (addresses symptom, not root)
Completeness: 1 (steps are too vague)
Groundedness: 2 (generic info, not specific)
Clarity: 2 (hard to follow)
Actionability: 1 (customer can't follow steps)
Tone: 3 (polite enough)
Safety: 3 (no risk)

Total: 16/32 = Fair (needs improvement)
```

---

## When Using with LLM Judge

In Phase 4, this rubric will be used by an LLM to evaluate generated responses.

**The LLM will:**
- Score each dimension independently
- Provide reasoning for each score
- Calculate total score
- Classify as Excellent/Good/Fair/Poor

**Humans will:**
- Review LLM scores for plausibility
- Provide ground-truth scores for subset
- Measure LLM-human agreement

---

## Important Notes

- **Each dimension is independent** — A response can be relevant but unclear
- **No perfect response** — Even good responses have room for improvement
- **Context matters** — A response appropriate for FAQ may not work for escalation
- **Consistency is key** — Apply standards uniformly across all responses

---

Thank you for careful evaluation!
