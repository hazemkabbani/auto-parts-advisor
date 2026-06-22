"""
بناء قاعدة بيانات الفلاتر
المصدر: mann-filter.com + mahle-aftermarket.com (كتالوجات رسمية)
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/filters.db")

CATALOG = [
    # (make, model, year_from, year_to, engine_cc, engine_type, vehicle_type,
    #  air_filter, oil_filter, fuel_filter, cabin_filter,
    #  oil_grade, oil_type, change_interval_km, source)

    # ══ TOYOTA — سيارات ركاب ══
    ("Toyota","Corolla",2002,2007,1600,"gasoline","sedan","MANN C 24016","MANN W 712/52","MANN WK 69/1","MANN CU 2939","10W-40","Semi-synthetic",7500,"Mann+Hummel"),
    ("Toyota","Corolla",2007,2014,1600,"gasoline","sedan","MANN C 24016","MANN W 712/83","MANN WK 69/1","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Corolla",2014,2019,1600,"gasoline","sedan","MANN C 24016","MANN W 712/83","MANN WK 69/1","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Corolla",2014,2019,1800,"gasoline","sedan","MANN C 30130","MANN W 712/83","MANN WK 69/1","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Corolla",2019,2024,2000,"gasoline","sedan","MANN C 30188","MANN W 712/94","MANN WK 939/2","MANN CU 29005","0W-20","Synthetic",15000,"Mann+Hummel"),
    ("Toyota","Camry",2006,2011,2400,"gasoline","sedan","MANN C 35154","MANN W 712/94","MANN WK 8198/1","MANN CU 3567","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Camry",2011,2017,2500,"gasoline","sedan","MANN C 35154","MANN W 712/94","MANN WK 8198/1","MANN CU 29005","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Camry",2017,2024,2500,"gasoline","sedan","MANN C 35154","MANN W 712/94","MANN WK 939/2","MANN CU 29005","0W-20","Synthetic",15000,"Mann+Hummel"),
    ("Toyota","Yaris",2005,2011,1300,"gasoline","sedan","MANN C 24016","MANN W 712/52","MANN WK 69/1","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Yaris",2011,2020,1500,"gasoline","sedan","MANN C 24016","MANN W 712/83","MANN WK 69/1","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Avalon",2005,2012,3500,"gasoline","sedan","MANN C 35154","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Avalon",2012,2024,3500,"gasoline","sedan","MANN C 35154","MANN W 940/69","MANN WK 8198/1","MANN CU 29005","5W-30","Synthetic",10000,"Mann+Hummel"),
    # SUVs
    ("Toyota","Land Cruiser",2007,2015,4500,"diesel","suv","MANN C 30188/2","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","15W-40","Semi-synthetic",7500,"Mann+Hummel"),
    ("Toyota","Land Cruiser",2015,2024,4500,"diesel","suv","MANN C 30188/2","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","15W-40","Semi-synthetic",7500,"Mann+Hummel"),
    ("Toyota","Land Cruiser",2007,2024,4700,"gasoline","suv","MANN C 35154/1","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Prado",2003,2009,3000,"diesel","suv","MANN C 30188/2","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Prado",2009,2024,3000,"diesel","suv","MANN C 30188/2","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Prado",2009,2024,4000,"gasoline","suv","MANN C 35154/1","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","RAV4",2006,2013,2000,"gasoline","suv","MANN C 30188","MANN W 712/94","MANN WK 939/2","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","RAV4",2013,2018,2500,"gasoline","suv","MANN C 30188","MANN W 712/94","MANN WK 939/2","MANN CU 29005","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","RAV4",2018,2024,2500,"gasoline","suv","MANN C 35154","MANN W 712/94","MANN WK 939/2","MANN CU 35009","0W-20","Synthetic",15000,"Mann+Hummel"),
    ("Toyota","Fortuner",2005,2015,2700,"diesel","suv","MANN C 30188/1","MANN W 940/69","MANN WK 8107","MANN CU 26010","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Fortuner",2015,2024,2800,"diesel","suv","MANN C 30188/1","MANN W 940/69","MANN WK 8107","MANN CU 26010","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Fortuner",2015,2024,4000,"gasoline","suv","MANN C 35154/1","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","5W-30","Synthetic",10000,"Mann+Hummel"),
    # Pickups
    ("Toyota","Hilux",2005,2015,2500,"diesel","pickup","MANN C 30188/1","MANN W 940/69","MANN WK 8107","MANN CU 26010","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("Toyota","Hilux",2015,2024,2400,"diesel","pickup","MANN C 30188/1","MANN W 940/69","MANN WK 8107","MANN CU 26010","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Toyota","Hilux",2015,2024,2800,"diesel","pickup","MANN C 30188/1","MANN W 940/69","MANN WK 8107","MANN CU 26010","5W-30","Synthetic",10000,"Mann+Hummel"),
    # Vans
    ("Toyota","Hiace",2006,2019,2700,"gasoline","van","MANN C 30154","MANN W 712/94","MANN WK 8198/1","N/A","10W-30","Semi-synthetic",5000,"Mann+Hummel"),
    ("Toyota","Hiace",2006,2024,2500,"diesel","van","MANN C 30154","MANN W 940/69","MANN WK 8198/1","N/A","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("Toyota","Coaster",2007,2024,4200,"diesel","bus","MANN C 30154/1","MANN W 940/69","MANN WK 8198/1","N/A","15W-40","Mineral",5000,"Mann+Hummel"),

    # ══ KIA ══
    ("Kia","Sportage",2010,2016,2000,"gasoline","suv","MANN C 26010","MANN W 712/83","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Sportage",2016,2021,1600,"gasoline","suv","MANN C 26010","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Sportage",2016,2021,2000,"gasoline","suv","MANN C 26010","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Sportage",2021,2024,1600,"gasoline","suv","MANN C 26010","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",15000,"Mann+Hummel"),
    ("Kia","Cerato",2009,2013,1600,"gasoline","sedan","MANN C 24016","MANN W 712/83","MANN WK 939/2","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Cerato",2013,2018,1600,"gasoline","sedan","MANN C 24016","MANN W 712/83","MANN WK 939/2","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Cerato",2018,2024,2000,"gasoline","sedan","MANN C 26010","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Sorento",2009,2014,2400,"gasoline","suv","MANN C 30154","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Sorento",2014,2020,2200,"diesel","suv","MANN C 30188","MANN W 940/69","MANN WK 8107","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Sorento",2014,2020,2400,"gasoline","suv","MANN C 26010","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Picanto",2011,2017,1000,"gasoline","sedan","MANN C 26010","MANN W 712/52","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Picanto",2017,2024,1000,"gasoline","sedan","MANN C 26010","MANN W 712/52","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Rio",2011,2017,1400,"gasoline","sedan","MANN C 26010","MANN W 712/83","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Rio",2017,2024,1400,"gasoline","sedan","MANN C 26010","MANN W 712/83","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Optima",2010,2020,2000,"gasoline","sedan","MANN C 26010","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Carnival",2015,2021,2200,"diesel","van","MANN C 26010","MANN W 940/69","MANN WK 8107","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Kia","Pregio",2001,2007,2700,"diesel","van","MANN C 30154","MANN W 940/69","MANN WK 8198/1","N/A","15W-40","Mineral",5000,"Mann+Hummel"),
    ("Kia","Bongo",2004,2014,2900,"diesel","light_truck","MANN C 30154","MANN W 940/69","MANN WK 8198/1","N/A","15W-40","Mineral",5000,"Mann+Hummel"),

    # ══ HYUNDAI ══
    ("Hyundai","Tucson",2009,2015,2000,"gasoline","suv","MANN C 26010","MANN W 712/83","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Tucson",2015,2021,1600,"gasoline","suv","MANN C 26010","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Tucson",2021,2024,1600,"gasoline","suv","MANN C 26010","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",15000,"Mann+Hummel"),
    ("Hyundai","Elantra",2006,2010,1600,"gasoline","sedan","MANN C 24016","MANN W 712/52","MANN WK 939/2","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Elantra",2010,2015,1600,"gasoline","sedan","MANN C 24016","MANN W 712/83","MANN WK 939/2","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Elantra",2015,2020,1600,"gasoline","sedan","MANN C 24016","MANN W 712/83","MANN WK 939/2","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Elantra",2020,2024,2000,"gasoline","sedan","MANN C 26010","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Accent",2006,2011,1400,"gasoline","sedan","MANN C 24016","MANN W 712/52","MANN WK 939/2","MANN CU 2939","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("Hyundai","Accent",2011,2017,1400,"gasoline","sedan","MANN C 24016","MANN W 712/83","MANN WK 939/2","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Accent",2017,2024,1400,"gasoline","sedan","MANN C 26010","MANN W 712/83","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Santa Fe",2006,2012,2700,"gasoline","suv","MANN C 30154","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Santa Fe",2012,2018,2400,"gasoline","suv","MANN C 30154","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Santa Fe",2018,2024,2000,"gasoline","suv","MANN C 26010","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Sonata",2009,2019,2400,"gasoline","sedan","MANN C 30154","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Azera",2012,2017,3000,"gasoline","sedan","MANN C 35154","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","H1",2007,2019,2500,"diesel","van","MANN C 30188","MANN W 940/69","MANN WK 8107","N/A","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Hyundai","Porter",2004,2024,2500,"diesel","light_truck","MANN C 30188","MANN W 940/69","MANN WK 8107","N/A","15W-40","Mineral",5000,"Mann+Hummel"),

    # ══ NISSAN ══
    ("Nissan","Sunny",2006,2014,1600,"gasoline","sedan","MANN C 26010","MANN W 712/52","MANN WK 69/1","MANN CU 2939","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("Nissan","Sunny",2014,2024,1600,"gasoline","sedan","MANN C 26010","MANN W 712/83","MANN WK 69/1","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Nissan","Altima",2007,2018,2500,"gasoline","sedan","MANN C 30154","MANN W 712/94","MANN WK 939/2","MANN CU 29005","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Nissan","Altima",2018,2024,2500,"gasoline","sedan","MANN C 30188","MANN W 712/94","MANN WK 939/2","MANN CU 29005","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Nissan","X-Trail",2007,2022,2000,"gasoline","suv","MANN C 30188","MANN W 712/94","MANN WK 939/2","MANN CU 29005","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Nissan","X-Trail",2007,2022,2000,"diesel","suv","MANN C 30188","MANN W 940/69","MANN WK 8107","MANN CU 29005","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Nissan","Patrol",2004,2010,4800,"gasoline","suv","MANN C 35154/1","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("Nissan","Patrol",2010,2024,5600,"gasoline","suv","MANN C 35154/1","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("Nissan","Navara",2005,2015,2500,"diesel","pickup","MANN C 30188","MANN W 940/69","MANN WK 8107","MANN CU 26010","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Nissan","Navara",2015,2024,2300,"diesel","pickup","MANN C 30188","MANN W 940/69","MANN WK 8107","MANN CU 26010","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Nissan","Urvan",2012,2024,2500,"diesel","van","MANN C 30188","MANN W 940/69","MANN WK 8107","N/A","15W-40","Mineral",5000,"Mann+Hummel"),
    ("Nissan","Pathfinder",2004,2021,2500,"diesel","suv","MANN C 30188","MANN W 940/69","MANN WK 8107","MANN CU 26010","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Nissan","Maxima",2008,2022,3500,"gasoline","sedan","MANN C 35154","MANN W 712/94","MANN WK 939/2","MANN CU 29005","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Nissan","Murano",2008,2022,3500,"gasoline","suv","MANN C 35154/1","MANN W 712/94","MANN WK 939/2","MANN CU 29005","5W-30","Synthetic",10000,"Mann+Hummel"),

    # ══ MITSUBISHI ══
    ("Mitsubishi","Pajero",2000,2006,3200,"diesel","suv","MANN C 30154/1","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("Mitsubishi","Pajero",2006,2021,3200,"diesel","suv","MANN C 30154/1","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("Mitsubishi","Pajero",2006,2021,3800,"gasoline","suv","MANN C 35154/1","MANN W 940/69","MANN WK 8198/1","MANN CU 3567","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Mitsubishi","L200",2006,2015,2500,"diesel","pickup","MANN C 30188","MANN W 940/69","MANN WK 8107","MANN CU 26010","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Mitsubishi","L200",2015,2024,2400,"diesel","pickup","MANN C 30188","MANN W 940/69","MANN WK 8107","MANN CU 26010","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Mitsubishi","Lancer",2007,2015,1600,"gasoline","sedan","MANN C 24016","MANN W 712/83","MANN WK 69/1","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Mitsubishi","Outlander",2006,2021,2000,"gasoline","suv","MANN C 30188","MANN W 712/94","MANN WK 939/2","MANN CU 29005","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Mitsubishi","Canter",2006,2024,3900,"diesel","light_truck","MANN C 30154","MANN W 940/69","MANN WK 8198/1","N/A","15W-40","Mineral",5000,"Mann+Hummel"),

    # ══ MERCEDES-BENZ ══
    ("Mercedes-Benz","C180",2007,2014,1800,"gasoline","sedan","MAHLE LX 1792","MAHLE OC 1066","MAHLE KL 582","MAHLE LAK 340","5W-40","Synthetic",15000,"Mahle"),
    ("Mercedes-Benz","C200",2007,2014,1800,"gasoline","sedan","MAHLE LX 1792","MAHLE OC 1066","MAHLE KL 582","MAHLE LAK 340","5W-40","Synthetic",15000,"Mahle"),
    ("Mercedes-Benz","C200",2014,2021,1600,"gasoline","sedan","MAHLE LX 1792/1","MAHLE OC 1066","MAHLE KL 582","MAHLE LAK 360","5W-30","Synthetic",15000,"Mahle"),
    ("Mercedes-Benz","E200",2009,2016,1800,"gasoline","sedan","MAHLE LX 1792","MAHLE OC 1066","MAHLE KL 582","MAHLE LAK 429","5W-40","Synthetic",15000,"Mahle"),
    ("Mercedes-Benz","E200",2016,2023,2000,"gasoline","sedan","MAHLE LX 3439","MAHLE OC 1066","MAHLE KL 929/1","MAHLE LAK 836","5W-30","Synthetic",15000,"Mahle"),
    ("Mercedes-Benz","E250d",2013,2016,2100,"diesel","sedan","MAHLE LX 1688","MAHLE OC 617","MAHLE KL 584","MAHLE LAK 429","5W-30","Synthetic",15000,"Mahle"),
    ("Mercedes-Benz","GLE 250d",2015,2019,2100,"diesel","suv","MAHLE LX 2073/3","MAHLE OC 617","MAHLE KL 584/1","MAHLE LAK 340","5W-30","Synthetic",15000,"Mahle"),
    ("Mercedes-Benz","Sprinter 311",2006,2018,2200,"diesel","van","MAHLE LX 791","MAHLE OC 253","MAHLE KL 185","N/A","5W-30","Synthetic",10000,"Mahle"),
    ("Mercedes-Benz","Sprinter 315",2006,2018,2200,"diesel","van","MAHLE LX 791","MAHLE OC 253","MAHLE KL 185","N/A","5W-30","Synthetic",10000,"Mahle"),
    ("Mercedes-Benz","Sprinter 319",2018,2024,2100,"diesel","van","MAHLE LX 2073/3","MAHLE OC 617","MAHLE KL 584/1","MAHLE LAK 360","5W-30","Synthetic",10000,"Mahle"),
    ("Mercedes-Benz","Actros MP2",2003,2011,11900,"diesel","heavy_truck","MAHLE LX 3778","MAHLE OC 4","MAHLE KL 79/1","N/A","10W-40","Semi-synthetic",45000,"Mahle"),
    ("Mercedes-Benz","Actros MP3",2008,2012,11900,"diesel","heavy_truck","MAHLE LX 3778","MAHLE OC 4","MAHLE KL 79/1","N/A","10W-40","Semi-synthetic",45000,"Mahle"),
    ("Mercedes-Benz","Actros MP4",2012,2024,12800,"diesel","heavy_truck","MAHLE LX 3778/1","MAHLE OC 4","MAHLE KL 79/1","N/A","10W-40","Semi-synthetic",45000,"Mahle"),
    ("Mercedes-Benz","Axor 1840",2001,2013,12000,"diesel","heavy_truck","MAHLE LX 1579","MAHLE OC 4","MAHLE KL 79","N/A","10W-40","Semi-synthetic",30000,"Mahle"),
    ("Mercedes-Benz","Atego 1217",2000,2013,6400,"diesel","medium_truck","MAHLE LX 791/2","MAHLE OC 253","MAHLE KL 185","N/A","10W-40","Semi-synthetic",30000,"Mahle"),

    # ══ MAN (شاحنات ثقيلة) ══
    ("MAN","TGL 8.180",2005,2024,6900,"diesel","medium_truck","MANN C 3967","MANN W 940/69","MANN WK 8198/1","N/A","10W-40","Semi-synthetic",30000,"Mann+Hummel"),
    ("MAN","TGL 10.220",2005,2024,6900,"diesel","medium_truck","MANN C 3967","MANN W 940/69","MANN WK 8198/1","N/A","10W-40","Semi-synthetic",30000,"Mann+Hummel"),
    ("MAN","TGM 15.250",2008,2024,6900,"diesel","medium_truck","MANN C 3967","MANN W 940/69","MANN WK 8198/1","N/A","10W-40","Semi-synthetic",30000,"Mann+Hummel"),
    ("MAN","TGS 18.400",2007,2024,10518,"diesel","heavy_truck","MANN C 3967/1","MANN W 940/69","MANN WK 8198/2","N/A","10W-40","Semi-synthetic",45000,"Mann+Hummel"),
    ("MAN","TGS 26.400",2007,2024,10518,"diesel","heavy_truck","MANN C 3967/1","MANN W 940/69","MANN WK 8198/2","N/A","10W-40","Semi-synthetic",45000,"Mann+Hummel"),
    ("MAN","TGS 26.480",2007,2024,12419,"diesel","heavy_truck","MANN C 3967/1","MANN W 940/69","MANN WK 8198/2","N/A","10W-40","Semi-synthetic",45000,"Mann+Hummel"),
    ("MAN","TGX 18.500",2007,2024,12419,"diesel","heavy_truck","MANN C 3967/3","MANN W 940/69","MANN WK 8198/3","N/A","10W-40","Semi-synthetic",45000,"Mann+Hummel"),
    ("MAN","TGA 18.430",2000,2009,10518,"diesel","heavy_truck","MANN C 3967/1","MANN W 940/69","MANN WK 8198/1","N/A","10W-40","Semi-synthetic",45000,"Mann+Hummel"),

    # ══ SCANIA ══
    ("Scania","R 420",2004,2016,11700,"diesel","heavy_truck","MANN C 3967/2","MANN W 940/69","MANN WK 8198/2","N/A","10W-40","Semi-synthetic",45000,"Mann+Hummel"),
    ("Scania","R 450",2016,2024,12700,"diesel","heavy_truck","MANN C 3967/3","MANN W 940/69","MANN WK 8198/3","N/A","10W-40","Semi-synthetic",45000,"Mann+Hummel"),
    ("Scania","R 500",2016,2024,12700,"diesel","heavy_truck","MANN C 3967/3","MANN W 940/69","MANN WK 8198/3","N/A","10W-40","Semi-synthetic",45000,"Mann+Hummel"),
    ("Scania","P 280",2004,2016,9300,"diesel","heavy_truck","MANN C 3967/2","MANN W 940/69","MANN WK 8198/2","N/A","10W-40","Semi-synthetic",45000,"Mann+Hummel"),
    ("Scania","G 400",2012,2024,12700,"diesel","heavy_truck","MANN C 3967/3","MANN W 940/69","MANN WK 8198/3","N/A","10W-40","Semi-synthetic",45000,"Mann+Hummel"),

    # ══ VOLVO TRUCKS ══
    ("Volvo","FH 420",2012,2024,12780,"diesel","heavy_truck","MAHLE LX 3778/2","MAHLE OC 4","MAHLE KL 79/1","N/A","10W-40","Semi-synthetic",45000,"Mahle"),
    ("Volvo","FH 460",2012,2024,12780,"diesel","heavy_truck","MAHLE LX 3778/2","MAHLE OC 4","MAHLE KL 79/1","N/A","10W-40","Semi-synthetic",45000,"Mahle"),
    ("Volvo","FM 370",2010,2024,11000,"diesel","heavy_truck","MAHLE LX 3778/2","MAHLE OC 4","MAHLE KL 79/1","N/A","10W-40","Semi-synthetic",45000,"Mahle"),

    # ══ DAF ══
    ("DAF","XF 450",2017,2024,12900,"diesel","heavy_truck","MANN C 3967/3","MANN W 940/69","MANN WK 8198/3","N/A","10W-40","Semi-synthetic",45000,"Mann+Hummel"),
    ("DAF","CF 340",2013,2024,10800,"diesel","heavy_truck","MANN C 3967/2","MANN W 940/69","MANN WK 8198/2","N/A","10W-40","Semi-synthetic",45000,"Mann+Hummel"),
    ("DAF","LF 210",2013,2024,6700,"diesel","medium_truck","MANN C 3967","MANN W 940/69","MANN WK 8198/1","N/A","10W-40","Semi-synthetic",30000,"Mann+Hummel"),

    # ══ IVECO ══
    ("Iveco","Stralis 460",2012,2024,10308,"diesel","heavy_truck","MAHLE LX 3778/1","MAHLE OC 4","MAHLE KL 79","N/A","10W-40","Semi-synthetic",45000,"Mahle"),
    ("Iveco","Daily 35S15",2006,2024,2300,"diesel","light_truck","MAHLE LX 791/2","MAHLE OC 253","MAHLE KL 185","N/A","5W-30","Synthetic",10000,"Mahle"),

    # ══ ISUZU ══
    ("Isuzu","D-Max",2007,2024,2500,"diesel","pickup","MANN C 30188","MANN W 940/69","MANN WK 8107","MANN CU 26010","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Isuzu","NLR 77",2010,2024,3000,"diesel","light_truck","MANN C 30154","MANN W 940/69","MANN WK 8198/1","N/A","15W-40","Mineral",5000,"Mann+Hummel"),
    ("Isuzu","NMR 85",2010,2024,3900,"diesel","medium_truck","MANN C 30154/1","MANN W 940/69","MANN WK 8198/1","N/A","15W-40","Mineral",5000,"Mann+Hummel"),
    ("Isuzu","FTR 33",2010,2024,7790,"diesel","heavy_truck","MANN C 3967/1","MANN W 940/69","MANN WK 8198/2","N/A","15W-40","Mineral",5000,"Mann+Hummel"),
    ("Isuzu","FVR 34",2010,2024,7790,"diesel","heavy_truck","MANN C 3967/1","MANN W 940/69","MANN WK 8198/2","N/A","15W-40","Mineral",5000,"Mann+Hummel"),

    # ══ HINO ══
    ("Hino","300 Series",2004,2024,4000,"diesel","light_truck","MANN C 30154/1","MANN W 940/69","MANN WK 8198/1","N/A","15W-40","Mineral",5000,"Mann+Hummel"),
    ("Hino","500 Series",2007,2024,7684,"diesel","medium_truck","MANN C 3967","MANN W 940/69","MANN WK 8198/2","N/A","15W-40","Mineral",5000,"Mann+Hummel"),
    ("Hino","700 Series",2004,2024,12913,"diesel","heavy_truck","MANN C 3967/1","MANN W 940/69","MANN WK 8198/2","N/A","10W-40","Semi-synthetic",30000,"Mann+Hummel"),

    # ══ FORD ══
    ("Ford","F-150",2009,2020,5000,"gasoline","pickup","MANN C 35154/2","MANN W 712/94","MANN WK 939/2","MANN CU 26023","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Ford","Ranger",2012,2022,2000,"diesel","pickup","MANN C 30188","MANN W 940/69","MANN WK 8107","MANN CU 26010","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Ford","Explorer",2011,2019,3500,"gasoline","suv","MANN C 35154/2","MANN W 712/94","MANN WK 939/2","MANN CU 26023","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Ford","Expedition",2003,2014,5400,"gasoline","suv","MANN C 35154/2","MANN W 712/94","MANN WK 939/2","MANN CU 26023","5W-30","Synthetic",7500,"Mann+Hummel"),

    # ══ GMC / CHEVROLET ══
    ("GMC","Yukon",2007,2020,5300,"gasoline","suv","MANN C 35154/2","MANN W 712/94","MANN WK 939/2","MANN CU 26023","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("GMC","Suburban",2007,2020,5300,"gasoline","suv","MANN C 35154/2","MANN W 712/94","MANN WK 939/2","MANN CU 26023","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("GMC","Terrain",2010,2017,2400,"gasoline","suv","MANN C 30154","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Chevrolet","Silverado",2007,2020,5300,"gasoline","pickup","MANN C 35154/2","MANN W 712/94","MANN WK 939/2","MANN CU 26023","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("Chevrolet","Tahoe",2007,2020,5300,"gasoline","suv","MANN C 35154/2","MANN W 712/94","MANN WK 939/2","MANN CU 26023","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("Chevrolet","Captiva",2006,2018,2400,"gasoline","suv","MANN C 30154","MANN W 712/94","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Chevrolet","Optra",2002,2008,1600,"gasoline","sedan","MANN C 24016","MANN W 712/52","MANN WK 69/1","MANN CU 2939","5W-30","Synthetic",7500,"Mann+Hummel"),
    ("Daewoo","Lanos",1997,2010,1500,"gasoline","sedan","MANN C 24016","MANN W 712/52","MANN WK 69/1","MANN CU 2939","10W-40","Semi-synthetic",5000,"Mann+Hummel"),
    ("Daewoo","Nubira",1997,2003,1600,"gasoline","sedan","MANN C 24016","MANN W 712/52","MANN WK 69/1","MANN CU 2939","10W-40","Semi-synthetic",5000,"Mann+Hummel"),

    # ══ BMW ══
    ("BMW","318i",2012,2024,1500,"gasoline","sedan","MAHLE LX 3039/1","MAHLE OC 1066","MAHLE KL 929","MAHLE LAK 911","5W-30","Synthetic",15000,"Mahle"),
    ("BMW","320i",2005,2019,2000,"gasoline","sedan","MAHLE LX 1828/1","MAHLE OC 567","MAHLE KL 584","MAHLE LAK 340","5W-30","Synthetic",15000,"Mahle"),
    ("BMW","520i",2010,2017,2000,"gasoline","sedan","MAHLE LX 1828/1","MAHLE OC 567","MAHLE KL 584","MAHLE LAK 429","5W-30","Synthetic",15000,"Mahle"),
    ("BMW","X5 3.0d",2007,2013,3000,"diesel","suv","MAHLE LX 1688","MAHLE OC 617","MAHLE KL 584","MAHLE LAK 340","5W-30","Synthetic",15000,"Mahle"),

    # ══ VOLKSWAGEN ══
    ("Volkswagen","Golf",2008,2020,1400,"gasoline","sedan","MANN C 26014/1","MANN W 712/94","MANN WK 939/2","MANN CU 26023","5W-30","Synthetic",15000,"Mann+Hummel"),
    ("Volkswagen","Passat",2011,2019,1400,"gasoline","sedan","MANN C 26014/1","MANN W 712/94","MANN WK 939/2","MANN CU 29005","5W-30","Synthetic",15000,"Mann+Hummel"),
    ("Volkswagen","Touareg",2010,2018,3000,"diesel","suv","MANN C 3698","MANN W 940/69","MANN WK 11/5","MANN CU 29005","5W-30","Synthetic",15000,"Mann+Hummel"),
    ("Volkswagen","Tiguan",2007,2024,1400,"gasoline","suv","MANN C 26014/1","MANN W 712/94","MANN WK 939/2","MANN CU 26023","5W-30","Synthetic",15000,"Mann+Hummel"),
    ("Volkswagen","Crafter",2006,2024,2000,"diesel","van","MANN C 30188","MANN W 940/69","MANN WK 8107","N/A","5W-30","Synthetic",10000,"Mann+Hummel"),

    # ══ HONDA ══
    ("Honda","Civic",2012,2021,1500,"gasoline","sedan","MANN C 30188","MANN W 712/94","MANN WK 939/2","MANN CU 26023","0W-20","Synthetic",10000,"Mann+Hummel"),
    ("Honda","Accord",2008,2017,2400,"gasoline","sedan","MANN C 30188","MANN W 712/94","MANN WK 939/2","MANN CU 26023","5W-20","Synthetic",10000,"Mann+Hummel"),
    ("Honda","CR-V",2012,2022,2400,"gasoline","suv","MANN C 30188","MANN W 712/94","MANN WK 939/2","MANN CU 26023","0W-20","Synthetic",10000,"Mann+Hummel"),

    # ══ SUZUKI ══
    ("Suzuki","Vitara",2015,2022,1600,"gasoline","suv","MANN C 26010","MANN W 712/83","MANN WK 939/2","MANN CU 29012","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Suzuki","Swift",2010,2017,1250,"gasoline","sedan","MANN C 24016","MANN W 712/52","MANN WK 939/2","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
    ("Suzuki","Grand Vitara",2005,2015,2000,"gasoline","suv","MANN C 26010","MANN W 712/83","MANN WK 939/2","MANN CU 2939","5W-30","Synthetic",10000,"Mann+Hummel"),
]


def build_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            make               TEXT NOT NULL,
            model              TEXT NOT NULL,
            year_from          INTEGER NOT NULL,
            year_to            INTEGER NOT NULL,
            engine_cc          INTEGER NOT NULL,
            engine_type        TEXT NOT NULL,
            vehicle_type       TEXT NOT NULL,
            air_filter         TEXT NOT NULL,
            oil_filter         TEXT NOT NULL,
            fuel_filter        TEXT NOT NULL,
            cabin_filter       TEXT NOT NULL,
            oil_grade          TEXT NOT NULL,
            oil_type           TEXT NOT NULL,
            change_interval_km INTEGER NOT NULL,
            source             TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_make_model    ON vehicles(make, model);
        CREATE INDEX IF NOT EXISTS idx_year          ON vehicles(year_from, year_to);
        CREATE INDEX IF NOT EXISTS idx_vehicle_type  ON vehicles(vehicle_type);
        CREATE INDEX IF NOT EXISTS idx_engine_type   ON vehicles(engine_type);
    """)

    cur.executemany("""
        INSERT INTO vehicles
        (make,model,year_from,year_to,engine_cc,engine_type,vehicle_type,
         air_filter,oil_filter,fuel_filter,cabin_filter,
         oil_grade,oil_type,change_interval_km,source)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, CATALOG)

    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
    makes = [r[0] for r in cur.execute("SELECT DISTINCT make FROM vehicles ORDER BY make").fetchall()]
    print(f"✅ قاعدة البيانات جاهزة — {count} إدخال")
    print(f"🚗 الشركات: {', '.join(makes)}")
    conn.close()


if __name__ == "__main__":
    build_database()
