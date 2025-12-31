"""Pre-built scenario templates for training simulations.

Provides ready-to-use scenario configurations for common training situations:
- Angry Customer: Handle escalated customer complaints
- Curious Learner: Guide a student through product discovery
"""

from typing import Any

# Template: Angry Customer
ANGRY_CUSTOMER_TEMPLATE = {
    "scenario": {
        "name": "Angry Customer - Billing Dispute",
        "description": "Practice handling an escalated customer who is upset about an unexpected charge on their account. Learn de-escalation techniques and problem resolution.",
        "category": "Customer Service",
        "difficulty": "Hard",
        "is_active": True,
    },
    "nodes": [
        {
            "node_type": "statement",
            "name": "Customer Opens",
            "text_content": "CUSTOMER: I'VE BEEN ON HOLD FOR 30 MINUTES! This is absolutely unacceptable! I just got my bill and there's a $150 charge I never authorized! What kind of scam are you running here?!",
            "next_index": 1,
        },
        {
            "node_type": "question",
            "name": "Agent Response 1",
            "text_content": "How do you respond to the upset customer?",
            "options": [
                {"label": "I understand your frustration. Let me look into this charge right away and see how I can help.", "next_index": 2},
                {"label": "Sir, please calm down. I can't help you if you're yelling at me.", "next_index": 5},
                {"label": "That charge is probably from the service agreement you signed.", "next_index": 6},
            ],
        },
        {
            "node_type": "setVariable",
            "name": "Set Good Start",
            "variable_name": "approach",
            "variable_value": "empathetic",
            "next_index": 3,
        },
        {
            "node_type": "statement",
            "name": "Customer Calms Slightly",
            "text_content": "CUSTOMER: *takes a breath* Okay... okay. I'm sorry for yelling, I'm just really stressed. I'm on a fixed income and I can't afford surprise charges. Can you really help me?",
            "next_index": 4,
        },
        {
            "node_type": "question",
            "name": "Agent Response 2",
            "text_content": "The customer is calming down. What's your next step?",
            "options": [
                {"label": "Absolutely. I'm pulling up your account now. While I look into this, can you tell me when you first noticed this charge?", "next_index": 7},
                {"label": "I'll try. What's your account number?", "next_index": 8},
            ],
        },
        {
            "node_type": "setVariable",
            "name": "Set Bad Start",
            "variable_name": "approach",
            "variable_value": "defensive",
            "next_index": 9,
        },
        {
            "node_type": "statement",
            "name": "Customer Escalates More",
            "text_content": "CUSTOMER: Excuse me?! I didn't sign anything! Let me speak to your supervisor RIGHT NOW!",
            "next_index": 10,
        },
        {
            "node_type": "statement",
            "name": "Investigation Success",
            "text_content": "CUSTOMER: I saw it on my statement this morning... Actually, looking at it now, the date matches when I called about my service upgrade last month.",
            "next_index": 11,
        },
        {
            "node_type": "statement",
            "name": "Missed Opportunity",
            "text_content": "CUSTOMER: *sighs* Fine, it's 4829551. But you better fix this.",
            "next_index": 11,
        },
        {
            "node_type": "statement",
            "name": "Customer Very Angry",
            "text_content": "CUSTOMER: I CAN'T CALM DOWN! You people have stolen from me! I want this fixed NOW or I'm going to the news!",
            "next_index": 10,
        },
        {
            "node_type": "question",
            "name": "Recovery Attempt",
            "text_content": "The customer is very upset. How do you try to recover the situation?",
            "options": [
                {"label": "I hear you, and you have every right to be upset. Let me personally make sure we resolve this for you today. First, let me review your account.", "next_index": 11},
                {"label": "I'm transferring you to my supervisor now.", "next_index": 12},
            ],
        },
        {
            "node_type": "statement",
            "name": "Find The Issue",
            "text_content": "You review the account and see: The $150 charge was a technician visit fee for a service call last month. Notes show the customer was told about this charge at the time of scheduling.",
            "next_index": 13,
        },
        {
            "node_type": "end",
            "name": "Transferred - Failed",
            "text_content": "You transferred the call. While sometimes necessary, this opportunity to resolve the issue directly was missed. The customer will likely have to explain everything again.\n\n[SCENARIO END - Score: 40/100]",
        },
        {
            "node_type": "question",
            "name": "Resolution Choice",
            "text_content": "You found the source of the charge. The customer was technically informed, but may not have fully understood. How do you proceed?",
            "options": [
                {"label": "I found the charge. It's from your service visit on October 15th. I see you were informed, but I understand this may not have been clear. Given the confusion, I can offer you a 50% courtesy credit.", "next_index": 14},
                {"label": "The charge is valid. You agreed to it when you scheduled the service visit last month.", "next_index": 15},
                {"label": "I'm going to waive this entire charge for you as a one-time courtesy, and I'll add a note to ensure you're clearly informed of any charges in the future.", "next_index": 16},
            ],
        },
        {
            "node_type": "statement",
            "name": "Balanced Resolution",
            "text_content": "CUSTOMER: That... that's fair. Thank you for understanding. I guess I was just caught off guard. I really appreciate you taking the time to look into this.",
            "next_index": 17,
        },
        {
            "node_type": "statement",
            "name": "Customer Stays Upset",
            "text_content": "CUSTOMER: That's not acceptable! I was never properly informed! I want to speak to someone who can actually help me!",
            "next_index": 10,
        },
        {
            "node_type": "statement",
            "name": "Full Resolution",
            "text_content": "CUSTOMER: Oh wow, really? Thank you so much! I can't tell you how much I appreciate that. You've completely turned my day around. I'm sorry I was so upset earlier.",
            "next_index": 18,
        },
        {
            "node_type": "end",
            "name": "Good Ending",
            "text_content": "Excellent work! You de-escalated the situation, investigated thoroughly, and found a balanced solution that acknowledged the customer's frustration while being fair to the company.\n\n[SCENARIO END - Score: 85/100]\n\nKey Takeaways:\n- Started with empathy to defuse anger\n- Gathered information patiently\n- Offered a fair compromise\n- Customer left satisfied",
        },
        {
            "node_type": "end",
            "name": "Great Ending",
            "text_content": "Outstanding! You completely turned around an extremely upset customer. While waiving the full charge may not always be possible, in this case it built tremendous customer loyalty.\n\n[SCENARIO END - Score: 95/100]\n\nKey Takeaways:\n- Exceptional empathy throughout\n- Used discretion appropriately\n- Proactively prevented future issues\n- Created a loyal customer advocate",
        },
    ],
    "entry_node_name": "Customer Opens",
}


# Template: Curious Learner
CURIOUS_LEARNER_TEMPLATE = {
    "scenario": {
        "name": "Curious Learner - Product Discovery",
        "description": "Help a potential customer understand your product features. Practice consultative selling and needs discovery techniques.",
        "category": "Sales",
        "difficulty": "Medium",
        "is_active": True,
    },
    "nodes": [
        {
            "node_type": "statement",
            "name": "Learner Intro",
            "text_content": "CUSTOMER: Hi! I've been hearing a lot about your software but I'm not really sure if it's right for me. I run a small bakery and I'm looking for something to help me manage orders. Can you tell me more?",
            "next_index": 1,
        },
        {
            "node_type": "question",
            "name": "Opening Response",
            "text_content": "How do you start the conversation?",
            "options": [
                {"label": "I'd love to help! Before I dive into features, can you tell me a bit more about your bakery? What's your biggest challenge right now?", "next_index": 2},
                {"label": "Our software has order management, inventory tracking, and customer management. It's $99/month.", "next_index": 6},
                {"label": "Absolutely! We work with lots of bakeries. Let me show you our demo.", "next_index": 7},
            ],
        },
        {
            "node_type": "setVariable",
            "name": "Set Discovery Approach",
            "variable_name": "approach",
            "variable_value": "consultative",
            "next_index": 3,
        },
        {
            "node_type": "statement",
            "name": "Customer Shares Needs",
            "text_content": "CUSTOMER: Well, we've grown a lot lately! We're getting more custom cake orders, and I'm losing track of who ordered what and when they need it. Last week I almost forgot someone's wedding cake! I'm writing everything in a notebook and it's just not working anymore.",
            "next_index": 4,
        },
        {
            "node_type": "question",
            "name": "Dig Deeper",
            "text_content": "The customer has shared their pain point. What's your next move?",
            "options": [
                {"label": "A wedding cake - that must have been stressful! How many custom orders would you say you're handling per week now?", "next_index": 5},
                {"label": "Our software would definitely fix that! You can enter all your orders and get reminders.", "next_index": 8},
            ],
        },
        {
            "node_type": "statement",
            "name": "More Details",
            "text_content": "CUSTOMER: Oh it was terrifying! We're doing maybe 15-20 custom orders a week now. Plus all our regular pastry sales. And I'm trying to manage ingredient inventory too - sometimes I realize I'm out of something right when I need it.",
            "next_index": 9,
        },
        {
            "node_type": "statement",
            "name": "Price Shock",
            "text_content": "CUSTOMER: Oh... $99 a month? That seems like a lot for a small bakery. I'm not sure I need all those features. Maybe I should just get a better notebook system...",
            "next_index": 10,
        },
        {
            "node_type": "statement",
            "name": "Demo Overwhelm",
            "text_content": "CUSTOMER: *watching demo* This looks complicated... I'm not very tech-savvy. I just want something simple. I'm not sure this is right for me.",
            "next_index": 10,
        },
        {
            "node_type": "statement",
            "name": "Premature Solution",
            "text_content": "CUSTOMER: That sounds helpful I guess... but how does it actually work? Will I have to enter everything manually? I'm really busy in the mornings.",
            "next_index": 11,
        },
        {
            "node_type": "question",
            "name": "Tailored Solution",
            "text_content": "You now understand her needs well. How do you present your solution?",
            "options": [
                {"label": "It sounds like you need two things: order tracking so nothing falls through the cracks, and inventory alerts so you never run out. Our Bakery Basic plan at $49/month has exactly that, plus a simple calendar view. Want me to show you?", "next_index": 12},
                {"label": "Our full Enterprise plan would handle all of that and much more! It's $299/month but includes everything.", "next_index": 13},
            ],
        },
        {
            "node_type": "question",
            "name": "Recover Interest",
            "text_content": "The customer seems hesitant. How do you re-engage?",
            "options": [
                {"label": "I hear you - let me take a step back. What's the one thing that would make the biggest difference for you right now?", "next_index": 3},
                {"label": "Well, if you change your mind, here's my card.", "next_index": 14},
            ],
        },
        {
            "node_type": "question",
            "name": "Handle Workflow Question",
            "text_content": "She's interested but has practical concerns. How do you address them?",
            "options": [
                {"label": "Great question! Most bakery owners take orders on their phone. Our app lets you add an order in about 30 seconds - customer name, order details, pickup date. Would that work for you?", "next_index": 9},
                {"label": "You'd need to enter orders when they come in, yes. But it saves time later!", "next_index": 8},
            ],
        },
        {
            "node_type": "statement",
            "name": "Customer Excited",
            "text_content": "CUSTOMER: $49? That's much more reasonable! And I love that it has a calendar view - that's exactly what I need. I'd love to see how the inventory alerts work!",
            "next_index": 15,
        },
        {
            "node_type": "statement",
            "name": "Oversold",
            "text_content": "CUSTOMER: $299?! No, no, that's way out of my budget. I think I'll just stick with my notebook for now. Thanks anyway.",
            "next_index": 16,
        },
        {
            "node_type": "end",
            "name": "Lost Customer",
            "text_content": "The customer left without a solution to their problem.\n\n[SCENARIO END - Score: 25/100]\n\nKey Takeaways:\n- Failed to understand customer needs\n- Didn't recover from objections\n- Customer still struggling with notebooks",
        },
        {
            "node_type": "question",
            "name": "Demo Time",
            "text_content": "The customer is eager to learn more. How do you proceed?",
            "options": [
                {"label": "Let me show you! *shares screen* Here's the order calendar. See how each order shows up as a card? And here - if I click 'butter' in your ingredients, I can set an alert at 5 pounds. When you're running low, you get a text.", "next_index": 17},
                {"label": "I'll email you a link to our demo videos. You can watch them when you have time.", "next_index": 18},
            ],
        },
        {
            "node_type": "end",
            "name": "Oversell Fail",
            "text_content": "You lost the sale by not matching the solution to the customer's actual needs and budget.\n\n[SCENARIO END - Score: 35/100]\n\nKey Takeaways:\n- Good discovery but poor solution matching\n- Didn't consider customer's budget\n- Overshot with features they didn't need",
        },
        {
            "node_type": "statement",
            "name": "Customer Ready to Buy",
            "text_content": "CUSTOMER: Oh this is perfect! I can see exactly when my wedding cake order is due, and I'll know when to order more flour. This would have saved me so much stress! How do I sign up?",
            "next_index": 19,
        },
        {
            "node_type": "statement",
            "name": "Missed Momentum",
            "text_content": "CUSTOMER: Oh... okay. I'll try to watch them this weekend, but you know how it is - I'm so busy. I'll let you know if I have questions!",
            "next_index": 20,
        },
        {
            "node_type": "end",
            "name": "Successful Sale",
            "text_content": "Excellent! You guided the customer through discovery, matched the solution to their specific needs, and closed with a clear next step.\n\n[SCENARIO END - Score: 95/100]\n\nKey Takeaways:\n- Asked discovery questions before presenting\n- Listened for specific pain points\n- Matched solution to budget and needs\n- Used live demo at the right moment\n- Customer excited and ready to buy",
        },
        {
            "node_type": "end",
            "name": "Follow Up Needed",
            "text_content": "The customer was interested but didn't commit. You'll need to follow up.\n\n[SCENARIO END - Score: 60/100]\n\nKey Takeaways:\n- Good discovery and connection\n- Lost momentum at the close\n- Should have demonstrated while customer was engaged\n- Follow-up needed but may lose to competitor",
        },
    ],
    "entry_node_name": "Learner Intro",
}


def get_all_templates() -> list[dict[str, Any]]:
    """Get all available scenario templates."""
    return [
        {"id": "angry_customer", "name": "Angry Customer - Billing Dispute", **ANGRY_CUSTOMER_TEMPLATE},
        {"id": "curious_learner", "name": "Curious Learner - Product Discovery", **CURIOUS_LEARNER_TEMPLATE},
    ]


def get_template_by_id(template_id: str) -> dict[str, Any] | None:
    """Get a specific template by ID."""
    templates = {
        "angry_customer": ANGRY_CUSTOMER_TEMPLATE,
        "curious_learner": CURIOUS_LEARNER_TEMPLATE,
    }
    return templates.get(template_id)
