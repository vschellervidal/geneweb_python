# GeneWeb Python

GeneWeb Python is a Python 3.11+ port of the original GeneWeb genealogy software written in OCaml.

## Overview

GeneWeb is an open source genealogy software that comes with a Web interface and can be used off-line or as a Web service. This Python port aims to maintain compatibility with the original OCaml implementation while providing a modern Python API.

## Features

- **Core Types**: Fundamental genealogy data types (persons, families, events, dates)
- **Date Handling**: Support for multiple calendars (Gregorian, Julian, French, Hebrew)
- **Name Processing**: Advanced name normalization, comparison, and phonetic algorithms
- **Type Safety**: Full type annotations compatible with mypy
- **Modern Python**: Uses Python 3.11+ features like `match/case` and `@dataclass`

## Installation

```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install with test dependencies
pip install -e ".[test]"
```

## Quick Start

```python
from geneweb.def.adef import Fix, Dmy, Precision, Calendar, GregorianDate
from geneweb.def.def import GenPerson, Sex, Access
from geneweb.util.date import leap_year, nb_days_in_month
from geneweb.util.name import lower, title, strip_lower

# Create a date
birth_date = Dmy(day=15, month=3, year=1990, prec=Precision.SURE, delta=0)
greg_date = GregorianDate(dmy=birth_date, calendar=Calendar.GREGORIAN)

# Create a person
person = GenPerson(
    first_name="Jean",
    surname="Martin",
    occ=0,
    image="",
    public_name="",
    qualifiers=[],
    aliases=[],
    first_names_aliases=[],
    surnames_aliases=[],
    titles=[],
    rparents=[],
    related=[],
    occupation="Engineer",
    sex=Sex.MALE,
    access=Access.PUBLIC,
    birth=greg_date,
    birth_place="Paris",
    birth_note="",
    birth_src="",
    baptism=None,
    baptism_place="",
    baptism_note="",
    baptism_src="",
    death=None,
    death_place="",
    death_note="",
    death_src="",
    burial=None,
    burial_place="",
    burial_note="",
    burial_src="",
    pevents=[],
    notes="",
    psources="",
    key_index=1
)

# Use utility functions
print(f"Is 2024 a leap year? {leap_year(2024)}")
print(f"Days in February 2024: {nb_days_in_month(2, 2024)}")
print(f"Lowercase name: {lower('JEAN-PIERRE')}")
print(f"Title case: {title('jean-pierre martin')}")
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=geneweb

# Run specific test file
pytest tests/test_adef.py
```

### Type Checking

```bash
# Run mypy type checker
mypy geneweb/

# Run ruff linter
ruff check geneweb/
```

### Code Formatting

```bash
# Format code with ruff
ruff format geneweb/
```

## Architecture

The Python port follows the same module structure as the original OCaml code:

- `geneweb.def`: Core type definitions
  - `adef.py`: Basic types (dates, couples, strings)
  - `def.py`: Domain types (persons, families, events)
- `geneweb.util`: Utility modules
  - `date.py`: Date manipulation
  - `name.py`: Name processing
- `geneweb.core`: Core algorithms
- `geneweb.db`: Database operations
- `geneweb.lib`: High-level library functions

## Translation Notes

### OCaml → Python Mappings

| OCaml | Python | Notes |
|-------|--------|-------|
| `type fix = int` | `class Fix` | Custom type for consanguinity rates |
| `type date = Dgreg of dmy * calendar \| Dtext of string` | `Union[GregorianDate, TextDate]` | Sum types → Union types |
| `type dmy = { day: int; ... }` | `@dataclass(frozen=True)` | Records → Dataclasses |
| `exception HttpExn` | `class HttpExn(Exception)` | Exceptions → Exception classes |
| `'a option` | `Optional[T]` | Option types → Optional |
| `'a list` | `List[T]` | Lists → Lists |
| `'a array` | `List[T]` | Arrays → Lists |
| Pattern matching | `match/case` | Pattern matching → match statements |

### Key Design Decisions

1. **Immutability**: Used `@dataclass(frozen=True)` for immutable types
2. **Type Safety**: Full type annotations with generics
3. **Error Handling**: Python exceptions instead of OCaml exceptions
4. **Recursion**: Converted tail recursion to loops where appropriate
5. **Modules**: OCaml modules → Python classes and packages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the GPL-2.0-only license, same as the original GeneWeb.

## Acknowledgments

- Original GeneWeb team for the OCaml implementation
- Python community for excellent tooling and libraries
