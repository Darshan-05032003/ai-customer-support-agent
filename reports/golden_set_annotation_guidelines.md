# Golden Set Annotation Guidelines

**Purpose:** Guide human annotators in labeling customer support conversations for evaluation.

**Annotator Role:** You are labeling what the CUSTOMER's actual problem is, not judging the brand's response.

---

## Overview

Each conversation consists of:
1. **Customer messages** — The customer's statements/questions/complaints
2. **Brand responses** — AmazonHelp's replies
3. **Full context** — All messages in chronological order

Your job: Assign an **intent** label to each customer's primary problem.

---

## Step 1: Read the Full Conversation

**Before assigning any label:**
- Read all customer messages
- Read all brand responses
- Understand the conversation flow
- Note any changes in the customer's stated problem

**Pay attention to:**
- What is the customer's FIRST stated issue?
- Does the issue change or evolve?
- Is there frustration, escalation, or persistence?

---

## Step 2: Identify the Primary Intent

**Primary intent** is the main customer problem that started the conversation.

**Choose ONE** from the taxonomy (or OTHER_UNCLEAR if none fit).

**Do NOT infer intent from brand response alone.** Use customer's own words.

**Example:**
```
Customer: "My order hasn't arrived. It's been 3 weeks."
Brand: "We'll investigate. Can you provide..."
Customer: "Also, I was charged twice."

Primary intent: ORDER_STATUS (the originating problem)
Secondary: PAYMENT_BILLING (emerged later)
```

---

## Step 3: Assign Secondary Intent (If Applicable)

If the conversation involves a second distinct problem:
- **Primary intent:** Main issue
- **Secondary intent:** Additional issue that emerged

**Leave secondary_intent as null if only one issue.**

---

## Step 4: Mark Ambiguity

**is_ambiguous = True if:**
- Multiple valid interpretations of the intent
- Insufficient context to determine intent
- Customer statement is unclear or contradictory
- Intent could reasonably belong to 2+ categories

**is_ambiguous = False if:**
- Clear, unambiguous customer statement
- Intent is obvious from context

---

## Step 5: Assess Escalation Requirement

**INDEPENDENT OF INTENT** — Escalation is a separate label.

**escalation_required = True if:**
- Customer explicitly requests human/supervisor assistance
- Issue involves account security or fraud
- Refund/payment dispute (policy-sensitive)
- Customer shows extreme frustration after multiple failed attempts
- Brand lacks authority to resolve
- Issue requires access to customer's account/payment info

**escalation_required = False if:**
- Issue can be self-serve (tracking info, FAQ, etc.)
- Brand provided solution that customer accepted
- Routine troubleshooting resolved the issue
- Single-contact resolution occurred

**IMPORTANT:** Do NOT assume escalation based on tone alone.
Some frustrated customers can be satisfied without escalation.

---

## Intent Taxonomy

**DO NOT use intent keywords as definitions.**

### 1. ORDER_STATUS
**Definition:** Customer is asking about status, tracking, or delivery timeline of an order.

**Include:**
- "Where is my order?"
- "When will it arrive?"
- "How do I track it?"
- "What's the delivery date?"

**Exclude:**
- Order hasn't arrived YET (→ LATE_DELIVERY if complaining)
- Item is missing from order (→ MISSING_ITEM)
- Wrong item received (→ WRONG_ITEM)

### 2. LATE_DELIVERY
**Definition:** Customer is complaining that delivery is delayed beyond expected/promised date.

**Include:**
- "It was supposed to arrive yesterday"
- "Still not here and it's been 2 weeks"
- "Why is this taking so long?"

**Exclude:**
- Just asking status (→ ORDER_STATUS)
- Item is missing entirely (→ MISSING_ITEM)
- Item arrived damaged (→ DAMAGED_ITEM)

### 3. MISSING_ITEM
**Definition:** Customer ordered something, delivery arrived, but something from the order is missing.

**Include:**
- "I ordered 2 items but only got 1"
- "The case wasn't in the box"
- "My order is incomplete"

**Exclude:**
- Item never arrived (→ LATE_DELIVERY)
- Item arrived but is broken (→ DAMAGED_ITEM)

### 4. DAMAGED_ITEM
**Definition:** Ordered item arrived in broken or non-functional condition.

**Include:**
- "Product arrived broken"
- "Screen is shattered"
- "Doesn't work out of box"

**Exclude:**
- Item is missing (→ MISSING_ITEM)
- Item doesn't meet expectations (→ PRODUCT_QUALITY)

### 5. REFUND_RETURN
**Definition:** Customer wants refund or to return an item.

**Include:**
- "I want my money back"
- "How do I return this?"
- "Can I get a refund?"
- "Want to return the item"

**Exclude:**
- Already received refund (resolved)
- Disputing the refund amount (→ PAYMENT_BILLING)

### 6. PAYMENT_BILLING
**Definition:** Charges, billing errors, incorrect amounts, payment method issues.

**Include:**
- "I was charged twice"
- "This price is wrong"
- "Why is my card declining?"
- "Billing shows wrong amount"

**Exclude:**
- Asking for refund (→ REFUND_RETURN)
- Subscription charges (→ SUBSCRIPTION)

### 7. ACCOUNT_LOGIN
**Definition:** Problems accessing account, forgotten password, login issues.

**Include:**
- "I can't log in"
- "Forgot my password"
- "My account is locked"
- "Can't access my account"

**Exclude:**
- Security concern (→ ACCOUNT_SECURITY)
- Account payment (→ PAYMENT_BILLING)

### 8. ACCOUNT_SECURITY
**Definition:** Account compromised, fraud, unauthorized access, data breach concern.

**Include:**
- "Someone accessed my account"
- "My account was hacked"
- "Unauthorized charges"
- "Password was exposed"

**Exclude:**
- Forgot password (→ ACCOUNT_LOGIN)
- Billing issue (→ PAYMENT_BILLING)

### 9. SUBSCRIPTION
**Definition:** Prime membership or subscriptions (activation, cancellation, renewal, charges).

**Include:**
- "How do I cancel Prime?"
- "Is Prime worth it?"
- "Subscription was charged"
- "How do I get Prime?"

**Exclude:**
- One-time order (→ ORDER_STATUS)
- Billing issue (→ PAYMENT_BILLING)

### 10. PRODUCT_INFORMATION
**Definition:** Asking about product details, availability, specifications, compatibility.

**Include:**
- "What color does it come in?"
- "Is this in stock?"
- "What are the specs?"
- "Does it work with...?"

**Exclude:**
- Already purchased and having issues (→ other intents)

### 11. TECHNICAL_ISSUE
**Definition:** Website, app, or digital service not working correctly.

**Include:**
- "Website is down"
- "App keeps crashing"
- "Can't complete checkout"
- "Search doesn't work"

**Exclude:**
- Account login (→ ACCOUNT_LOGIN)
- Service quality complaint (→ SERVICE_QUALITY)

### 12. SHIPPING_ADDRESS
**Definition:** Address incorrect, needs to change delivery location, wrong address used.

**Include:**
- "Send it to a different address"
- "I gave you the wrong address"
- "Please update my address"

**Exclude:**
- Order hasn't arrived (→ LATE_DELIVERY)
- Delivery to wrong location occurred (→ WRONG_DELIVERY)

### 13. SERVICE_QUALITY
**Definition:** General complaint about brand's service quality, response times, customer support experience.

**Include:**
- "Your customer service is terrible"
- "I've been waiting for a response"
- "Very slow support"
- "Poor experience with your team"

**Exclude:**
- Specific product issue (→ product-related intents)
- Specific process problem (→ other intents)

### OTHER_UNCLEAR
**Definition:** Use ONLY if:**
- Message is in a language you cannot understand
- Text is too garbled to parse
- Intent truly doesn't fit any category
- No clear customer problem statement

**If you select OTHER_UNCLEAR:**
- Explain in annotator_notes
- Describe what you'd need to classify it

---

## Common Boundary Cases

### ORDER_STATUS vs. LATE_DELIVERY
- **ORDER_STATUS:** "Where is my order?" or "When will it arrive?"
- **LATE_DELIVERY:** "It was supposed to be here 3 days ago!"
→ **Rule:** If customer is complaining about the DELAY, use LATE_DELIVERY

### DAMAGED_ITEM vs. PRODUCT_QUALITY
- **DAMAGED_ITEM:** "Arrived broken"
- **PRODUCT_QUALITY:** "Doesn't work as advertised" or "Battery drains fast"
→ **Rule:** Physical damage = DAMAGED_ITEM; functionality mismatch = PRODUCT_QUALITY

### REFUND_RETURN vs. PAYMENT_BILLING
- **REFUND_RETURN:** "I want a refund"
- **PAYMENT_BILLING:** "I was refunded $50 but should have been $75"
→ **Rule:** Requesting return = REFUND; disputing amount = PAYMENT_BILLING

### ACCOUNT_LOGIN vs. ACCOUNT_SECURITY
- **ACCOUNT_LOGIN:** "I forgot my password"
- **ACCOUNT_SECURITY:** "Someone else accessed my account"
→ **Rule:** Locked out by mistake = LOGIN; compromised = SECURITY

---

## Annotator Notes

For every conversation, add brief notes such as:
- Why you chose this intent
- If ambiguous, what would clarify it
- If escalation needed, why
- Any unusual aspects of the conversation

**Example notes:**
- "Clear order status question, resolved with tracking link"
- "Ambiguous — could be LATE_DELIVERY or DAMAGED_ITEM, but customer never clarified"
- "Escalation needed — customer demanded supervisor after 3 failed attempts"

---

## Quality Checklist

Before submitting your annotation:

- [ ] I read the full conversation, not just first message
- [ ] I labeled the CUSTOMER'S problem, not my opinion of the brand response
- [ ] I assigned PRIMARY_INTENT only (null secondary unless truly 2 problems)
- [ ] I considered ambiguity honestly
- [ ] I assessed escalation independently
- [ ] I added notes explaining my reasoning
- [ ] If I used OTHER_UNCLEAR, I explained why

---

## When in Doubt

1. **Re-read the customer's own words** — Avoid inferring intent from brand response
2. **Use the simplest category** — If it fits multiple, choose the most specific
3. **Check boundaries** — Review similar intents above
4. **Mark ambiguous** — If you're uncertain, say so (don't guess)
5. **Ask for clarification** — In notes, describe what would help

---

## Submission

When done:
- Ensure all fields are filled (null is OK for secondary intent)
- Review annotator_notes for clarity
- Submit for review

Thank you for your careful labeling!
