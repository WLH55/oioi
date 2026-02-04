## ADDED Requirements

### Requirement: Module-specific exceptions
Each module SHALL define its own exception classes in `exceptions.py`.

#### Scenario: Module-specific exception
- **GIVEN** the "dramas" module
- **WHEN** a drama is not found
- **THEN** system SHALL raise `DramaNotFound` exception from `src.dramas.exceptions`

### Requirement: Module-specific constants
Each module SHALL define its own constants and error codes in `constants.py`.

#### Scenario: Error code isolation
- **GIVEN** the "tasks" module
- **WHEN** defining error codes
- **THEN** error codes SHALL be defined in `src.tasks.constants`

### Requirement: Module-specific configuration
Each module SHALL have its own Pydantic BaseSettings in `config.py` if needed.

#### Scenario: Module configuration
- **GIVEN** a module that needs specific environment variables
- **WHEN** the module loads
- **THEN** configuration SHALL be loaded from `src.<module>.config`

### Requirement: Module utilities isolation
Each module SHALL have its own utility functions in `utils.py`.

#### Scenario: Module-specific utilities
- **GIVEN** the "storyboards" module needs data transformation
- **WHEN** writing utility functions
- **THEN** functions SHALL be placed in `src.storyboards.utils`

### Requirement: Clear module boundaries
The system SHALL enforce clear boundaries between modules through explicit imports.

#### Scenario: Cross-module communication
- **GIVEN** module "episodes" needs data from "dramas"
- **WHEN** accessing the drama module
- **THEN** access SHALL go through:
  - Public functions in `service.py`
  - Defined dependencies in `dependencies.py`
  - NOT through internal module functions
