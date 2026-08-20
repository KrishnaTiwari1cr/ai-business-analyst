import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.database.connection import engine
from app.database.schema import (
    Base,
    Region,
    SalesChannel,
    Customer,
    Product,
    Order,
    OrderItem,
)


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

NUM_CUSTOMERS = 500
NUM_PRODUCTS = 100
NUM_ORDERS = 5000

random.seed(42)


# ---------------------------------------------------------
# SAMPLE DATA
# ---------------------------------------------------------

REGIONS = [
    "North",
    "South",
    "East",
    "West",
    "Central",
]

SALES_CHANNELS = [
    "Online",
    "Retail",
    "Distributor",
    "Direct Sales",
]

PRODUCT_CATEGORIES = [
    "Electronics",
    "Furniture",
    "Office Supplies",
    "Accessories",
    "Software",
]


# ---------------------------------------------------------
# CREATE REGIONS
# ---------------------------------------------------------

def create_regions(session):

    regions = []

    for region_name in REGIONS:
        region = Region(
            region_name=region_name
        )

        session.add(region)
        regions.append(region)

    session.flush()

    return regions


# ---------------------------------------------------------
# CREATE SALES CHANNELS
# ---------------------------------------------------------

def create_channels(session):

    channels = []

    for channel_name in SALES_CHANNELS:
        channel = SalesChannel(
            channel_name=channel_name
        )

        session.add(channel)
        channels.append(channel)

    session.flush()

    return channels


# ---------------------------------------------------------
# CREATE CUSTOMERS
# ---------------------------------------------------------

def create_customers(session, regions):

    customers = []

    first_names = [
        "Aarav",
        "Vivaan",
        "Aditya",
        "Arjun",
        "Rohan",
        "Rahul",
        "Kabir",
        "Ananya",
        "Priya",
        "Isha",
        "Neha",
        "Riya",
    ]

    last_names = [
        "Sharma",
        "Verma",
        "Gupta",
        "Singh",
        "Tiwari",
        "Patel",
        "Kumar",
        "Mehta",
        "Malhotra",
        "Agarwal",
    ]

    for customer_id in range(1, NUM_CUSTOMERS + 1):

        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        customer = Customer(
            customer_name=f"{first_name} {last_name}",
            email=f"customer{customer_id}@example.com",
            region_id=random.choice(regions).region_id,
        )

        session.add(customer)
        customers.append(customer)

    session.flush()

    return customers


# ---------------------------------------------------------
# CREATE PRODUCTS
# ---------------------------------------------------------

def create_products(session):

    products = []

    product_names = [
        "Laptop",
        "Monitor",
        "Keyboard",
        "Mouse",
        "Headphones",
        "Printer",
        "Desk",
        "Office Chair",
        "Tablet",
        "Smartphone",
        "Cloud Software",
        "Antivirus Software",
        "USB Hub",
        "Webcam",
        "External SSD",
    ]

    for product_id in range(1, NUM_PRODUCTS + 1):

        product_name = random.choice(product_names)

        category = random.choice(
            PRODUCT_CATEGORIES
        )

        price = round(
            random.uniform(50, 2000),
            2
        )

        cost = round(
            price * random.uniform(0.45, 0.75),
            2
        )

        product = Product(
            product_name=f"{product_name} {product_id}",
            category=category,
            price=Decimal(str(price)),
            cost=Decimal(str(cost)),
        )

        session.add(product)
        products.append(product)

    session.flush()

    return products


# ---------------------------------------------------------
# CREATE ORDERS + ORDER ITEMS
# ---------------------------------------------------------

def create_orders(
    session,
    customers,
    regions,
    channels,
    products,
):

    start_date = date(2024, 1, 1)

    for order_id in range(1, NUM_ORDERS + 1):

        customer = random.choice(customers)

        region_id = customer.region_id

        channel = random.choice(channels)

        random_days = random.randint(
            0,
            730
        )

        order_date = (
            start_date +
            timedelta(days=random_days)
        )

        order = Order(
            order_id=order_id,
            customer_id=customer.customer_id,
            region_id=region_id,
            channel_id=channel.channel_id,
            order_date=order_date,
        )

        session.add(order)

        session.flush()

        number_of_items = random.randint(
            1,
            5
        )

        selected_products = random.sample(
            products,
            number_of_items
        )

        for product in selected_products:

            quantity = random.randint(
                1,
                5
            )

            unit_price = float(
                product.price
            )

            revenue = (
                unit_price *
                quantity
            )

            cost = (
                float(product.cost) *
                quantity
            )

            profit = revenue - cost

            order_item = OrderItem(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=quantity,
                unit_price=Decimal(
                    str(round(unit_price, 2))
                ),
                revenue=Decimal(
                    str(round(revenue, 2))
                ),
                cost=Decimal(
                    str(round(cost, 2))
                ),
                profit=Decimal(
                    str(round(profit, 2))
                ),
            )

            session.add(order_item)


# ---------------------------------------------------------
# MAIN SEED FUNCTION
# ---------------------------------------------------------

def seed_database():

    print("Starting database seeding...")

    Base.metadata.create_all(engine)

    with Session(engine) as session:

        # Clear existing data
        session.query(OrderItem).delete()
        session.query(Order).delete()
        session.query(Customer).delete()
        session.query(Product).delete()
        session.query(SalesChannel).delete()
        session.query(Region).delete()

        session.commit()

        print("Creating regions...")
        regions = create_regions(session)

        print("Creating sales channels...")
        channels = create_channels(session)

        print("Creating customers...")
        customers = create_customers(
            session,
            regions
        )

        print("Creating products...")
        products = create_products(
            session
        )

        print("Creating orders...")
        create_orders(
            session,
            customers,
            regions,
            channels,
            products,
        )

        session.commit()

    print()
    print("Database seeded successfully!")
    print()
    print(f"Customers: {NUM_CUSTOMERS}")
    print(f"Products: {NUM_PRODUCTS}")
    print(f"Orders: {NUM_ORDERS}")


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    seed_database()