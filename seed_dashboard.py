import os
import django
import random
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from solar.models import Client, Tariff, SolarPlant, MeterReading, Payment, Notification

User = get_user_model()

def seed_data():
    users = User.objects.all()
    if not users:
        print("No users found to seed.")
        return

    tariff, _ = Tariff.objects.get_or_create(
        rate_per_kwh=5.50,
        defaults={'effective_date': datetime.date(2025, 1, 1)}
    )

    for i, user in enumerate(users):
        # Create Client
        client, _ = Client.objects.get_or_create(
            user=user,
            defaults={
                'client_id': f'CUST-00{i+1}',
                'address': '123 Solar Way',
                'joining_date': datetime.date(2025, 1, 1)
            }
        )
        
        # Create Plant
        plant, _ = SolarPlant.objects.get_or_create(
            plant_id=f'PLANT-{i+1}A',
            client=client,
            defaults={
                'capacity_kw': 150.0,
                'installation_date': datetime.date(2025, 1, 15),
                'location': 'Main Roof',
                'solar_panel_brand': 'SunPower',
                'inverter_brand': 'SMA',
                'number_of_panels': 400,
                'project_cost': 7500000,
                'client_investment': 5000000,
                'company_investment': 2500000,
                'tariff': tariff,
                'contract_period_months': 240
            }
        )
        
        # Create 6 months of data
        today = datetime.date.today()
        for month_offset in range(6):
            month_date = (today.replace(day=1) - datetime.timedelta(days=30 * month_offset)).replace(day=1)
            
            # Meter Reading
            reading, created = MeterReading.objects.get_or_create(
                plant=plant,
                reading_date=month_date,
                defaults={
                    'daily_generation': 500.0 + random.uniform(-50, 50),
                    'monthly_generation': 15000.0 + random.uniform(-1000, 1000),
                    'lifetime_generation': 15000.0 * (6 - month_offset),
                    'self_consumption': 5000.0 + random.uniform(-500, 500)
                }
            )
            
            # Payment based on reading
            if created:
                Payment.objects.create(
                    client=client,
                    plant=plant,
                    month=month_date,
                    exported_units=reading.monthly_generation - reading.self_consumption,
                    tariff_rate=tariff.rate_per_kwh,
                    maintenance_percentage=5.0,
                    tax_percentage=18.0,
                    payment_status='COMPLETED',
                    payment_date=month_date + datetime.timedelta(days=5)
                )
                
        # Notifications
        Notification.objects.get_or_create(
            client=client,
            title="Monthly Report Available",
            defaults={'message': "Your generation report is ready."}
        )

    print(f"Successfully seeded data for {len(users)} users!")

if __name__ == '__main__':
    seed_data()
