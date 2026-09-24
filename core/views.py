from django.shortcuts import render

def home(request):
    """Home / Landing page with high-energy comic style hero, club previews, featured pitch cards, live stats, and founder testimonials."""
    stats = [
        {"number": "180+", "label": "Active Entrepreneur Clubs", "color": "yellow"},
        {"number": "5,400+", "label": "Innovators & Hustlers", "color": "pink"},
        {"number": "$2.8M+", "label": "College Startup Grants", "color": "green"},
        {"number": "340+", "label": "Co-Founders Paired", "color": "cyan"},
    ]

    featured_clubs = [
        {
            "name": "GenAI Disruptors Club",
            "slug": "genai-disruptors",
            "tagline": "Building LLM-powered agents and multimodal SaaS applications",
            "category": "Artificial Intelligence",
            "badge_color": "purple",
            "bg_color": "comic-box-purple",
            "members": 642,
            "leads": "Aarav Sharma & Priya Sen",
            "weekly_event": "Sunday Prompt & Pitch Demo Day",
            "tags": ["AI/ML", "LLMs", "B2B SaaS"],
        },
        {
            "name": "D2C Brand Mavericks",
            "slug": "d2c-mavericks",
            "tagline": "Next-gen consumer lifestyle, organic beverage & apparel founders",
            "category": "Consumer & Retail",
            "badge_color": "yellow",
            "bg_color": "comic-box-yellow",
            "members": 418,
            "leads": "Rohan Mehta",
            "weekly_event": "Supply Chain & Packaging Mastermind",
            "tags": ["Ecommerce", "TikTok Ads", "Supply Chain"],
        },
        {
            "name": "ClimateTech & Clean Energy Hub",
            "slug": "climatetech-hub",
            "tagline": "Hardware, EV battery analytics, and circular economy startups",
            "category": "Sustainability",
            "badge_color": "green",
            "bg_color": "comic-box-green",
            "members": 312,
            "leads": "Maya Verma",
            "weekly_event": "Green Grant Proposal Hackathon",
            "tags": ["CleanTech", "Hardware", "ESG Grants"],
        },
        {
            "name": "FinTech & Web3 Builders",
            "slug": "fintech-web3",
            "tagline": "Algorithmic micro-investing, UPI neo-banking, and DeFi rails",
            "category": "FinTech",
            "badge_color": "cyan",
            "bg_color": "comic-box-cyan",
            "members": 520,
            "leads": "Karan Malhotra",
            "weekly_event": "Regulatory Sandbox & Seed Review",
            "tags": ["NeoBank", "UPI 2.0", "Security"],
        },
    ]

    trending_pitches = [
        {
            "title": "NeuroNotes AI",
            "founder": "Siddharth Ray (IIT Delhi)",
            "one_liner": "Voice-to-executable architecture diagrams for engineering squads",
            "seeking": "Seeking $75k Pre-Seed & Full-Stack Lead",
            "upvotes": 284,
            "badge": "HOT PITCH",
            "category": "Developer Tools",
        },
        {
            "title": "EcoLoop Logistics",
            "founder": "Ananya Joshi (BITS Pilani)",
            "one_liner": "Zero-waste reusable parcel boxes with QR deposit escrow",
            "seeking": "Seeking Pilot E-commerce Partners",
            "upvotes": 196,
            "badge": "IMPACT",
            "category": "Supply Chain",
        },
        {
            "title": "KioskPay POS",
            "founder": "Vikram Sethi (SRM University)",
            "one_liner": "Offline UPI tap-to-pay soundbox for hyper-local campus food stalls",
            "seeking": "Looking for Hardware Co-Founder",
            "upvotes": 341,
            "badge": "TOP RATED",
            "category": "Fintech",
        },
    ]

    testimonials = [
        {
            "quote": "Joined the SaaS Syndicate club in semester 5. Found my technical co-founder within 2 weeks, and we just raised our university angel grant!",
            "author": "Tanvi Chawla",
            "role": "Founder, FlowDoc (Raised ₹15L)",
            "club": "SaaS Growth Syndicate",
        },
        {
            "quote": "The weekly comic-style live pitch roasts gave us the brutally honest feedback no professor ever had time to provide. Game changing.",
            "author": "Kabir Das",
            "role": "Co-founder, QuickCart Campus",
            "club": "Gen-Z Hustlers Club",
        },
    ]

    context = {
        "stats": stats,
        "featured_clubs": featured_clubs,
        "trending_pitches": trending_pitches,
        "testimonials": testimonials,
    }
    return render(request, "core/index.html", context)


def about(request):
    """About the Thinkers platform: Mission, origin story, comic principles, and why interactive clubs outperform traditional networking."""
    return render(request, "core/about.html")


def how_it_works(request):
    """Interactive comic guide: 4 step roadmap to entrepreneur club success."""
    return render(request, "core/how_it_works.html")
