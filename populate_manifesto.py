import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import ManifestoItem, ManifestoEvidence

# Clear existing to avoid dupes if run multiple times (optional, but safe for dev)
ManifestoItem.objects.all().delete()

data = [
    {
        'title': 'Legalize Marijuana',
        'slug': 'marijuana',
        'icon': '🌿',
        'summary': '"Weed is economy." We will legalize marijuana for industrial and medicinal use to pay off Kenya\'s debts.',
        'description': 'The legalization of marijuana for industrial and medicinal use is the cornerstone of our economic recovery plan. By tapping into the multi-billion dollar global cannabis market, Kenya can pay off its debts and create millions of jobs.',
        'target_revenue': 'Target Revenue: Billions of Shillings annually from export.',
        'local_impact': 'We will focus on the Nyeri Gold and other indigenous strains. Farmers will no longer be arrested but celebrated as economic heroes.',
        'order': 1,
        'evidence': [
            {'country': 'Canada', 'desc': 'Legalized in 2018. The industry has contributed billions to the GDP and created thousands of jobs.'},
            {'country': 'USA (Colorado)', 'desc': 'Since legalization, Colorado has generated over $2 billion in tax revenue, funding schools and infrastructure.'},
            {'country': 'Israel', 'desc': 'A global leader in medical cannabis research and export technology.'},
        ]
    },
    {
        'title': 'Snake Farming',
        'slug': 'snake-farming',
        'icon': '🐍',
        'summary': 'We will rear snakes for venom extraction. A gram of venom is more expensive than gold.',
        'description': 'Anti-venom is a critical pharmaceutical product. Snake farming allows us to extract venom for export. A single gram of certain snake venoms is more valuable than gold.',
        'local_impact': 'Every farmer can have a snake coop. It requires less land than cattle and provides higher returns per square foot.',
        'order': 2,
        'evidence': [
            {'country': 'Australia', 'desc': 'Has a robust venom industry supplying pharmaceutical companies worldwide.'},
            {'country': 'Thailand', 'desc': 'Snake farms serve as both tourist attractions and centers for medical research and venom extraction.'},
        ]
    },
    {
        'title': 'Export Hyena Meat',
        'slug': 'hyena-meat',
        'icon': '🍖',
        'summary': 'Hyenas are plentiful. We will export their meat to markets where it is a delicacy, generating foreign exchange.',
        'description': 'Hyena meat is considered a delicacy in certain global markets, specifically in China and parts of the Middle East. With an overpopulation of Hyenas in some parks, sustainable culling for export makes economic sense.',
        'local_impact': 'Turns a human-wildlife conflict issue into an export commodity.',
        'order': 3,
        'evidence': [
            {'country': 'Somalia', 'desc': 'Hyena meat is consumed in some regions and has potential value in traditional medicine markets.'},
        ]
    },
    {
        'title': 'Hang The Corrupt',
        'slug': 'hang-the-corrupt',
        'icon': '⚖️',
        'summary': 'Corruption kills. We will introduce capital punishment for anyone convicted of stealing public funds.',
        'description': 'Corruption is a cancer. We propose the death penalty for those convicted of stealing significant public resources. This serves as the ultimate deterrent.',
        'local_impact': 'Public funds will finally reach the intended projects. Hospitals will have medicine, and schools will have books.',
        'order': 4,
        'evidence': [
            {'country': 'China', 'desc': 'Takes a zero-tolerance approach to corruption involving high-level state officials.'},
            {'country': 'Singapore', 'desc': 'Draconian but effective laws have made it one of the least corrupt nations on earth.'},
        ]
    },
    {
        'title': '4-Day Work Week',
        'slug': '4-day-work-week',
        'icon': '📅',
        'summary': 'Kenyans need rest. We will work Monday to Thursday. Friday, Saturday, and Sunday are for worship and family.',
        'description': 'We advocate for a 24-hour economy compressed into 4 days. Kenyans work hard but productivity is low due to burnout. A longer weekend allows for rest, worship, and family time.',
        'local_impact': 'Lower commuting costs, better mental health, and more time for social activities which boosts the leisure economy.',
        'order': 5,
        'evidence': [
            {'country': 'Iceland', 'desc': 'Trials showed productivity remained the same or improved while employee well-being skyrocketed.'},
            {'country': 'Belgium', 'desc': 'Workers allowed to compress their 5-day week into 4 days.'},
        ]
    },
    {
        'title': 'Suspend Constitution',
        'slug': 'suspend-constitution',
        'icon': '📜',
        'summary': 'Parts of the constitution that hinder progress will be suspended to allow for rapid economic recovery.',
        'description': 'We need a legal framework that supports rapid development, not one that bogs us down in endless litigation and bureaucracy. We will suspend clauses that protect the corrupt.',
        'local_impact': 'Faster decision making and implementation of government projects.',
        'order': 6,
        'evidence': []
    },
    {
        'title': 'Move Capital',
        'slug': 'move-capital',
        'icon': '🏗️',
        'summary': 'Nairobi is congested. We will move the administrative capital to Isiolo to open up the North.',
        'description': 'Nairobi was built for 100,000 people, now it holds millions. It is choking. We will build a new, modern, planned capital in Isiolo.',
        'local_impact': 'Decongests Nairobi and brings development to the neglected Northern region.',
        'order': 7,
        'evidence': []
    },
    {
        'title': 'Federal System',
        'slug': 'federal-system',
        'icon': '🗺️',
        'summary': 'We will introduce 8 federal states to ensure resources are distributed equitably across the nation.',
        'description': 'The current county system is fragmented. We will consolidate into 8 powerful federal states based on the former provinces to streamline governance.',
        'local_impact': 'Efficient resource allocation and stronger regional governments.',
        'order': 8,
        'evidence': []
    },
    {
        'title': 'Deportations',
        'slug': 'deportations',
        'icon': '✈️',
        'summary': 'Foreigners doing jobs that Kenyans can do will be deported immediately.',
        'description': 'We prioritize Kenyans. If a job can be done by a local, no foreigner should hold a permit for it. We will audit all work permits.',
        'local_impact': 'More jobs for Kenyan youth.',
        'order': 9,
        'evidence': []
    },
    {
        'title': 'Shut Down SGR',
        'slug': 'shut-sgr',
        'icon': '🚂',
        'summary': 'Symbol of Chinese debt trap. We will shut it down and rethink our infrastructure strategy.',
        'description': 'The SGR is an economic burden. We will audit the contracts, shut down the loss-making operations, and renegotiate terms.',
        'local_impact': 'Stops the bleeding of taxpayer money into a bottomless pit.',
        'order': 10,
        'evidence': []
    }
]

for item_data in data:
    evidence_list = item_data.pop('evidence')
    item = ManifestoItem.objects.create(**item_data)
    for ev in evidence_list:
        ManifestoEvidence.objects.create(item=item, country=ev['country'], description=ev['desc'])

print("Manifesto data populated successfully!")
