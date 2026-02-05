## ADDED Requirements

### Requirement: Decoupled BaseSettings
The system SHALL separate Pydantic BaseSettings across modules and domains.

#### Scenario: Module-specific settings
- **GIVEN** the "tasks" module needs specific environment variables
- **WHEN** the module configuration is defined
- **THEN** a `TaskConfig` class SHALL exist in `src.tasks.config`
- **AND** it SHALL inherit from `BaseSettings`

### Requirement: Global settings isolation
The system SHALL maintain a global `Config` class in `src/config.py` for cross-cutting concerns.

#### Scenario: Global configuration
- **GIVEN** application-wide settings like database URL and CORS
- **WHEN** the application starts
- **THEN** settings SHALL be loaded from `src.config.Settings`

### Requirement: Settings instantiation
Each module SHALL instantiate its settings class for easy import.

#### Scenario: Import settings instance
- **GIVEN** the "videos" module has configuration
- **WHEN** other code needs video settings
- **THEN** code SHALL import `from src.videos.config import video_settings`

### Requirement: Configuration type safety
The system SHALL use Pydantic for configuration type validation.

#### Scenario: Type-safe configuration
- **GIVEN** a setting requires a specific type (e.g., integer port)
- **WHEN** the environment variable is set
- **THEN** Pydantic SHALL validate the type
- **AND** SHALL raise an error if invalid

### Requirement: Environment-specific configuration
The system SHALL support environment-specific configuration values.

#### Scenario: Development vs production
- **GIVEN** different settings for development and production
- **WHEN** the application runs
- **THEN** settings SHALL be loaded from environment variables
- **AND** default values SHALL be provided for local development
