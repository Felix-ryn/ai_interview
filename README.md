# 🤖 AI Interviewer: Intelligent Mock Interview Platform

**AI Interviewer** adalah platform simulasi wawancara kerja berbasis Kecerdasan Buatan (AI). Sistem ini membantu kandidat berlatih dengan memberikan pertanyaan dinamis, melakukan penilaian objektif menggunakan NLP, serta menghasilkan umpan balik mendalam berbasis kompetensi.

---

## ✨ Fitur Utama

### 🧠 Core AI & NLP (Backend)
- **Dynamic Question Generation**  
  Menghasilkan pertanyaan wawancara secara otomatis sesuai konteks.

- **AI Scoring System**  
  Menghitung skor berdasarkan rubrik penilaian melalui `ai_scoring_service.py`.

- **Narrative Feedback**  
  Memberikan saran perbaikan dalam bentuk narasi yang personal dan kontekstual.

- **NLP Processor**  
  Menganalisis kualitas jawaban pengguna menggunakan Natural Language Processing.

---

### 💻 Interactive Dashboard (Frontend)
- **Interview Session Management**  
  Pengalaman wawancara yang interaktif dengan *Progress Indicator*.

- **Detailed Feedback Visuals**  
  Menampilkan *ScoreCard*, *Narrative Feedback*, dan *Detailed Rubric*.

- **Real-time Tips**  
  Memberikan tips selama sesi wawancara berlangsung (*TipBox*).

- **Modern UI**  
  Dibangun dengan arsitektur komponen modular menggunakan React.

---

## 🛠️ Tech Stack

### Frontend
- React.js (Vite)
- Tailwind CSS / PostCSS
- Lucide React
- Axios

### Backend (ML & API)
- Python (FastAPI)
- LLM Integration (Gemini / OpenAI)
- NLP Libraries (spaCy / NLTK)
- Pydantic
---

## 🗂️ Struktur Proyek

### 📁 Frontend (`ai_interview_frontend`)
```text
├── src/
│   ├── components/
│   │   ├── common/      # Reusable UI (Button, Dropdown, dll)
│   │   ├── feedback/    # ScoreCard, Rubric, Narrative
│   │   └── interview/   # QuestionCard & TipBox
│   ├── hooks/           # Logic reusable (useInterviewSession.js)
│   ├── pages/           # HomePage, InterviewPage, FeedbackPage
│   └── services/        # Integrasi API (api.js)
📁 Backend (backend-ml)
├── app/
│   ├── api/             # Endpoint & Controller
│   ├── core/            # NLP Processor, LLM Service, Question Generator
│   ├── models/          # Pydantic Models & Schema
│   ├── helpers/         # Utility & Scoring Calculator
│   └── services/        # Business Logic (Scoring & Assessment)
```
⚙️ Instalasi & Setup
1. Backend Setup
```
cd backend-ml
pip install -r requirements.txt
```
# Pastikan API Key LLM sudah diset di environment
```
python main.py
```
2. Frontend Setup
```
cd ai_interview_frontend
npm install
npm run dev
```
📊 Alur Kerja Sistem
User memulai sesi di HomePage
Backend menghasilkan pertanyaan melalui question_generator.py
User menjawab pertanyaan
Jawaban dianalisis oleh nlp_processor.py
AI Scoring Service menghitung nilai menggunakan scoring_matrix.py
Hasil ditampilkan di FeedbackPage berupa:
Score
Rubric Detail
Narrative Feedback
📌 Analisis Arsitektur
1. Separation of Concerns

Struktur frontend sudah sangat baik dengan pemisahan:
common → reusable component
dfeedback → hasil evaluasi
dinterview → flow utama

2. Backend Architecture

core → logika berat (NLP, LLM, Question Generator)
dservices → business logic

3. Scalability

Struktur ini:
Mudah dikembangkanMudah ditambah fitur AI baruSiap untuk deployment skala besar
