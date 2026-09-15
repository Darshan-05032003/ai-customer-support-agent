# Intent Taxonomy for AmazonHelp Customer Support

**Discovery Date:** September 16, 2026  
**Data Source:** 162,562 customer messages from reconstructed conversations  
**Methodology:** Semantic pattern-based discovery with manual refinement

---

## Executive Summary

Analysis of 162,562 customer messages from the AmazonHelp Twitter support channel identified **12 natural support intent categories**. These categories represent distinct customer needs and problems that require different support responses.

**Key Finding:** The distribution is heavily skewed toward general inquiries (52.6%), followed by order logistics issues (order status 14.8% + delivery issues 8.9%). This suggests a need for robust triage to distinguish between information requests and problem resolution.

---

## Intent Categories

### 1. GENERAL_INQUIRY (52.6%, 85,518 messages)

**Definition:** Customer reaching out for general help, acknowledgment, or non-specific assistance. Includes thank-yous, expressions of frustration without specific problem, or messages too ambiguous to categorize.

**Inclusion Criteria:**
- Contains "help" or "need" without specific issue
- Expressions of gratitude or thanks
- Vague frustration without specific problem
- Follow-up messages or acknowledgments
- Off-topic or non-English messages

**Exclusion Criteria:**
- Messages with clear, specific problem (use appropriate category)
- Direct questions about order, account, or product

**Typical Language:**
- "thanks", "help please", "need assistance", "frustrated", "unacceptable"
- Japanese, Spanish, or other non-English messages
- Generic complaints without details

**Examples:**
```
"amazonのfiretvstickが見れない😢"
"ありがとうございます。 今、電話で主人が対応していただいてます。"
"@amazonhelp help please!"
```

**Support Response Type:** Triage to specific team or request clarification

---

### 2. ORDER_STATUS (14.8%, 24,102 messages)

**Definition:** Customer inquiring about the status, tracking number, or location of an existing order. Includes questions about when order will arrive, where to find tracking info, or how to check order progress.

**Inclusion Criteria:**
- Explicit questions about "where is my order"
- Asking for tracking number or tracking status
- "Order number", "order status" in message
- Asking when order will arrive
- Requests to check/look up specific order

**Exclusion Criteria:**
- Problem with delivery (late, missing) → DELIVERY_ISSUE
- Problem with order contents (wrong item, damaged) → specific category
- General order questions → might be PRODUCT_INFORMATION

**Typical Language:**
- "tracking", "where", "status", "when", "order number", "ETA"
- "can you check", "what's the status", "where is my order"

**Examples:**
```
"3 different people have given 3 different answers and i still don't have my order"
"status of my order 112-6293285-6789803?"
"what's the tracking number for order ABC123?"
```

**Support Response Type:** Provide tracking link, current status, ETA

---

### 3. DELIVERY_ISSUE (8.9%, 14,403 messages)

**Definition:** Customer reporting that delivery is late, package didn't arrive, or delivery has a problem. Includes issues with delivery date, missing packages, late arrivals, or delivery-specific failures.

**Inclusion Criteria:**
- "Not delivered" or "didn't arrive"
- "Late delivery" or "delayed"
- Package marked delivered but not received
- Missing from expected delivery location
- Delivery date changed/uncertain

**Exclusion Criteria:**
- Damaged/defective on arrival → DAMAGED_ITEM
- Wrong item delivered → different category
- General concern about logistics → ORDER_STATUS

**Typical Language:**
- "late delivery", "not delivered", "didn't arrive", "still waiting", "missed delivery"
- "late", "delayed", "no delivery date", "out for delivery" (but never arrived)

**Examples:**
```
"i'm never using amazon again! after waiting in all day as item is 'out for delivery', they've only gone and sent it to the wrong address"
"late delivery again! this is the 3rd time"
"says delivered saturday, was not"
```

**Support Response Type:** Investigate delivery, file claim, offer replacement or refund

---

### 4. PRIME_SUBSCRIPTION (4.4%, 7,200 messages)

**Definition:** Customer inquiring about, managing, or complaining about Prime membership or subscription benefits. Includes questions about membership status, cancellation, renewal, or benefits.

**Inclusion Criteria:**
- "Prime" + membership/subscription/cancel/benefit
- Questions about Prime benefits or eligibility
- Requests to cancel/modify Prime
- Complaints about Prime service
- Subscription management questions

**Exclusion Criteria:**
- General service complaint → CUSTOMER_SERVICE_COMPLAINT
- Specific issue while using Prime feature → specific category

**Typical Language:**
- "prime", "membership", "cancel", "subscription", "renew", "benefit", "prime member"
- "why pay for prime", "cancel my subscription"

**Examples:**
```
"i haven't even used prime in almost 3 months, how do i cancel?"
"time to cancel my amazon prime membership"
"why has prime become so unreliable?"
```

**Support Response Type:** Explain benefits, process cancellation, offer retention offer

---

### 5. ACCOUNT_LOGIN (4.1%, 6,734 messages)

**Definition:** Customer having trouble accessing their account, logging in, resetting password, or managing account credentials.

**Inclusion Criteria:**
- "Can't login" or "login issue"
- "Forgot password" or "reset password"
- Account access problems
- Can't remember email for account
- Account locked or not recognized

**Exclusion Criteria:**
- Account security concern (fraud/hack) → escalation
- General account question → other category
- Billing account issue → BILLING_PAYMENT

**Typical Language:**
- "password", "login", "log in", "access", "account", "forgot", "reset", "email"
- "can't login", "won't recognize", "can't remember"

**Examples:**
```
"i don't remember the email address i used. can you look up the account by my bank information?"
"it's not allowing me to update it to register my new amazon account"
```

**Support Response Type:** Send password reset link, verify identity, unlock account

---

### 6. TECHNICAL_ISSUE (3.6%, 5,856 messages)

**Definition:** Customer reporting technical problems with website, mobile app, or service platform. Includes crashes, slowness, broken features, or service outages.

**Inclusion Criteria:**
- Website or app not working
- Error messages or crashes
- Page loading issues
- Feature broken or unavailable
- Service slow or unresponsive

**Exclusion Criteria:**
- Order/delivery/product issue → specific category
- Account login problem → ACCOUNT_LOGIN
- General service complaint → CUSTOMER_SERVICE_COMPLAINT

**Typical Language:**
- "app", "website", "technical", "error", "crash", "broken", "slow", "bug", "issue"
- "won't load", "keeps crashing", "error message"

**Examples:**
```
"please spend time & money to fix your app. constant issues with it"
"website is down again"
"getting error 500 when trying to checkout"
```

**Support Response Type:** Troubleshoot, provide workaround, escalate to engineering

---

### 7. REFUND_RETURN (3.2%, 5,228 messages)

**Definition:** Customer requesting or inquiring about refund, return, or the return process. Includes questions about how to return items and asking for refunds.

**Inclusion Criteria:**
- Requesting refund for order
- Asking how to return item
- Return process questions
- Refund status inquiry
- "Return" or "refund" in message with intent to get money back

**Exclusion Criteria:**
- Problem requiring refund (wrong item, damaged) → specific problem category
- Just mentioning refund was processed (no request) → GENERAL_INQUIRY

**Typical Language:**
- "refund", "return", "money back", "how to return", "return process", "refunded"
- "want refund", "refund status", "can i return"

**Examples:**
```
"how do i return this? and how long until refund?"
"i need a refund"
"what's your return process?"
```

**Support Response Type:** Provide return label/instructions, initiate refund, check refund status

---

### 8. CUSTOMER_SERVICE_COMPLAINT (3.0%, 4,918 messages)

**Definition:** Customer expressing dissatisfaction with Amazon's customer service quality, responsiveness, or support experience. Meta-complaints about support process.

**Inclusion Criteria:**
- Complaints about support responsiveness
- Frustration with previous support interaction
- Criticism of customer service quality
- "Terrible customer service" or similar
- Multiple failed support attempts

**Exclusion Criteria:**
- Complaint about specific product/service → problem category
- Specific unresolved issue → specific category
- General frustration → GENERAL_INQUIRY

**Typical Language:**
- "customer service", "support", "poor service", "terrible", "frustrated with support"
- "no response", "unhelpful", "rude agent"

**Examples:**
```
"way to drop the ball on customer service so pissed right now!"
"i frankly don't have the patience for another chat with your customer service people today"
"terrible customer service. won't renew prime"
```

**Support Response Type:** Apologize, offer priority support, escalate for quality review

---

### 9. BILLING_PAYMENT (2.5%, 4,142 messages)

**Definition:** Customer reporting billing errors, unexpected charges, or payment-related problems. Includes double charges, billing disputes, or subscription renewal issues.

**Inclusion Criteria:**
- Charged twice or wrong amount
- Unexpected charge
- Billing error or dispute
- Subscription renewal charge questioned
- Payment method issue

**Exclusion Criteria:**
- Question about price (product info) → PRODUCT_INFORMATION
- Requesting refund (general refund) → REFUND_RETURN
- Question about payment accepted → other

**Typical Language:**
- "charged", "billing", "payment", "double charged", "wrong amount", "fee", "bill"
- "why was i charged", "unexpected charge"

**Examples:**
```
"i was just charged today. how do i get a refund? I was told my membership wouldn't be renewed"
"you charged me twice for the same item"
```

**Support Response Type:** Review charges, reverse erroneous charges, verify subscription

---

### 10. PRODUCT_INFORMATION (1.1%, 1,757 messages)

**Definition:** Customer requesting information about a product, including specifications, features, availability, or usage details.

**Inclusion Criteria:**
- Questions about product specs or features
- "Do you have" / "Is this available"
- Product usage questions
- Asking about product details
- Compatibility questions

**Exclusion Criteria:**
- Complaint about product quality → specific category
- Already purchased product → other category
- General inquiry → GENERAL_INQUIRY

**Typical Language:**
- "product", "specs", "details", "information", "features", "available", "do you have"
- "is this compatible", "does it have"

**Examples:**
```
"what are the specifications for this laptop?"
"is this item available in my country?"
"can this work with [other product]?"
```

**Support Response Type:** Provide product details, link to product page, check availability

---

### 11. SHIPPING_ADDRESS (1.0%, 1,583 messages)

**Definition:** Customer providing, asking to change, or reporting issues with shipping/delivery address. Includes address corrections and location clarifications.

**Inclusion Criteria:**
- Providing shipping address
- Asking to change address
- Wrong address reported
- Address delivery issue
- Clarifying delivery location

**Exclusion Criteria:**
- Delivery failed to address → DELIVERY_ISSUE
- General address question → other category

**Typical Language:**
- "address", "shipping", "ship to", "change address", "wrong address", "deliver to"
- "address is", "send to", "shipped to wrong"

**Examples:**
```
"can you change the shipping address to my new apartment?"
"it was shipped to the wrong address"
```

**Support Response Type:** Confirm/update address, investigate misdirected shipment, offer resend

---

### 12. DAMAGED_ITEM (0.7%, 1,121 messages)

**Definition:** Customer reporting that a received item is damaged, defective, broken, or in poor condition upon arrival.

**Inclusion Criteria:**
- Item arrived damaged
- Product is broken or defective
- Packaging damage
- Item broken on arrival
- Defective/non-functional product

**Exclusion Criteria:**
- Item not received at all → DELIVERY_ISSUE
- Product quality complaint (works but customer doesn't like) → GENERAL_INQUIRY
- Item quality issue not related to damage → other category

**Typical Language:**
- "damaged", "broken", "defective", "arrived damaged", "cracked", "bent", "torn"
- "doesn't work", "arrived broken"

**Examples:**
```
"the box arrived dented and the item inside is broken"
"both games came rattling inside their cases. one is broken"
"is it possible to prevent amzl from delivering? stuff is either lost/stolen/broken every time"
```

**Support Response Type:** Offer replacement or refund, process damage claim

---

## Intent Distribution Summary

| Rank | Intent | Count | % | Implication |
|------|--------|-------|---|----|
| 1 | GENERAL_INQUIRY | 85,518 | 52.6% | Need strong triage/clarification |
| 2 | ORDER_STATUS | 24,102 | 14.8% | Self-service tracking should reduce volume |
| 3 | DELIVERY_ISSUE | 14,403 | 8.9% | Logistics problems are major source |
| 4 | PRIME_SUBSCRIPTION | 7,200 | 4.4% | Membership management important |
| 5 | ACCOUNT_LOGIN | 6,734 | 4.1% | Self-service password reset needed |
| 6 | TECHNICAL_ISSUE | 5,856 | 3.6% | App/website stability critical |
| 7 | REFUND_RETURN | 5,228 | 3.2% | Return/refund process should be automated |
| 8 | CUSTOMER_SERVICE_COMPLAINT | 4,918 | 3.0% | Service quality issues present |
| 9 | BILLING_PAYMENT | 4,142 | 2.5% | Billing disputes need investigation |
| 10 | PRODUCT_INFORMATION | 1,757 | 1.1% | Product pages should contain details |
| 11 | SHIPPING_ADDRESS | 1,583 | 1.0% | Address management should be self-service |
| 12 | DAMAGED_ITEM | 1,121 | 0.7% | Logistics damage is rare but present |

---

## Boundary Cases & Overlaps

### Order Status vs. Delivery Issue
- **ORDER_STATUS:** "Where is my order?" / "What's the tracking?" → Information request
- **DELIVERY_ISSUE:** "It's late / didn't arrive" → Problem requiring action

### Refund/Return vs. Damaged Item
- If item is damaged AND customer wants refund → Use DAMAGED_ITEM (more specific)
- If just asking about refund process → Use REFUND_RETURN

### Technical Issue vs. General Complaint
- **TECHNICAL_ISSUE:** "Website crashes", "App won't load" → Platform problem
- **CUSTOMER_SERVICE_COMPLAINT:** "Your support is terrible" → Meta-complaint

### Prime Subscription vs. Billing/Payment
- **PRIME_SUBSCRIPTION:** "How to cancel Prime?" / "What are benefits?" → Membership
- **BILLING_PAYMENT:** "Why was I charged for Prime?" → Billing error

---

## Secondary Intent Rules

Some messages may have a secondary intent:

**Example 1:**
```
Primary: DELIVERY_ISSUE (late delivery)
Secondary: CUSTOMER_SERVICE_COMPLAINT (frustrated with lack of response)
```

**Example 2:**
```
Primary: DAMAGED_ITEM (arrived broken)
Secondary: REFUND_RETURN (requesting refund)
```

**Rule:** When annotating, assign primary intent based on what the customer needs immediately. Secondary intent is optional and useful for routing escalations.

---

## Characteristics of Each Category

### By Tone
- **Professional/Neutral:** ORDER_STATUS, PRODUCT_INFORMATION, SHIPPING_ADDRESS
- **Frustrated/Angry:** DELIVERY_ISSUE, DAMAGED_ITEM, CUSTOMER_SERVICE_COMPLAINT
- **Neutral/Grateful:** GENERAL_INQUIRY (thanks), ACCOUNT_LOGIN
- **Mixed:** REFUND_RETURN, BILLING_PAYMENT

### By Complexity
- **Low (quick resolution):** ORDER_STATUS, PRODUCT_INFORMATION, ACCOUNT_LOGIN
- **Medium (needs investigation):** DELIVERY_ISSUE, DAMAGED_ITEM, BILLING_PAYMENT
- **High (may need escalation):** REFUND_RETURN, TECHNICAL_ISSUE, CUSTOMER_SERVICE_COMPLAINT

### By Self-Service Potential
- **High (automatable):** ORDER_STATUS, ACCOUNT_LOGIN, SHIPPING_ADDRESS
- **Medium (partially automatable):** PRODUCT_INFORMATION, PRIME_SUBSCRIPTION
- **Low (needs human):** DELIVERY_ISSUE, DAMAGED_ITEM, BILLING_PAYMENT, CUSTOMER_SERVICE_COMPLAINT

---

## Escalation Signals by Intent

| Intent | Escalation Signal | Action |
|--------|---|---|
| ORDER_STATUS | Multiple follow-ups with conflicting info | Investigate + manual resolution |
| DELIVERY_ISSUE | Multiple failed attempts to receive | File carrier claim + offer refund |
| DAMAGED_ITEM | High-value item damaged | Expedite replacement or refund |
| REFUND_RETURN | Refund status unknown | Manual investigation required |
| BILLING_PAYMENT | Fraud suspected | Security team review |
| ACCOUNT_LOGIN | Account access persistent issue | Account recovery specialist |
| TECHNICAL_ISSUE | Service outage confirmed | Engineering escalation |
| CUSTOMER_SERVICE_COMPLAINT | Multiple negative interactions | Retention team + review |

---

## Validation & Quality

**How to use this taxonomy:**

1. **For annotation:** Read message → identify primary intent using keywords and definition
2. **For classification:** Train classifier on labeled examples from each category
3. **For routing:** Route by intent to appropriate specialist team
4. **For metrics:** Track resolution rates and customer satisfaction by intent

**Expected classifier performance:**
- Easy intents (ORDER_STATUS, DAMAGED_ITEM): 85-95% F1
- Medium intents (DELIVERY_ISSUE, REFUND_RETURN): 75-85% F1
- Hard intents (GENERAL_INQUIRY, CUSTOMER_SERVICE_COMPLAINT): 60-75% F1
- Weighted average: 75-80% F1 expected on diverse customer messages

---

## Notes

- **Language mix:** Data contains English + Japanese + Spanish + other languages. GENERAL_INQUIRY heavily includes non-English. Consider language detection for multilingual support.
- **Context dependency:** Some messages require conversation context to classify correctly. Single messages may be ambiguous.
- **Temporal patterns:** Delivery issues likely spike during busy seasons; subscription cancellations may correlate with service problems.
- **Data quality:** Some messages are very short (1-2 words) or incomplete, which may reduce classifier confidence.

---

**Taxonomy Finalized:** Ready for Phase 4 annotation and classifier training.

**Next Steps:**
1. Annotate 250-300 golden candidates with primary intent
2. Train TF-IDF + Logistic Regression baseline classifier
3. Evaluate on test set
4. Build Flask UI for annotation interface
