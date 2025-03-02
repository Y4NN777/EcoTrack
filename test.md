EcoTrack - Waste Management System Documentation

Team Members and Contributions

Development Team: Triple A (Axel, Ali, Aslane)

DABO R Yanis Axel

Role: Full Stack Developer

Contributions:

Designed and implemented database models and relationships

Developed the authentication system with secure password hashing

Integrated admin functionality for system and user management

Implemented robust data validation to ensure data integrity

OUEDRAOGO Yanis Aslane & DABO R Yanis Axel

Roles: UI/UX Designer & Frontend Developer (Aslane) and Full Stack Developer (Axel)

Contributions:

Crafted user-friendly interface designs

Developed responsive templates

Integrated client-side validation for enhanced user experience

Implemented the user dashboard for streamlined navigation

GUISSOU Ali & DABO R Yanis Axel

Roles: Backend Developer (Ali) and Full Stack Developer (Axel)

Contributions:

Seamlessly integrated frontend and backend components

Developed a comprehensive reporting system

Created data visualization features for insightful analysis

Managed waste collection functionality

Authored technical documentation

Project Supervision

Instructor: Mr. Porgo

Course: Python Programming II

Software Overview

Purpose

EcoTrack is a web-based waste management system designed to streamline and enhance the management of waste collection activities. The platform enables organizations to monitor waste collection processes, schedule pickups, and generate basic performance reports, thereby promoting efficient resource utilization.

Features

1. User Management

Role-Based Access Control:

Administrator: Full system management and user control

Operator: Handles collection and scheduling tasks

Reporting User: Access to view and export reports

Secure Authentication: Password hashing for user accounts

User Profiles: Manage and update personal and role-specific details

2. Waste Collection Management

Data Recording:

Record waste types, quantities, collection dates, and locations

Track collection statuses

Data Management:

View, edit, and filter collection records

Basic sorting for efficient data handling

3. Schedule Management

Create and manage collection schedules

Assign teams to predefined routes

Monitor and update schedule statuses

View upcoming collection activities

4. Basic Reporting

Dashboard with collection statistics

Visual representation of waste type distribution

Export collection data in CSV format

Track basic performance metrics

Technical Implementation

Technology Stack

Backend: Python 3.12 with Flask

Database: SQLite managed through SQLAlchemy

Frontend:

HTML5, CSS, Bootstrap 5

JavaScript

Chart.js for data visualization

SweetAlert2 for interactive notifications

Project Structure

wms/
├── app.py                 # Application configuration and initialization
├── routes.py              # Main route handlers
├── models.py              # Database models
├── requirements.txt       # Project dependencies
│
├── blueprints/            # Feature modules
│   ├── admin.py           # Admin functionality
│   ├── auth.py            # Authentication
│   ├── operator.py        # Collection operations
│   └── reporting.py       # Basic reporting
│
├── static/                # Static assets
│   ├── css/
│   │   └── styles.css    # Custom styling
│   └── js/
│       └── main.js       # Core JavaScript
│
├── templates/             # HTML templates
│   ├── admin/             # Admin interface
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   └── waste_types.html
│   ├── operator/          # Operator interface
│   │   ├── collections.html
│   │   └── schedules.html
│   ├── reporting/         # Reporting interface
│   │   ├── dashboard.html
│   │   └── reports.html
│   └── auth/              # Authentication
│       ├── login.html
│       └── register.html
│
└── instance/              # Instance data
    ├── wms.db             # SQLite database with initial data
    └── reports/           # Directory for CSV report files

Database Models

User

Fields:

Username

Password

Email and personal information

Role-based access level

Account status

WasteType

Fields:

Name

Description

Disposal method

Timestamp for creation

Collection

Fields:

Waste type reference

Quantity collected

Collection date

Location

Status tracking

Schedule

Fields:

Route information

Pickup date

Team assignment

Status tracking

Report

Fields:

Report type

Time period

Format (e.g., CSV)

Generation timestamp

Setup Guide

Prerequisites

Python 3.12 installed

pip package manager

A web browser (Chrome or Firefox recommended)

Installation Steps

Set Up the Python Environment

python -m venv venv
venv\Scripts\activate

Install Dependencies

pip install -r requirements.txt

Initialize the Database

flask db upgrade

Note: This step is optional as the database includes pre-configured data:

Admin, operator, and reporting user credentials

Initial waste types

Sample collections and schedules

Run the Application

flask run

Usage Guide

Administrator Functions

Manage user accounts and assign roles

Configure waste types and disposal methods

Update system settings

Operator Functions

Log and update waste collections

Manage collection schedules and team assignments

Monitor task progress

Reporting Functions

Access visual dashboards

Export data in CSV format

Analyze waste distribution and performance metrics

Security Features

Password hashing for user credentials

Role-based access control for secure data segregation

Form validation to prevent invalid submissions

CSRF protection for enhanced security

Session management to protect user sessions

Known Limitations

Reporting capabilities are limited to basic statistics

Lack of advanced analytics or machine learning features

Limited data visualization options

Single database backend support

No API endpoints for external integrations

Technical Notes and Known Issues

JavaScript Chart Implementation

Inline JavaScript is used to integrate Flask template variables directly into charts.

This method causes syntax warnings in some IDEs but does not affect functionality.

Example:

<script>
  const data = {{ chart_data|tojson|safe }};
  // Initialize chart
</script>

Future improvements may include external JavaScript files and API data fetching.

Browser Console Warnings

Console warnings due to template syntax do not impact performance or functionality.

Complexity and Demonstrated Skills

Software Complexity

EcoTrack represents a medium-to-high complexity project for a team of students, requiring:

A well-designed architecture integrating multiple layers of functionality

Role-based access control ensuring secure, tiered access to features

Dynamic front-end interactions synchronized with real-time data from the backend

Reporting and visualization modules that present critical data insights effectively

The project’s complexity arises from:

Integrating diverse technologies such as Flask, SQLite, and Chart.js

Balancing simplicity and functionality within tight development timelines

Handling multiple roles and workflows (admin, operator, reporter)

Demonstrated Skills

The development of EcoTrack highlighted several technical and non-technical skills:

Technical Skills

Backend Development: Proficient use of Flask for routing, database management with SQLAlchemy, and implementing robust authentication mechanisms.

Frontend Development: Expertise in creating responsive and user-friendly interfaces using HTML5, CSS, Bootstrap 5, and JavaScript.

Data Visualization: Implementing real-time dashboards and interactive charts with Chart.js.

Database Management: Structuring complex relational models and ensuring data integrity.

Security: Employing password hashing, CSRF protection, and secure session management.

Non-Technical Skills

Collaboration: Coordination among team members to seamlessly integrate frontend and backend functionalities.

Time Management: Delivering a functional prototype within limited timeframes.

Problem-Solving: Addressing challenges such as template-variable integration with inline JavaScript and ensuring real-time updates.

Documentation: Providing clear and comprehensive documentation for future scalability and maintainability.

These skills collectively demonstrate the team’s readiness for tackling real-world software development projects with a focus on problem-solving, collaboration, and adaptability.
