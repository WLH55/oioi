## ADDED Requirements

### Requirement: Dependency-based validation
The system SHALL use FastAPI dependencies for data validation against database constraints.

#### Scenario: Validate resource exists
- **GIVEN** an endpoint that needs a drama by ID
- **WHEN** the endpoint is called with a drama_id
- **THEN** system SHALL validate the drama exists through a dependency
- **AND** if drama does not exist, SHALL raise `DramaNotFound` exception

### Requirement: Dependency chaining
The system SHALL support dependencies that depend on other dependencies.

#### Scenario: Chain validation
- **GIVEN** an endpoint that needs both a valid drama and valid episode
- **WHEN** the endpoint is called
- **THEN** system SHALL first validate the drama exists
- **AND** THEN validate the episode belongs to that drama
- **AND** both validations SHALL use separate dependencies

### Requirement: Dependency reuse
The system SHALL cache dependency results within a request scope.

#### Scenario: Dependency called multiple times
- **GIVEN** a dependency `valid_drama_id` is used in multiple parameters
- **WHEN** the endpoint handler executes
- **THEN** the dependency SHALL be executed only once
- **AND** the cached result SHALL be reused

### Requirement: Async dependencies
The system SHALL prefer async dependencies for database operations.

#### Scenario: Async dependency validation
- **GIVEN** a dependency that queries the database
- **WHEN** the dependency is defined
- **THEN** it SHALL be defined as `async def`
- **AND** SHALL use await for database calls

### Requirement: RESTful dependency patterns
The system SHALL follow REST conventions for dependency naming to enable reuse.

#### Scenario: Consistent path parameters
- **GIVEN** endpoints `GET /dramas/{drama_id}` and `GET /dramas/{drama_id}/episodes`
- **WHEN** both endpoints validate drama_id
- **THEN** both SHALL use the same path parameter name `drama_id`
- **AND** MAY use the same validation dependency
