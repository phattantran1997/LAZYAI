import { Routes, Route } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import UploadScreen from './UploadScreen'
import ChatScreen from './ChatScreen'
import MarkScreen from './MarkScreen'

const TeacherDashboard = () => {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <Routes>
          <Route path="upload" element={<UploadScreen />} />
          <Route path="chat" element={<ChatScreen />} />
          <Route path="mark" element={<MarkScreen />} />
          <Route path="*" element={<UploadScreen />} />
        </Routes>
      </main>
    </div>
  )
}

export default TeacherDashboard 