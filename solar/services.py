from decimal import Decimal

def calculate_solar_investment(monthly_bill: float) -> dict:
    """
    Business logic to calculate solar investment metrics.
    All calculations are done here outside of views.
    """
    monthly_bill = Decimal(str(monthly_bill))
    
    # Investment calculation based on prompt: Monthly Bill * 12 * 2.5
    investment = monthly_bill * Decimal('12') * Decimal('2.5')
    
    # Savings calculations
    annual_savings = monthly_bill * Decimal('12')
    three_year = annual_savings * Decimal('3')
    five_year = annual_savings * Decimal('5')
    ten_year = annual_savings * Decimal('10')
    fifteen_year = annual_savings * Decimal('15')
    twenty_year = annual_savings * Decimal('20')
    
    # Break-even period
    # If annual_savings > 0, break_even = investment / annual_savings
    if annual_savings > 0:
        break_even = investment / annual_savings
    else:
        break_even = Decimal('0')
        
    # Maintenance cost (assume 1% of investment per year over 20 years = 20%)
    maintenance_cost = investment * Decimal('0.20')
    
    # Net Profit over 20 years
    net_profit = twenty_year - investment - maintenance_cost
    
    # ROI over 20 years (%)
    if investment > 0:
        roi = (net_profit / investment) * Decimal('100')
    else:
        roi = Decimal('0')
        
    # Future Value (for simplicity, using net_profit)
    future_value = net_profit
    
    # Environmental Impact (Assumptions for India/₹ based on prompt's example '₹2,000')
    # Assume ₹8 per kWh.
    monthly_kwh = monthly_bill / Decimal('8')
    annual_kwh = monthly_kwh * Decimal('12')
    
    # CO2 saved: 0.85 kg per kWh -> tons = (kg / 1000)
    # Total tons over 20 years
    annual_co2_tons = (annual_kwh * Decimal('0.85')) / Decimal('1000')
    carbon_saved = annual_co2_tons * Decimal('20')
    
    # Trees saved (approx 40 trees per ton of CO2)
    trees_saved = int(carbon_saved * Decimal('40'))
    
    return {
        'monthly_bill': round(monthly_bill, 2),
        'investment': round(investment, 2),
        'annual_savings': round(annual_savings, 2),
        'three_year': round(three_year, 2),
        'five_year': round(five_year, 2),
        'ten_year': round(ten_year, 2),
        'fifteen_year': round(fifteen_year, 2),
        'twenty_year': round(twenty_year, 2),
        'roi': round(roi, 2),
        'break_even': round(break_even, 2),
        'maintenance_cost': round(maintenance_cost, 2),
        'carbon_saved': round(carbon_saved, 2),
        'trees_saved': trees_saved,
        'net_profit': round(net_profit, 2),
        'future_value': round(future_value, 2),
    }
