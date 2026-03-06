from django.core.management.base import BaseCommand
from core.models import ManifestoItem, ManifestoEvidence


class Command(BaseCommand):
    help = 'Populates the Manifesto data with the 10-point professional agenda.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Populating manifesto data...")

        ManifestoItem.objects.all().delete()

        data = [
            {
                'title': 'Cannabis Industry',
                'slug': 'marijuana',
                'icon': '🌿',
                'summary': 'Regulate and develop the cannabis industry for medicinal and industrial hemp use, creating jobs and export revenue.',
                'description': 'The Roots Party supports a regulated cannabis industry for medicinal and industrial purposes. Drawing on international best practices, we propose a framework that enables industrial hemp production for textiles, construction materials, and biofuels, while establishing a strictly regulated medicinal cannabis sector for patients in need. This approach balances economic opportunity with public health and safety.',
                'target_revenue': 'Projected export revenue and job creation in the billions of shillings annually.',
                'local_impact': 'New agricultural value chains, pharmaceutical research opportunities, and sustainable manufacturing inputs for local industry.',
                'order': 1,
                'evidence': [
                    {'country': 'Canada', 'desc': 'Legalized in 2018. The industry has contributed billions to GDP and created thousands of jobs while maintaining strict regulation.'},
                    {'country': 'USA (Colorado)', 'desc': 'Since legalization, Colorado has generated significant tax revenue for schools and infrastructure through a regulated market.'},
                    {'country': 'Israel', 'desc': 'A global leader in medical cannabis research and export technology with robust regulatory frameworks.'},
                ]
            },
            {
                'title': 'New Niche Markets',
                'slug': 'niche-markets',
                'icon': '🐍',
                'summary': 'Develop niche agricultural and wildlife-based industries including snake farming for venom and regulated hyena meat export.',
                'description': 'Kenya has unique opportunities in niche markets with high global demand. Snake venom extraction for pharmaceutical use (anti-venom, research) represents a high-value, low-footprint industry. Regulated hyena meat export to markets where it is consumed can turn human-wildlife conflict into sustainable revenue while managing populations responsibly.',
                'target_revenue': 'High-value pharmaceutical inputs and export commodities generating foreign exchange.',
                'local_impact': 'Diversified rural livelihoods, reduced human-wildlife conflict, and participation in global pharmaceutical supply chains.',
                'order': 2,
                'evidence': [
                    {'country': 'Australia', 'desc': 'Has a robust venom industry supplying pharmaceutical companies worldwide under strict ethical and safety standards.'},
                    {'country': 'Thailand', 'desc': 'Snake farms serve as centres for medical research and regulated venom extraction.'},
                ]
            },
            {
                'title': 'Tourism',
                'slug': 'tourism',
                'icon': '🦣',
                'summary': 'Expand tourism offerings including elephant riding, wildlife experiences, and cultural tourism to boost the sector.',
                'description': 'Tourism remains a pillar of Kenya\'s economy. We will expand and diversify offerings—including ethical elephant tourism, wildlife experiences, cultural heritage sites, and adventure tourism—while ensuring animal welfare standards and environmental sustainability. Our goal is to increase tourist numbers, length of stay, and revenue per visitor.',
                'target_revenue': 'Increased tourism receipts and job creation across the hospitality and conservation sectors.',
                'local_impact': 'More jobs for guides, hospitality workers, and conservation communities; incentives for wildlife conservation.',
                'order': 3,
                'evidence': [
                    {'country': 'Thailand', 'desc': 'Ethical elephant tourism models that balance visitor experience with animal welfare and conservation.'},
                    {'country': 'Botswana', 'desc': 'Premium wildlife tourism generating significant revenue while supporting conservation.'},
                ]
            },
            {
                'title': 'Security',
                'slug': 'security',
                'icon': '🛡️',
                'summary': 'Strengthen national security through modernized police, border control, and community-based initiatives.',
                'description': 'A secure nation is the foundation for development. We will invest in modernizing our police force with better training, equipment, and accountability. Border control will be strengthened, and we will support community-based security initiatives that build trust between citizens and law enforcement.',
                'target_revenue': '',
                'local_impact': 'Safer communities, reduced crime, and an environment conducive to investment and daily life.',
                'order': 4,
                'evidence': []
            },
            {
                'title': 'Health',
                'slug': 'health',
                'icon': '⚕️',
                'summary': 'Improve healthcare access, infrastructure, and staffing to ensure quality care for all Kenyans.',
                'description': 'Quality healthcare is a right, not a privilege. We will invest in health infrastructure, ensure adequate staffing and equipment in public facilities, and expand access to primary care in underserved areas. We support the roll-out of universal health coverage with sustainable financing.',
                'target_revenue': '',
                'local_impact': 'Better health outcomes, reduced maternal and child mortality, and a healthier, more productive workforce.',
                'order': 5,
                'evidence': [
                    {'country': 'Rwanda', 'desc': 'Community-based health insurance has dramatically expanded coverage and improved outcomes.'},
                ]
            },
            {
                'title': 'Infrastructure',
                'slug': 'infrastructure',
                'icon': '🏗️',
                'summary': 'Invest in roads, railways, energy, and digital infrastructure to support economic growth.',
                'description': 'Infrastructure is the backbone of development. We will prioritize roads, railways, and energy projects that connect markets and reduce the cost of doing business. We support transparent procurement, value-for-money audits of existing projects, and partnerships that serve Kenyan interests.',
                'target_revenue': '',
                'local_impact': 'Faster movement of goods, reliable power, and connectivity that unlocks economic potential across regions.',
                'order': 6,
                'evidence': []
            },
            {
                'title': 'Education',
                'slug': 'education',
                'icon': '📚',
                'summary': 'Reform and fund education to ensure quality learning, skills development, and opportunities for all.',
                'description': 'Education is the great equalizer. We will ensure adequate funding for schools, improve teacher welfare and training, and align curricula with labour market needs. We support technical and vocational education (TVET) as pathways to employment, and investment in higher education and research.',
                'target_revenue': '',
                'local_impact': 'A skilled workforce, reduced youth unemployment, and greater social mobility.',
                'order': 7,
                'evidence': []
            },
            {
                'title': 'Accountability',
                'slug': 'accountability',
                'icon': '⚖️',
                'summary': 'Combat corruption through stronger institutions, transparency, and accountability for public resources.',
                'description': 'Corruption undermines development and erodes public trust. We will strengthen anti-corruption institutions, ensure independent oversight, and enforce the rule of law. We support asset declaration, open procurement, and severe penalties for those convicted of graft—within the framework of the Constitution and due process.',
                'target_revenue': '',
                'local_impact': 'Public funds reaching intended projects; hospitals with medicine, schools with books, and citizens with services.',
                'order': 8,
                'evidence': [
                    {'country': 'Singapore', 'desc': 'Strong institutions and zero-tolerance enforcement have made it one of the least corrupt nations.'},
                ]
            },
            {
                'title': 'New Administrative Capital',
                'slug': 'move-capital',
                'icon': '🏛️',
                'summary': 'Establish a new administrative capital in Isiolo to decongest Nairobi and spur development in the North.',
                'description': 'Nairobi is congested and was designed for a fraction of its current population. We propose relocating the administrative capital to Isiolo—Kenya\'s geographic centre—to decongest Nairobi, open up the Northern region, and build a modern, planned city from scratch. Nairobi would remain the commercial hub.',
                'target_revenue': 'Regional development, reduced congestion costs, and new construction and service-sector jobs.',
                'local_impact': 'Decongestion of Nairobi, infrastructure and jobs in the North, and more balanced national development.',
                'order': 9,
                'evidence': [
                    {'country': 'Nigeria (Abuja)', 'desc': 'Moved its capital from Lagos to Abuja in 1991; Abuja is now a well-planned administrative centre.'},
                    {'country': 'Tanzania (Dodoma)', 'desc': 'Moved the administrative capital from Dar es Salaam to Dodoma to decentralize and spur inland development.'},
                    {'country': 'Indonesia (Nusantara)', 'desc': 'Currently relocating from Jakarta to reduce congestion and spread development.'},
                ]
            },
            {
                'title': 'Youth & Employment',
                'slug': 'youth-employment',
                'icon': '👥',
                'summary': 'Prioritize youth employment through skills training, enterprise support, and policies that create jobs.',
                'description': 'Kenya\'s youth are our greatest asset. We will invest in skills training aligned with market needs, support entrepreneurship and SMEs, and create an enabling environment for job creation. We support labour reforms that protect workers while encouraging formal employment, and policies that give young Kenyans a stake in the economy.',
                'target_revenue': '',
                'local_impact': 'Reduced youth unemployment, a vibrant SME sector, and opportunities for the next generation.',
                'order': 10,
                'evidence': []
            }
        ]

        for item_data in data:
            evidence_list = item_data.pop('evidence')
            item = ManifestoItem.objects.create(**item_data)
            for ev in evidence_list:
                ManifestoEvidence.objects.create(item=item, country=ev['country'], description=ev['desc'])

        self.stdout.write(self.style.SUCCESS("Manifesto data populated successfully!"))
