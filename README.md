# Smart Book Library

Smart Book Library is a web application built with **FastAPI** that allows users to read books online, maintain personal libraries, and interact with **AI-powered assistants**. The platform combines a digital library with intelligent Q&A bots to make book discovery and reading more interactive.

## Features
- **Read books online** – Clean, distraction-free interface.  
- **Personal library** – Save and track your favorite books.  
- **Title-based search** – Quickly find books by name.  
- **Book-specific AI bot** – Ask questions, get summaries, or clarify content instantly.  
- **Global AI assistant** – Discover new books with AI-powered recommendations.  

## Tech Stack
- **Backend:** FastAPI  
- **Database:** SQLite with SQLAlchemy and Alembic  
- **AI Integration:** LangChain  
- **Task Queue:** Celery with Redis (for background processing)  
- **Authentication:** JWT-based with role-based access control  
- **Testing:** Unit and integration tests with Pytest  

## Installation
```bash
git clone https://github.com/your-username/smart-book-library.git
cd smart-book-library
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
