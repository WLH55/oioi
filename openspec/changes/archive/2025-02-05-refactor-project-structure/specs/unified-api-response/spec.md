## ADDED Requirements

### Requirement: Unified response format
All API endpoints SHALL return a unified response format with code, message, and data fields.

#### Scenario: Successful response
- **GIVEN** an API endpoint is called successfully
- **WHEN** the endpoint returns data
- **THEN** the response SHALL contain:
  - `code`: 200 for success
  - `message`: success message string
  - `data`: the actual response data

#### Scenario: Error response
- **GIVEN** an API endpoint encounters an error
- **WHEN** the error is returned
- **THEN** the response SHALL contain:
  - `code`: appropriate error code
  - `message`: error description
  - `data`: null or additional error information

### Requirement: ApiResponse generic model
The system SHALL provide a generic ApiResponse model for type-safe response definitions.

#### Scenario: Typed response model
- **GIVEN** an endpoint returns a list of users
- **WHEN** defining the response_model
- **THEN** it SHALL be `ApiResponse[List[User]]`
- **AND** the `data` field SHALL contain the user list

### Requirement: ResponseCode constants
The system SHALL provide a ResponseCode class with standardized response codes.

#### Scenario: Using response codes
- **GIVEN** a developer needs to return an error response
- **WHEN** calling ApiResponse.error()
- **THEN** the code SHALL be from ResponseCode constants
- **AND** available codes SHALL include:
  - SUCCESS = 200
  - CREATED = 201
  - BAD_REQUEST = 400
  - UNAUTHORIZED = 401
  - FORBIDDEN = 403
  - NOT_FOUND = 404
  - CONFLICT = 409
  - INTERNAL_ERROR = 500
  - SERVICE_UNAVAILABLE = 503

### Requirement: Success response helper
The ApiResponse class SHALL provide a success() class method for creating successful responses.

#### Scenario: Success response with data
- **GIVEN** an endpoint successfully retrieves data
- **WHEN** returning the response
- **THEN** it SHALL use `ApiResponse.success(data=result, message="操作成功")`
- **AND** the response SHALL have code=200

#### Scenario: Success response without data
- **GIVEN** an endpoint successfully performs an action
- **WHEN** returning the response
- **THEN** it SHALL use `ApiResponse.success(message="操作成功")`
- **AND** the data field SHALL be null

### Requirement: Error response helper
The ApiResponse class SHALL provide an error() class method for creating error responses.

#### Scenario: Error response with code
- **GIVEN** a resource is not found
- **WHEN** returning the error
- **THEN** it SHALL use `ApiResponse.error(code=ResponseCode.NOT_FOUND, message="资源不存在")`

### Requirement: Response model declaration
All router endpoints SHALL declare response_model as ApiResponse.

#### Scenario: Endpoint response model
- **GIVEN** a router endpoint is defined
- **WHEN** adding the endpoint decorator
- **THEN** it SHALL include `response_model=ApiResponse`
- **OR** for typed responses: `response_model=ApiResponse[List[User]]`
