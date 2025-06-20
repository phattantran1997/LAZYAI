import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LoginScreen from './screens/LoginScreen'
import TeacherDashboard from './screens/TeacherDashboard'
import StudentChatScreen from './screens/StudentChatScreen'
import { AuthProvider } from './contexts/AuthContext'
import RegisterScreen from './screens/RegisterScreen'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginScreen />} />
          <Route path="/signup" element={<RegisterScreen />} />
          <Route path="/teacher/*" element={<TeacherDashboard />} />
          <Route path="/student" element={<StudentChatScreen />} />
          {/* <Route path="/chat/:teacherId" element={<StudentChatScreen />} /> */}
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App 