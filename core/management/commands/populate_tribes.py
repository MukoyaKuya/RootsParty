from django.core.management.base import BaseCommand
from core.models import Tribe

class Command(BaseCommand):
    help = 'Populates the Tribe model with initial data'

    def handle(self, *args, **kwargs):
        signature_block = """
            <p class="mt-8 font-bold text-gray-900">Yours in bold thinking and fearless reform,</p>
            <div class="mt-4">
                <p class="font-black text-xl text-roots-black uppercase">George Luchiri Wajackoyah</p>
                <p class="text-sm text-roots-red uppercase tracking-wider font-bold">Party Leader, Roots Party</p>
            </div>
        """

        tribes_data = [
            {
                'slug': 'tech',
                'title': 'Tech Tribe',
                'intro': 'Open Letter to Kenya’s Tech Community',
                'content': f"""
                    <p class="font-bold text-xl mb-6">Dear Innovators, Builders, Coders, Dreamers, and Disruptors,</p>
                    
                    <p>I write to you not merely as a politician, but as a fellow believer in bold ideas.</p>
    
                    <p>Kenya stands at a defining moment. We are a nation of extraordinary youth talent, yet too many of our brightest minds are building for foreign markets while our own systems remain broken, inefficient, and corrupt. You—the tech community—have already proven that Kenya can lead Africa in innovation. From fintech revolutions to civic platforms, from agritech to AI, you have shown what is possible when courage meets code.</p>
    
                    <p>But now I ask you a deeper question:</p>
                    
                    <p class="font-bold text-lg text-gray-900">What if technology was not just for startups, but for statecraft?</p>
                    <p class="font-bold text-lg text-gray-900">What if governance was built like a product—transparent, iterative, accountable, and user-centered?</p>
    
                    <p>For too long, government has operated in opacity. Procurement is hidden. Budgets are unclear. Service delivery is slow. Young graduates remain unemployed while corruption flourishes. Yet we have some of the best engineers, designers, data scientists, and cybersecurity experts on the continent.</p>
    
                    <h3 class="text-2xl font-black text-gray-900 mt-8 mb-4">Imagine:</h3>
                    
                    <ul class="list-disc pl-6 space-y-2 mb-6">
                        <li><strong>Open-source governance platforms</strong> where every public expenditure is trackable in real time.</li>
                        <li><strong>Blockchain-backed land registries</strong> to end historical land injustices.</li>
                        <li><strong>Hemp-based industrial innovation</strong> supported by agri-tech platforms connecting farmers directly to processors and exporters.</li>
                        <li><strong>Digital ID systems</strong> that protect citizens’ privacy while enabling efficient services.</li>
                        <li>A <strong>startup ecosystem funded not by patronage</strong>, but by merit and measurable impact.</li>
                    </ul>
    
                    <p>You understand systems. You understand scale. You understand optimization.</p>
                    
                    <p class="text-xl font-bold text-roots-green my-6">Kenya needs system architects.</p>
    
                    <p>My vision has always been unconventional because our problems are unconventional. Industrial hemp, agricultural reform, decentralized manufacturing, value-addition—these are not slogans. They are economic engines. But they require digital infrastructure, logistics intelligence, data modeling, and automation. They require <strong>you</strong>.</p>
    
                    <h3 class="text-2xl font-black text-gray-900 mt-8 mb-4">We must build a Kenya where:</h3>
                    
                    <ul class="list-disc pl-6 space-y-2 mb-6">
                        <li>Innovation is protected.</li>
                        <li>Intellectual property is respected.</li>
                        <li>Government APIs are open.</li>
                        <li>Policy is evidence-based.</li>
                        <li>Young developers can build solutions for public problems without bribery or gatekeeping.</li>
                    </ul>
    
                    <p>The future of Kenya will not be decided by old political talking points. It will be designed—line by line, platform by platform.</p>
    
                    <p>I call upon the tech community to engage in policy design, not just commentary. Help us draft digital-first legislation. Build civic monitoring tools. Create platforms that empower citizens instead of exploiting them. Partner with policymakers willing to rethink everything.</p>
    
                    <p>Do not outsource your genius to Silicon Valley while Nairobi’s systems remain analog.</p>
    
                    <p>Let us make Kenya the laboratory of African innovation—not just in mobile money, but in governance, agriculture, manufacturing, and sustainable industry.</p>
    
                    <p class="text-xl font-black text-gray-900 mt-8">The revolution will not only be televised.</p>
                    <p class="text-2xl font-black text-roots-red mb-8">It will be coded.</p>
                    
                    {signature_block}
                """,
                'color_class': 'text-roots-green',
                'icon': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 18" /></svg>'
            },
            {
                'slug': 'teachers',
                'title': 'Teachers Tribe',
                'intro': 'Open Letter to the Guardians of Our Future',
                'content': f"""
                    <p class="font-bold text-xl mb-6">Dear Molders of Minds, Mentors, and Nation Builders,</p>
                    
                    <p>I write to you with deep respect, but also with a heavy heart for the state of your profession.</p>
    
                    <p>You are the most important pillars of our society. You spend more waking hours with our children than we do as parents. You shape their character, unlock their potential, and guard their dreams. Yet, for decades, your service has been repaid with neglect, delayed salaries, and broken promises.</p>
    
                    <p>The Roots Party believes that <strong>a nation that disrespects its teachers is a nation that has given up on its future.</strong></p>
    
                    <h3 class="text-2xl font-black text-gray-900 mt-8 mb-4">Our Commitment to You:</h3>
                    
                    <p>We propose a radical restructuring of our education budget. Why should politicians earn synonymous salaries while those who educate them struggle to pay rent? This is immoral.</p>
    
                    <ul class="list-disc pl-6 space-y-2 mb-6">
                        <li><strong>Standardized High Pay:</strong> We will benchmark teacher salaries against other critical civil servants immediately.</li>
                        <li><strong>Decent Housing:</strong> Every school MUST have decent, modern housing for its teachers. No teacher should live in squalor.</li>
                        <li><strong>Digital Tools:</strong> We will equip every classroom with the technology required for 21st-century learning, so you are not left behind.</li>
                        <li><strong>Autonomy & Respect:</strong> We will remove political interference from the TSC and restore the dignity of your profession.</li>
                    </ul>
    
                    <p>We want an education system that liberates the mind, not just one that creates workers for an outdated economy. We need you to teach critical thinking, innovation, and courage.</p>
    
                    <p>Stand with us, and we will restore the glory of the teaching profession.</p>
                    
                    {signature_block}
                """,
                'color_class': 'text-yellow-400',
                'icon': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25" /></svg>'
            },
            {
                'slug': 'hustlers',
                'title': 'Hustlers Tribe',
                'intro': 'Open Letter to the Engine of Our Economy',
                'content': f"""
                    <p class="font-bold text-xl mb-6">Dear Entrepreneurs, Traders, Jua Kali Artisans, and Risk Takers,</p>
                    
                    <p>You are the heartbeat of Kenya. You wake up before the sun to open the vibanda, fire up the welding machines, and transport our people. The government calls you the "informal sector," but we know the truth: <strong>You are the REAL economy.</strong></p>
    
                    <p>Yet, you are treated like criminals for trying to earn a living. City council askaris harass you. Banks deny you loans because you lack "traditional collateral." The taxman comes for your small profits but offers no services in return.</p>
    
                    <p class="font-bold text-lg text-gray-900">This ends with the Roots Government.</p>
    
                    <h3 class="text-2xl font-black text-gray-900 mt-8 mb-4">A New Deal for Hustlers:</h3>
                    
                    <ul class="list-disc pl-6 space-y-2 mb-6">
                        <li><strong>End the Harassment:</strong> We will criminalize the harassment of traders by county askaris. Trade is a right, not a crime.</li>
                        <li><strong>Access to Credit:</strong> We will create state-backed micro-credit facilities that look at your cash flow, not your land title.</li>
                        <li><strong>Decent Workspaces:</strong> We will build modern, covered markets with electricity, water, and sanitation in every ward.</li>
                        <li><strong>Value Chain Integration:</strong> We will connect jua kali manufacturers directly to government procurement. Why import furniture when Gikomba can build it?</li>
                    </ul>
    
                    <p>We see your sweat. We respect your hustle. We will not give you handouts; we will give you the environment to thrive.</p>
    
                    <p>Let us build an economy that works for the many, not the few.</p>
                    
                    {signature_block}
                """,
                'color_class': 'text-purple-400',
                'icon': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 10.5V6.75a4.5 4.5 0 1 1 9 0v3.75M3.75 21.75h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H3.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" /></svg>'
            },
            {
                'slug': 'medicine',
                'title': 'Tribe Medicine',
                'intro': 'Open Letter to Our Healers and Frontline Warriors',
                'content': f"""
                    <p class="font-bold text-xl mb-6">Dear Doctors, Nurses, COs, Lab Techs, and Health Workers,</p>
                    
                    <p>You stand between our people and the grave. In the darkest moments of the pandemic, you were our shield. Every day, you perform miracles in facilities that lack basic supplies.</p>
    
                    <p>It is a national shame that a doctor in Kenya has to strike to be paid. It is a scandal that our hospitals lack drugs while corrupt officials loot billions. This betrayal of our healers is a betrayal of life itself.</p>
    
                    <h3 class="text-2xl font-black text-gray-900 mt-8 mb-4">The Roots Prescription:</h3>
    
                    <p>We propose a revolutionary approach to healthcare funded by our new industrial hemp economy.</p>
                    
                    <ul class="list-disc pl-6 space-y-2 mb-6">
                        <li><strong>Medicinal Sovereignty:</strong> We will invest heavily in local pharmaceutical manufacturing, including medicinal marijuana and anti-venom production. We stop importing what we can make.</li>
                        <li><strong>Standardized Healthcare:</strong> One quality of care for all. The President should be treated in the same hospitals as the mwananchi. If it's not good enough for him, it's not good enough for you.</li>
                        <li><strong>Better Pay & Protection:</strong> We will implement a comprehensive health workforce strategy that guarantees better pay, hazard allowances, and mental health support for you.</li>
                    </ul>
    
                    <p>A healthy nation is a wealthy nation. We cannot have health without honoring the healer.</p>
                    
                    {signature_block}
                """,
                'color_class': 'text-blue-400',
                'icon': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>'
            },
            {
                'slug': 'farmers',
                'title': 'Farmers Tribe',
                'intro': 'Open Letter to the Hands That Feed Us',
                'content': f"""
                    <p class="font-bold text-xl mb-6">Dear Farmers, Pastoralists, and Growers,</p>
                    
                    <p>You are the backbone of this country. You feed us. Yet, you are often the poorest among us. This paradox is the result of decades of cartel capture and policy neglect.</p>
    
                    <p>They tell you to plant maize when the profit is in avocados. They sell you fake fertilizer. They import eggs and milk from neighbors while yours rots. They have turned agriculture into a poverty trap.</p>
    
                    <h3 class="text-2xl font-black text-gray-900 mt-8 mb-4">The Green Gold Revolution:</h3>
    
                    <p>The Roots Party offers a bold new path. We stop doing the same thing expecting different results.</p>
                    
                    <ul class="list-disc pl-6 space-y-2 mb-6">
                        <li><strong>Industrial Hemp:</strong> We will legalize and regulate the cultivation of industrial hemp for export. This is a multi-billion dollar industry that can transform rural economies overnight.</li>
                        <li><strong>Snake Farming:</strong> We will tap into the lucrative anti-venom market. Niche, high-value farming is the future.</li>
                        <li><strong>Crush the Cartels:</strong> We will eliminate the middlemen who eat your sweat. Government will facilitate direct access to global markets.</li>
                        <li><strong>Value Addition:</strong> No more exporting raw materials. We process here. We package here. We brand here.</li>
                    </ul>
    
                    <p>Your land is your gold mine. We will help you mine it.</p>
                    
                    {signature_block}
                """,
                'color_class': 'text-green-400',
                'icon': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10"><path stroke-linecap="round" stroke-linejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" /></svg>'
            }
        ]

        count = 0
        for data in tribes_data:
            tribe, created = Tribe.objects.update_or_create(
                slug=data['slug'],
                defaults={
                    'title': data['title'],
                    'intro': data['intro'],
                    'content': data['content'],
                    'color_class': data['color_class'],
                    'icon': data['icon'],
                    'order': count
                }
            )
            count += 1
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created tribe: {tribe.title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated tribe: {tribe.title}'))
