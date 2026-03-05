"""Seed the database with initial products and a sample store."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal, engine, Base
from backend.models.user import User, UserRole
from backend.models.store import Store
from backend.models.product import Product, StoreProduct
from backend.models.order import Order, OrderItem
from backend.utils.security import hash_password

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# --- Seed Products ---
products_data = [
    # (name, regional_name, description, category, region, image_url, gst_rate)
    ("Chorafali", "ચોરાફળી", "Crispy, spicy Diwali snack dusted with black salt masala", "Festive", "Gujarat", "https://upload.wikimedia.org/wikipedia/commons/c/c6/Khakhra_br%C3%B6d.png", 12.0), # Using khakhra as fallback
    ("Bhakarwadi", "भाकरवडी", "Sweet and spicy pinwheel snack from Pune", "Savory", "Maharashtra", "https://upload.wikimedia.org/wikipedia/commons/9/9a/Chakli_in_a_bowl.jpg", 12.0), # Fallback to chakli style
    ("Mathiya", "મઠીયા", "Traditional crispy Diwali flatbread with bubbly texture", "Festive", "Gujarat", "https://upload.wikimedia.org/wikipedia/commons/f/f2/Mathri.JPG", 12.0), # Fallback to Mathri
    ("Poha Chiwda", "पोहा चिवडा", "Light savory mixture of flattened rice, nuts, and spices", "Tea-Time", "Maharashtra", "https://upload.wikimedia.org/wikipedia/commons/c/c6/Bombaymix.jpg", 12.0), # Fallback
    ("Khakhra", "ખાખરા", "Thin roasted whole wheat cracker, perfect for travel", "Breakfast", "Gujarat", "https://upload.wikimedia.org/wikipedia/commons/c/c6/Khakhra_br%C3%B6d.png", 5.0),
    ("Chakli", "चकली", "Spiral crunchy deep-fried snack made from rice flour", "Festive", "Maharashtra", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Chakli_in_a_bowl.jpg/960px-Chakli_in_a_bowl.jpg", 12.0),
    ("Shankarpali", "शंकरपाळे", "Diamond-shaped lightly sweet crispy cookies", "Sweet", "Maharashtra", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Shankarpali_sweets_mithai_Western_India_2012.jpg/960px-Shankarpali_sweets_mithai_Western_India_2012.jpg", 5.0),
    ("Navratan Mix Namkeen", "नवरत्न मिक्स", "A signature premium blend of chickpeas, lentils, peanuts, and crispy noodles seasoned perfectly.", "Savory", "Maharashtra", "https://upload.wikimedia.org/wikipedia/commons/c/c6/Bombaymix.jpg", 12.0),
    ("Sev Namkeen", "શેવ / સેવ", "Classic crispy gram flour noodles, essential for any namkeen mix.", "Savory", "Maharashtra", "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Shop_selling_Bikaneri_bhujia_in_Jaipur.jpg/960px-Shop_selling_Bikaneri_bhujia_in_Jaipur.jpg", 12.0),
    ("Khasta Kachori", "खस्ता कचौरी", "Flaky, crispy deep-fried pastry filled with spicy moong dal mixture.", "Snack", "Gujarat", "https://upload.wikimedia.org/wikipedia/commons/8/8f/Rajasthani_Raj_Kachori.jpg", 12.0),
    ("Farali Chiwda", "फराળી चिवडा", "Sweet and spicy potato and peanut mix, ideal for fasting days.", "Tea-Time", "Maharashtra", "https://upload.wikimedia.org/wikipedia/commons/c/c6/Bombaymix.jpg", 12.0),
    ("Thekua", "ठेकुआ", "Crunchy deep-fried sweet biscuit made with wheat flour, jaggery, and coconut.", "Festive", "Bihar", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Thekua_-_Chhath_Festival_-_Kolkata_2013-11-09_4316.JPG/960px-Thekua_-_Chhath_Festival_-_Kolkata_2013-11-09_4316.JPG", 20.0),
    ("Pinni", "पिन्नी", "Nutrient-rich winter sweet made with wheat flour, desi ghee, jaggery, and nuts.", "Sweet", "Haryana", "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Pinni_cropped.JPG/960px-Pinni_cropped.JPG", 30.0),
    ("Tilkut", "तिलकुट", "A traditional Gaya winter sweet made with pounded sesame seeds and jaggery.", "Sweet", "Bihar", "https://upload.wikimedia.org/wikipedia/commons/a/aa/Tilkut_Sweet.jpg", 5.0),
    ("Anarsa", "अनरसा", "A sweet pastry-like snack made from rice flour, jaggery, and coated with poppy seeds.", "Festive", "Bihar", "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Anarsa.jpg/960px-Anarsa.jpg", 10.0),
]

# Clear existing data to ensure only shippable ones remain and images are updated
# Delete Order history first due to FKs
db.query(OrderItem).delete()
db.query(Order).delete()
db.query(StoreProduct).delete()
db.query(Product).delete()
db.commit()

created_products = []
for name, rname, desc, cat, reg, img, gst in products_data:
    p = Product(name=name, regional_name=rname, description=desc, category=cat, region=reg, image_url=img, gst_rate=gst)
    db.add(p)
    db.flush()
    created_products.append(p)
    print(f"  Added product: {name} (GST: {gst}%)")


# --- Seed a store owner ---
owner = db.query(User).filter(User.email == "chitale@example.com").first()
if not owner:
    owner = User(
        email="chitale@example.com",
        name="Chitale Bandhu",
        password_hash=hash_password("store123"),
        phone="+91-9876543210",
        country="India",
        role=UserRole.store_owner,
    )
    db.add(owner)
    db.flush()
    print("  Created store owner: Chitale Bandhu")

# --- Seed a sample store ---
store = db.query(Store).filter(Store.name == "Chitale Bandhu Mithaiwale").first()
if not store:
    store = Store(
        owner_id=owner.id,
        name="Chitale Bandhu Mithaiwale",
        city="Pune",
        region="Maharashtra",
        address="1234 Deccan Gymkhana, Pune 411004",
        story="Established in 1950, Chitale Bandhu is one of India's most iconic sweet and snack shops. Known worldwide for their signature Bhakarwadi, they ship to over 50 countries.",
        phone="+91-20-25671234",
        rating=4.8,
        image_url="/images/chitale_logo.png",
        is_verified=True,
        established_year=1950,
    )
    db.add(store)
    db.flush()
    print("  Created store: Chitale Bandhu Mithaiwale")

# --- Seed a second store ---
owner2 = db.query(User).filter(User.email == "induben@example.com").first()
if not owner2:
    owner2 = User(
        email="induben@example.com",
        name="Induben Khakhrawala",
        password_hash=hash_password("store123"),
        phone="+91-9988776655",
        country="India",
        role=UserRole.store_owner,
    )
    db.add(owner2)
    db.flush()

store2 = db.query(Store).filter(Store.name == "Induben Khakhrawala").first()
if not store2:
    store2 = Store(
        owner_id=owner2.id,
        name="Induben Khakhrawala",
        city="Ahmedabad",
        region="Gujarat",
        address="Law Garden, Ahmedabad 380006",
        story="A legendary Ahmedabad institution since 1975. Induben pioneered the commercial Khakhra revolution, offering over 50 flavors from their original rooftop kitchen.",
        phone="+91-79-26300123",
        rating=4.6,
        image_url="/images/induben_logo.png",
        is_verified=True,
        established_year=1975,
    )
    db.add(store2)
    db.flush()
    print("  Created store: Induben Khakhrawala")

# --- Seed New Stores ---

# 1. Das Khaman House (Gujarat)
owner3 = db.query(User).filter(User.email == "das@example.com").first()
if not owner3:
    owner3 = User(
        email="das@example.com", name="Das Khaman House",
        password_hash=hash_password("store123"), phone="+91-79-11223344", country="India", role=UserRole.store_owner
    )
    db.add(owner3)
    db.flush()

store3 = db.query(Store).filter(Store.name == "Das Khaman House").first()
if not store3:
    store3 = Store(
        owner_id=owner3.id, name="Das Khaman House", city="Ahmedabad", region="Gujarat",
        address="Navrangpura, Ahmedabad", story="Famous for their authentic Gujarati snacks, especially the soft and spongy khaman and crispy chorafali.",
        phone="+91-79-11223344", rating=4.7, image_url="/images/das_khaman_logo.png", is_verified=True, established_year=1922
    )
    db.add(store3)
    db.flush()
    print("  Created store: Das Khaman House")

# 2. Sukhadia Garbaddas Bapuji (Gujarat)
owner4 = db.query(User).filter(User.email == "sukhadia@example.com").first()
if not owner4:
    owner4 = User(email="sukhadia@example.com", name="Sukhadia Garbaddas Bapuji", password_hash=hash_password("store123"), role=UserRole.store_owner)
    db.add(owner4)
    db.flush()

store4 = db.query(Store).filter(Store.name == "Sukhadia Garbaddas Bapuji").first()
if not store4:
    store4 = Store(
        owner_id=owner4.id, name="Sukhadia Garbaddas Bapuji", city="Nadiad", region="Gujarat",
        address="Station Road, Nadiad", story="A heritage brand since 1888, offering premium traditional sweets and savory Gujarati namkeens.",
        rating=4.9, image_url="/images/sukhadia_logo.png", is_verified=True, established_year=1888
    )
    db.add(store4)
    db.flush()
    print("  Created store: Sukhadia Garbaddas Bapuji")

# 3. Prakash Shakahari Upahar Kendra (Maharashtra)
owner5 = db.query(User).filter(User.email == "prakash@example.com").first()
if not owner5:
    owner5 = User(email="prakash@example.com", name="Prakash Upahar Kendra", password_hash=hash_password("store123"), role=UserRole.store_owner)
    db.add(owner5)
    db.flush()

store5 = db.query(Store).filter(Store.name == "Prakash Shakahari Upahar Kendra").first()
if not store5:
    store5 = Store(
        owner_id=owner5.id, name="Prakash Shakahari Upahar Kendra", city="Mumbai", region="Maharashtra",
        address="Dadar, Mumbai", story="A beloved institution in Dadar, known for its authentic and delicious Maharashtrian vegetarian fare.",
        rating=4.7, image_url="/images/prakash_logo.png", is_verified=True, established_year=1946
    )
    db.add(store5)
    db.flush()
    print("  Created store: Prakash Shakahari Upahar Kendra")

# 4. Laxmi Narayan Chiwda (Maharashtra)
owner6 = db.query(User).filter(User.email == "laxminarayan@example.com").first()
if not owner6:
    owner6 = User(email="laxminarayan@example.com", name="Laxmi Narayan Chiwda", password_hash=hash_password("store123"), role=UserRole.store_owner)
    db.add(owner6)
    db.flush()

store6 = db.query(Store).filter(Store.name == "Laxmi Narayan Best Chiwda").first()
if not store6:
    store6 = Store(
        owner_id=owner6.id, name="Laxmi Narayan Best Chiwda", city="Pune", region="Maharashtra",
        address="Bhavani Peth, Pune", story="Pioneers of the famous Pune Chiwda, serving crispy, premium quality mixtures for decades.",
        rating=4.8, image_url="/images/laxmi_narayan_logo.png", is_verified=True, established_year=1945
    )
    db.add(store6)
    db.flush()
    print("  Created store: Laxmi Narayan Best Chiwda")

# 5. Jairamdas Bhojraj (Kalyan)
owner7 = db.query(User).filter(User.email == "jairamdas@example.com").first()
if not owner7:
    owner7 = User(email="jairamdas@example.com", name="Jairamdas Bhojraj", password_hash=hash_password("store123"), role=UserRole.store_owner)
    db.add(owner7)
    db.flush()

store7 = db.query(Store).filter(Store.name == "Jairamdas Bhojraj").first()
if not store7:
    store7 = Store(
        owner_id=owner7.id, name="Jairamdas Bhojraj", city="Kalyan", region="Maharashtra",
        address="Shivaji Chowk, Kalyan", story="A brand deeply trusted in Kalyan for its massive variety of high-quality Sev, Mixtures, and customized Namkeens.",
        rating=4.7, image_url="/images/jairamdas_logo.png", is_verified=True, established_year=1960
    )
    db.add(store7)
    db.flush()
    print("  Created store: Jairamdas Bhojraj")

# 6. Purushottam Kandoi (Ghatkopar)
owner8 = db.query(User).filter(User.email == "purushottam@example.com").first()
if not owner8:
    owner8 = User(email="purushottam@example.com", name="Purushottam Kandoi", password_hash=hash_password("store123"), role=UserRole.store_owner)
    db.add(owner8)
    db.flush()

store8 = db.query(Store).filter(Store.name == "Purushottam Kandoi Haribhai Damodar Mithaiwala").first()
if not store8:
    store8 = Store(
        owner_id=owner8.id, name="Purushottam Kandoi Haribhai Damodar Mithaiwala", city="Mumbai", region="Maharashtra",
        address="Ghatkopar East, Mumbai", story="An iconic Ghatkopar destination offering an extremely wide array of authentic farsaans, dhoklas, and heritage sweets.",
        rating=4.8, image_url="/images/purushottam_logo.png", is_verified=True, established_year=1952
    )
    db.add(store8)
    db.flush()
    print("  Created store: Purushottam Kandoi Haribhai Damodar Mithaiwala")

# 7. Harilal's (Bihar)
owner9 = db.query(User).filter(User.email == "harilals@example.com").first()
if not owner9:
    owner9 = User(email="harilals@example.com", name="Harilal's", password_hash=hash_password("store123"), role=UserRole.store_owner)
    db.add(owner9)
    db.flush()

store9 = db.query(Store).filter(Store.name == "Harilal's").first()
if not store9:
    store9 = Store(
        owner_id=owner9.id, name="Harilal's", city="Patna", region="Bihar",
        address="Kankarbagh, Patna", story="A trusted name in Patna for authentic traditional Bihari sweets and snacks like Khaja and Litti Chokha.",
        rating=4.6, image_url="/images/harilals_logo.png", is_verified=True, established_year=1978
    )
    db.add(store9)
    db.flush()
    print("  Created store: Harilal's")

# 8. Nobin Chandra Das (West Bengal)
owner10 = db.query(User).filter(User.email == "nobindas@example.com").first()
if not owner10:
    owner10 = User(email="nobindas@example.com", name="Nobin Chandra Das", password_hash=hash_password("store123"), role=UserRole.store_owner)
    db.add(owner10)
    db.flush()

store10 = db.query(Store).filter(Store.name == "Nobin Chandra Das & Sons").first()
if not store10:
    store10 = Store(
        owner_id=owner10.id, name="Nobin Chandra Das & Sons", city="Kolkata", region="West Bengal",
        address="Shobhabazar, Kolkata", story="The legendary creators of the Bengali Rosogolla, maintaining a sweet legacy since 1866.",
        rating=4.9, image_url="/images/nobin_das_logo.png", is_verified=True, established_year=1866
    )
    db.add(store10)
    db.flush()
    print("  Created store: Nobin Chandra Das & Sons")

# 9. Matu Ram's (Haryana)
owner11 = db.query(User).filter(User.email == "maturam@example.com").first()
if not owner11:
    owner11 = User(email="maturam@example.com", name="Matu Ram Halwai", password_hash=hash_password("store123"), role=UserRole.store_owner)
    db.add(owner11)
    db.flush()

store11 = db.query(Store).filter(Store.name == "Matu Ram Halwai").first()
if not store11:
    store11 = Store(
        owner_id=owner11.id, name="Matu Ram Halwai", city="Gohana", region="Haryana",
        address="Old Bus Stand, Gohana", story="Famous across India for their massive, 250-gram Gohana Jalebis cooked in pure desi ghee.",
        rating=4.7, image_url="/images/matu_ram_logo.png", is_verified=True, established_year=1958
    )
    db.add(store11)
    db.flush()
    print("  Created store: Matu Ram Halwai")

# 10. Laxmi Misthan Bhandar (Rajasthan)
owner12 = db.query(User).filter(User.email == "lmb@example.com").first()
if not owner12:
    owner12 = User(email="lmb@example.com", name="Laxmi Misthan Bhandar", password_hash=hash_password("store123"), role=UserRole.store_owner)
    db.add(owner12)
    db.flush()

store12 = db.query(Store).filter(Store.name == "Laxmi Misthan Bhandar").first()
if not store12:
    store12 = Store(
        owner_id=owner12.id, name="Laxmi Misthan Bhandar", city="Jaipur", region="Rajasthan",
        address="Johari Bazar, Jaipur", story="An iconic landmark in the Pink City known for its royal Ghevar and rich traditional Rajputana sweets.",
        rating=4.8, image_url="/images/laxmi_misthan_logo.png", is_verified=True, established_year=1727
    )
    db.add(store12)
    db.flush()
    print("  Created store: Laxmi Misthan Bhandar")

# 11. Pramod Laddu Bhandar (Gaya)
owner13 = db.query(User).filter(User.email == "pramod@example.com").first()
if not owner13:
    owner13 = User(email="pramod@example.com", name="Pramod Laddu Bhandar", password_hash=hash_password("store123"), role=UserRole.store_owner)
    db.add(owner13)
    db.flush()

store13 = db.query(Store).filter(Store.name == "Pramod Laddu Bhandar").first()
if not store13:
    store13 = Store(
        owner_id=owner13.id, name="Pramod Laddu Bhandar", city="Gaya", region="Bihar",
        address="Tekari Road, Gaya", story="A heritage shop in Gaya, world-famous for their winter specialty, the authentic crispy Tilkut and soft Anarsa.",
        rating=4.9, image_url="/images/mathiya.png", is_verified=True, established_year=1945
    )
    db.add(store13)
    db.flush()
    print("  Created store: Pramod Laddu Bhandar")

# --- Link products to stores with prices ---
# Chitale sells all Marathi + some Gujarati
store1_prices = {
    "Bhakarwadi": 280, "Poha Chiwda": 190, "Chakli": 220,
    "Shankarpali": 250, "Chorafali": 300, "Mathiya": 260,
}

for prod in created_products:
    if prod.name in store1_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            sp = StoreProduct(store_id=store.id, product_id=prod.id, price=store1_prices[prod.name], weight_grams=250)
            db.add(sp)

# Induben sells Gujarati items
store2_prices = {
    "Khakhra": 150, "Chorafali": 260, "Mathiya": 240,
    "Bhakarwadi": 300,
}

for prod in created_products:
    if prod.name in store2_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store2.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            sp = StoreProduct(store_id=store2.id, product_id=prod.id, price=store2_prices[prod.name], weight_grams=250)
            db.add(sp)

# Das Khaman (Gujarat)
store3_prices = {"Chorafali": 280, "Khakhra": 180}
for prod in created_products:
    if prod.name in store3_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store3.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            db.add(StoreProduct(store_id=store3.id, product_id=prod.id, price=store3_prices[prod.name], weight_grams=250))

# Sukhadia (Gujarat)
store4_prices = {"Mathiya": 300, "Chorafali": 320, "Khakhra": 200}
for prod in created_products:
    if prod.name in store4_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store4.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            db.add(StoreProduct(store_id=store4.id, product_id=prod.id, price=store4_prices[prod.name], weight_grams=250))

# Prakash (Maharashtra)
store5_prices = {"Poha Chiwda": 210, "Bhakarwadi": 260, "Shankarpali": 240, "Farali Chiwda": 220}
for prod in created_products:
    if prod.name in store5_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store5.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            db.add(StoreProduct(store_id=store5.id, product_id=prod.id, price=store5_prices[prod.name], weight_grams=250))

# Laxmi Narayan (Maharashtra)
store6_prices = {"Poha Chiwda": 250, "Bhakarwadi": 290, "Chakli": 240, "Farali Chiwda": 260}
for prod in created_products:
    if prod.name in store6_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store6.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            db.add(StoreProduct(store_id=store6.id, product_id=prod.id, price=store6_prices[prod.name], weight_grams=250))

# Jairamdas Bhojraj (Kalyan)
store7_prices = {"Navratan Mix Namkeen": 240, "Sev Namkeen": 180, "Poha Chiwda": 200, "Mathiya": 250}
for prod in created_products:
    if prod.name in store7_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store7.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            db.add(StoreProduct(store_id=store7.id, product_id=prod.id, price=store7_prices[prod.name], weight_grams=250))

# Purushottam Kandoi (Ghatkopar)
store8_prices = {"Khasta Kachori": 280, "Farali Chiwda": 250, "Chorafali": 290}
for prod in created_products:
    if prod.name in store8_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store8.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            db.add(StoreProduct(store_id=store8.id, product_id=prod.id, price=store8_prices[prod.name], weight_grams=250))

# Harilal's (Bihar)
store9_prices = {"Thekua": 250, "Sev Namkeen": 180}
for prod in created_products:
    if prod.name in store9_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store9.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            db.add(StoreProduct(store_id=store9.id, product_id=prod.id, price=store9_prices[prod.name], weight_grams=250))

# Nobin Chandra Das (West Bengal)
store10_prices = {"Mathiya": 200, "Sev Namkeen": 150} # Replaced perishable sweets with dry snacks
for prod in created_products:
    if prod.name in store10_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store10.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            db.add(StoreProduct(store_id=store10.id, product_id=prod.id, price=store10_prices[prod.name], weight_grams=250))

# Matu Ram Halwai (Haryana)
store11_prices = {"Pinni": 450, "Sev Namkeen": 200}
for prod in created_products:
    if prod.name in store11_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store11.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            db.add(StoreProduct(store_id=store11.id, product_id=prod.id, price=store11_prices[prod.name], weight_grams=250))

# Laxmi Misthan Bhandar (Rajasthan)
store12_prices = {"Khasta Kachori": 250, "Navratan Mix Namkeen": 280, "Mathiya": 200}
for prod in created_products:
    if prod.name in store12_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store12.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            db.add(StoreProduct(store_id=store12.id, product_id=prod.id, price=store12_prices[prod.name], weight_grams=250))

# Pramod Laddu Bhandar (Gaya)
store13_prices = {"Tilkut": 350, "Anarsa": 280, "Sev Namkeen": 180}
for prod in created_products:
    if prod.name in store13_prices:
        existing = db.query(StoreProduct).filter(StoreProduct.store_id == store13.id, StoreProduct.product_id == prod.id).first()
        if not existing:
            db.add(StoreProduct(store_id=store13.id, product_id=prod.id, price=store13_prices[prod.name], weight_grams=250))

db.commit()
print("\nDatabase seeded successfully!")
db.close()
