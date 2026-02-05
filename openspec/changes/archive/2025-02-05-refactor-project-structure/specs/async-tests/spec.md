## ADDED Requirements

### Requirement: Async test client
The system SHALL use an async test client for integration tests.

#### Scenario: Async client setup
- **GIVEN** the test suite is initialized
- **WHEN** creating a test client
- **THEN** the client SHALL use httpx or similar async library
- **AND** SHALL be configured with the FastAPI app

### Requirement: Async test functions
All test functions that use the test client SHALL be async.

#### Scenario: Async test definition
- **GIVEN** a test that makes API calls
- **WHEN** the test is defined
- **THEN** the test function SHALL be marked as `async def`
- **AND** SHALL use `await` for async operations

### Requirement: Test database isolation
The system SHALL use a separate database for testing.

#### Scenario: Test database configuration
- **GIVEN** the test suite runs
- **WHEN** tests access the database
- **THEN** tests SHALL use a separate test database
- **AND** production data SHALL NOT be affected

### Requirement: Test fixtures
The system SHALL provide fixtures for common test dependencies.

#### Scenario: Common test fixtures
- **GIVEN** multiple tests need similar setup
- **WHEN** writing tests
- **THEN** fixtures SHALL be available for:
  - Test client
  - Database session
  - Authentication tokens
  - Test data

### Requirement: Test organization by module
Tests SHALL be organized by module under the `tests/` directory.

#### Scenario: Test file structure
- **GIVEN** a module at `src/dramas/`
- **WHEN** writing tests for the drama module
- **THEN** tests SHALL be placed in `tests/dramas/`
- **AND** test files SHALL mirror the structure of `src/dramas/`
