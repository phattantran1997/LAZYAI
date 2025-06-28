// src/App.tsx
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import LoginScreen from './screens/LoginScreen'
import RegisterScreen from './screens/RegisterScreen'
import TeacherDashboard from './screens/TeacherDashboard'
import StudentChatScreen from './screens/StudentChatScreen'
import ProtectedRouter from './components/ProtectedRouter'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginScreen />} />
          <Route path="/signup" element={<RegisterScreen />} />

          <Route 
            path="/teacher/*" 
            element={
              <ProtectedRouter requiredRole="Teachers">
                <TeacherDashboard />
              </ProtectedRouter>
            } 
          />
          <Route 
            path="/student" 
            element={
              <ProtectedRouter requiredRole="Students">
                <StudentChatScreen />
              </ProtectedRouter>
            } 
          />
          
          {/* Default route - redirect to login */}
          <Route path="/" element={<Navigate to="/login" />} />
          
          {/* Redirect to login if no route matches */}
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
