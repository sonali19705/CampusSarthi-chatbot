# Campus Sarthi Chatbot

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Issues](https://img.shields.io/github/issues/sonali19705/CampusSarthi-chatbot)](https://github.com/sonali19705/CampusSarthi-chatbot/issues)

---

## Overview
Campus Sarthi is a multilingual chatbot designed to assist students and faculty in navigating college-related queries.  
It provides instant answers about courses, faculty, library, exams, and general campus information, supporting multiple languages for inclusivity.

---

## Features
- Language-agnostic support (English, Hindi, Gujarati, etc.)
- Quick responses to frequently asked questions (FAQs)
- Admin interface for uploading PDFs and CSVs to update the knowledge base
- Interactive front-end with theme switching
- Real-time chat responses
- Easy integration with college websites

---

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** FastAPI (Python)
- **Database:** Chroma vector database for semantic search
- **Version Control:** GitHub

---

## How it Works

1. **User sends a query** through the chat interface.
2. **Frontend JavaScript** captures the message and sends it to the backend API.
3. **FastAPI backend** processes the query:
   - Checks the vector database (Chroma) for semantic matches.
   - Searches uploaded PDFs/CSVs for relevant answers.
4. **Response is sent back** to the frontend in real-time.
5. **User sees the answer** in the chat window.

## Project Structure
CampusSarthi-chatbot/
│
├── frontend/ # HTML, CSS, JS files
│ ├── index.html
│ ├── style.css
│ └── script.js
├── backend/ # FastAPI backend files
│ ├── main.py
│ └── utils.py
├── vector_db/ # Chroma vector DB for chatbot knowledge
├── uploads/ # PDFs and CSV files uploaded via admin
├── README.md # Project documentation
└── requirements.txt # Python dependencies

## Installation

1.Clone the repository:

git clone https://github.com/sonali19705/CampusSarthi-chatbot.git
# cd CampusSarthi-chatbot

2.Create a virtual environment and activate it:

python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

3.Install dependencies:

pip install -r requirements.txt

4.Run the backend:

uvicorn backend.main:app --reload

5.Open the frontend:

Open frontend/index.html in a web browser.

## Usage

Chat with Campus Sarthi through the web interface.

Admins can upload PDFs/CSVs to update the chatbot knowledge base.

Switch languages using the language selector in the chat interface.