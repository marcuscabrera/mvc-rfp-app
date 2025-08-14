# API Documentation

## Overview

This document describes the REST API endpoints for the MVC RFP application.

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Login
```http
POST /api/auth/login
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

### Organizations

#### GET /api/organizations
Retrieve all organizations

#### POST /api/organizations
Create a new organization

#### GET /api/organizations/:id
Retrieve a specific organization

#### PUT /api/organizations/:id
Update an organization

#### DELETE /api/organizations/:id
Delete an organization

### Projects

#### GET /api/projects
Retrieve all projects

#### POST /api/projects
Create a new project

#### GET /api/projects/:id
Retrieve a specific project

### Users

#### GET /api/users
Retrieve all users

#### POST /api/users
Create a new user

### Questions

#### GET /api/questions
Retrieve all questions

#### POST /api/questions
Create a new question

### Responses

#### GET /api/responses
Retrieve all responses

#### POST /api/responses
Create a new response

## Error Handling

The API returns standard HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

API requests are limited to 100 requests per minute per IP address.

## CORS

Cross-Origin Resource Sharing (CORS) is configured to allow requests from the frontend application.
