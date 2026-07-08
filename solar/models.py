from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError('The Mobile Number field must be set')
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(mobile_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Profile preferences
    dark_mode = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['email', 'full_name']

    def __str__(self):
        return f"{self.full_name} ({self.mobile_number})"


class SolarCalculation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='calculations')
    monthly_bill = models.DecimalField(max_digits=12, decimal_places=2)
    investment = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Savings projections
    annual_savings = models.DecimalField(max_digits=12, decimal_places=2)
    three_year = models.DecimalField(max_digits=12, decimal_places=2)
    five_year = models.DecimalField(max_digits=12, decimal_places=2)
    ten_year = models.DecimalField(max_digits=12, decimal_places=2)
    fifteen_year = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    twenty_year = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Metrics
    roi = models.DecimalField(max_digits=5, decimal_places=2, help_text="Return on Investment %")
    break_even = models.DecimalField(max_digits=5, decimal_places=2, help_text="Break even period in years")
    maintenance_cost = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Environmental impact
    carbon_saved = models.DecimalField(max_digits=10, decimal_places=2, help_text="Tons of CO2")
    trees_saved = models.IntegerField()
    
    net_profit = models.DecimalField(max_digits=12, decimal_places=2)
    future_value = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Simulator V2 Parameters
    sim_project_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    sim_monthly_gen = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    sim_own_usage = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    sim_tariff_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sim_maint_val = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    sim_tax_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sim_net_yearly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Calculation for {self.user.full_name} - {self.created_at.strftime('%Y-%m-%d')}"
        
    def format_inr(self, value):
        if value is None: return "0"
        try:
            s = str(int(float(value)))
        except (ValueError, TypeError):
            return "0"
        if len(s) <= 3: return s
        res = s[-3:]
        s = s[:-3]
        while len(s) > 2:
            res = s[-2:] + "," + res
            s = s[:-2]
        if s:
            res = s + "," + res
        return res

    @property
    def formatted_project_cost(self):
        return self.format_inr(self.sim_project_cost)

    @property
    def formatted_net_yearly(self):
        return self.format_inr(self.sim_net_yearly)
        
    @property
    def sim_monthly_exported(self):
        gen = self.sim_monthly_gen or 0
        usage = self.sim_own_usage or 0
        export = gen - usage
        return export if export > 0 else 0

    @property
    def sim_export_kwh_yr(self):
        return self.sim_monthly_exported * 12
        
    @property
    def formatted_export_kwh_yr(self):
        return self.format_inr(self.sim_export_kwh_yr)
    
    class Meta:
        ordering = ['-created_at']

# --- New Models for Dashboard Data ---

class Client(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='client_profile')
    client_id = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    tax_id = models.CharField(max_length=50, blank=True, null=True, help_text="Aadhaar / Tax ID")
    joining_date = models.DateField(default=timezone.now)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.client_id} - {self.user.full_name}"

class Tariff(models.Model):
    effective_date = models.DateField()
    rate_per_kwh = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"₹{self.rate_per_kwh} from {self.effective_date}"

class SolarPlant(models.Model):
    plant_id = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='plants')
    capacity_kw = models.DecimalField(max_digits=8, decimal_places=2)
    installation_date = models.DateField()
    location = models.CharField(max_length=255)
    solar_panel_brand = models.CharField(max_length=100)
    inverter_brand = models.CharField(max_length=100)
    number_of_panels = models.IntegerField()
    project_cost = models.DecimalField(max_digits=12, decimal_places=2)
    client_investment = models.DecimalField(max_digits=12, decimal_places=2)
    company_investment = models.DecimalField(max_digits=12, decimal_places=2)
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True)
    contract_period_months = models.IntegerField()
    status = models.BooleanField(default=True)

    @property
    def total_investment(self):
        return self.client_investment + self.company_investment

    def __str__(self):
        return f"{self.plant_id} - {self.client.user.full_name}"

class MeterReading(models.Model):
    plant = models.ForeignKey(SolarPlant, on_delete=models.CASCADE, related_name='readings')
    reading_date = models.DateField()
    daily_generation = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_generation = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    annual_generation = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    lifetime_generation = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    self_consumption = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    electricity_exported = models.DecimalField(max_digits=15, decimal_places=2, default=0, editable=False, help_text="Calculated automatically")
    
    def save(self, *args, **kwargs):
        # Formula: Exported = Total Generation - Self Consumption
        # Using daily_generation as the base for the day's export
        self.electricity_exported = self.daily_generation - self.self_consumption
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plant.plant_id} - {self.reading_date}"

class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments')
    plant = models.ForeignKey(SolarPlant, on_delete=models.CASCADE, related_name='payments')
    month = models.DateField(help_text="Month of the payment (usually 1st day of month)")
    exported_units = models.DecimalField(max_digits=10, decimal_places=2)
    tariff_rate = models.DecimalField(max_digits=5, decimal_places=2)
    maintenance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    payment_status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    payment_date = models.DateField(null=True, blank=True)
    
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

    def __str__(self):
        return f"Payment for {self.client.user.full_name} - {self.month.strftime('%b %Y')}"

class Notification(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification: {self.title}"
