from django.core.management.base import BaseCommand

from Ltfront.models import Product, ProductSpecification


PRODUCTS = [
    {
        "name": "HP Omen 16",
        "category": "Laptops",
        "price": "89999.00",
        "image": "shop/images/hp-omen-16.svg",
        "description": "Performance laptop for gaming, development, and everyday productivity.",
    },
    {
        "name": "Dell Inspiron 15",
        "category": "Laptops",
        "price": "62999.00",
        "image": "shop/images/dell-inspiron-15.svg",
        "description": "Versatile laptop for study, office work, coding, and entertainment.",
    },
    {
        "name": "Samsung Galaxy S24",
        "category": "Smartphones",
        "price": "74999.00",
        "image": "shop/images/galaxy-s24.svg",
        "description": "Premium smartphone with a bright display and advanced camera features.",
    },
    {
        "name": "iPhone 15",
        "category": "Smartphones",
        "price": "69999.00",
        "image": "shop/images/iphone-15.svg",
        "description": "Modern smartphone with a high-quality display, camera, and strong performance.",
    },
    {
        "name": "Sony WH-1000XM5",
        "category": "Headphones",
        "price": "29990.00",
        "image": "shop/images/sony-wh1000xm5.svg",
        "description": "Over-ear wireless headphones designed for immersive listening and noise reduction.",
    },
    {
        "name": "JBL Tune 770NC",
        "category": "Headphones",
        "price": "7999.00",
        "image": "shop/images/jbl-tune-770nc.svg",
        "description": "Wireless headphones with active noise cancellation and long battery life.",
    },
    {
        "name": "Samsung 55-inch 4K TV",
        "category": "Televisions",
        "price": "54999.00",
        "image": "shop/images/samsung-55-tv.svg",
        "description": "Large 4K smart television for movies, sports, streaming, and gaming.",
    },
    {
        "name": "LG 43-inch Smart TV",
        "category": "Televisions",
        "price": "34999.00",
        "image": "shop/images/lg-43-tv.svg",
        "description": "Compact 4K smart TV suitable for bedrooms, study rooms, and living spaces.",
    },
    {
        "name": "PlayStation 5",
        "category": "Gaming",
        "price": "49990.00",
        "image": "shop/images/playstation-5.svg",
        "description": "Next-generation gaming console for high-resolution and high-frame-rate gaming.",
    },
    {
        "name": "Logitech Gaming Mouse",
        "category": "Accessories",
        "price": "2499.00",
        "image": "shop/images/logitech-gaming-mouse.svg",
        "description": "Responsive gaming mouse with programmable controls and an ergonomic design.",
    },
    {
        "name": 'Asus ROG Strix G16 (G614PW-RV078WS)',
        "category": 'Laptops',
        "price": '349990.00',
        "image": 'shop/images/hp-omen-16.svg',
        "description": 'Latest 2026 gaming laptop with Ryzen 9 8940HX, RTX 5080 graphics, 16GB DDR5 RAM, and 1TB SSD.',
    },
    {
        "name": 'Asus ROG Strix Scar 18 G835LXG-TQ492WS',
        "category": 'Laptops',
        "price": '699990.00',
        "image": 'shop/images/dell-inspiron-15.svg',
        "description": 'Flagship 18-inch gaming laptop with a Mini LED display, RTX 5090 graphics, 64GB DDR5 RAM, and 2TB SSD.',
    },
    {
        "name": 'Asus ROG Zephyrus G16 GU606AW-TB043WS',
        "category": 'Laptops',
        "price": '529990.00',
        "image": 'shop/images/hp-omen-16.svg',
        "description": 'Premium 16-inch OLED gaming laptop with Core Ultra 9, RTX 5080 graphics, 32GB RAM, and 2TB SSD.',
    },
    {
        "name": 'Asus ROG Zephyrus Duo 16 GX651AR-SR074WS',
        "category": 'Laptops',
        "price": '569990.00',
        "image": 'shop/images/dell-inspiron-15.svg',
        "description": 'Dual-screen OLED performance laptop with Core Ultra 9, RTX 5070 Ti graphics, 32GB RAM, and 2TB SSD.',
    },
    {
        "name": 'MSI Raider 18 Max HX A2WI-1257IN',
        "category": 'Laptops',
        "price": '549990.00',
        "image": 'shop/images/hp-omen-16.svg',
        "description": 'High-end 18-inch gaming powerhouse with Mini LED display, Core Ultra 9, RTX 5080 graphics, and 2TB SSD.',
    },
    {
        "name": 'Samsung Galaxy S26 Ultra',
        "category": 'Smartphones',
        "price": '139999.00',
        "image": 'shop/images/galaxy-s24.svg',
        "description": '2026 flagship Android smartphone with a 200MP camera system, Snapdragon 8 Elite Gen 5, and advanced AI features.',
    },
    {
        "name": 'vivo X300 Pro',
        "category": 'Smartphones',
        "price": '119999.00',
        "image": 'shop/images/iphone-15.svg',
        "description": 'Premium camera-focused smartphone with 16GB RAM, 512GB storage, a 6510mAh battery, and 90W charging.',
    },
    {
        "name": 'Samsung Galaxy Z Fold 8',
        "category": 'Smartphones',
        "price": '174999.00',
        "image": 'shop/images/galaxy-s24.svg',
        "description": 'Large-screen foldable flagship with a 7.61-inch main display, Snapdragon 8 Elite Gen 5, and 12GB RAM.',
    },
    {
        "name": 'OPPO Find X9 Ultra',
        "category": 'Smartphones',
        "price": '169999.00',
        "image": 'shop/images/iphone-15.svg',
        "description": 'Ultra-premium camera smartphone with a 200MP main camera, 512GB storage, and 100W charging.',
    },
    {
        "name": 'Google Pixel 11 Pro',
        "category": 'Smartphones',
        "price": '119999.00',
        "image": 'shop/images/galaxy-s24.svg',
        "description": 'Google flagship built around the Tensor G6 platform with a high-end camera system and clean Android experience.',
    },
    {
        "name": 'Sony WH-1000XM6',
        "category": 'Headphones',
        "price": '44990.00',
        "image": 'shop/images/sony-wh1000xm5.svg',
        "description": 'Flagship wireless noise-cancelling headphones known for strong ANC, detailed sound, and smart features.',
    },
    {
        "name": 'Bose QuietComfort Ultra Headphones (2nd Gen)',
        "category": 'Headphones',
        "price": '49900.00',
        "image": 'shop/images/jbl-tune-770nc.svg',
        "description": 'Premium ANC headphones with immersive audio, strong noise cancellation, and long-wear comfort.',
    },
    {
        "name": 'Bowers & Wilkins PX7 S3',
        "category": 'Headphones',
        "price": '59500.00',
        "image": 'shop/images/sony-wh1000xm5.svg',
        "description": 'Premium wireless ANC over-ear headphones with refined sound and a luxury build.',
    },
    {
        "name": 'Sennheiser MOMENTUM 5 Wireless',
        "category": 'Headphones',
        "price": '39990.00',
        "image": 'shop/images/jbl-tune-770nc.svg',
        "description": 'New 2026 wireless headphones with adaptive ANC, Dolby Atmos, 42mm drivers, and up to 57 hours of battery life.',
    },
    {
        "name": 'Apple AirPods Pro 3',
        "category": 'Headphones',
        "price": '27900.00',
        "image": 'shop/images/sony-wh1000xm5.svg',
        "description": 'New-generation wireless earbuds with advanced ANC, heart-rate sensing, Spatial Audio, and USB-C charging.',
    },
    {
        "name": 'Sony BRAVIA 9 II',
        "category": 'Televisions',
        "price": '839900.00',
        "image": 'shop/images/samsung-55-tv.svg',
        "description": 'Premium 2026 Mini LED TV with advanced RGB backlight control, 120Hz refresh rate, and Google TV.',
    },
    {
        "name": 'LG G6 OLED',
        "category": 'Televisions',
        "price": '184990.00',
        "image": 'shop/images/lg-43-tv.svg',
        "description": 'Premium OLED TV with a high-brightness Tandem WOLED evo panel and advanced gaming features.',
    },
    {
        "name": 'Samsung Neo QLED QN80H',
        "category": 'Televisions',
        "price": '87490.00',
        "image": 'shop/images/samsung-55-tv.svg',
        "description": 'Bright-room Neo QLED Mini LED television with a 144Hz refresh rate and smart TV features.',
    },
    {
        "name": 'Xiaomi TV S Mini LED',
        "category": 'Televisions',
        "price": '99999.00',
        "image": 'shop/images/lg-43-tv.svg',
        "description": 'Value-focused QD Mini LED 4K TV with strong local dimming and gaming-friendly features.',
    },
    {
        "name": 'LG C6 OLED',
        "category": 'Televisions',
        "price": '132990.00',
        "image": 'shop/images/samsung-55-tv.svg',
        "description": '2026 OLED evo television aimed at high-refresh gaming and cinematic viewing.',
    },
    {
        "name": 'Nintendo Switch 2',
        "category": 'Gaming',
        "price": '49990.00',
        "image": 'shop/images/playstation-5.svg',
        "description": 'Current-generation Nintendo hybrid console with custom NVIDIA graphics and 256GB storage.',
    },
    {
        "name": 'Sony PlayStation 5 Pro',
        "category": 'Gaming',
        "price": '109999.00',
        "image": 'shop/images/playstation-5.svg',
        "description": 'Premium PlayStation console focused on higher-fidelity 4K gaming and enhanced graphics performance.',
    },
    {
        "name": 'ROG Xbox Ally X',
        "category": 'Gaming',
        "price": '139990.00',
        "image": 'shop/images/playstation-5.svg',
        "description": 'Windows 11 handheld gaming PC with Ryzen AI Z2 Extreme, 24GB RAM, 1TB SSD, and a 120Hz display.',
    },
    {
        "name": 'MSI MPG 322UR QD-OLED X24',
        "category": 'Gaming',
        "price": '109999.00',
        "image": 'shop/images/playstation-5.svg',
        "description": 'High-end 31.5-inch 4K QD-OLED gaming monitor with 240Hz refresh rate and 0.03ms response time.',
    },
    {
        "name": 'Alienware AW2726DM',
        "category": 'Gaming',
        "price": '46999.00',
        "image": 'shop/images/playstation-5.svg',
        "description": '27-inch QD-OLED gaming monitor with QHD resolution, 240Hz refresh rate, and ultra-fast response.',
    },
    {
        "name": 'Logitech MX Master 4',
        "category": 'Accessories',
        "price": '15995.00',
        "image": 'shop/images/logitech-gaming-mouse.svg',
        "description": 'Latest flagship wireless productivity mouse with advanced haptics and precision controls.',
    },
    {
        "name": 'Logitech MX Keypad',
        "category": 'Accessories',
        "price": '15999.00',
        "image": 'shop/images/logitech-gaming-mouse.svg',
        "description": 'New AI-focused programmable control pad with customizable LCD keys for coding and creative workflows.',
    },
    {
        "name": 'Logitech Spotlight 2',
        "category": 'Accessories',
        "price": '7995.00',
        "image": 'shop/images/logitech-gaming-mouse.svg',
        "description": 'Wireless presentation remote with advanced pointer controls, haptics, and multi-device connectivity.',
    },
    {
        "name": 'Xiaomi Power Bank 20000 165W',
        "category": 'Accessories',
        "price": '5499.00',
        "image": 'shop/images/logitech-gaming-mouse.svg',
        "description": 'High-power 20,000mAh portable charger with up to 165W combined output and a built-in USB-C cable.',
    },
    {
        "name": 'Xiaomi UltraThin Magnetic Power Bank 5000 15W',
        "category": 'Accessories',
        "price": '5599.00',
        "image": 'shop/images/logitech-gaming-mouse.svg',
        "description": 'Compact magnetic wireless power bank designed for convenient portable charging.',
    },

]
PRODUCT_SPECS = {
    "HP Omen 16": [
        ("Configuration", "Without HP Care"),
        ("Brand", "HP"),
        ("Model Name", "HP Gaming Laptop"),
        ("Screen Size", "16 Inches"),
        ("Colour", "Shadow Black"),
        ("Hard Disk Size", "1 TB"),
        ("CPU Model", "Intel Core Ultra 7"),
        ("RAM Memory", "24 GB"),
        ("Operating System", "Windows 11 Home"),
        ("Special Feature", "Anti Glare Coating, Backlit Keyboard"),
        ("Graphics Card", "Dedicated"),
    ],

    "Dell Inspiron 15": [
        ("Brand", "Dell"),
        ("Model Name", "Inspiron 15"),
        ("Screen Size", "15.6 Inches"),
        ("Storage", "512 GB SSD"),
        ("RAM Memory", "16 GB"),
        ("Operating System", "Windows 11"),
    ],
}

class Command(BaseCommand):
    help = "Create or update the demo electronics products."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for product_data in PRODUCTS:
            name = product_data["name"]

            product, created = Product.objects.update_or_create(
                name=name,
                defaults=product_data,
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            specifications = PRODUCT_SPECS.get(name, [])

            ProductSpecification.objects.filter(product=product).delete()

            for order, (label, value) in enumerate(specifications, start=1):
                ProductSpecification.objects.create(
                    product=product,
                    label=label,
                    value=value,
                    order=order,
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {created_count} created, {updated_count} updated."
            )
        )
