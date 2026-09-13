import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import DashboardPage from './pages/DashboardPage'
import CasesListPage from './pages/CasesListPage'
import LoginPage from './pages/LoginPage'
import InvestigationGraphPage from './pages/InvestigationGraphPage'
import AIAssistantPage from './pages/AIAssistantPage'
import EvidencePage from './pages/EvidencePage'
import IOCAnalysisPage from './pages/IOCAnalysisPage'
import TimelinePage from './pages/TimelinePage'
import ReportsPage from './pages/ReportsPage'
import SettingsPage from './pages/SettingsPage'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="cases" element={<CasesListPage />} />
        <Route path="evidence" element={<EvidencePage />} />
        <Route path="ioc-analysis" element={<IOCAnalysisPage />} />
        <Route path="investigation-graph" element={<InvestigationGraphPage />} />
        <Route path="timeline" element={<TimelinePage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="ai-assistant" element={<AIAssistantPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      {/* Catch-all fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
