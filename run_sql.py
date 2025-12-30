import asyncio
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from src.config import settings
from sqlalchemy import text


DB_URL = settings.connect_url
SQL_FOLDER = Path("sql")
PROC_SUFFIX = "_proc.sql"

import src.log_settings
import logging
logger = logging.getLogger(__name__)

async def run_sql_folder(engine, folder: Path):
    files = sorted(p for p in folder.iterdir() if p.suffix == ".sql")

    if not files:
        print(f"No .sql files found in {folder}")
        logger.error(f"No .sql files found in {folder}")
        return

    async with engine.begin() as conn:
        for file in files:
            logger.info(f"Running file: {file.name}")
            print(f"\n▶ Running file: {file.name}")

            sql = file.read_text(encoding="utf-8")

            print(file)
            logger.info(f"File content: {sql}")


            if file.name.endswith(PROC_SUFFIX):
                print(f"run procedure ->")
                logger.info(f"run procedure ->")
                try:
                    await conn.execute(text(stmt))
                except Exception as e:
                    print(e)
                    logger.error(f"Error in run script procedure: {e}")
            else:
                statements = [
                    stmt.strip()
                    for stmt in sql.split(";")
                    if stmt.strip()
                ]

                for i, stmt in enumerate(statements, 1):
                    print(f"run statement {i}")
                    logger.info(f"run statement {i}")
                    try:
                        await conn.execute(text(stmt))
                    except Exception as e:
                        print(e)
                        logger.error(f"Error in run script: {e}")
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
