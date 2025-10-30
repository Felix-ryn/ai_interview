import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import InterviewPage from './pages/InterviewPage';
import FeedbackPage from './pages/FeedbackPage';

function App() {
  return (
    <Router>
      {/* 🟢 HANYA ROUTES DI SINI. HomePage akan menyediakan styling min-h-screen. */}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/interview/:sessionId" element={<InterviewPage />} />
        <Route path="/feedback" element={<FeedbackPage />} />
      </Routes>
    </Router>
  );
}

export default App;