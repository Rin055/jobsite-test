# Django Job Platform

A full-stack Django application for job postings and applications with role-based permissions.

## Features

- User registration and authentication
- Role-based system: Employers and Job Seekers
- Employers can post, edit, and delete their own jobs
- Employers can view and manage applications for their jobs
- Job seekers can browse jobs and apply
- Job seekers can view their application status

## Setup

1. Install dependencies:

   ```bash
   pip install django
   ```

2. Run migrations:

   ```bash
   python manage.py migrate
   ```

3. Create superuser:

   ```bash
   python manage.py createsuperuser
   ```

4. Run the server:
   ```bash
   python manage.py runserver
   ```

## Models

- **Profile**: Extends User model with employer flag and company info
- **Job**: Job postings with title, description, company, location, salary
- **Application**: Job applications with cover letter and resume upload

## Views

- Job listing and detail views
- Job creation, editing, deletion (employers only)
- Application submission (job seekers only)
- Application management (employers only)
- User profile management

## Permissions

- Only employers can post/edit/delete jobs
- Only job owners can view applications for their jobs
- Employers cannot apply for jobs
- Users can only edit their own profile

## For Claude AI Design Instructions

Please design beautiful, modern, and responsive HTML/CSS templates for this Django job platform. The current templates use Bootstrap 5 and are functional but basic.

### Key Pages to Design:

1. **Home/Job List** (`jobs/job_list.html`)
   - Hero section with search
   - Job cards with company logos, salaries, locations
   - Filter sidebar (location, salary range, job type)
   - Pagination

2. **Job Detail** (`jobs/job_detail.html`)
   - Attractive job header with company info
   - Rich job description formatting
   - Apply button with call-to-action
   - Related jobs section

3. **Job Posting Form** (`jobs/job_form.html`)
   - Multi-step wizard or clean single form
   - Rich text editor for job description
   - Company logo upload
   - Preview functionality

4. **Application Form** (`jobs/apply.html`)
   - Professional application layout
   - Resume upload with drag-and-drop
   - Cover letter text area
   - Progress indicator

5. **Dashboard Views**
   - Employer dashboard with job stats
   - Job seeker dashboard with application tracking
   - Profile completion progress

6. **Authentication Pages** (`accounts/register.html`, `accounts/login.html`)
   - Modern login/register forms
   - Social login options (optional)
   - Role selection during registration

### Design Requirements:

- **Color Scheme**: Professional blue/white theme with accent colors
- **Typography**: Clean, readable fonts (Google Fonts)
- **Responsive**: Mobile-first design
- **Accessibility**: WCAG compliant
- **Performance**: Optimized images and CSS
- **User Experience**: Intuitive navigation, clear CTAs, loading states

### Technical Notes:

- Use Bootstrap 5 classes already included
- Maintain Django template syntax
- Add custom CSS in static files
- Include JavaScript for enhanced UX (optional)
- Use Font Awesome or similar for icons

### Prompt for Claude:

"Design beautiful, modern HTML templates for a Django job platform. The app has job listings, applications, and user roles (employers/job seekers). Current templates are basic Bootstrap. Make them stunning with modern UI/UX, responsive design, and professional appearance. Include all the existing Django template variables and form handling."
