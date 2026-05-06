import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import PrivateRoute from '../PrivateRoute'

const mockUseAuth = vi.fn()

vi.mock('../../context/AuthContext', () => ({
  useAuth: () => mockUseAuth(),
}))

describe('PrivateRoute', () => {
  it('shows a loading state while authentication is being resolved', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      token: null,
      isLoading: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    render(
      <MemoryRouter>
        <PrivateRoute />
      </MemoryRouter>,
    )

    expect(screen.getByText('Laden...')).toBeInTheDocument()
  })

  it('redirects to /login when no user is authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      token: null,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    })

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route path="/dashboard" element={<PrivateRoute />}>
            <Route index element={<div>Protected Dashboard</div>} />
          </Route>
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByText('Login Page')).toBeInTheDocument()
    expect(screen.queryByText('Protected Dashboard')).not.toBeInTheDocument()
  })
})
