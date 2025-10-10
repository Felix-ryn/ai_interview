// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import InterviewPage from './pages/InterviewPage';
import FeedbackPage from './pages/FeedbackPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        {/* Rute dinamis untuk sesi wawancara dan feedback */}
        <Route path="/interview/:sessionId" element={<InterviewPage />} />
        <Route path="/feedback/:sessionId" element={<FeedbackPage />} />
      </Routes>
    </Router>
  );
}

export default App;
