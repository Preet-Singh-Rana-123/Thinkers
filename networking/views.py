from django.shortcuts import render, Http404

MEMBERS_DATA = [
    {
        "username": "aarav_sharma",
        "name": "Aarav Sharma",
        "role": "Technical Founder",
        "role_badge": "yellow",
        "avatar": "AS",
        "college": "IIT Delhi (Batch 2026)",
        "headline": "Building Autonomous Multi-Agent AI Workflows for DevOps",
        "bio": "Final year CSE undergrad obsessed with distributed systems, LangGraph, and Rust. Previously built a campus food aggregator that handled 15,000 orders.",
        "skills": ["Python", "Rust", "FastAPI", "Docker", "PyTorch", "Kubernetes"],
        "seeking": "Seeking Growth/Biz Co-Founder & Pre-Seed Angel",
        "club": "GenAI Disruptors Club",
        "badges": ["Serial Pitcher", "Top Contributor", "Hackathon Champ"],
        "projects": [
            {"title": "AgentOps Studio", "desc": "Monitoring dashboard for autonomous LLM agents.", "stars": "240"},
            {"title": "CampusBite", "desc": "Hyperlocal food delivery inside college hostels.", "stars": "110"},
        ]
    },
    {
        "username": "priya_sen",
        "name": "Priya Sen",
        "role": "Product Designer & Strategist",
        "role_badge": "pink",
        "avatar": "PS",
        "college": "NID Ahmedabad",
        "headline": "FinTech & Web3 UI/UX Architect | Design System Lover",
        "bio": "Obsessed with creating frictionless checkout journeys and delightful micro-interactions. Consulted for 3 early-stage YC startups on design audits.",
        "skills": ["Figma", "Design Systems", "User Research", "Prototyping", "Design Tokens"],
        "seeking": "Open to Collaborate on FinTech / B2B SaaS MVPs",
        "club": "FinTech & Web3 Builders",
        "badges": ["Design Guru", "5x Mentor", "Active Hustler"],
        "projects": [
            {"title": "Aura Design System", "desc": "Clean, accessible component library for fintech.", "stars": "420"},
        ]
    },
    {
        "username": "rohan_mehta",
        "name": "Rohan Mehta",
        "role": "Growth Marketer & D2C Founder",
        "role_badge": "cyan",
        "avatar": "RM",
        "college": "SRCC, Delhi University",
        "headline": "Scaled campus apparel brand from ₹0 to ₹18L revenue in 8 months",
        "bio": "Commerce student with a knack for viral reels, supply chain sourcing from Tirupur, and Meta performance marketing.",
        "skills": ["Meta Ads", "TikTok Ads", "Shopify Plus", "Supply Chain", "Klaviyo"],
        "seeking": "Looking for Operations & Tech Partners",
        "club": "D2C Brand Mavericks",
        "badges": ["10x Growth", "D2C Leader"],
        "projects": [
            {"title": "ThreadVibe", "desc": "Oversized graphic hoodies for engineering colleges.", "stars": "85"},
        ]
    },
    {
        "username": "tanvi_chawla",
        "name": "Tanvi Chawla",
        "role": "SaaS Founder",
        "role_badge": "purple",
        "avatar": "TC",
        "college": "BITS Pilani (Goa)",
        "headline": "Solo Developer of FlowDoc Forms ($1.4k MRR)",
        "bio": "Full-stack engineer building bootstrapped micro-SaaS tools. Believes in shipping small, charging early, and talking to 5 users every day.",
        "skills": ["Django", "React", "PostgreSQL", "TailwindCSS", "Stripe API"],
        "seeking": "Looking for B2B Outbound Sales Specialist",
        "club": "SaaS Growth Syndicate",
        "badges": ["Revenue Maker", "Solo Hustler", "Syndicate Chair"],
        "projects": [
            {"title": "FlowDoc", "desc": "Smart conditional dynamic forms for student clubs.", "stars": "310"},
        ]
    },
    {
        "username": "maya_verma",
        "name": "Maya Verma",
        "role": "ClimateTech Researcher",
        "role_badge": "green",
        "avatar": "MV",
        "college": "IIT Madras",
        "headline": "Developing Sodium-Ion Battery Thermal Monitoring Algorithms",
        "bio": "Postgrad researcher passionate about battery life cycle extension and zero-emission urban transport.",
        "skills": ["Battery Tech", "MATLAB", "IoT", "Embedded C", "Patent Filing"],
        "seeking": "Seeking Commercialization Co-founder & Hardware Pilot",
        "club": "ClimateTech & Clean Energy Hub",
        "badges": ["Green Pioneer", "Patent Holder"],
        "projects": [
            {"title": "BattSense Sensor", "desc": "Real-time thermal runaway warning chip.", "stars": "190"},
        ]
    },
    {
        "username": "vikram_sethi",
        "name": "Vikram Sethi",
        "role": "Hardware & IoT Hacker",
        "role_badge": "yellow",
        "avatar": "VS",
        "college": "SRM Institute",
        "headline": "Prototyping Offline Tap-to-Pay POS Hardware for Campus Canteens",
        "bio": "Passionate about PCB design, ESP32 microcontrollers, and offline mesh networks for instant merchant notifications.",
        "skills": ["ESP32", "KiCAD", "Firmware", "MQTT", "C++", "3D Printing"],
        "seeking": "Looking for Fintech API Software Lead",
        "club": "FinTech & Web3 Builders",
        "badges": ["Hardware Wizard", "Hackathon Runner-up"],
        "projects": [
            {"title": "KioskPay V1", "desc": "Low-cost NFC payment reader with soundbox.", "stars": "150"},
        ]
    },
]

def members_list(request):
    """Explore all entrepreneurs in the network with role filtering."""
    role = request.GET.get('role', 'all')
    search_q = request.GET.get('q', '').strip().lower()

    members = MEMBERS_DATA

    if role != 'all':
        members = [m for m in members if role.lower() in m['role'].lower()]

    if search_q:
        members = [
            m for m in members
            if search_q in m['name'].lower()
            or search_q in m['college'].lower()
            or any(search_q in s.lower() for s in m['skills'])
        ]

    context = {
        "members": members,
        "current_role": role,
        "search_q": search_q,
    }
    return render(request, "networking/members_list.html", context)


def member_profile(request, username):
    """Detailed Entrepreneur Trading Card & Bio."""
    member = next((m for m in MEMBERS_DATA if m['username'] == username), None)
    if not member:
        raise Http404("Entrepreneur Not Found")

    context = {
        "member": member,
    }
    return render(request, "networking/member_profile.html", context)


def speed_networking(request):
    """Virtual Speed Networking Lounge with live countdown, queue, and instant match simulator."""
    context = {
        "active_queue_count": 42,
        "next_session": "Thursday, 7:00 PM IST",
        "sample_attendees": MEMBERS_DATA[:4],
    }
    return render(request, "networking/speed_networking.html", context)
