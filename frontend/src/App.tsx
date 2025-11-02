import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import Header from './components/Header';
import Home from './components/Home';
import Login from './components/Login';
import Profile from './components/Profile';
import Dashboard from './components/Dashboard';
import AdminPage from './components/AdminPage';
import Feedback from './components/Feedback';
import FeedbackPage from './components/FeedbackPage';
import AuthCallback from './components/AuthCallback';
import About from './components/About';
import Terms from './components/Terms';
import Privacy from './components/Privacy';
import Footer from './components/Footer';
import ChatButton from './components/ChatButton';
import BuildList from './components/BuildList';
import BuildDetail from './components/BuildDetail';
import BuildForm from './components/BuildForm';
import BuildTop from './components/BuildTop';
import { UserRole } from './types/user';

const AppContent: React.FC = () => {
  const { user } = useAuth();
  const isAdmin = user?.role === UserRole.ADMIN || user?.role === UserRole.SUPER_ADMIN;

  return (
    <div className="theme-transition min-h-screen flex flex-col bg-white dark:bg-gray-900">
      <Router>
        <Header />
        <main className="flex-1 pt-0">
          <Routes>
            <Route path="/auth/callback" element={<AuthCallback />} />
            <Route path="/home" element={<Home />} />
            <Route path="/login" element={user ? <Navigate to="/profile" /> : <Login />} />
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin" 
              element={
                <ProtectedRoute>
                  <AdminPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin/feedback" 
              element={
                <ProtectedRoute>
                  <Feedback />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/feedback" 
              element={<FeedbackPage />} 
            />
            <Route 
              path="/reviews" 
              element={<FeedbackPage />} 
            />
            {/* Роуты для сборок */}
            <Route path="/builds" element={<BuildList />} />
            <Route path="/builds/top" element={<BuildTop />} />
            <Route 
              path="/builds/create" 
              element={
                <ProtectedRoute>
                  <BuildForm />
                </ProtectedRoute>
              } 
            />
            <Route path="/builds/:id" element={<BuildDetail />} />
            <Route 
              path="/builds/:id/edit" 
              element={
                <ProtectedRoute>
                  <BuildForm />
                </ProtectedRoute>
              } 
            />
            <Route path="/about" element={<About />} />
            <Route path="/terms" element={<Terms />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route 
              path="/" 
              element={<Navigate to="/home" />} 
            />
          </Routes>
        </main>
        <Footer />
        {/* Кнопка чата - показывается только для обычных пользователей, не для администраторов */}
        {user && !isAdmin && <ChatButton />}
      </Router>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;



