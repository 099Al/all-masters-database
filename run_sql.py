import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from src.config import settings



DB_URL = settings.connect_url
SQL_FOLDER = Path("sql")
PROC_SUFFIX = "_proc.sql"



async def run_sql_folder(engine, folder: Path):
    files = sorted(p for p in folder.iterdir() if p.suffix == ".sql")

    if not files:
        print(f"No .sql files found in {folder}")
        return

    async with engine.begin() as conn:
        for file in files:
            print(f"\n▶ Running file: {file.name}")

            sql = file.read_text(encoding="utf-8")

            print(file)


            if file.name.endswith(PROC_SUFFIX):
                print(f"run procedure ->")
                #await conn.execute(text(stmt))
            else:
                statements = [
                    stmt.strip()
                    for stmt in sql.split(";")
                    if stmt.strip()
                ]

                for i, stmt in enumerate(statements, 1):
                    print(f"run statement {i}")
                    print(stmt)
                    #await conn.execute(text(stmt))

    print("\n All SQL scripts executed successfully")

# -----------------------
# ENTRYPOINT
# -----------------------

async def main():
    engine = create_async_engine(
        DB_URL,
        #echo=True,          # show SQL in logs
        future=True,
    )

    try:
        await run_sql_folder(engine, SQL_FOLDER)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
