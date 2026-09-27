# customer-dataverse-integration_API
AWS REST API integration between a customer web application and Microsoft Dataverse.
# Customer Dataverse Integration API

## Overview

This project implements a customer management web application integrated
with Microsoft Dataverse through an AWS-hosted REST API.

## Architecture

Customer Web Application
        |
        | HTTPS / REST
        v
AWS API Gateway
        |
        v
AWS Lambda
        |
        | OAuth 2.0
        v
Microsoft Entra ID
        |
        v
Dataverse Web API
        |
        v
Microsoft Dataverse


## Technology Stack

### Frontend
- React
- HTML
- CSS
- JavaScript

### Backend
- Python
- REST API
- AWS Lambda
- Amazon API Gateway

### AWS
- API Gateway
- Lambda
- S3
- CloudFront
- Secrets Manager
- CloudWatch
- SQS (future enhancement)

### Microsoft
- Microsoft Entra ID
- Microsoft Dataverse
- Dataverse Web API


## REST API

| Method | Endpoint | Description |
|---|---|---|
| GET | /customers | Get all customers |
| GET | /customers/{id} | Get customer |
| POST | /customers | Create customer |
| PUT | /customers/{id} | Update customer |
| DELETE | /customers/{id} | Delete customer |


## Project Structure

customer-dataverse-integration_API/

    frontend/
        src/

    backend/
        handlers/
        services/
        repositories/
        models/
        auth/
        tests/

## Security

Secrets must never be committed to this repository.

Dataverse credentials will be stored in AWS Secrets Manager.

The application uses Microsoft Entra ID OAuth 2.0 authentication
for communication between AWS Lambda and Microsoft Dataverse.


## Status

Current phase:

Stage 1 - Microsoft Dataverse and Entra ID configuration.

Then at the bottom select Commit changes.

Use:

Initial project README

as the commit message.

2. Add .gitignore

After that, click:

Add file → Create new file

Name it:

.gitignore

Put:

# Environment variables
.env
.env.*

# Python
__pycache__/
*.py[cod]
venv/
.venv/

# Node
node_modules/
dist/
build/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# AWS
.aws-sam/

# Terraform
.terraform/
*.tfstate
*.tfstate.*
