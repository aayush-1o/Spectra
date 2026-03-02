/**
 * Spectra — App Router
 * Defines all client-side routes using React Router v6.
 */

import { BrowserRouter, Route, Routes } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        {/* Additional routes added in Phase 4:
            /map       → MapPage
            /graph     → GraphPage
            /anomalies → AnomaliesPage
            /search    → SearchPage
            /about     → AboutPage (Ethics)
        */}
      </Routes>
    </BrowserRouter>
  )
}
