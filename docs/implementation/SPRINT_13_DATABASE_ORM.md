# Sprint 13 — Ububiko: Database & ORM Foundation

**Goal**: Build a Laravel Eloquent-like ORM for the I Programming Language — entirely in Kinyarwanda.

## Kinyarwanda Naming Glossary

The I language is Kinyarwanda. Every public API name must be in Kinyarwanda.

| Kinyarwanda | English | Context |
|-------------|---------|---------|
| `ububiko` | database | Package name |
| `ububiko_bubiko` | table | Database table |
| `igice` | column | Table column |
| `inyandiko` | record/row | Database row |
| `ibikoresho` | model | ORM model |
| `imibare` | query | Query builder |
| `gusobanura` | describe/schema | Schema definition |
| `guhindura` | alter/migrate | Migration |
| `kwiyunga` | join | SQL JOIN |
| `ihitamwo` | where | WHERE clause |
| `uryaheje` | order/sort | ORDER BY |
| `igitero` | limit | LIMIT |
| `kubika` | save | Save record |
| `gukuramo` | delete | Delete record |
| `kubona` | find/select | Find/select records |
| `shyiramo` | insert | INSERT |
| `hindura` | update | UPDATE |
| `siba` | drop/delete | DROP/DELETE |
| `tangura` | create | CREATE TABLE |
| `kubona_buri` | all | Select all |
| `kubona_imwe` | first | Select first |
| `ibara` | count | COUNT |
| `igiteranyo` | sum | SUM |
| `ibiharuro` | average | AVG |
| `nta_gushyira` | null | NULL |
| `nta_bihinduka` | immutable | Read-only |
| `ubwoko` | type | Column type |
| `inyandiko_ya` | belongs_to | Relationship |
| `ifite` | has_one/has_many | Relationship |
| `pivote` | pivot | Many-to-many pivot |
| `gisanzwe` | default | Default value |
| `birindwa` | unique | UNIQUE constraint |
| `ntabwo_birambuye` | nullable | Allow NULL |
| `ubwangano` | primary_key | Primary key |
| `byongera` | auto_increment | Auto-increment |
| `ubukoro` | index | Database index |
| `yoboye` | soft_delete | Soft delete |
| `imiterere` | timestamps | created_at/updated_at |

## Architecture

```
src/ububiko/
├── __init__.py              # Package: ububiko v0.1.0
├── uhuguriro.py             # Connection pool (uhuguriro = connection)
├── imibare.py               # Query builder (imibare = queries)
├── gusobanura.py            # Schema definition (gusobanura = describe)
├── icyerekezo.py            # Schema builder DDL (icyerekezo = blueprint)
├── guhindura.py             # Migration engine (guhindura = alter)
├── ibikoresho.py            # BaseModel ActiveRecord (ibikoresho = model)
├── imikoreshereze.py        # Relationships (imikoreshereze = relations)
├── ubusabane.py             # Query scopes (ubusabane = scopes/filters)
└── impinduramuburiri.py     # Accessors & mutators (impinduramuburiri = transformers)
```

## Module Details

### uhuguriro.py — Connection Pool

```python
from ububiko.uhuguriro import Uhuguriro

# Uhuguriro = Connection
uhuguriro = Uhuguriro("app.db")

# With transaction (ihumiro = transaction)
with uhuguriro.ihumiro() as ih:
    ih.yandika("INSERT INTO abantu (izina) VALUES (?)", ("Jean",))

# Auto-managed connection
with uhuguriro.uko() as uko:
    uko.yandika("SELECT * FROM abantu")
```

**Key methods:**
- `Uhuguriro(db_path)` — create connection pool
- `uhuguriro.ihumiro()` — transaction context manager
- `uhuguriro.uko()` — connection context manager
- `uhuguriro.gufungura()` — open connection
- `uhuguriro.kufunga()` — close connection
- `uhuguriro.kubanza()` — begin transaction
- `uhuguriro.kwemeza()` — commit
- `uhuguriro.kureka()` — rollback

**PRAGMAs (SQLite WAL mode):**
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;
PRAGMA cache_size = -8000;
PRAGMA foreign_keys = ON;
```

### imibare.py — Query Builder

```python
from ububiko.imibare import Imibare

# SELECT — Imibare = Query
imibare = (Imibare(uhuguriro)
    .hitamwo("imyaka", ">=", 18)
    .uryaheje("izina")
    .igitero(10))

# KIGERAHO = get results
abantu = imibare.kigeraho()
# [{"id": 1, "izina": "Jean", "imyaka": 25}, ...]

# KONA = find one
umuntu = Imibare(uhuguriro).hitamwo("id", "=", 1).kona()

# IBARA = count
ibara = Imibare(uhuguriro).hitamwo("imyaka", ">=", 18).ibara()

# SHYIRAMO = insert
Imibare(uhuguriro).shyiramo("abantu", izina="Jean", imyaka=25)

# HINDURA = update
Imibare(uhuguriro).table("abantu").hitamwo("id", "=", 1).hindura(izina="Bob")

# SIBA = delete
Imibare(uhuguriro).table("abantu").hitamwo("id", "=", 1).siba()
```

**All methods in Kinyarwanda:**

| Method | English | Description |
|--------|---------|-------------|
| `.hitamwo(col, op, val)` | where | Add WHERE clause |
| `.hitamwo_bitewe(col, op, val)` | or_where | OR WHERE |
| `.hitamwo_mu(col, values)` | where_in | WHERE IN |
| `.hitamwo_sihitamwo(col)` | where_null | WHERE IS NULL |
| `.uryaheje(col, dir)` | order_by | ORDER BY |
| `.igitero(n)` | limit | LIMIT |
| `.gushyiraho(n)` | offset | OFFSET |
| `.tandukanye()` | distinct | SELECT DISTINCT |
| `.kwiyunga(table, c1, op, c2)` | join | JOIN |
| `.kwiyunga_ibumoso(table, c1, op, c2)` | left_join | LEFT JOIN |
| `.group_by(*cols)` | group_by | GROUP BY |
| `.ibara()` | count | COUNT(*) |
| `.igiteranyo(col)` | sum | SUM(col) |
| `.ibiharuro(col)` | avg | AVG(col) |
| `.kigeraho()` | get | Execute and return all |
| `.kona()` | first | Execute and return first |
| `.irabonekera()` | exists | Check existence |
| `.shyiramo(table, **kw)` | insert | INSERT |
| `.shyiramo_birenze(table, rows)` | insert_many | INSERT multiple |
| `.hindura(**kw)` | update | UPDATE |
| `.siba()` | delete | DELETE |
| `.yandika()` | to_sql | Debug SQL |

### gusobanura.py — Schema Definition

```python
from ububiko.gusobanura import Igice, UbubikoBubiko, Ubukoro

# Igice = Column
# UbubikoBubiko = Table
# Ubukoro = Index

ibice = [
    Igice("id", "umubumbe", ubwangano=True, byongera=True),
    Igice("izina", "umuntu(255)", ntabwo_birambuye=False),
    Igice("email", "umuntu(255)", ntabwo_birambuye=False, birindwa=True),
    Igice("imyaka", "umubumbe", gisanzwe=0),
    Igice("yoboye", "ukuri", gisanzwe=False),
    Igice("imiterere", "itariki"),
]

ububiko = UbubikoBubiko("abantu", ibice, ubukoro=[
    Ubukoro("ubukoro_email", ["email"], birindwa=True),
])

# Kugaragaza — display DDL
print(ububiko.kugaragaza())
# CREATE TABLE abantu (
#   id UMUBUMBE PRIMARY KEY AUTOINCREMENT,
#   izina UMUNTU(255) NOT NULL,
#   email UMUNTU(255) NOT NULL UNIQUE,
#   imyaka UMUBUMBE DEFAULT 0,
#   yoboye UKURI DEFAULT 0,
#   imiterere ITARIKI
# );
```

**Column types (Kinyarwanda):**

| Kinyarwanda | English | SQL |
|-------------|---------|-----|
| `umubumbe` | integer | INTEGER |
| `umubumbe_munini` | bigint | BIGINT |
| `umuntu(n)` | varchar(n) | VARCHAR(n) |
| `ubusobanuro` | text | TEXT |
| `ibibya(n,m)` | decimal | DECIMAL(n,m) |
| `ubwigenge` | float | FLOAT |
| `ukuri` | boolean | BOOLEAN |
| `itariki` | date | DATE |
| `igihe` | datetime | DATETIME |
| `ibyuma` | blob | BLOB |
| `ibikubiyemo` | json | JSON |

**Column constraints:**

| Kinyarwanda | English |
|-------------|---------|
| `ubwangano` | primary_key |
| `byongera` | auto_increment |
| `ntabwo_birambuye` | nullable |
| `birindwa` | unique |
| `gisanzwe` | default |
| `ubukoro` | index |
| `ubukoro_bibiri` | composite_index |

### guhindura.py — Migration Engine

```python
from ububiko.guhindura import Guhindura

class ShturaAbantu(Guhindura):
    """ShturaAbantu = CreateUsersTable"""

    def inyuma(self):  # up
        self.tangura("abantu", [
            Igice("id", "umubumbe", ubwangano=True, byongera=True),
            Igice("izina", "umuntu(255)", ntabwo_birambuye=False),
            Igice("email", "umuntu(255)", ntabwo_birambuye=False, birindwa=True),
            Igice("imiterere", "itariki"),
        ])

    def subira_inyuma(self):  # down
        self.siba_ububiko("abantu")

class OngerahoImyaka(Guhindura):
    """OngerahoImyaka = AddAgeToUsers"""

    def inyuma(self):
        self.ongeraho_igice("abantu", Igice("imyaka", "umubumbe", gisanzwe=0))

    def subira_inyuma(self):
        self.kuramo_igice("abantu", "imyaka")

# Migration tracking
Guhindura.kwinjira(uhuguriro)  # run pending
Guhindura.subira_inyuma(uhuguriro)  # rollback last batch
Guhindura.imerere(uhuguriro)  # show status
```

**Migration operations (Kinyarwanda):**

| Method | English | Description |
|--------|---------|-------------|
| `tangura(name, columns)` | create_table | CREATE TABLE |
| `siba_ububiko(name)` | drop_table | DROP TABLE |
| `tangura_izina(old, new)` | rename_table | RENAME TABLE |
| `ongeraho_igice(table, column)` | add_column | ADD COLUMN |
| `kuramo_igice(table, col)` | drop_column | DROP COLUMN |
| `hindura_izina(table, old, new)` | rename_column | RENAME COLUMN |
| `guhindura_igice(table, column)` | alter_column | ALTER COLUMN |
| `ongeraho_ubukoro(name, table, cols)` | add_index | ADD INDEX |
| `siba_ubukoro(name)` | drop_index | DROP INDEX |

### ibikoresho.py — BaseModel (ActiveRecord)

```python
from ububiko.ibikoresho import Ibikoresho

class Umuntu(Ibikoresho):
    """Umuntu = User (ibikoresho = model)"""
    _ububiko = "abantu"  # _table
    _uzuzanya = ["izina", "email", "imyaka"]  # _fillable
    # _hidden, _casts, _imiterere (timestamps)

# SHYIRAMO = Create
umuntu = Umuntu.shyiramo(izina="Jean", email="jean@example.com", imyaka=25)

# GUKORA = New + save
umuntu = Umuntu(izina="Alice", email="alice@example.com")
umuntu.kubika()

# KUBONA = Find
umuntu = Umuntu.kubona(1)  # find by ID
umuntu = Umuntu.hitamwo("email", "=", "jean@example.com").kona()  # first
abantu = Umuntu.kubona_buri()  # all
abantu = Umuntu.hitamwo("imyaka", ">=", 18).kigeraho()  # get

# HINDURA = Update
umuntu.izina = "Bob"
umuntu.kubika()  # save changes

# SIBA = Delete
umuntu.siba()
Umuntu.hitamwo("id", "=", 1).siba()

# IBARA = Count
ibara = Umuntu.ibara()
ibara = Umuntu.hitamwo("imyaka", ">=", 18).ibara()
```

**Model properties (Kinyarwanda):**

| Property | English |
|----------|---------|
| `_ububiko` | table name |
| `_ubwangano` | primary key |
| `_uzuzanya` | fillable fields |
| `_bihishe` | hidden fields |
| `_hindura` | type casts |
| `_imiterere` | timestamps |

**Model methods (Kinyarwanda):**

| Method | English |
|--------|---------|
| `.kubika()` | save |
| `.siba()` | delete |
| `.kubona(id)` | find |
| `.kubona_buri()` | all |
| `.hitamwo(col, op, val)` | where |
| `.kona()` | first |
| `.ibara()` | count |
| `.kugaragaza()` | to_dict |
| `.kugaragaza_json()` | to_json |
| `.ntabwo_byahindutse()` | is_clean |
| `.byahindutse(field)` | was_changed |

### imikoreshereze.py — Relationships

```python
class Umuntu(Ibikoresho):
    _ububiko = "abantu"

    def inkwoko(self):
        """inkwoko = phone (hasOne)"""
        return self.ifite(Inkwoko)

    def inkono(self):
        """inkono = posts (hasMany)"""
        return self.ifite(Inkono)

class Inkono(Ibikoresho):
    _ububiko = "inkono"

    def umwanditsi(self):
        """umwanditsi = author (belongsTo)"""
        return self.inyandiko_ya(Umuntu)

    def ibinyobwa(self):
        """ibinyobwa = tags (belongsToMany)"""
        return self.inyandiko_ya_birenze(Igitingo)
```

**Relationship methods (Kinyarwanda):**

| Method | English | Description |
|--------|---------|-------------|
| `.ifite(Related)` | has_one | One-to-one |
| `.ifite_birenze(Related)` | has_many | One-to-many |
| `.inyandiko_ya(Related)` | belongs_to | Inverse FK |
| `.inyandiko_ya_birenze(Related)` | belongsToMany | Many-to-many via pivot |
| `.gisanzwe()` | morph_to | Polymorphic inverse |
| `.ifite_gisanzwe(Related)` | morph_many | Polymorphic has-many |

**Eager loading:**
```python
# with_ = neza (load with)
abantu = Umuntu.neza("inkwoko", "inkono").kigeraho()
umuntu = Umuntu.neza("inkono.umwanditsi").kubona(1)
```

### ubusabane.py — Query Scopes

```python
class Umuntu(Ibikoresho):
    _ububiko = "abantu"

    # ubusabane = scope
    def ubusabane_kurangira(self, imibare):
        """kurangira = active"""
        return imibare.hitamwo("kurangira", "=", True)

    def ubusabane_imyaka(self, imibare):
        """imyaka = adults"""
        return imibare.hitamwo("imyaka", ">=", 18)

    @classmethod
    def ubusabane_zose(cls):
        """zose = all (global scopes)"""
        return [UbusabaneYoboye()]

# Usage
abantu = Umuntu.kurangira().imyaka().kigeraho()
```

### impinduramuburiri.py — Accessors, Mutators, Casting

```python
class Umuntu(Ibikoresho):
    _ububiko = "abantu"
    _hindura = {  # _casts
        "imyaka": "umubumbe",
        "kurangira": "ukuri",
        "amateka": "ibikubiyemo",
        "itariki_yo_kwiyandikisha": "igihe",
    }

    # impinduramuburiri = accessor
    def get_izina_attribute(self, agaciro):
        return agaciro.upper()

    # guhinduramuburiri = mutator
    def set_izina_attribute(self, agaciro):
        self._ibicuruzwa["izina"] = agaciro.lower()
```

**Cast types (Kinyarwanda):**

| Kinyarwanda | English |
|-------------|---------|
| `umubumbe` | integer |
| `ubwigenge` | float |
| `umuntu` | string |
| `ukuri` | boolean |
| `ibikubiyemo` | array (JSON) |
| `igikubiyemo` | json |
| `igihe` | datetime |
| `itariki` | date |
| `bihishijwe` | encrypted |

### icyerekezo.py — Schema Builder DDL

```python
from ububiko.icyerekezo import Icyerekezo

# Icyerekezo = Blueprint
icyerekezo = Icyerekezo(uhuguriro)

# Tangura = Create
icyerekezo.tangura("abantu", lambda t: [
    t.id(),
    t.umuntu("izina"),
    t.umuntu("email").birindwa(),
    t.umubumbe("imyaka").gisanzwe(0),
    t.ukuri("kurangira").gisanzwe(True),
    t.imiterere(),
])

# Guhindura = Alter
icyerekezo.guhindura("abantu", lambda t: [
    t.umuntu("telefone").ntabwo_birambuye(),
    t.kuramo("icyumweru_cya_kadhalika"),
])

# Siba = Drop
icyerekezo.siba("abantu")

# Tangura_izina = Rename
icyerekezo.tangura_izina("ubukiriya_bwa_kadhalika", "abantu")

# Kubona = Check
icyerekezo.kubona_ububiko("abantu")  # has_table
icyerekezo.kubona_igice("abantu", "email")  # has_column
```

## Implementation Order

1. `uhuguriro.py` — Connection pool with WAL mode
2. `imibare.py` — Query builder (SELECT, INSERT, UPDATE, DELETE)
3. `gusobanura.py` — Column, Table, Index definitions
4. `icyerekezo.py` — SchemaBuilder DDL operations
5. `guhindura.py` — Migration engine
6. `ibikoresho.py` — BaseModel with CRUD
7. `imikoreshereze.py` — Relationship system
8. `ubusabane.py` — Query scopes
9. `impinduramuburiri.py` — Accessors, mutators, casting

## Test Plan

~155 tests across 9 test files (all test file names in Kinyarwanda):

| File | Tests | Coverage |
|------|-------|----------|
| `test_uhuguriro.py` | 15 | Pool, transactions, WAL mode, PRAGMA |
| `test_imibare.py` | 25 | All query builder operations |
| `test_gusobanura.py` | 15 | Column, Table, Index definitions |
| `test_icyerekezo.py` | 15 | SchemaBuilder DDL operations |
| `test_guhindura.py` | 20 | Migration up/down/status |
| `test_ibikoresho.py` | 25 | CRUD, casting, serialization |
| `test_imikoreshereze.py` | 20 | All relationship types |
| `test_ubusabane.py` | 10 | Local + global scopes |
| `test_impinduramuburiri.py` | 10 | Accessors, mutators, casting |
| **Total** | **~155** | |

## Files Created/Modified

- `src/ububiko/` — New package (9 modules)
- `src/urubuga/app.py` — Add `.ububiko` property for database access
- `tests/unit/ububiko/` — New test directory (9 test files)
- `pyproject.toml` — Add `ububiko*` packages
