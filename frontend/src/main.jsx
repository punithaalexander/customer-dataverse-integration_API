import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { AuthProvider } from 'react-oidc-context'
import './index.css'
import App from './App.jsx'

const cognitoAuthConfig = {
  authority:
    'https://cognito-idp.ap-southeast-2.amazonaws.com/ap-southeast-2_53vJA32mE',

  client_id:
    '5vturmag1k9k7c13gdbfb20o4h',

  redirect_uri:
    'http://localhost:5173',

  response_type:
    'code',

  scope:
    'openid email phone',
    
  onSigninCallback: () => {
    window.history.replaceState(
      {},
      document.title,
      window.location.pathname
    )
  },
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider {...cognitoAuthConfig}>
      <App />
    </AuthProvider>
  </StrictMode>,
)