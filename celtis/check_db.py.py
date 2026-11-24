import sqlite3, sys
for p in sys.argv[1:]:
    print("\n==", p)
    try:
        c = sqlite3.connect(p)
        tables = [r[0] for r in c.execute(
            "select name from sqlite_master where type='table' order by name")]
        if not tables:
            print("  (EMPTY — no tables)"); continue
        total = 0
        for t in tables:
            n = c.execute(f'select count(*) from "{t}"').fetchone()[0]
            total += n
            print(f"  {t:30} {n} rows")
        print(f"  TOTAL: {total} rows")
    except Exception as e:
        print("  ERROR:", e)