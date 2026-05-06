import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import Login from '../Login'

const mockNavigate = vi.fn()
const mockLogin = vi.fn()
const mockLoginUser = vi.fn()
const mockRegisterUser = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>(
    'react-router-dom',
  )
  return { ...actual, useNavigate: () => mockNavigate }
})

vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ login: mockLogin }),
}))

vi.mock('../../api/client', () => ({
  loginUser: (...args: unknown[]) => mockLoginUser(...args),
  registerUser: (...args: unknown[]) => mockRegisterUser(...args),
}))

function renderLogin() {
  return render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>,
  )
}

describe('Login page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the login form by default without the email field', () => {
    renderLogin()
    expect(
      screen.getByRole('heading', { name: 'Anmeldung' }),
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Benutzername')).toBeInTheDocument()
    expect(screen.getByLabelText('Passwort')).toBeInTheDocument()
    expect(screen.queryByLabelText('E-Mail')).not.toBeInTheDocument()
  })

  it('switches to register mode and reveals the email field', async () => {
    const user = userEvent.setup()
    renderLogin()

    await user.click(screen.getByRole('button', { name: 'Registrieren' }))

    expect(
      screen.getByRole('heading', { name: 'Konto erstellen' }),
    ).toBeInTheDocument()
    expect(screen.getByLabelText('E-Mail')).toBeInTheDocument()
  })

  it('submits credentials, stores the token and navigates home on success', async () => {
    const user = userEvent.setup()
    mockLoginUser.mockResolvedValue({
      access_token: 'tok-123',
      user: { id: 1, username: 'eugen', email: 'e@x.de', role: 'admin' },
    })

    renderLogin()

    await user.type(screen.getByLabelText('Benutzername'), 'eugen')
    await user.type(screen.getByLabelText('Passwort'), 'secret123')
    await user.click(screen.getByRole('button', { name: 'Anmelden' }))

    expect(mockLoginUser).toHaveBeenCalledWith('eugen', 'secret123')
    expect(mockLogin).toHaveBeenCalledWith('tok-123', {
      id: 1,
      username: 'eugen',
      email: 'e@x.de',
      role: 'admin',
    })
    expect(mockNavigate).toHaveBeenCalledWith('/')
  })
})
