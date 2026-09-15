# Escalation Annotation Guidelines

**Purpose:** Define when a customer support issue should be escalated to a human agent.

**This is INDEPENDENT from intent classification.**

---

## Definition of Escalation

**An issue requires escalation when:**
- The automated/first-line response cannot resolve it
- It requires human judgment, policy decision, or account access
- The customer explicitly requests human assistance
- The situation has become emotionally charged or adversarial

**An issue does NOT require escalation when:**
- Self-service information satisfies the customer
- Automated processes can fully resolve it
- The customer accepted the brand's solution

---

## Escalation Criteria

### 1. EXPLICIT REQUEST FOR HUMAN ASSISTANCE

**Mark escalation = TRUE if:**
- Customer says: "I want to speak to a manager/supervisor/human"
- "Get me a real person"
- "This is not acceptable, escalate this"
- "I need to speak to someone with authority"

**Example:**
```
Customer: "I've tried everything. I need someone who can actually fix this."
Brand: "Let me troubleshoot with you..."
Customer: "No. I want a manager."
→ ESCALATE = TRUE
```

---

### 2. SECURITY OR FRAUD CONCERNS

**Mark escalation = TRUE if:**
- Account compromised or breach suspected
- Unauthorized charges or access
- Payment card fraud
- Data privacy concern
- Suspicious account activity

**Example:**
```
Customer: "Someone charged my card without permission"
→ ESCALATE = TRUE (requires account investigation)
```

---

### 3. POLICY-SENSITIVE REFUNDS/DISPUTES

**Mark escalation = TRUE if:**
- Refund amount disputed by customer
- Return policy exception requested
- Warranty claim requiring verification
- Customer challenges decision policy
- High-value transaction involved

**Example:**
```
Customer: "You said refund takes 5 days, but I haven't received it after 2 weeks."
→ ESCALATE = TRUE (requires account access and investigation)
```

---

### 4. REPEATED FAILED RESOLUTION ATTEMPTS

**Mark escalation = TRUE if:**
- Same issue already attempted 2+ times
- Customer has contacted support multiple times
- Brand's solutions haven't worked
- Brand lacks authority to fully resolve

**Example:**
```
Message 1: Customer: "Feature doesn't work." Brand: "Try this."
Message 3: Customer: "Still doesn't work." Brand: "Try this other way."
Message 5: Customer: "NOTHING HAS WORKED."
→ ESCALATE = TRUE (needs technical specialist or compensation)
```

---

### 5. EXTREME FRUSTRATION OR THREAT

**Mark escalation = TRUE if:**
- Customer threatens legal action
- Customer threatens public complaint/review
- Customer expresses extreme frustration after multiple attempts
- Customer is becoming abusive (though brand still tries to help)

**IMPORTANT:** Not every upset customer needs escalation.
- A frustrated customer can sometimes be satisfied with ONE good response
- Escalation is not punishment; it's redirecting to better resources

**Example (escalate):**
```
Customer: "I've wasted 3 hours of my time on this. This is unacceptable."
(After 3 failed troubleshooting attempts)
→ ESCALATE = TRUE
```

**Example (do NOT escalate):**
```
Customer: "This is frustrating!" 
(But it's their first contact and problem is simple)
→ ESCALATE = FALSE (one good response should help)
```

---

### 6. ACCOUNT ACCESS OR DATA RETRIEVAL NEEDED

**Mark escalation = TRUE if:**
- Customer needs account modification
- Payment method requires updating
- Personal data needs verification
- Subscription changes need confirmation
- High-risk account changes

**Example:**
```
Customer: "Can you update my address on file?"
→ ESCALATE = TRUE (security: must verify customer identity)
```

---

### 7. UNSOLVABLE BY POLICY

**Mark escalation = TRUE if:**
- Exception to policy needed
- Brand's standard answer doesn't fit
- Customer situation is outside normal scope
- Creative solution required

**Example:**
```
Customer: "My package was delivered to wrong house, neighbor won't return it."
→ ESCALATE = TRUE (requires non-standard resolution)
```

---

## Escalation Criteria Reference Table

| Scenario | Escalate? | Why |
|----------|-----------|-----|
| Forgot password | NO | Self-service reset |
| Account hacked | YES | Requires investigation |
| Tracking number question | NO | Self-service info |
| Order arrived wrong address | YES | May need reship/exception |
| Confused about features | NO | Support info sufficient |
| Repeated failed troubleshooting | YES | Needs specialist |
| Simple refund request | NO | Standard process |
| Refund amount disputed | YES | Policy exception |
| Wants to change delivery address | MAYBE | If time-sensitive, YES |
| Extremely frustrated (1st attempt) | NO | Try one good response |
| Extremely frustrated (3rd attempt) | YES | Needs fresh approach |
| Threatens lawsuit | YES | Legal sensitivity |
| Just wants to vent | NO | Empathetic response OK |

---

## What Does NOT Require Escalation

❌ Customer doesn't like the answer (even if upset)  
❌ Customer needs information you can provide  
❌ Simple troubleshooting can resolve it  
❌ First contact with this issue  
❌ Customer is just frustrated (not abusive)  
❌ One skilled response will likely resolve it  

---

## Annotation Process

1. **Read the full conversation**
2. **Ask:** Has this issue been tried before?
3. **Ask:** Is this a security/fraud/policy issue?
4. **Ask:** Did customer explicitly ask for escalation?
5. **Ask:** Has troubleshooting failed multiple times?
6. **Ask:** Does this need human judgment or account access?

If ANY answer is YES → mark `escalation_required = TRUE`

---

## Annotator Notes for Escalation

Always explain your escalation decision:
- "Escalate because: third failed troubleshooting attempt"
- "Escalate because: security issue requires account investigation"
- "Do NOT escalate because: one helpful response should resolve"

---

## Important Principles

1. **Escalation ≠ Failure**
   - A good support system recognizes when to escalate
   - Not every issue can be solved instantly
   - Human judgment has value

2. **Escalation ≠ Punishment**
   - Don't escalate to "teach them a lesson"
   - Escalate because it HELPS the customer

3. **Escalation ≠ Ambiguity**
   - If you're unsure whether it needs escalation, mark it
   - Note your uncertainty in annotator_notes

4. **Timing Matters**
   - Escalate WHEN the issue becomes unresolvable
   - Not necessarily at the first sign of frustration

---

## Final Checklist

- [ ] Did I read the FULL conversation?
- [ ] Is this security, fraud, or policy-sensitive?
- [ ] Has the issue been tried multiple times without resolution?
- [ ] Does it require human judgment or account access?
- [ ] Did the customer explicitly ask for help?
- [ ] Did I note my reasoning in annotator_notes?

---

Thank you for careful escalation judgment!
