# Project Completion Plan — Draft Log

## 1. Research Phase

- Studied existing tools such as PANW and Zscaler to understand design patterns and data models.
- Searched for relevant public datasets but none matched assignment requirements.
- Decided to create my own dataset.

## 2. Dataset Creation

- Wrote Python code to generate synthetic, Zscaler-like security event logs.
- Ensured dataset realism by matching field formats (timestamps, URLs, IPs, actions, etc.).
- Validated dataset structure through test generation and iteration.

## 3. Cursor Rules Setup

- Created a cursorrules file to enforce:
  - Coding conventions
  - Project structure discipline
  - TDD approach (unit tests first, code after)
  - Documentation and linting requirements
- Integrated rules into the Cursor development workflow.

## 4. UI/UX Exploration Using Stitch (with Google)

- Worked with ChatGPT to craft a tailored prompt for Stitch (https://switch.withgoogle.com/stitch) to generate:
  - UI/UX wireframes
  - Full use-case clarifications
  - User flows
- Used Stitch to produce:
  - High-level UI screens
  - Exported HTML files and assets
  - Reviewed and refined the UX to align with requirements.

## 5. Architecture & API Design Using Cursor

- Defined application architecture inside Cursor using ChatGPT-assisted prompts.
- Designed and documented REST API endpoints following OpenAPI standards.
- Iteratively refined the prompt to:
  - Improve accuracy
  - Make architecture more modular
  - Ensure backend and frontend responsibilities were clearly separated
  - Tailor implementation to my exact needs

## 6. Full Backend & Frontend Planning in Cursor

- Using improved prompts, instructed Cursor to generate:
  - Backend implementation plan (routes, controllers, services, auth, storage, batching)
  - Frontend structure (pages, components, state management)
  - Code organization strategy
- Provided additional screenshots, project plan, and wireframes to Cursor to better guide the code generation.

## 7. Code Generation & Test-Driven Development

- Prompted Cursor to generate:
  - Application code
  - Full unit test suite
- Ran generated tests, fixed issues, and allowed Cursor to auto-regenerate failing parts.
- Completed final touches including:
  - File upload batching improvements
  - Authentication enhancements
  - Validation improvements

## 8. Deployment & Manual Validation

- Deployed the application.
- Exported an Insomnia workspace for API testing.
- Used Insomnia to manually verify all generated API endpoints and flows.
- Confirmed backend and frontend functionality.

