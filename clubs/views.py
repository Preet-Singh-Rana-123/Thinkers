from django.shortcuts import render, Http404

# Curated list of entrepreneur clubs
CLUBS_DATA = [
    {
        "id": 1,
        "name": "GenAI Disruptors Club",
        "slug": "genai-disruptors",
        "category": "ai",
        "category_label": "AI & DeepTech",
        "badge_color": "purple",
        "bg_color": "comic-box-purple",
        "tagline": "Building autonomous AI agents, fine-tuned LLMs, and multimodal tools.",
        "description": "The GenAI Disruptors Club is the premier collegiate circle for hackers and prompt engineers building on top of modern frontier models. Every week we dissect new research papers, showcase live demo MVPs, and test multi-agent architectures.",
        "members_count": 642,
        "lead": "Aarav Sharma & Priya Sen",
        "university": "Cross-Campus (Pan-India)",
        "frequency": "Every Thursday @ 8:00 PM IST",
        "tags": ["LLMs", "LangChain", "Autonomous Agents", "VectorDB"],
        "announcements": [
            {
                "date": "Yesterday",
                "author": "Aarav Sharma (Club Lead)",
                "content": "Reminder: Tomorrow is our Micro-Agent Hack Sprint! We have $500 in OpenAI API credits generously sponsored for the winning project!",
                "badge": "PRIZE SPRINT"
            },
            {
                "date": "3 days ago",
                "author": "Priya Sen",
                "content": "Welcome 45 new members from IIT Bombay & BITS Goa! Don't forget to introduce your startup idea in the introductions thread.",
                "badge": "WELCOME"
            }
        ],
        "upcoming_events": [
            {"title": "Agentic Workflows Teardown", "date": "Tomorrow, 8:00 PM", "type": "Live Code Review"},
            {"title": "Alumni VC Office Hours w/ PeakVentures", "date": "Sunday, 11:00 AM", "type": "Pitch Feedback"},
        ],
        "pitches": [
            {"title": "NeuroNotes AI", "founder": "Siddharth Ray", "upvotes": 284, "seeking": "Full-Stack Dev"},
            {"title": "DocuPulse Agent", "founder": "Meera Patel", "upvotes": 179, "seeking": "Seed Angel"},
        ],
        "members": [
            {"name": "Aarav Sharma", "role": "Club Founder & Tech Lead", "avatar": "AS", "color": "yellow"},
            {"name": "Priya Sen", "role": "Co-Host & Product Designer", "avatar": "PS", "color": "pink"},
            {"name": "Siddharth Ray", "role": "AI Researcher", "avatar": "SR", "color": "cyan"},
            {"name": "Meera Patel", "role": "Full-Stack Builder", "avatar": "MP", "color": "green"},
            {"name": "Aditya Kulkarni", "role": "Prompt Engineer", "avatar": "AK", "color": "purple"},
        ]
    },
    {
        "id": 2,
        "name": "D2C Brand Mavericks",
        "slug": "d2c-mavericks",
        "category": "d2c",
        "category_label": "D2C & Consumer",
        "badge_color": "yellow",
        "bg_color": "comic-box-yellow",
        "tagline": "Next-gen consumer lifestyle, organic beverage, and apparel entrepreneurs.",
        "description": "From formulation and packaging design to TikTok viral marketing and logistics fulfillment. We gather campus physical product creators who dream of building the next unicorn consumer brand.",
        "members_count": 418,
        "lead": "Rohan Mehta & Sanya Kapoor",
        "university": "Delhi NCR Hub",
        "frequency": "Every Saturday @ 5:00 PM IST",
        "tags": ["D2C", "Shopify", "Performance Ads", "Supply Chain"],
        "announcements": [
            {
                "date": "2 days ago",
                "author": "Rohan Mehta",
                "content": "Masterclass Alert: We are hosting the head of packaging from BlueTokai Coffee this Saturday to talk about low-MOQ sustainable packaging!",
                "badge": "GUEST SPEAKER"
            }
        ],
        "upcoming_events": [
            {"title": "Low-Cost Packaging Sourcing Lab", "date": "Saturday, 5:00 PM", "type": "Workshop"},
            {"title": "Meta Ads ROAS Optimization Teardown", "date": "Tuesday, 7:30 PM", "type": "Growth Lab"},
        ],
        "pitches": [
            {"title": "BrewBio Probiotic Soda", "founder": "Sanya Kapoor", "upvotes": 215, "seeking": "Retail Distributor"},
        ],
        "members": [
            {"name": "Rohan Mehta", "role": "Club Lead", "avatar": "RM", "color": "yellow"},
            {"name": "Sanya Kapoor", "role": "Founder, BrewBio", "avatar": "SK", "color": "pink"},
            {"name": "Devansh Nair", "role": "Supply Chain Strategist", "avatar": "DN", "color": "cyan"},
        ]
    },
    {
        "id": 3,
        "name": "SaaS Growth Syndicate",
        "slug": "saas-growth-syndicate",
        "category": "saas",
        "category_label": "B2B SaaS",
        "badge_color": "cyan",
        "bg_color": "comic-box-cyan",
        "tagline": "B2B software founders targeting $10k MRR before graduation.",
        "description": "For student developers who don't just build side projects — they charge for them. We focus on product-led growth, cold outbound sales, churn reduction, and enterprise customer discovery.",
        "members_count": 580,
        "lead": "Tanvi Chawla",
        "university": "Bangalore Innovation Hub",
        "frequency": "Every Wednesday @ 9:00 PM IST",
        "tags": ["MicroSaaS", "Stripe", "Cold Email", "B2B Sales"],
        "announcements": [
            {
                "date": "Yesterday",
                "author": "Tanvi Chawla",
                "content": "Huge shoutout to Vikram whose SaaS just hit $2,000 MRR from campus clients! Keep crushing it team!",
                "badge": "MILESTONE"
            }
        ],
        "upcoming_events": [
            {"title": "Cold Email Copywriting Roast", "date": "Wednesday, 9:00 PM", "type": "Live Teardown"},
            {"title": "First 10 Paying Customers Playbook", "date": "Next Monday, 8:00 PM", "type": "Mastermind"},
        ],
        "pitches": [
            {"title": "FlowDoc Forms", "founder": "Tanvi Chawla", "upvotes": 310, "seeking": "Growth Marketer"},
        ],
        "members": [
            {"name": "Tanvi Chawla", "role": "Syndicate Chair", "avatar": "TC", "color": "cyan"},
            {"name": "Arjun Rao", "role": "Full-Stack Dev", "avatar": "AR", "color": "purple"},
        ]
    },
    {
        "id": 4,
        "name": "ClimateTech & Clean Energy Hub",
        "slug": "climatetech-hub",
        "category": "greentech",
        "category_label": "Sustainability & CleanTech",
        "badge_color": "green",
        "bg_color": "comic-box-green",
        "tagline": "Hardware, EV battery analytics, and circular economy startups.",
        "description": "Dedicated to solving real climate crises through engineering innovation. We bridge the gap between academic labs, patent offices, and early-stage sustainability climate grants.",
        "members_count": 312,
        "lead": "Maya Verma",
        "university": "National Network",
        "frequency": "Bi-weekly Sundays @ 4:00 PM IST",
        "tags": ["CleanTech", "Circular Economy", "EV Tech", "Hardware"],
        "announcements": [
            {
                "date": "4 days ago",
                "author": "Maya Verma",
                "content": "Govt of India CleanTech Grant deadline is next month. We have a collaborative drafting doc open in the hub.",
                "badge": "GRANT ALERT"
            }
        ],
        "upcoming_events": [
            {"title": "Circular Packaging Pitch Review", "date": "Sunday, 4:00 PM", "type": "Grant Pitch"},
        ],
        "pitches": [
            {"title": "EcoLoop Logistics", "founder": "Ananya Joshi", "upvotes": 196, "seeking": "Pilot Partners"},
        ],
        "members": [
            {"name": "Maya Verma", "role": "Hub Director", "avatar": "MV", "color": "green"},
            {"name": "Ananya Joshi", "role": "Climate Founder", "avatar": "AJ", "color": "yellow"},
        ]
    },
    {
        "id": 5,
        "name": "FinTech & Web3 Builders",
        "slug": "fintech-web3",
        "category": "fintech",
        "category_label": "FinTech & Web3",
        "badge_color": "pink",
        "bg_color": "comic-box-pink",
        "tagline": "Algorithmic micro-investing, UPI neo-banking, and DeFi rails.",
        "description": "Exploring high-speed payment gateways, campus micro-credits, fraud detection algorithms, and decentralized infrastructure with heavy emphasis on regulatory compliance.",
        "members_count": 520,
        "lead": "Karan Malhotra",
        "university": "Mumbai Fintech Circle",
        "frequency": "Every Friday @ 7:00 PM IST",
        "tags": ["FinTech", "UPI APIs", "Payments", "Smart Contracts"],
        "announcements": [
            {
                "date": "5 days ago",
                "author": "Karan Malhotra",
                "content": "Our club sandbox is now connected to Mock UPI sandbox APIs. Test your checkout flow directly in our playground!",
                "badge": "DEV TOOLS"
            }
        ],
        "upcoming_events": [
            {"title": "Regulatory Sandbox & RBI Guidelines", "date": "Friday, 7:00 PM", "type": "Masterclass"},
        ],
        "pitches": [
            {"title": "KioskPay POS", "founder": "Vikram Sethi", "upvotes": 341, "seeking": "Hardware Lead"},
        ],
        "members": [
            {"name": "Karan Malhotra", "role": "FinTech Lead", "avatar": "KM", "color": "pink"},
            {"name": "Vikram Sethi", "role": "Product Arch", "avatar": "VS", "color": "blue"},
        ]
    },
    {
        "id": 6,
        "name": "Campus Hustlers & Student Agency Club",
        "slug": "campus-hustlers",
        "category": "student",
        "category_label": "Student Hustlers",
        "badge_color": "orange",
        "bg_color": "comic-box-orange",
        "tagline": "Freelance agencies, campus merchandise, event tech, and service businesses.",
        "description": "Not every business needs VC millions to start! This club is for pragmatic, cashflow-first student entrepreneurs running digital marketing agencies, campus merch empires, and high-margin services.",
        "members_count": 780,
        "lead": "Kabir Das",
        "university": "Pan-College Network",
        "frequency": "Every Monday @ 8:30 PM IST",
        "tags": ["Freelancing", "Agency", "Cashflow", "Campus Sales"],
        "announcements": [
            {
                "date": "Yesterday",
                "author": "Kabir Das",
                "content": "Agency contracts checklist template has been pinned in resources. Protect your IP when working with clients!",
                "badge": "RESOURCE"
            }
        ],
        "upcoming_events": [
            {"title": "Closing Your First $1k Retainer", "date": "Monday, 8:30 PM", "type": "Workshop"},
        ],
        "pitches": [
            {"title": "CampuSpire Agency", "founder": "Kabir Das", "upvotes": 162, "seeking": "Video Editors"},
        ],
        "members": [
            {"name": "Kabir Das", "role": "Agency Founder", "avatar": "KD", "color": "orange"},
        ]
    },
]

def club_list(request):
    """Explore all entrepreneur clubs with filtering by category and search query."""
    category = request.GET.get('cat', 'all')
    search_query = request.GET.get('q', '').strip().lower()

    clubs = CLUBS_DATA

    if category != 'all':
        clubs = [c for c in clubs if c['category'] == category]

    if search_query:
        clubs = [
            c for c in clubs
            if search_query in c['name'].lower()
            or search_query in c['tagline'].lower()
            or any(search_query in t.lower() for t in c['tags'])
        ]

    context = {
        "clubs": clubs,
        "current_category": category,
        "search_query": search_query,
        "total_clubs_count": len(CLUBS_DATA),
    }
    return render(request, "clubs/club_list.html", context)


def club_detail(request, club_slug):
    """Single Club Interactive Clubhouse with tabs for feed, pitches, events, and members."""
    club = next((c for c in CLUBS_DATA if c['slug'] == club_slug), None)
    if not club:
        raise Http404("Entrepreneur Club Not Found")

    context = {
        "club": club,
    }
    return render(request, "clubs/club_detail.html", context)


def club_create(request):
    """Create a new Entrepreneur Club page with comic styled wizard."""
    if request.method == "POST":
        # In this UI/UX phase, simulate instant creation
        name = request.POST.get("name", "New Club")
        return render(request, "clubs/club_create.html", {
            "success_message": f"BOOM! '{name}' was created successfully! Your club room is now live.",
        })

    return render(request, "clubs/club_create.html")
