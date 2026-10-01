# Database

> 25 nodes · cohesion 0.13

## Key Concepts

- **Database** (24 connections) — `src/storage/database.py`
- **database.py** (11 connections) — `src/storage/database.py`
- **._get_connection()** (9 connections) — `src/storage/database.py`
- **typing** (8 connections)
- **job_fetcher.py** (7 connections) — `src/scraper/job_fetcher.py`
- **JobFetcher** (6 connections) — `src/scraper/job_fetcher.py`
- **test_database.py** (5 connections) — `tests/test_database.py`
- **.get_all_applications()** (3 connections) — `src/storage/database.py`
- **.get_application()** (3 connections) — `src/storage/database.py`
- **.__init__()** (3 connections) — `src/storage/database.py`
- **._init_db()** (3 connections) — `src/storage/database.py`
- **datetime** (2 connections)
- **.fetch_jobs()** (2 connections) — `src/scraper/job_fetcher.py`
- **.__init__()** (2 connections) — `src/scraper/job_fetcher.py`
- **.add_application()** (2 connections) — `src/storage/database.py`
- **.get_stats()** (2 connections) — `src/storage/database.py`
- **.is_already_applied()** (2 connections) — `src/storage/database.py`
- **.update_status()** (2 connections) — `src/storage/database.py`
- **Any** (2 connections)
- **test_database_init_and_crud()** (2 connections) — `tests/test_database.py`
- **Connection** (1 connections)
- **jobspy** (1 connections)
- **sqlite3** (1 connections)
- **Any** (1 connections)
- **Path** (1 connections)

## Relationships

- [run.py](run.py.md) (21 shared connections)
- [MasterProfile](MasterProfile.md) (3 shared connections)
- [app.py](app.py.md) (2 shared connections)
- [config_loader.py](config_loader.py.md) (1 shared connections)

## Source Files

- `src/scraper/job_fetcher.py`
- `src/storage/database.py`
- `tests/test_database.py`

## Audit Trail

- EXTRACTED: 63 (95%)
- INFERRED: 3 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*