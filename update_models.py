import re

with open('solar/models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. MeterReading changes
old_meter = """    self_consumption = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    @property
    def electricity_exported(self):
        return self.daily_generation - self.self_consumption

    def __str__(self):"""

new_meter = """    self_consumption = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    electricity_exported = models.DecimalField(max_digits=15, decimal_places=2, default=0, editable=False, help_text="Calculated automatically")
    
    def save(self, *args, **kwargs):
        # Formula: Exported = Total Generation - Self Consumption
        # Using daily_generation as the base for the day's export
        self.electricity_exported = self.daily_generation - self.self_consumption
        super().save(*args, **kwargs)

    def __str__(self):"""

content = content.replace(old_meter, new_meter)

# 2. Payment changes
old_payment = """    payment_date = models.DateField(null=True, blank=True)

    @property
    def gross_revenue(self):
        return self.exported_units * self.tariff_rate
        
    @property
    def maintenance_charge(self):
        return self.gross_revenue * (self.maintenance_percentage / 100)
        
    @property
    def tax_amount(self):
        return self.gross_revenue * (self.tax_percentage / 100)
        
    @property
    def net_earnings(self):
        return self.gross_revenue - self.maintenance_charge - self.tax_amount

    def __str__(self):"""

new_payment = """    payment_date = models.DateField(null=True, blank=True)
    
    gross_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0, editable=False)
    maintenance_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    net_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0, editable=False)

    def save(self, *args, **kwargs):
        # Gross Revenue = Exported Units * Tariff Rate
        self.gross_revenue = self.exported_units * self.tariff_rate
        
        # Maintenance Charge = Gross Revenue * Maintenance %
        self.maintenance_charge = self.gross_revenue * (self.maintenance_percentage / 100)
        
        # Tax = Gross Revenue * Tax %
        self.tax_amount = self.gross_revenue * (self.tax_percentage / 100)
        
        # Net Earnings = Gross Revenue - Maintenance - Tax
        self.net_earnings = self.gross_revenue - self.maintenance_charge - self.tax_amount
        
        super().save(*args, **kwargs)

    def __str__(self):"""

content = content.replace(old_payment, new_payment)

with open('solar/models.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated models with save methods and fields.")
