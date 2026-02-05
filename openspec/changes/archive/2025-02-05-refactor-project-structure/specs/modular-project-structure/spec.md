## ADDED Requirements

### Requirement: Domain-based directory structure
The system SHALL organize code by business domain modules rather than file types.

#### Scenario: Module structure
- **WHEN** creating a new business module
- **THEN** system creates a directory under `src/` containing all module-specific files

### Requirement: Module file organization
Each module directory SHALL contain specific files for different concerns.

#### Scenario: Complete module structure
- **GIVEN** a module named "dramas"
- **WHEN** the module is created
- **THEN** the following files SHALL exist:
  - `router.py` - FastAPI router with all endpoints
  - `schemas.py` - Pydantic models for request/response
  - `models.py` - SQLAlchemy database models
  - `dependencies.py` - FastAPI dependencies for validation
  - `service.py` - Business logic layer
  - `config.py` - Module-specific configuration
  - `constants.py` - Constants and error codes
  - `exceptions.py` - Module-specific exceptions
  - `utils.py` - Helper functions

### Requirement: Global configuration location
The system SHALL place global configurations in the `src/` root directory.

#### Scenario: Global files exist
- **GIVEN** the refactored project structure
- **WHEN** viewing `src/` directory
- **THEN** the following files SHALL exist:
  - `config.py` - Global application settings
  - `database.py` - Database connection setup
  - `models.py` - Global database models (if any)
  - `exceptions.py` - Global exception classes
  - `main.py` - FastAPI application entry point

### Requirement: Explicit module imports
The system SHALL use explicit module names when importing from other modules.

#### Scenario: Import from other module
- **GIVEN** module "episodes" needs to use services from "dramas"
- **WHEN** writing import statements
- **THEN** imports SHALL follow format: `from src.dramas import service as drama_service`

### Requirement: Tests directory organization
The system SHALL organize tests by module under the `tests/` directory.

#### Scenario: Test structure mirrors source
- **GIVEN** a module at `src/dramas/`
- **WHEN** writing tests
- **THEN** tests SHALL be placed in `tests/dramas/`

### Requirement: Requirements file separation
The system SHALL separate dependencies by environment.

#### Scenario: Requirements structure
- **GIVEN** the project dependencies
- **WHEN** organizing requirements files
- **THEN** the following files SHALL exist:
  - `requirements/base.txt` - Core dependencies
  - `requirements/dev.txt` - Development dependencies
  - `requirements/prod.txt` - Production-only dependencies
