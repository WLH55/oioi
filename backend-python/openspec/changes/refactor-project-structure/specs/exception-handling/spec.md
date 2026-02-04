## ADDED Requirements

### Requirement: Custom exception classes
The system SHALL provide custom exception classes for different error scenarios.

#### Scenario: Business validation exception
- **GIVEN** request parameters fail business rules
- **WHEN** raising an exception
- **THEN** it SHALL raise `BusinessValidationException`
- **AND** the exception SHALL contain a message
- **AND** the exception MAY contain an error code

#### Scenario: HTTP client exception
- **GIVEN** a third-party API call fails
- **WHEN** raising an exception
- **THEN** it SHALL raise `HttpClientException`
- **AND** the exception SHALL contain a message
- **AND** the exception MAY contain an HTTP status code

### Requirement: Global exception handlers
The system SHALL register global exception handlers for all custom exceptions.

#### Scenario: Business validation handler
- **GIVEN** BusinessValidationException is raised
- **WHEN** the exception is caught
- **THEN** the handler SHALL return ApiResponse with:
  - code = ResponseCode.BAD_REQUEST
  - message = exception message
  - data = null
- **AND** HTTP status SHALL be 400

#### Scenario: HTTP client handler
- **GIVEN** HttpClientException is raised
- **WHEN** the exception is caught
- **THEN** the handler SHALL return ApiResponse with:
  - code = exception code or ResponseCode.INTERNAL_ERROR
  - message = exception message
  - data = null
- **AND** HTTP status SHALL match the exception code

#### Scenario: General exception handler
- **GIVEN** an unhandled exception occurs
- **WHEN** the exception is caught
- **THEN** the handler SHALL return ApiResponse with:
  - code = ResponseCode.INTERNAL_ERROR
  - message = exception message or "服务器内部错误"
  - data = null
- **AND** HTTP status SHALL be 500

### Requirement: Module-specific exceptions
Each module MAY define its own exception classes.

#### Scenario: Module exception
- **GIVEN** the "dramas" module needs specific exceptions
- **WHEN** defining exceptions
- **THEN** they SHALL be in `src.dramas.exceptions`
- **AND** exceptions SHALL inherit from base exception classes
- **AND** example exceptions: DramaNotFound, InvalidDramaData

### Requirement: Exception registration
All custom exception handlers SHALL be registered in the main application.

#### Scenario: Exception handler registration
- **GIVEN** the FastAPI app is created
- **WHEN** initializing the app
- **THEN** all custom exception handlers SHALL be registered
- **AND** the registration SHALL happen before routes are included

### Requirement: Validation through exceptions
Dependencies SHALL raise exceptions for validation failures.

#### Scenario: Resource not found dependency
- **GIVEN** a dependency validates a resource exists
- **WHEN** the resource is not found
- **THEN** the dependency SHALL raise a module-specific exception (e.g., DramaNotFound)
- **AND** the exception SHALL be handled by the global handler

### Requirement: Pydantic validation errors
Request validation errors from Pydantic SHALL be converted to ApiResponse format.

#### Scenario: Pydantic validation failure
- **GIVEN** request body fails Pydantic validation
- **WHEN** the validation error occurs
- **THEN** the handler SHALL return ApiResponse with:
  - code = ResponseCode.BAD_REQUEST
  - message = validation error details
  - data = null
