# Schoolify – Secure Role-Based School Management System

## Project Overview

This project is a Role-based school management web application, which is developed as a part of the Secure Web Development (Continuous Assessment) module.

This application is intentionally designed as a vulnerable web application with minimal security controls and then gradually hardened by the implementing the core web security mechanisms which includes authentication, authorization, password hashing, and database encryption.

The application supports three different user roles:

- Principal  
- Teacher  
- Parent  

Each user permissions has been defined according to their roles by enforcing Role-Based Access Control (RBAC) at the backend level.

---

## Project Objectives

- To show how the vulnerable Web application can be secured using the industry best practices.
- Implement authentication and authorization using JWT
- Enforce RBAC across multiple user roles
- Secure user credentials using bcrypt password hashing
- Protect sensitive data using field-level encryption in MongoDB
- Provide a working application with a frontend and backend

---

## System Architecture

The system follows a three-tier architecture:

- Frontend: React (Vite)
- Backend: FastAPI (Python)
- Database: MongoDB

Security is enforced at multiple layers:

- Authentication via JWT
- Authorization via RBAC
- Password hashing via bcrypt
- Data encryption via Fernet

---

## Security Features Implemented

### 1 JWT-Based Authentication

- Stateless authentication using JSON Web Tokens
- JWT contains user ID, role, and expiry timestamp
- All protected endpoints require a valid Bearer token
- Tokens are validated on every request

---

### 2 Role-Based Access Control (RBAC)

RBAC is enforced on the backend to ensure strict separation of privileges:

**Role - Permissions**

- Principal - Create and manage teachers
- Teacher - Create students, upload exam results, compare performance
- Parent - View only their own child’s profile and exam results

Unauthorized actions result in HTTP 403 Forbidden responses.

---

### 3 Password Hashing & Credential Security

- Plaintext password storage was removed
- Passwords are hashed using bcrypt via Passlib
- Only password_hash is stored in MongoDB
- Hash verification is used during login and password changes

This protects credentials even if the database is compromised.

---

### 4 Database Security – Field-Level Encryption

- Sensitive personal data (PII) is encrypted before storage
- Encryption implemented using Fernet (cryptography library)
- Encrypted fields include:
  - User full names
  - Student names
- Data is decrypted only when required for authorized responses

This ensures confidentiality even in the event of database access attacks.

---

## Testing & Validation

The application was tested using:

- Postman for functional and security testing
- Role-based testing to verify authorization enforcement
- Authentication tests to validate JWT protection
- Database inspection via MongoDB Compass to confirm:
  - Password hashing
  - Encrypted data storage

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (local)
- Git

---

## Backend Setup
- git clone https://github.com/satyavardhan912/schoolify.git
- cd schoolify
- pip install -r requirements.txt

Run the backend:
- uvicorn app.main:app --reload

Backend will run at:
- http://localhost:8000

Frontend Setup:
- cd FrontEnd
- npm install
- npm run dev

Frontend will run at:
- http://localhost:5173

Database Configuration:
- mongodb://localhost:27017/schoolify
Collections:
- users
- students
- exams

Seed / Test Credentials:
- A seed script is used to provision a principal account for testing.
- Principal Account: (we can change this)
- Email: principal@test.com
- Password: Principal@123

This account can be used in:
-  Postman
- Frontend login
- Video demonstration

-----------------------------------------------------------------------------------------------

Project Branches

| Branch                                                                           | Description                                      |
| --------------------------------------                                          | ------------------------------------------------ |
| `code-with-Vulnerabilities-(backend)`                                            | Initial vulnerable backend (baseline)            |
| `This-branch-is-with-security-updates-(only-backend)`                            | Backend with implemented security fixes          |
| `Complete-application-with-security-updates-(FrontEnd-and-backend)`              | Full application with frontend + secured backend |

--------------------------------------------------------------------------------------------------------------

Conclusion

Schoolify demonstrates how core web security principles can be practically applied to secure a real-world web application. Through the use of authentication, authorization, cryptography, and secure data handling, the project highlights the importance of integrating security throughout the software development lifecycle.


Academic Note

This project was developed as part of an academic assessment.
No AI tools were used to generate application code.
Security concepts were implemented manually to demonstrate understanding.
