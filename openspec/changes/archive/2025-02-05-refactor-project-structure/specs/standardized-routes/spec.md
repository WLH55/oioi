## ADDED Requirements

### Requirement: HTTP method restriction
The system SHALL only use GET and POST HTTP methods for all endpoints.

#### Scenario: Query operations use GET
- **GIVEN** an endpoint retrieves data
- **WHEN** defining the route
- **THEN** the method SHALL be GET
- **AND** the path SHALL describe the query operation (e.g., `/info`, `/list`)

#### Scenario: Create/update/delete operations use POST
- **GIVEN** an endpoint creates, updates, or deletes data
- **WHEN** defining the route
- **THEN** the method SHALL be POST
- **AND** the path SHALL describe the operation (e.g., `/create`, `/update`, `/delete`)

### Requirement: Route naming convention
All routes SHALL follow the pattern `/module/operation`.

#### Scenario: Standard route names
- **GIVEN** a module named "users"
- **WHEN** defining routes
- **THEN** routes SHALL follow:
  - `GET /users/info` - get single item
  - `GET /users/list` - get list of items
  - `POST /users/create` - create item
  - `POST /users/update` - update item
  - `POST /users/delete` - delete item

#### Scenario: Nested resource routes
- **GIVEN** a nested resource (episodes under dramas)
- **WHEN** defining routes
- **THEN** routes SHALL follow:
  - `GET /episodes/info` - get episode info
  - `POST /episodes/create` - create episode
  - The relationship SHALL be validated via dependencies, not route structure

### Requirement: Request parameter validation
All request parameters SHALL be defined using Pydantic models.

#### Scenario: POST request body
- **GIVEN** a POST endpoint accepts data
- **WHEN** defining parameters
- **THEN** request body SHALL be a Pydantic BaseModel
- **AND** fields SHALL have validation rules (min_length, max_length, etc.)

#### Scenario: GET query parameters
- **GIVEN** a GET endpoint accepts parameters
- **WHEN** defining parameters
- **THEN** parameters SHALL use FastAPI Query()
- **AND** SHALL include description and constraints

### Requirement: Pagination parameters
List endpoints SHALL use consistent pagination parameter names.

#### Scenario: Standard pagination
- **GIVEN** a list endpoint is defined
- **WHEN** accepting pagination parameters
- **THEN** parameters SHALL be named:
  - `page`: current page number (default: 1, ge: 1)
  - `page_size`: items per page (default: 10, ge: 1, le: 100)

#### Scenario: Paginated response format
- **GIVEN** a list endpoint returns paginated data
- **WHEN** returning the response
- **THEN** the data field SHALL contain:
  - `list`: the items
  - `total`: total count of items
  - `page`: current page number
  - `page_size`: items per page

### Requirement: API documentation
All endpoints SHALL include summary and description documentation.

#### Scenario: Endpoint documentation
- **GIVEN** a router endpoint is defined
- **WHEN** adding the endpoint decorator
- **THEN** it SHALL include `summary="简短描述"`
- **AND** SHALL include a docstring with:
  - Description of what the endpoint does
  - Args section listing parameters
  - Returns section describing the response

### Requirement: Response model type hint
All endpoints SHALL use ApiResponse as the response_model.

#### Scenario: Response model declaration
- **GIVEN** any endpoint is defined
- **WHEN** adding the decorator
- **THEN** it SHALL include `response_model=ApiResponse`
- **OR** for typed data: `response_model=ApiResponse[DataType]`
