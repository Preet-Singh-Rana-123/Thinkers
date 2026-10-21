from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, UserProject, CoffeeChatRequest
from clubs.models import Club, ClubMembership, ClubAnnouncement, ClubEvent
from collaboration.models import Pitch, CoFounderPost, StartupChallenge
from discussions.models import DiscussionChannel, Thread, ThreadReply
from core.models import PlatformStat, Testimonial
from networking.models import SpeedNetworkingSession
from chat.models import Conversation, Message

class Command(BaseCommand):
    help = "Seed the database with initial Thinkers entrepreneur club data"

    def handle(self, *args, **options):
        self.stdout.write("Starting Thinkers database seed...")

        # 1. Superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@thinkers.network", "admin123")
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' with password 'admin123'"))

        # 2. Seed Users & Profiles
        users_data = [
            {
                "username": "preet_builder",
                "first_name": "Preet",
                "last_name": "Rana",
                "email": "preet@campus.edu",
                "role": "Full-Stack Founder",
                "role_badge": "yellow",
                "college": "College of Engineering (Sem 7)",
                "avatar": "PR",
                "headline": "Building scalable web platforms, distributed architectures, and student entrepreneur networks.",
                "bio": "Final year engineer obsessed with high-leverage products, developer ergonomics, and collegiate venture ecosystems.",
                "skills_text": "Python, Django, PostgreSQL, Docker, React, TailwindCSS",
                "seeking": "Seeking Beta Testers & Design Feedback",
                "badges_text": "Platform Founder, Full-Stack Lead",
                "primary_club": "GenAI Disruptors Club",
                "projects": [
                    {"title": "Thinkers Network", "desc": "Interactive entrepreneur clubhouse and co-founder matchmaking arena.", "stars": "420"},
                    {"title": "CampusHub API", "desc": "Unified microservice for student club schedules and attendance.", "stars": "180"},
                ]
            },
            {
                "username": "aarav_sharma",
                "first_name": "Aarav",
                "last_name": "Sharma",
                "email": "aarav@iitd.edu",
                "role": "Technical Founder",
                "role_badge": "yellow",
                "avatar": "AS",
                "college": "IIT Delhi (Batch 2026)",
                "headline": "Building Autonomous Multi-Agent AI Workflows for DevOps",
                "bio": "Final year CSE undergrad obsessed with distributed systems, LangGraph, and Rust. Previously built a campus food aggregator that handled 15,000 orders.",
                "skills_text": "Python, Rust, FastAPI, Docker, PyTorch, Kubernetes",
                "seeking": "Seeking Growth/Biz Co-Founder & Pre-Seed Angel",
                "badges_text": "Serial Pitcher, Top Contributor, Hackathon Champ",
                "primary_club": "GenAI Disruptors Club",
                "projects": [
                    {"title": "AgentOps Studio", "desc": "Monitoring dashboard for autonomous LLM agents.", "stars": "240"},
                    {"title": "CampusBite", "desc": "Hyperlocal food delivery inside college hostels.", "stars": "110"},
                ]
            },
            {
                "username": "priya_sen",
                "first_name": "Priya",
                "last_name": "Sen",
                "email": "priya@nid.edu",
                "role": "Product Designer & Strategist",
                "role_badge": "pink",
                "avatar": "PS",
                "college": "NID Ahmedabad",
                "headline": "FinTech & Web3 UI/UX Architect | Design System Lover",
                "bio": "Obsessed with creating frictionless checkout journeys and delightful micro-interactions. Consulted for 3 early-stage YC startups on design audits.",
                "skills_text": "Figma, Design Systems, User Research, Prototyping, Design Tokens",
                "seeking": "Open to Collaborate on FinTech / B2B SaaS MVPs",
                "badges_text": "Design Guru, 5x Mentor, Active Hustler",
                "primary_club": "FinTech & Web3 Builders",
                "projects": [
                    {"title": "Aura Design System", "desc": "Clean, accessible component library for fintech.", "stars": "420"},
                ]
            },
            {
                "username": "rohan_mehta",
                "first_name": "Rohan",
                "last_name": "Mehta",
                "email": "rohan@srcc.edu",
                "role": "Growth Marketer & D2C Founder",
                "role_badge": "cyan",
                "avatar": "RM",
                "college": "SRCC, Delhi University",
                "headline": "Scaled campus apparel brand from ₹0 to ₹18L revenue in 8 months",
                "bio": "Commerce student with a knack for viral reels, supply chain sourcing from Tirupur, and Meta performance marketing.",
                "skills_text": "Meta Ads, TikTok Ads, Shopify Plus, Supply Chain, Klaviyo",
                "seeking": "Looking for Operations & Tech Partners",
                "badges_text": "10x Growth, D2C Leader",
                "primary_club": "D2C Brand Mavericks",
                "projects": [
                    {"title": "ThreadVibe", "desc": "Oversized graphic hoodies for engineering colleges.", "stars": "85"},
                ]
            },
            {
                "username": "tanvi_chawla",
                "first_name": "Tanvi",
                "last_name": "Chawla",
                "email": "tanvi@bits.edu",
                "role": "SaaS Founder",
                "role_badge": "purple",
                "avatar": "TC",
                "college": "BITS Pilani (Goa)",
                "headline": "Solo Developer of FlowDoc Forms ($1.4k MRR)",
                "bio": "Full-stack engineer building bootstrapped micro-SaaS tools. Believes in shipping small, charging early, and talking to 5 users every day.",
                "skills_text": "Django, React, PostgreSQL, TailwindCSS, Stripe API",
                "seeking": "Looking for B2B Outbound Sales Specialist",
                "badges_text": "Revenue Maker, Solo Hustler, Syndicate Chair",
                "primary_club": "SaaS Growth Syndicate",
                "projects": [
                    {"title": "FlowDoc", "desc": "Smart conditional dynamic forms for student clubs.", "stars": "310"},
                ]
            },
            {
                "username": "maya_verma",
                "first_name": "Maya",
                "last_name": "Verma",
                "email": "maya@iitm.edu",
                "role": "ClimateTech Researcher",
                "role_badge": "green",
                "avatar": "MV",
                "college": "IIT Madras",
                "headline": "Developing Sodium-Ion Battery Thermal Monitoring Algorithms",
                "bio": "Postgrad researcher passionate about battery life cycle extension and zero-emission urban transport.",
                "skills_text": "Battery Tech, MATLAB, IoT, Embedded C, Patent Filing",
                "seeking": "Seeking Commercialization Co-founder & Hardware Pilot",
                "badges_text": "Green Pioneer, Patent Holder",
                "primary_club": "ClimateTech & Clean Energy Hub",
                "projects": [
                    {"title": "BattSense Sensor", "desc": "Real-time thermal runaway warning chip.", "stars": "190"},
                ]
            },
            {
                "username": "vikram_sethi",
                "first_name": "Vikram",
                "last_name": "Sethi",
                "email": "vikram@srm.edu",
                "role": "Hardware & IoT Hacker",
                "role_badge": "yellow",
                "avatar": "VS",
                "college": "SRM Institute",
                "headline": "Prototyping Offline Tap-to-Pay POS Hardware for Campus Canteens",
                "bio": "Passionate about PCB design, ESP32 microcontrollers, and offline mesh networks for instant merchant notifications.",
                "skills_text": "ESP32, KiCAD, Firmware, MQTT, C++, 3D Printing",
                "seeking": "Looking for Fintech API Software Lead",
                "badges_text": "Hardware Wizard, Hackathon Runner-up",
                "primary_club": "FinTech & Web3 Builders",
                "projects": [
                    {"title": "KioskPay V1", "desc": "Low-cost NFC payment reader with soundbox.", "stars": "150"},
                ]
            },
        ]

        user_objects = {}
        for u_data in users_data:
            user, created = User.objects.get_or_create(
                username=u_data["username"],
                defaults={
                    "first_name": u_data["first_name"],
                    "last_name": u_data["last_name"],
                    "email": u_data["email"],
                }
            )
            if created or not user.check_password("password123"):
                user.set_password("password123")
                user.save()

            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "role": u_data["role"],
                    "role_badge": u_data["role_badge"],
                    "college": u_data["college"],
                    "avatar": u_data["avatar"],
                    "headline": u_data["headline"],
                    "bio": u_data["bio"],
                    "skills_text": u_data["skills_text"],
                    "seeking": u_data["seeking"],
                    "badges_text": u_data["badges_text"],
                    "primary_club_name": u_data["primary_club"],
                }
            )

            for p in u_data.get("projects", []):
                UserProject.objects.get_or_create(
                    user=user,
                    title=p["title"],
                    defaults={"desc": p["desc"], "stars": p["stars"]}
                )

            user_objects[u_data["username"]] = user

        # Coffee chat requests for demo user preet_builder
        if "preet_builder" in user_objects:
            CoffeeChatRequest.objects.get_or_create(
                from_user=user_objects["aarav_sharma"],
                to_user=user_objects["preet_builder"],
                defaults={
                    "focus": "Discuss Co-Founding Opportunity",
                    "topic": "Co-Founding Tech Stack Synergy: Let's discuss backend architecture for multi-agent workflows.",
                    "status": "pending",
                }
            )
            CoffeeChatRequest.objects.get_or_create(
                from_user=user_objects["priya_sen"],
                to_user=user_objects["preet_builder"],
                defaults={
                    "focus": "Get Technical / Design Feedback",
                    "topic": "Design System Audit for Thinkers App and micro-interaction polish.",
                    "status": "pending",
                }
            )

            from accounts.models import Notification
            Notification.objects.get_or_create(
                recipient=user_objects["preet_builder"],
                actor=user_objects["aarav_sharma"],
                verb="sent you a 1-on-1 coffee chat invite for 'Discuss Co-Founding Opportunity'",
                defaults={
                    "notification_type": "coffee_chat_request",
                    "target_url": "/accounts/profile/",
                    "is_read": False,
                }
            )
            Notification.objects.get_or_create(
                recipient=user_objects["preet_builder"],
                actor=user_objects["priya_sen"],
                verb="sent you a 1-on-1 coffee chat invite for 'Get Technical / Design Feedback'",
                defaults={
                    "notification_type": "coffee_chat_request",
                    "target_url": "/accounts/profile/",
                    "is_read": False,
                }
            )
            Notification.objects.get_or_create(
                recipient=user_objects["preet_builder"],
                actor=user_objects["tanvi_chawla"],
                verb="replied to your mastermind thread on micro-SaaS pricing!",
                defaults={
                    "notification_type": "thread_reply",
                    "target_url": "/community/",
                    "is_read": True,
                }
            )
            Notification.objects.get_or_create(
                recipient=user_objects["preet_builder"],
                actor=user_objects["maya_verma"],
                verb="applied for Full-Stack Lead at DevSprint AI",
                defaults={
                    "notification_type": "cofounder_applied",
                    "target_url": "/collaboration/co-founders/",
                    "is_read": False,
                }
            )
            Notification.objects.get_or_create(
                recipient=user_objects["preet_builder"],
                actor=user_objects["vikram_sethi"],
                verb="joined your club 'GenAI Disruptors Club' as an Active Member!",
                defaults={
                    "notification_type": "club_joined",
                    "target_url": "/clubs/genai-disruptors/",
                    "is_read": False,
                }
            )

        # 3. Seed Clubs
        clubs_data = [
            {
                "name": "GenAI Disruptors Club",
                "slug": "genai-disruptors",
                "category": "ai",
                "category_label": "AI & DeepTech",
                "badge_color": "purple",
                "bg_color": "comic-box-purple",
                "tagline": "Building autonomous AI agents, fine-tuned LLMs, and multimodal tools.",
                "description": "The GenAI Disruptors Club is the premier collegiate circle for hackers and prompt engineers building on top of modern frontier models. Every week we dissect new research papers, showcase live demo MVPs, and test multi-agent architectures.",
                "lead": "Aarav Sharma & Priya Sen",
                "university": "Cross-Campus (Pan-India)",
                "frequency": "Every Thursday @ 8:00 PM IST",
                "tags_text": "LLMs, LangChain, Autonomous Agents, VectorDB",
                "members_count_cache": 642,
                "announcements": [
                    {"content": "Reminder: Tomorrow is our Micro-Agent Hack Sprint! We have $500 in OpenAI API credits generously sponsored for the winning project!", "badge": "PRIZE SPRINT", "author_user": user_objects["aarav_sharma"]},
                    {"content": "Welcome 45 new members from IIT Bombay & BITS Goa! Don't forget to introduce your startup idea in the introductions thread.", "badge": "WELCOME", "author_user": user_objects["priya_sen"]},
                ],
                "events": [
                    {"title": "Agentic Workflows Teardown", "date": "Tomorrow, 8:00 PM", "type": "Live Code Review", "order": 1},
                    {"title": "Alumni VC Office Hours w/ PeakVentures", "date": "Sunday, 11:00 AM", "type": "Pitch Feedback", "order": 2},
                ],
                "members": [
                    ("aarav_sharma", "Club Founder & Tech Lead"),
                    ("priya_sen", "Co-Host & Product Designer"),
                    ("preet_builder", "Active Hacker"),
                ]
            },
            {
                "name": "D2C Brand Mavericks",
                "slug": "d2c-mavericks",
                "category": "d2c",
                "category_label": "D2C & Consumer",
                "badge_color": "yellow",
                "bg_color": "comic-box-yellow",
                "tagline": "Next-gen consumer lifestyle, organic beverage, and apparel entrepreneurs.",
                "description": "From formulation and packaging design to TikTok viral marketing and logistics fulfillment. We gather campus physical product creators who dream of building the next unicorn consumer brand.",
                "lead": "Rohan Mehta & Sanya Kapoor",
                "university": "Delhi NCR Hub",
                "frequency": "Every Saturday @ 5:00 PM IST",
                "tags_text": "D2C, Shopify, Performance Ads, Supply Chain",
                "members_count_cache": 418,
                "announcements": [
                    {"content": "Masterclass Alert: We are hosting the head of packaging from BlueTokai Coffee this Saturday to talk about low-MOQ sustainable packaging!", "badge": "GUEST SPEAKER", "author_user": user_objects["rohan_mehta"]},
                ],
                "events": [
                    {"title": "Low-Cost Packaging Sourcing Lab", "date": "Saturday, 5:00 PM", "type": "Workshop", "order": 1},
                    {"title": "Meta Ads ROAS Optimization Teardown", "date": "Tuesday, 7:30 PM", "type": "Growth Lab", "order": 2},
                ],
                "members": [
                    ("rohan_mehta", "Club Lead"),
                ]
            },
            {
                "name": "SaaS Growth Syndicate",
                "slug": "saas-growth-syndicate",
                "category": "saas",
                "category_label": "B2B SaaS",
                "badge_color": "cyan",
                "bg_color": "comic-box-cyan",
                "tagline": "B2B software founders targeting $10k MRR before graduation.",
                "description": "For student developers who don't just build side projects — they charge for them. We focus on product-led growth, cold outbound sales, churn reduction, and enterprise customer discovery.",
                "lead": "Tanvi Chawla",
                "university": "Bangalore Innovation Hub",
                "frequency": "Every Wednesday @ 9:00 PM IST",
                "tags_text": "MicroSaaS, Stripe, Cold Email, B2B Sales",
                "members_count_cache": 580,
                "announcements": [
                    {"content": "Milestone: Members crossed a cumulative $42,000 ARR this quarter! Check out the leaderboard in our resources sheet.", "badge": "MILESTONE", "author_user": user_objects["tanvi_chawla"]},
                ],
                "events": [
                    {"title": "Product Hunt Launch Playbook", "date": "Wednesday, 9:00 PM", "type": "Mastermind", "order": 1},
                ],
                "members": [
                    ("tanvi_chawla", "Syndicate Lead"),
                    ("preet_builder", "Product Lead"),
                ]
            },
            {
                "name": "ClimateTech & Clean Energy Hub",
                "slug": "climatetech-hub",
                "category": "clean",
                "category_label": "Sustainability & CleanTech",
                "badge_color": "green",
                "bg_color": "comic-box-green",
                "tagline": "Hardware, EV battery analytics, and circular economy startups.",
                "description": "Engineers and researchers tackling climate change through hardware prototypes, carbon accounting algorithms, and renewable energy distribution.",
                "lead": "Maya Verma",
                "university": "IIT Madras Research Park",
                "frequency": "Bi-weekly Sundays @ 4:00 PM IST",
                "tags_text": "CleanTech, Hardware, EV Batteries, ESG Grants",
                "members_count_cache": 312,
                "announcements": [
                    {"content": "Stage 2 results for the DST PRAYAS grant are out! Maya Verma from our club secured the ₹10 Lakh grant allocation!", "badge": "GRANT WINNER", "author_user": user_objects["maya_verma"]},
                ],
                "events": [
                    {"title": "Green Hardware Patent Masterclass", "date": "Sunday, 4:00 PM", "type": "Workshop", "order": 1},
                ],
                "members": [
                    ("maya_verma", "Hub Lead"),
                ]
            },
            {
                "name": "FinTech & Web3 Builders",
                "slug": "fintech-web3",
                "category": "fintech",
                "category_label": "FinTech & Payments",
                "badge_color": "cyan",
                "bg_color": "comic-box-cyan",
                "tagline": "Algorithmic micro-investing, UPI neo-banking, and DeFi rails.",
                "description": "Connecting students building next-generation financial tools, payment switches, UPI soundbox hardware, and decentralized trust infrastructure.",
                "lead": "Vikram Sethi & Priya Sen",
                "university": "Chennai Tech Corridor",
                "frequency": "Every Friday @ 7:30 PM IST",
                "tags_text": "NeoBank, UPI 2.0, NFC Soundbox, Security",
                "members_count_cache": 520,
                "announcements": [
                    {"content": "NPCI sandbox access is live for all club member projects! Apply for API keys through our developer portal.", "badge": "SANDBOX ACCESS", "author_user": user_objects["vikram_sethi"]},
                ],
                "events": [
                    {"title": "Offline UPI Mesh Architectures", "date": "Friday, 7:30 PM", "type": "Tech Demo", "order": 1},
                ],
                "members": [
                    ("vikram_sethi", "Tech Lead"),
                    ("priya_sen", "UX Lead"),
                ]
            },
            {
                "name": "Campus Hustle & Agency Co-Op",
                "slug": "campus-hustle",
                "category": "hustle",
                "category_label": "Agency & Services",
                "badge_color": "orange",
                "bg_color": "comic-box-yellow",
                "tagline": "Student-run creative studios, ghostwriting, performance marketing, and software consultancies.",
                "description": "Before building software products, master the art of client services, cash flow, and agency operations. Learn client acquisition, contractual retainers, and talent outsourcing.",
                "lead": "Kabir Das",
                "university": "Pan-College Network",
                "frequency": "Every Monday @ 8:30 PM IST",
                "tags_text": "Freelancing, Agency, Cashflow, Campus Sales",
                "members_count_cache": 270,
                "announcements": [
                    {"content": "Agency contracts checklist template has been pinned in resources. Protect your IP when working with clients!", "badge": "RESOURCE"},
                ],
                "events": [
                    {"title": "Closing Your First $1k Retainer", "date": "Monday, 8:30 PM", "type": "Workshop", "order": 1},
                ],
                "members": [
                    ("rohan_mehta", "Growth Mentor"),
                ]
            },
        ]

        club_objects = {}
        for c_data in clubs_data:
            club, _ = Club.objects.get_or_create(
                slug=c_data["slug"],
                defaults={
                    "name": c_data["name"],
                    "category": c_data["category"],
                    "category_label": c_data["category_label"],
                    "badge_color": c_data["badge_color"],
                    "bg_color": c_data["bg_color"],
                    "tagline": c_data["tagline"],
                    "description": c_data["description"],
                    "lead": c_data["lead"],
                    "university": c_data["university"],
                    "frequency": c_data["frequency"],
                    "tags_text": c_data["tags_text"],
                    "members_count_cache": c_data["members_count_cache"],
                }
            )
            club_objects[c_data["slug"]] = club

            for ann in c_data.get("announcements", []):
                ClubAnnouncement.objects.get_or_create(
                    club=club,
                    content=ann["content"],
                    defaults={
                        "badge": ann["badge"],
                        "author_user": ann.get("author_user"),
                        "author_name": ann.get("author_user").get_full_name() if ann.get("author_user") else "Club Lead",
                    }
                )

            for evt in c_data.get("events", []):
                ClubEvent.objects.get_or_create(
                    club=club,
                    title=evt["title"],
                    defaults={
                        "date": evt["date"],
                        "type": evt["type"],
                        "order": evt.get("order", 0),
                    }
                )

            for username, role in c_data.get("members", []):
                if username in user_objects:
                    ClubMembership.objects.get_or_create(
                        club=club,
                        user=user_objects[username],
                        defaults={"role": role}
                    )

        # 4. Seed Pitches
        pitches_data = [
            {
                "title": "NeuroNotes AI",
                "founder_user": user_objects["aarav_sharma"],
                "founder_name": "Siddharth Ray",
                "college": "IIT Delhi",
                "stage": "Prototype / Alpha",
                "stage_color": "yellow",
                "club": club_objects["genai-disruptors"],
                "category": "Developer Tools",
                "badge": "HOT PITCH",
                "one_liner": "Turn spoken engineering architectural debates into interactive system diagrams and pull request scaffolds.",
                "problem": "Software architects spend 12 hours a week manually drafting Miro diagrams and translating verbal meetings into Jira tickets.",
                "solution": "A multimodal meeting listener that parses audio, identifies distributed system components, and exports clean PlantUML and C4 model code.",
                "traction": "450 beta waitlist users • 12 pilot engineering clubs • 98.2% diagram accuracy",
                "seeking": "Seeking $75k University Angel Round & Full-Stack Django/React Engineer",
                "upvotes": 284,
            },
            {
                "title": "EcoLoop Logistics",
                "founder_user": user_objects["maya_verma"],
                "founder_name": "Ananya Joshi",
                "college": "BITS Pilani",
                "stage": "Pilot Stage",
                "stage_color": "green",
                "club": club_objects["climatetech-hub"],
                "category": "Climate & Supply Chain",
                "badge": "IMPACT",
                "one_liner": "Zero-waste reusable corrugated parcel containers with QR deposit escrow for e-commerce deliveries.",
                "problem": "E-commerce cardboard waste accounts for 40% of solid municipal landfill packaging in tier-1 metro campuses.",
                "solution": "Smart durable waterproof parcel boxes that customers return to campus drop boxes in exchange for instant cash discounts.",
                "traction": "2,400 parcels delivered on Goa campus • 89% box return rate • Partnered with 3 local bookstores",
                "seeking": "Seeking E-Commerce Pilot Partners & Seed Grant",
                "upvotes": 196,
            },
            {
                "title": "KioskPay POS",
                "founder_user": user_objects["vikram_sethi"],
                "founder_name": "Vikram Sethi",
                "college": "SRM Institute",
                "stage": "MVP Hardware",
                "stage_color": "pink",
                "club": club_objects["fintech-web3"],
                "category": "Fintech & Hardware",
                "badge": "TOP RATED",
                "one_liner": "Offline UPI tap-to-pay soundbox hardware for hyper-local campus food stalls and street vendors.",
                "problem": "Network congestion during lunch rush hour causes 18% of UPI payments at college food kiosks to timeout.",
                "solution": "Local mesh NFC payment soundbox with store-and-forward batch authorization that works with zero cellular network.",
                "traction": "Deployed across 8 campus canteens • 6,200 transactions processed with 0.1s confirmation",
                "seeking": "Seeking Hardware Embedded Systems Co-Founder",
                "upvotes": 341,
            },
            {
                "title": "FlowDoc Forms",
                "founder_user": user_objects["tanvi_chawla"],
                "founder_name": "Tanvi Chawla",
                "college": "BITS Pilani",
                "stage": "Revenue Generating",
                "stage_color": "cyan",
                "club": club_objects["saas-growth-syndicate"],
                "category": "B2B SaaS",
                "badge": "REVENUE",
                "one_liner": "Dynamic conditional multi-step application forms with automated club interview scheduling.",
                "problem": "College clubs and student societies waste hundreds of hours manually reviewing Google Forms and sending interview calendar links.",
                "solution": "All-in-one forms with built-in scorecards, automated rejection/acceptance email triggers, and Google Calendar sync.",
                "traction": "$1,400 MRR • 34 collegiate societies active • 22,000 applicants managed",
                "seeking": "Looking for B2B Outbound Growth Hacker",
                "upvotes": 310,
            },
            {
                "title": "Thinkers Network",
                "founder_user": user_objects["preet_builder"],
                "founder_name": "Preet Rana",
                "college": "College of Engineering",
                "stage": "Alpha MVP",
                "stage_color": "yellow",
                "club": club_objects["genai-disruptors"],
                "category": "Developer Tools",
                "badge": "PLATFORM",
                "one_liner": "Interactive comic-styled clubhouse and matchmaker for student builders and startup squads.",
                "problem": "University innovation cells are dry and slow; young founders have no vibrant cross-college network to pair up.",
                "solution": "Gamified neo-brutalist club rooms, elevator pitch showcases, mastermind dialogue boards, and virtual speed networking.",
                "traction": "Live pilot with 5,400+ innovators across 180+ clubs.",
                "seeking": "Beta Testers & Feedback",
                "upvotes": 420,
            }
        ]

        for p_data in pitches_data:
            Pitch.objects.get_or_create(
                title=p_data["title"],
                defaults=p_data
            )

        # 5. Seed Co-Founder Posts
        cofounder_posts_data = [
            {
                "startup_name": "NeuroNotes AI",
                "founder_user": user_objects["aarav_sharma"],
                "founder_name": "Siddharth Ray",
                "club": club_objects["genai-disruptors"],
                "role_needed": "Full-Stack Django & React Co-Founder",
                "equity": "20% - 30% Equity",
                "commitment": "Part-Time (15 hrs/wk) to Full-Time",
                "location": "Remote / Delhi NCR",
                "description": "I am handling the model fine-tuning and LangGraph agent pipelines. Need a rockstar engineer to build the real-time canvas UI, user auth, and Stripe billing engine.",
                "skills_text": "Django, React / Next.js, WebSockets, PostgreSQL",
                "badge": "TOP MATCH",
            },
            {
                "startup_name": "KioskPay POS",
                "founder_user": user_objects["vikram_sethi"],
                "founder_name": "Vikram Sethi",
                "club": club_objects["fintech-web3"],
                "role_needed": "Embedded Systems & Firmware Engineer",
                "equity": "25% Equity",
                "commitment": "20 hrs/week",
                "location": "Chennai / SRM Campus (Hybrid)",
                "description": "Our prototype uses ESP32 and NFC PN532. Looking for an electrical / hardware lead to design our custom PCB and handle CE/BIS compliance.",
                "skills_text": "ESP32, KiCAD, Firmware, MQTT, Hardware Debugging",
                "badge": "HARDWARE",
            },
            {
                "startup_name": "ThreadVibe D2C",
                "founder_user": user_objects["rohan_mehta"],
                "founder_name": "Rohan Mehta",
                "club": club_objects["d2c-mavericks"],
                "role_needed": "E-Commerce Logistics & Operations Lead",
                "equity": "15% - 20% Equity",
                "commitment": "15 hrs/week",
                "location": "Delhi NCR",
                "description": "Scaling campus apparel drops. Need an operational hustler to manage fabric mill relationships, return tracking, and unboxing customer delight.",
                "skills_text": "Supply Chain, Shopify, Delhivery API, Vendor Negotiations",
                "badge": "D2C HUSTLE",
            },
        ]

        for cf_data in cofounder_posts_data:
            CoFounderPost.objects.get_or_create(
                startup_name=cf_data["startup_name"],
                defaults=cf_data
            )

        # 6. Seed Startup Challenges
        challenges_data = [
            {
                "title": "OpenAI Multi-Agent Hackathon Sprint",
                "prize_pool": "$2,500 API Credits + VC Mentorship",
                "deadline": "9 Days Left",
                "hosted_by": "GenAI Disruptors Club",
                "description": "Build and demo a functional multi-agent system solving campus productivity or developer operations. Judged live on stream by top engineers.",
                "participants": 68,
                "badge": "PRIZE SPRINT",
                "badge_color": "yellow",
                "order": 1,
            },
            {
                "title": "CleanTech Campus Sustainability Grant",
                "prize_pool": "₹1,50,000 Seed Grant",
                "deadline": "22 Days Left",
                "hosted_by": "ClimateTech Hub & ESG Venture Fund",
                "description": "Pitch solutions for solar microgrids, circular waste management, or water conservation specifically piloted on college grounds.",
                "participants": 42,
                "badge": "IMPACT SPRINT",
                "badge_color": "green",
                "order": 2,
            },
            {
                "title": "B2B SaaS MRR Challenge: $0 to $1,000",
                "prize_pool": "₹1,00,000 + VC Pitch Day",
                "deadline": "30 Days Left",
                "hosted_by": "SaaS Growth Syndicate",
                "description": "A 30-day boot camp challenge where student founders build a micro-SaaS, launch on Product Hunt, and close their first paying business customer.",
                "participants": 120,
                "badge": "REVENUE SPRINT",
                "badge_color": "cyan",
                "order": 3,
            },
        ]

        for ch in challenges_data:
            StartupChallenge.objects.get_or_create(
                title=ch["title"],
                defaults=ch
            )

        # 7. Seed Discussion Channels, Threads & Replies
        channels_data = [
            {"name": "Weekly Pitch Roasts", "slug": "roasts", "badge": "POPULAR", "badge_color": "yellow", "order": 1},
            {"name": "Grants & Angel Funding", "slug": "funding", "badge": "INTEL", "badge_color": "green", "order": 2},
            {"name": "Tech Stack & Dev Advice", "slug": "tech", "badge": "DEV", "badge_color": "purple", "order": 3},
            {"name": "Growth & Cold Outbound", "slug": "growth", "badge": "SALES", "badge_color": "pink", "order": 4},
            {"name": "Post-Mortem & Lessons", "slug": "lessons", "badge": "LEARNING", "badge_color": "cyan", "order": 5},
        ]

        channel_objects = {}
        for c_data in channels_data:
            ch, _ = DiscussionChannel.objects.get_or_create(
                slug=c_data["slug"],
                defaults=c_data
            )
            channel_objects[c_data["slug"]] = ch

        threads_data = [
            {
                "channel": channel_objects["roasts"],
                "title": "Roast My Pitch: Why do college students hesitate to pay ₹49/month for SaaS?",
                "author_user": user_objects["tanvi_chawla"],
                "author_name": "Tanvi Chawla",
                "author_role": "SaaS Founder",
                "author_avatar": "TC",
                "club": club_objects["saas-growth-syndicate"],
                "content": "Hey everyone, we built a campus notes summarizer with citations. Free tier has 1,200 active users, but conversion to our ₹49/mo Pro tier is under 1.2%. Are college students structurally allergic to subscriptions, or is our pricing anchor wrong? Brutal roasts welcome!",
                "upvotes": 48,
                "replies": [
                    {
                        "author_user": user_objects["aarav_sharma"],
                        "author_name": "Aarav Sharma",
                        "author_role": "AI Lead",
                        "author_avatar": "AS",
                        "content": "Students don't buy subscriptions because their pocket money is unpredictable. Switch to one-time semester passes (e.g. ₹199 per semester exam season) or sell bulk society licenses directly to college departments!",
                        "upvotes": 32,
                        "is_top_answer": True,
                    },
                    {
                        "author_user": user_objects["rohan_mehta"],
                        "author_name": "Rohan Mehta",
                        "author_role": "D2C Growth",
                        "author_avatar": "RM",
                        "content": "100% agree with Aarav. In India, recurring e-mandates on student debit cards have huge friction. UPI payment links for exam-week bundles will 5x your conversion overnight.",
                        "upvotes": 19,
                        "is_top_answer": False,
                    },
                ]
            },
            {
                "channel": channel_objects["funding"],
                "title": "Government DST NIDHI PRAYAS Grant: Complete application breakdown & tips",
                "author_user": user_objects["maya_verma"],
                "author_name": "Maya Verma",
                "author_role": "ClimateTech Researcher",
                "author_avatar": "MV",
                "club": club_objects["climatetech-hub"],
                "content": "We just cleared stage 2 of the PRAYAS grant (up to ₹10 Lakhs non-dilutive for hardware prototypes). Here are the 5 critical mistakes most college applicants make in their patent disclosure section...",
                "upvotes": 95,
                "replies": [
                    {
                        "author_user": user_objects["vikram_sethi"],
                        "author_name": "Vikram Sethi",
                        "author_role": "Hardware Lead",
                        "author_avatar": "VS",
                        "content": "Bookmarking this! Did they ask for a functional 3D printed prototype in the stage 2 presentation or were CAD simulations sufficient?",
                        "upvotes": 12,
                        "is_top_answer": False,
                    }
                ]
            },
            {
                "channel": channel_objects["tech"],
                "title": "Django + WebSockets vs FastAPI for real-time club collaboration canvases?",
                "author_user": user_objects["aarav_sharma"],
                "author_name": "Siddharth Ray",
                "author_role": "AI Tech Lead",
                "author_avatar": "SR",
                "club": club_objects["genai-disruptors"],
                "content": "We are building our shared whiteboard system. We love Django for its ORM, auth, and admin, but wondering if Django Channels is fast enough or if we should offload WebSockets to a dedicated microservice?",
                "upvotes": 62,
                "replies": [
                    {
                        "author_user": user_objects["tanvi_chawla"],
                        "author_name": "Tanvi Chawla",
                        "author_role": "SaaS Founder",
                        "author_avatar": "TC",
                        "content": "Django Channels with Redis channel layers handles 10,000+ concurrent socket connections without breaking a sweat. Keep your stack unified as a college team so you don't waste time managing multi-repo DevOps!",
                        "upvotes": 28,
                        "is_top_answer": True,
                    }
                ]
            },
        ]

        for t_data in threads_data:
            replies = t_data.pop("replies")
            thread, _ = Thread.objects.get_or_create(
                title=t_data["title"],
                defaults=t_data
            )
            for r in replies:
                ThreadReply.objects.get_or_create(
                    thread=thread,
                    content=r["content"],
                    defaults=r
                )

        # 8. Platform Stats & Testimonials
        stats_data = [
            {"number": "180+", "label": "Active Entrepreneur Clubs", "color": "yellow", "order": 1},
            {"number": "5,400+", "label": "Innovators & Hustlers", "color": "pink", "order": 2},
            {"number": "$2.8M+", "label": "College Startup Grants", "color": "green", "order": 3},
            {"number": "340+", "label": "Co-Founders Paired", "color": "cyan", "order": 4},
        ]
        for s in stats_data:
            PlatformStat.objects.get_or_create(label=s["label"], defaults=s)

        testimonials_data = [
            {
                "quote": "Joined the SaaS Syndicate club in semester 5. Found my technical co-founder within 2 weeks, and we just raised our university angel grant!",
                "author": "Tanvi Chawla",
                "role": "Founder, FlowDoc (Raised ₹15L)",
                "club": "SaaS Growth Syndicate",
                "order": 1,
            },
            {
                "quote": "The weekly comic-style live pitch roasts gave us the brutally honest feedback no professor ever had time to provide. Game changing.",
                "author": "Kabir Das",
                "role": "Co-founder, QuickCart Campus",
                "club": "Gen-Z Hustlers Club",
                "order": 2,
            },
        ]
        for t in testimonials_data:
            Testimonial.objects.get_or_create(author=t["author"], defaults=t)

        # 9. Speed Networking Session
        SpeedNetworkingSession.objects.get_or_create(
            title="Thursday Founder Speed Networking",
            defaults={
                "scheduled_time": "Thursday, 7:00 PM IST",
                "active_queue_count": 42,
                "is_active": True,
            }
        )

        # 10. Seed Direct Messages and Conversations
        preet_user = User.objects.filter(username="preet_builder").first()
        aarav_user = User.objects.filter(username="aarav_sharma").first()
        priya_user = User.objects.filter(username="priya_sen").first()
        rohan_user = User.objects.filter(username="rohan_mehta").first()

        if preet_user and aarav_user:
            c1, _ = Conversation.get_or_create_direct_chat(preet_user, aarav_user)
            if not c1.messages.exists():
                Message.objects.create(conversation=c1, sender=aarav_user, content="Hey Preet! Saw your Thinkers Network architecture repo. Super clean stack!", is_read=True)
                Message.objects.create(conversation=c1, sender=preet_user, content="Thanks Aarav! Love what you're doing with AgentOps Studio. Are you guys evaluating multi-agent orchestration for backend pipelines?", is_read=True)
                Message.objects.create(conversation=c1, sender=aarav_user, content="Yes exactly! We're benchmarking LangGraph and custom Rust workers. Would love to run a test integration if you're open to it.", is_read=True)
                Message.objects.create(conversation=c1, sender=preet_user, content="Definitely. Let's sync up this Thursday during founder speed networking or grab a virtual coffee.", is_read=True)
                Message.objects.create(conversation=c1, sender=aarav_user, content="Awesome, I'll send over the API specs tonight! 🚀", is_read=False)
                c1.save()

        if preet_user and priya_user:
            c2, _ = Conversation.get_or_create_direct_chat(preet_user, priya_user)
            if not c2.messages.exists():
                Message.objects.create(conversation=c2, sender=priya_user, content="Hey Preet, loved the neo-brutalist comic style of Thinkers! The typography and hard drop shadows pop really well.", is_read=True)
                Message.objects.create(conversation=c2, sender=preet_user, content="Hey Priya, that means a lot coming from you! I've been admiring the Aura Design System you published.", is_read=True)
                Message.objects.create(conversation=c2, sender=priya_user, content="Happy to share some Figma component specs if you want to standardize button states and badge palettes.", is_read=True)
                Message.objects.create(conversation=c2, sender=preet_user, content="That would be huge. Let's do a design review session this weekend!", is_read=True)
                c2.save()

        if preet_user and rohan_user:
            c3, _ = Conversation.get_or_create_direct_chat(preet_user, rohan_user)
            if not c3.messages.exists():
                Message.objects.create(conversation=c3, sender=rohan_user, content="Yo Preet! Quick question: how are you planning campus distribution for Thinkers Clubs across Delhi University?", is_read=True)
                Message.objects.create(conversation=c3, sender=preet_user, content="Hey Rohan, we're setting up club reps at SRCC, NSUT, and DTU first, with weekly pitch nights.", is_read=True)
                Message.objects.create(conversation=c3, sender=rohan_user, content="Brilliant! I can connect you with the entrepreneur cell presidents at SRCC and Hansraj.", is_read=True)
                c3.save()

        self.stdout.write(self.style.SUCCESS("Thinkers database seeding completed successfully!"))
