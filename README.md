# Automated Onboarding System

The **Automated Onboarding System** is a web-based application designed to streamline the candidate onboarding process. This system allows HR teams to upload scanned forms (PDF or image), extract relevant details from them using Optical Character Recognition (OCR), and automatically store the extracted data in a MongoDB database. The aim of this project is to automate the time-consuming manual data entry and improve the overall efficiency of managing candidate records.

## Features

- **File Upload Interface**: Allows HR teams to upload scanned forms (images or PDFs).
- **OCR for Text Extraction**: Uses Tesseract OCR to extract text from scanned forms.
- **Database Integration**: Automatically stores extracted data in a MongoDB database.
- **Candidate Record Management**: Enables HR teams to view and search for candidate records.
- **Search and Filter**: HR teams can search candidates by name or email to view records.
- **Cloud Deployment**: The system will be deployed on Google Cloud Platform (GCP) with MongoDB Atlas for database hosting.

## Tech Stack

- **Frontend**: 
  - ReactJS for building the dynamic user interface.
  - Tailwind CSS for styling the UI components.
  - React-dropzone for the file upload component.
  
- **Backend**:
  - Django as the backend framework.
  - Django REST Framework (DRF) for building APIs.
  - Python libraries: 
    - **Pillow** and **PyPDF2** or **pdfminer.six** for processing image/PDF files.
    - **Tesseract OCR** (via Pytesseract) for text extraction from scanned forms.
  
- **Database**:
  - MongoDB for data storage.
  - MongoDB Compass (local development) and MongoDB Atlas (for deployment).

- **Authentication**:
  - JWT (JSON Web Tokens) for secure user authentication.

- **Deployment**:
  - Google Cloud Platform (GCP) for cloud hosting.
  - Docker (optional) for containerizing the backend for easy deployment.

## Getting Started

### Prerequisites

Before you can start using this system, ensure that you have the following installed:

- Python 3.8+
- Node.js 16+ (for React)
- MongoDB Compass (for local development) or MongoDB Atlas (for cloud deployment)
- Google Cloud Platform account (for deployment)
- Docker (optional, for containerization)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/automated-onboarding-system.git
   cd automated-onboarding-system
