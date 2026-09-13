import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import DashboardPage from './pages/DashboardPage'
import CasesListPage from './pages/CasesListPage'
import LoginPage from './pages/LoginPage'
import InvestigationGraphPage from './pages/InvestigationGraphPage'
import AIAssistantPage from './pages/AIAssistantPage'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="cases" element={<CasesListPage />} />
        <Route path="investigation-graph" element={<InvestigationGraphPage />} />
        <Route path="ai-assistant" element={<AIAssistantPage />} />
      </Route>
    </Routes>
  )
}

export default App
