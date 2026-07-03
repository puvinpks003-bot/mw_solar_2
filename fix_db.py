import sqlite3
import decimal

conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all columns of type decimal according to Django models
# To be safe, let's just check every column in the table
cursor.execute('SELECT * FROM solar_solarcalculation')
rows = cursor.fetchall()

bad_ids = []

for r in rows:
    row_id = r['id']
    for key in r.keys():
        val = r[key]
        if isinstance(val, (float, str)):
            # Django's sqlite3 backend uses this to convert to decimal:
            # create_decimal = decimal.Context(prec=28).create_decimal
            # create_decimal(value).quantize(...)
            try:
                # Mocking Django's behavior
                d = decimal.Context(prec=28).create_decimal(str(val))
                # Just doing decimal.Decimal is usually enough to catch it
            except decimal.InvalidOperation:
                print(f"Corrupted row found! ID: {row_id}, Column: {key}, Value: {repr(val)}")
                if row_id not in bad_ids:
                    bad_ids.append(row_id)
            
            # Another way Django fails: if it tries to quantize an infinity or NaN, it might throw InvalidOperation
            try:
                if isinstance(val, str) and val.strip() == '':
                    print(f"Empty string found! ID: {row_id}, Column: {key}")
                    if row_id not in bad_ids:
                        bad_ids.append(row_id)
            except Exception:
                pass

for bad_id in bad_ids:
    print(f"Deleting corrupted row {bad_id}...")
    cursor.execute(f"DELETE FROM solar_solarcalculation WHERE id = {bad_id}")

conn.commit()
print(f"Deleted {len(bad_ids)} corrupted rows.")
