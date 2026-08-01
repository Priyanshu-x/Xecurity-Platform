import asyncio
import os
import sys

# Add the parent directory to sys.path to allow imports from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
import app.models  # Ensure all models are registered
from app.models.product import Product
from app.models.plan import ProductPlan
from app.common.enums import PlanTier, PlanStatus

PLANS = [
    {
        "name": "Community",
        "slug": "community",
        "description": "Free tier for individual researchers and students. Includes core forensic analysis with basic reporting.",
        "tier": PlanTier.COMMUNITY,
        "max_users": 1,
        "max_devices": 1,
        "trial_days": 0,
    },
    {
        "name": "Professional",
        "slug": "professional",
        "description": "For independent forensic consultants and small teams. Includes advanced analysis, export to PDF/DOCX, and priority support.",
        "tier": PlanTier.PROFESSIONAL,
        "max_users": 5,
        "max_devices": 5,
        "trial_days": 14,
    },
    {
        "name": "Enterprise",
        "slug": "enterprise",
        "description": "For law enforcement agencies and corporate investigation teams. Unlimited users, centralized management, audit logging, and SLA support.",
        "tier": PlanTier.ENTERPRISE,
        "max_users": None,  # Unlimited
        "max_devices": None,  # Unlimited
        "trial_days": 30,
    },
    {
        "name": "Government",
        "slug": "government",
        "description": "Purpose-built for government agencies and national security. Includes air-gapped deployment, FedRAMP-ready controls, and dedicated support.",
        "tier": PlanTier.GOVERNMENT,
        "max_users": None,  # Unlimited
        "max_devices": None,  # Unlimited
        "trial_days": 0,
    },
]


async def seed_plans():
    async with AsyncSessionLocal() as db:
        # Find the first product (WhatsApp Forensic Analyzer)
        result = await db.execute(select(Product).limit(1))
        product = result.scalar_one_or_none()

        if not product:
            print("ERROR: No products found. Please create a product first.")
            return

        print(f"Using product: {product.name} (ID: {product.id})")

        for plan_data in PLANS:
            # Check if plan already exists by slug
            result = await db.execute(
                select(ProductPlan).where(
                    ProductPlan.slug == plan_data["slug"],
                    ProductPlan.product_id == product.id,
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                print(f"  Plan '{plan_data['name']}' already exists. Skipping.")
                continue

            plan = ProductPlan(
                product_id=product.id,
                status=PlanStatus.ACTIVE,
                **plan_data,
            )
            db.add(plan)
            print(f"  Created plan: {plan_data['name']} ({plan_data['tier'].value})")

        await db.commit()
        print("\nDone! Plans seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_plans())
