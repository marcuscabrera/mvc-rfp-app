# API Documentation

## Base URL
```
https://api.mvc-rfp.com/v1
```

## Overview
This document describes the REST API endpoints for the MVC RFP application.

## Authentication
The API uses JWT (JSON Web Tokens) for authentication.

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

### Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

## Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout

### Organizations
- `GET /organizations` - Retrieve all organizations
- `POST /organizations` - Create a new organization
- `GET /organizations/{id}` - Retrieve a specific organization
- `PUT /organizations/{id}` - Update an organization
- `DELETE /organizations/{id}` - Delete an organization

### Projects
- `GET /projects` - Retrieve all projects
- `POST /projects` - Create a new project
- `GET /projects/{id}` - Retrieve a specific project
- `PUT /projects/{id}` - Update a project
- `DELETE /projects/{id}` - Delete a project
- `GET /projects/{id}/rfps` - Get RFPs for a project

### Users
- `GET /users` - Retrieve all users
- `POST /users` - Create a new user
- `GET /users/{id}` - Retrieve a specific user
- `PUT /users/{id}` - Update a user
- `DELETE /users/{id}` - Delete a user
- `GET /users/{id}/roles` - Get user roles

### Questions
- `GET /questions` - Retrieve all questions
- `POST /questions` - Create a new question
- `GET /questions/{id}` - Retrieve a specific question
- `PUT /questions/{id}` - Update a question
- `DELETE /questions/{id}` - Delete a question
- `GET /questions/search` - Search questions

### Responses
- `GET /responses` - Retrieve all responses
- `POST /responses` - Create a new response
- `GET /responses/{id}` - Retrieve a specific response
- `PUT /responses/{id}` - Update a response
- `DELETE /responses/{id}` - Delete a response
- `POST /responses/bulk` - Create multiple responses

### Documents
- `GET /documents` - Retrieve all documents
- `POST /documents` - Upload a new document
- `GET /documents/{id}` - Retrieve a specific document
- `DELETE /documents/{id}` - Delete a document
- `GET /documents/{id}/download` - Download document

### Knowledge Base
- `GET /knowledge-base` - Retrieve knowledge base entries
- `POST /knowledge-base` - Create knowledge base entry
- `GET /knowledge-base/{id}` - Retrieve specific entry
- `PUT /knowledge-base/{id}` - Update knowledge base entry
- `DELETE /knowledge-base/{id}` - Delete knowledge base entry
- `POST /knowledge-base/search` - Search knowledge base

## Request/Response Format

### Standard Request Headers
```http
Content-Type: application/json
Authorization: Bearer {access_token}
```

### Standard Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2025-08-14T23:07:00Z"
}
```

## Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "timestamp": "2025-08-14T23:07:00Z"
}
```

## Rate Limiting

API requests are limited to:
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated requests
- Rate limit headers are included in responses:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Timestamp when limit resets

## CORS

Cross-Origin Resource Sharing (CORS) is configured to allow requests from authorized frontend applications.

## Versioning

API versioning is handled through the URL path (`/v1/`). When breaking changes are introduced, a new version will be released.

## Pagination

List endpoints support pagination using query parameters:
```http
GET /organizations?page=1&limit=50&sort=created_at&order=desc
```

### Pagination Response
```json
{
  "success": true,
  "data": [],
  "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "per_page": 50,
    "total_items": 500,
    "has_next": true,
    "has_previous": false
  }
}
```
