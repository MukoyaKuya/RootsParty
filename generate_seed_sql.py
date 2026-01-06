
import random
from datetime import datetime

def generate_sql(count=75000):
    first_names = ['John', 'Jane', 'James', 'Mary', 'Peter', 'Grace', 'David', 'Faith', 'Joseph', 'Esther', 'Samuel', 'Mercy', 'Daniel', 'Joyce', 'Francis', 'Alice', 'George', 'Ann', 'Michael', 'Rose', 'Wanjiku', 'Otieno', 'Nanjala', 'Kipchoge', 'Kamau', 'Muthoni', 'Ochieng', 'Achieng', 'Wanyama', 'Nafula', 'Kimani', 'Nyambura', 'Odhiambo', 'Anyango', 'Kipkorir', 'Chebet', 'Maina', 'Njeri', 'Omondi', 'Akoth', 'Mutua', 'Mwende', 'Rotich', 'Chepkemoi', 'Njoroge', 'Wairimu', 'Okoth', 'Atieno', 'Kibet', 'Jepkorir']
    last_names = ['Kamau', 'Omondi', 'Kiptoo', 'Wanjiku', 'Juma', 'Odhiambo', 'Mutua', 'Wafula', 'Maina', 'Otieno', 'Kariuki', 'Njeri', 'Mwangi', 'Anyango', 'Njoroge', 'Wairimu', 'Kipkorir', 'Achieng', 'Kimani', 'Nyambura', 'Kibet', 'Chebet', 'Rotich', 'Chepkemoi', 'Koech', 'Jepchirchir', 'Kosgei', 'Jepkemboi', 'Cheruiyot', 'Cherono', 'Rono', 'Jepleting', 'Tanui', 'Jepkosgei', 'Lelei', 'Chepkoech', 'Mutai', 'Chepngeno', 'Lagat', 'Chelagat', 'Choge', 'Jepchumba', 'Sang', 'Chepchirchir', 'Kiprotich', 'Chepkirui', 'Korir', 'Chebet', 'Kirui', 'Chepkorir']

    start_id = 60000000 
    
    print("Generating SQL...")
    
    with open('seed_members.sql', 'w', encoding='utf-8') as f:
        # Removed BEGIN; for granular commits
        f.write("INSERT INTO users_member (full_name, id_number, phone_number, created_at) VALUES \n")
        
        batch = []
        for i in range(count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            full_name = f"{first} {last}".replace("'", "''")
            id_number = str(start_id + i)
            phone = f"07{random.randint(10000000, 99999999)}"
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # (full_name, id_number, phone, now)
            batch.append(f"('{full_name}', '{id_number}', '{phone}', '{now_str}')")
            
            if len(batch) >= 100:
                f.write(",\n".join(batch))
                if i < count - 1:
                    f.write(";\nINSERT INTO users_member (full_name, id_number, phone_number, created_at) VALUES \n")
                else:
                    f.write(";\n")
                batch = []
                
        if batch:
            f.write(",\n".join(batch))
            f.write(";\n")
            
        # Removed COMMIT; 
    print("Done! Check seed_members.sql")

if __name__ == "__main__":
    generate_sql()
