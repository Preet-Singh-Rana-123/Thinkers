from django.shortcuts import render

PITCHES_DATA = [
    {
        "id": 1,
        "title": "NeuroNotes AI",
        "founder": "Siddharth Ray",
        "college": "IIT Delhi",
        "stage": "Prototype / Alpha",
        "stage_color": "yellow",
        "club": "GenAI Disruptors Club",
        "one_liner": "Turn spoken engineering architectural debates into interactive system diagrams and pull request scaffolds.",
        "problem": "Software architects spend 12 hours a week manually drafting Miro diagrams and translating verbal meetings into Jira tickets.",
        "solution": "A multimodal meeting listener that parses audio, identifies distributed system components, and exports clean PlantUML and C4 model code.",
        "traction": "450 beta waitlist users • 12 pilot engineering clubs • 98.2% diagram accuracy",
        "seeking": "Seeking $75k University Angel Round & Full-Stack Django/React Engineer",
        "upvotes": 284,
        "category": "Developer Tools",
    },
    {
        "id": 2,
        "title": "EcoLoop Logistics",
        "founder": "Ananya Joshi",
        "college": "BITS Pilani",
        "stage": "Pilot Stage",
        "stage_color": "green",
        "club": "ClimateTech & Clean Energy Hub",
        "one_liner": "Zero-waste reusable corrugated parcel containers with QR deposit escrow for e-commerce deliveries.",
        "problem": "E-commerce cardboard waste accounts for 40% of solid municipal landfill packaging in tier-1 metro campuses.",
        "solution": "Smart durable waterproof parcel boxes that customers return to campus drop boxes in exchange for instant cash discounts.",
        "traction": "2,400 parcels delivered on Goa campus • 89% box return rate • Partnered with 3 local bookstores",
        "seeking": "Seeking E-Commerce Pilot Partners & Seed Grant",
        "upvotes": 196,
        "category": "Climate & Supply Chain",
    },
    {
        "id": 3,
        "title": "KioskPay POS",
        "founder": "Vikram Sethi",
        "college": "SRM Institute",
        "stage": "MVP Hardware",
        "stage_color": "pink",
        "club": "FinTech & Web3 Builders",
        "one_liner": "Offline UPI tap-to-pay soundbox hardware for hyper-local campus food stalls and street vendors.",
        "problem": "Network congestion during lunch rush hour causes 18% of UPI payments at college food kiosks to timeout.",
        "solution": "Local mesh NFC payment soundbox with store-and-forward batch authorization that works with zero cellular network.",
        "traction": "Deployed across 8 campus canteens • 6,200 transactions processed with 0.1s confirmation",
        "seeking": "Seeking Hardware Embedded Systems Co-Founder",
        "upvotes": 341,
        "category": "Fintech & Hardware",
    },
    {
        "id": 4,
        "title": "FlowDoc Forms",
        "founder": "Tanvi Chawla",
        "college": "BITS Pilani",
        "stage": "Revenue Generating",
        "stage_color": "cyan",
        "club": "SaaS Growth Syndicate",
        "one_liner": "Dynamic conditional multi-step application forms with automated club interview scheduling.",
        "problem": "College clubs and student societies waste hundreds of hours manually reviewing Google Forms and sending interview calendar links.",
        "solution": "All-in-one forms with built-in scorecards, automated rejection/acceptance email triggers, and Google Calendar sync.",
        "traction": "$1,400 MRR • 34 collegiate societies active • 22,000 applicants managed",
        "seeking": "Looking for B2B Outbound Growth Hacker",
        "upvotes": 310,
        "category": "B2B SaaS",
    },
]

CO_FOUNDER_POSTS = [
    {
        "id": 1,
        "startup_name": "NeuroNotes AI",
        "founder": "Siddharth Ray",
        "club": "GenAI Disruptors",
        "role_needed": "Full-Stack Django & React Co-Founder",
        "equity": "20% - 30% Equity",
        "commitment": "Part-Time (15 hrs/wk) to Full-Time",
        "location": "Remote / Delhi NCR",
        "description": "I am handling the model fine-tuning and LangGraph agent pipelines. Need a rockstar engineer to build the real-time canvas UI, user auth, and Stripe billing engine.",
        "skills_required": ["Django", "React / Next.js", "WebSockets", "PostgreSQL"],
        "badge": "TOP MATCH",
    },
    {
        "id": 2,
        "startup_name": "KioskPay POS",
        "founder": "Vikram Sethi",
        "club": "FinTech & Web3 Builders",
        "role_needed": "Embedded Systems & Firmware Engineer",
        "equity": "25% Equity",
        "commitment": "20 hrs/week",
        "location": "Chennai / SRM Campus (Hybrid)",
        "description": "Our prototype uses ESP32 and NFC PN532. Looking for an electrical / hardware lead to design our custom PCB and handle CE/BIS compliance.",
        "skills_required": ["ESP32", "KiCAD", "Firmware", "MQTT", "Hardware Debugging"],
        "badge": "HARDWARE",
    },
    {
        "id": 3,
        "startup_name": "ThreadVibe D2C",
        "founder": "Rohan Mehta",
        "club": "D2C Brand Mavericks",
        "role_needed": "Head of Operations & Logistics",
        "equity": "15% - 20% Profit Share / Equity",
        "commitment": "Flexible",
        "location": "Delhi NCR",
        "description": "We did ₹18L revenue in 8 months and are struggling to keep up with order fulfillment and factory QC. Need someone disciplined with operations.",
        "skills_required": ["Supply Chain", "Vendor Management", "Shopify Apps", "Inventory Control"],
        "badge": "D2C BRAND",
    },
    {
        "id": 4,
        "startup_name": "EcoLoop Logistics",
        "founder": "Ananya Joshi",
        "club": "ClimateTech Hub",
        "role_needed": "Mobile App Developer (Flutter)",
        "equity": "18% Equity",
        "commitment": "10-15 hrs/week",
        "location": "Remote",
        "description": "Building the consumer QR return app that unlocks parcel escrow refunds. Need a snappy Flutter dev with camera QR scanning experience.",
        "skills_required": ["Flutter", "Dart", "Firebase", "REST APIs"],
        "badge": "GREEN IMPACT",
    },
]

CHALLENGES_DATA = [
    {
        "id": 1,
        "title": "National Student AI Agent Sprint",
        "prize_pool": "₹2,50,000 ($3,000)",
        "deadline": "14 Days Left (Ends Sept 25)",
        "hosted_by": "GenAI Disruptors & Campus Angels",
        "description": "Build an autonomous software agent that solves a daily operational bottleneck for university administrations or student bodies.",
        "participants": 84,
        "badge": "MEGA HACKATHON",
        "badge_color": "yellow",
    },
    {
        "id": 2,
        "title": "CleanTech Campus Sustainability Grant",
        "prize_pool": "₹1,50,000 Seed Grant",
        "deadline": "22 Days Left",
        "hosted_by": "ClimateTech Hub & ESG Venture Fund",
        "description": "Pitch solutions for solar microgrids, circular waste management, or water conservation specifically piloted on college grounds.",
        "participants": 42,
        "badge": "IMPACT SPRINT",
        "badge_color": "green",
    },
    {
        "id": 3,
        "title": "B2B SaaS MRR Challenge: $0 to $1,000",
        "prize_pool": "₹1,00,000 + VC Pitch Day",
        "deadline": "30 Days Left",
        "hosted_by": "SaaS Growth Syndicate",
        "description": "A 30-day boot camp challenge where student founders build a micro-SaaS, launch on Product Hunt, and close their first paying business customer.",
        "participants": 120,
        "badge": "REVENUE SPRINT",
        "badge_color": "cyan",
    },
]

def pitch_wall(request):
    """Pitch Wall showcase page with upvotes, category filters, and pitch deck submission modal."""
    category = request.GET.get('cat', 'all')
    pitches = PITCHES_DATA
    if category != 'all':
        pitches = [p for p in pitches if category.lower() in p['category'].lower()]

    context = {
        "pitches": pitches,
        "current_category": category,
    }
    return render(request, "collaboration/pitch_wall.html", context)


def co_founders(request):
    """Find a Co-Founder Matching Board."""
    context = {
        "posts": CO_FOUNDER_POSTS,
    }
    return render(request, "collaboration/co_founders.html", context)


def challenges(request):
    """Startup Sprints, Grants, and Hackathons."""
    context = {
        "challenges": CHALLENGES_DATA,
    }
    return render(request, "collaboration/challenges.html", context)
