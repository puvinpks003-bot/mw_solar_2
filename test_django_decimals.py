from solar.models import SolarCalculation

print("Checking records...")
for obj in SolarCalculation.objects.all():
    try:
        # Access all DecimalFields to trigger the converter
        _ = obj.roi
        _ = obj.break_even
        _ = obj.investment
        _ = obj.sim_project_cost
    except Exception as e:
        print(f"Error on ID {obj.id}: {e}")
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM solar_solarcalculation WHERE id={obj.id}")
            print(f"Force deleted ID {obj.id} via SQL")
        except Exception as e2:
            print(f"Failed to delete ID {obj.id}: {e2}")

print("Done")
