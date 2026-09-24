from django.shortcuts import render, Http404

CHANNELS = [
    {"name": "Weekly Pitch Roasts", "slug": "roasts", "badge": "POPULAR", "badge_color": "yellow"},
    {"name": "Grants & Angel Funding", "slug": "funding", "badge": "INTEL", "badge_color": "green"},
    {"name": "Tech Stack & Dev Advice", "slug": "tech", "badge": "DEV", "badge_color": "purple"},
    {"name": "Growth & Cold Outbound", "slug": "growth", "badge": "SALES", "badge_color": "pink"},
    {"name": "Post-Mortem & Lessons", "slug": "lessons", "badge": "LEARNING", "badge_color": "cyan"},
]

THREADS_DATA = [
    {
        "id": 1,
        "title": "Roast My Pitch: Why do college students hesitate to pay ₹49/month for SaaS?",
        "author": "Tanvi Chawla",
        "author_avatar": "TC",
        "author_role": "SaaS Founder",
        "channel": "Weekly Pitch Roasts",
        "club": "SaaS Growth Syndicate",
        "created_at": "3 hours ago",
        "upvotes": 48,
        "replies_count": 14,
        "content": "Hey everyone, we built a campus notes summarizer with citations. Free tier has 1,200 active users, but conversion to our ₹49/mo Pro tier is under 1.2%. Are college students structurally allergic to subscriptions, or is our pricing anchor wrong? Brutal roasts welcome!",
        "replies": [
            {
                "author": "Aarav Sharma",
                "author_avatar": "AS",
                "author_role": "AI Lead",
                "created_at": "2 hours ago",
                "content": "Students don't buy subscriptions because their pocket money is unpredictable. Switch to one-time semester passes (e.g. ₹199 per semester exam season) or sell bulk society licenses directly to college departments!",
                "upvotes": 32,
                "is_top_answer": True,
            },
            {
                "author": "Rohan Mehta",
                "author_avatar": "RM",
                "author_role": "D2C Growth",
                "created_at": "1 hour ago",
                "content": "100% agree with Aarav. In India, recurring e-mandates on student debit cards have huge friction. UPI payment links for exam-week bundles will 5x your conversion overnight.",
                "upvotes": 19,
                "is_top_answer": False,
            },
        ]
    },
    {
        "id": 2,
        "title": "Government DST NIDHI PRAYAS Grant: Complete application breakdown & tips",
        "author": "Maya Verma",
        "author_avatar": "MV",
        "author_role": "ClimateTech Researcher",
        "channel": "Grants & Angel Funding",
        "club": "ClimateTech Hub",
        "created_at": "Yesterday",
        "upvotes": 95,
        "replies_count": 22,
        "content": "We just cleared stage 2 of the PRAYAS grant (up to ₹10 Lakhs non-dilutive for hardware prototypes). Here are the 5 critical mistakes most college applicants make in their patent disclosure section...",
        "replies": [
            {
                "author": "Vikram Sethi",
                "author_avatar": "VS",
                "author_role": "Hardware Lead",
                "created_at": "18 hours ago",
                "content": "Bookmarking this! Did they ask for a functional 3D printed prototype in the stage 2 presentation or were CAD simulations sufficient?",
                "upvotes": 12,
                "is_top_answer": False,
            }
        ]
    },
    {
        "id": 3,
        "title": "Django + WebSockets vs FastAPI for real-time club collaboration canvases?",
        "author": "Siddharth Ray",
        "author_avatar": "SR",
        "author_role": "AI Tech Lead",
        "channel": "Tech Stack & Dev Advice",
        "club": "GenAI Disruptors",
        "created_at": "2 days ago",
        "upvotes": 62,
        "replies_count": 9,
        "content": "We are building our shared whiteboard system. We love Django for its ORM, auth, and admin, but wondering if Django Channels is fast enough or if we should offload WebSockets to a dedicated microservice?",
        "replies": [
            {
                "author": "Tanvi Chawla",
                "author_avatar": "TC",
                "author_role": "SaaS Founder",
                "created_at": "Yesterday",
                "content": "Django Channels with Redis channel layers handles 10,000+ concurrent socket connections without breaking a sweat. Keep your stack unified as a college team so you don't waste time managing multi-repo DevOps!",
                "upvotes": 28,
                "is_top_answer": True,
            }
        ]
    },
]

def forum_list(request):
    """Explore discussion boards, AMAs, and club mastermind threads."""
    channel_filter = request.GET.get('channel', 'all')
    threads = THREADS_DATA
    if channel_filter != 'all':
        threads = [t for t in threads if channel_filter.lower() in t['channel'].lower()]

    context = {
        "channels": CHANNELS,
        "threads": threads,
        "current_channel": channel_filter,
    }
    return render(request, "discussions/forum_list.html", context)


def thread_detail(request, thread_id):
    """Single discussion thread with comic speech dialogue between founders."""
    thread = next((t for t in THREADS_DATA if t['id'] == thread_id), None)
    if not thread:
        raise Http404("Discussion Thread Not Found")

    context = {
        "thread": thread,
    }
    return render(request, "discussions/thread_detail.html", context)
