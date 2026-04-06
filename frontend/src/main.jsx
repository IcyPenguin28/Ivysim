import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { PlayerTeamProvider } from './contexts/PlayerTeamContext.jsx'
import './css/index.css'
import App from './App.jsx'
import { OptionsProvider } from './contexts/OptionsContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <PlayerTeamProvider>
        <OptionsProvider>
          <App/>
        </OptionsProvider>
      </PlayerTeamProvider>
    </BrowserRouter>
  </StrictMode>,
)
