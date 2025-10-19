import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import InterviewPage from './pages/InterviewPage';
import FeedbackPage from './pages/FeedbackPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        {/* Rute dinamis untuk sesi wawancara */}
        <Route path="/interview/:sessionId" element={<InterviewPage />} />

        {/* 🟢 PERBAIKAN KRITIS: Hapus ":sessionId" dari rute /feedback */}
        {/* Rute ini sekarang hanya membutuhkan path dasar '/feedback' */}
        <Route path="/feedback" element={<FeedbackPage />} />
      </Routes>
    </Router>
  );
}

export default App;
