"""
Run with: python _fix_db.py
Applies missing columns/tables directly via SQL without using migrate.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# 1. Show existing tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cursor.fetchall()]
print("Existing tables:", tables)

# 2. Show existing columns in designs_design
cursor.execute("PRAGMA table_info(designs_design)")
design_cols = [r[1] for r in cursor.fetchall()]
print("designs_design columns:", design_cols)

# 3. Show existing columns in designs_stonesize
cursor.execute("PRAGMA table_info(designs_stonesize)")
stone_cols = [r[1] for r in cursor.fetchall()]
print("designs_stonesize columns:", stone_cols)

# 4. Show existing columns in designs_designcolor
cursor.execute("PRAGMA table_info(designs_designcolor)")
dc_cols = [r[1] for r in cursor.fetchall()]
print("designs_designcolor columns:", dc_cols)

# 5. Show applied migrations
cursor.execute("SELECT app, name FROM django_migrations WHERE app IN ('designs','accounts') ORDER BY id")
applied = cursor.fetchall()
print("Applied migrations:", applied)

# ── designs_stonesize ──────────────────────────────────────────────────────────
if 'price' in stone_cols and 'glass_stone_price' not in stone_cols:
    print("Renaming stonesize.price -> glass_stone_price ...")
    # SQLite doesn't support RENAME COLUMN before 3.25, use workaround
    cursor.execute("""
        CREATE TABLE designs_stonesize_new (
            id TEXT NOT NULL PRIMARY KEY,
            size VARCHAR(50) NOT NULL,
            glass_stone_price DECIMAL(10,2) NOT NULL DEFAULT 0,
            plastic_stone_price DECIMAL(10,2) NOT NULL DEFAULT 0,
            updated_at DATETIME NOT NULL,
            created_at DATETIME NOT NULL
        )
    """)
    cursor.execute("""
        INSERT INTO designs_stonesize_new (id, size, glass_stone_price, plastic_stone_price, updated_at, created_at)
        SELECT id, size, price, 0, updated_at, created_at FROM designs_stonesize
    """)
    cursor.execute("DROP TABLE designs_stonesize")
    cursor.execute("ALTER TABLE designs_stonesize_new RENAME TO designs_stonesize")
    print("  done.")
elif 'glass_stone_price' not in stone_cols:
    cursor.execute("ALTER TABLE designs_stonesize ADD COLUMN glass_stone_price DECIMAL(10,2) NOT NULL DEFAULT 0")
    print("Added glass_stone_price to stonesize.")

if 'plastic_stone_price' not in stone_cols:
    cursor.execute("ALTER TABLE designs_stonesize ADD COLUMN plastic_stone_price DECIMAL(10,2) NOT NULL DEFAULT 0")
    print("Added plastic_stone_price to stonesize.")

# ── designs_design ─────────────────────────────────────────────────────────────
if 'color_count' not in design_cols:
    cursor.execute("ALTER TABLE designs_design ADD COLUMN color_count INTEGER NOT NULL DEFAULT 0")
    print("Added color_count to designs_design.")

if 'is_printable' not in design_cols:
    cursor.execute("ALTER TABLE designs_design ADD COLUMN is_printable BOOL NOT NULL DEFAULT 0")
    print("Added is_printable to designs_design.")

# Remove mold_price if it exists (SQLite: just leave it, it won't cause errors)
# We can't easily DROP COLUMN in old SQLite, but it won't break anything.

# ── designs_designcolor ────────────────────────────────────────────────────────
if 'use_plastic_stone' not in dc_cols:
    cursor.execute("ALTER TABLE designs_designcolor ADD COLUMN use_plastic_stone BOOL NOT NULL DEFAULT 0")
    print("Added use_plastic_stone to designs_designcolor.")

# ── designs_moldprice ──────────────────────────────────────────────────────────
if 'designs_moldprice' not in tables:
    cursor.execute("""
        CREATE TABLE designs_moldprice (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            price DECIMAL(10,2) NOT NULL,
            updated_at DATETIME NOT NULL,
            created_at DATETIME NOT NULL
        )
    """)
    print("Created designs_moldprice table.")

# ── Remove color_count from designs_design (now a @property) ──────────────────
cursor.execute("PRAGMA table_info(designs_design)")
design_cols_now = [r[1] for r in cursor.fetchall()]
if 'color_count' in design_cols_now:
    print("Removing color_count column from designs_design (rebuilding table)...")
    # Get all current columns except color_count
    cursor.execute("PRAGMA table_info(designs_design)")
    all_cols = [(r[1], r[2], r[3], r[4]) for r in cursor.fetchall() if r[1] != 'color_count']
    col_defs = ', '.join(
        f'"{c[0]}" {c[1]}{"  NOT NULL" if c[2] else ""}{"  DEFAULT " + str(c[3]) if c[3] else ""}'
        for c in all_cols
    )
    col_names = ', '.join(f'"{c[0]}"' for c in all_cols)
    cursor.execute(f"CREATE TABLE designs_design_new ({col_defs})")
    cursor.execute(f"INSERT INTO designs_design_new ({col_names}) SELECT {col_names} FROM designs_design")
    cursor.execute("DROP TABLE designs_design")
    cursor.execute("ALTER TABLE designs_design_new RENAME TO designs_design")
    print("  done.")

# ── accounts_userprofile role field ───────────────────────────────────────────
# TextChoices only changes validation, not DB schema — no SQL needed.

# ── orders_order: add stone_type ──────────────────────────────────────────────
cursor.execute("PRAGMA table_info(orders_order)")
order_cols = [r[1] for r in cursor.fetchall()]
if 'stone_type' not in order_cols:
    cursor.execute("ALTER TABLE orders_order ADD COLUMN stone_type VARCHAR(10) NOT NULL DEFAULT 'glass'")
    print("Added stone_type to orders_order.")

# ── designs_designcolor: remove stone_size_id and use_plastic_stone ───────────
cursor.execute("PRAGMA table_info(designs_designcolor)")
dc_cols_now = [r[1] for r in cursor.fetchall()]
if 'stone_size_id' in dc_cols_now or 'use_plastic_stone' in dc_cols_now:
    print("Removing stone_size_id and use_plastic_stone from designs_designcolor...")
    keep = [c for c in dc_cols_now if c not in ('stone_size_id', 'use_plastic_stone')]
    col_names_str = ', '.join(f'"{c}"' for c in keep)
    cursor.execute(f"""
        CREATE TABLE designs_designcolor_new AS
        SELECT {col_names_str} FROM designs_designcolor
    """)
    cursor.execute("DROP TABLE designs_designcolor")
    cursor.execute("ALTER TABLE designs_designcolor_new RENAME TO designs_designcolor")
    print("  done.")

# ── Mark migrations as applied in django_migrations ───────────────────────────
from django.utils import timezone
now = timezone.now().isoformat()

migrations_to_mark = [
    ('designs', '0006_rename_price_update_stone'),
    ('designs', '0007_add_moldprice_remove_design_mold_price'),
    ('designs', '0008_alter_stonesize_glass_stone_price'),
    ('designs', '0009_remove_design_color_count'),
    ('designs', '0010_remove_designcolor_stone_fields'),
    ('accounts', '0004_add_designer_role'),
    ('orders',   '0006_add_stone_type_to_order'),
]

for app, name in migrations_to_mark:
    cursor.execute(
        "SELECT COUNT(*) FROM django_migrations WHERE app=%s AND name=%s", [app, name]
    )
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
            [app, name, now]
        )
        print(f"Marked migration {app}.{name} as applied.")
    else:
        print(f"Migration {app}.{name} already marked.")

connection.commit()
print("\nAll done. Database is up to date.")
