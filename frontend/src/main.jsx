import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

import "./styles/globals.css";
import "./styles/navbar.css";
import "./styles/hero.css";
import "./styles/upload.css";
import "./styles/cards.css";
import "./styles/results.css";
import "./styles/animations.css";
import "./styles/responsive.css";

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
