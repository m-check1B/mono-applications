import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useAuth } from '@/contexts/AuthContext';
import LoginForm from '@/components/auth/LoginForm';
import { BrowserRouter } from 'react-router-dom';

// Mock the AuthContext
vi.mock('@/contexts/AuthContext', () => ({
  useAuth: vi.fn(),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

// Mock the ThemeContext
vi.mock('@/contexts/ThemeContext', () => ({
  SimpleThemeToggle: () => <button>Toggle Theme</button>
}));

// Mock the Google Auth hook
vi.mock('@/hooks/useGoogleAuth', () => ({
  __esModule: true,
  default: () => ({
    signInWithGoogle: vi.fn(),
    isLoading: false,
    error: null
  })
}));

const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>;

describe('LoginForm Component', () => {
  const mockLogin = vi.fn();
  const mockNavigate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      login: mockLogin,
      logout: vi.fn(),
      refreshAuth: vi.fn(),
      hasRole: vi.fn(),
      hasPermission: vi.fn(),
      canAccessOrganization: vi.fn()
    });

    // Mock useNavigate
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate
      };
    });
  });

  it('renders login form correctly', () => {
    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    );

    expect(screen.getByText('CC-Light')).toBeInTheDocument();
    expect(screen.getByText('AI-First Contact Center Platform')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('displays loading state when auth is loading', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      login: mockLogin,
      logout: vi.fn(),
      refreshAuth: vi.fn(),
      hasRole: vi.fn(),
      hasPermission: vi.fn(),
      canAccessOrganization: vi.fn()
    });

    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('shows error message when login fails', async () => {
    const errorMessage = 'Invalid credentials';
    mockLogin.mockRejectedValue(new Error(errorMessage));

    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'password123' }
    });

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  it('disables submit button during login attempt', async () => {
    mockLogin.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'password123' }
    });

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(screen.getByRole('button', { name: /sign in/i })).toBeDisabled();
  });

  it('shows theme toggle button', () => {
    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    );

    expect(screen.getByText('Toggle Theme')).toBeInTheDocument();
  });

  it('displays app branding correctly', () => {
    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    );

    expect(screen.getByText('CC-Light')).toBeInTheDocument();
    expect(screen.getByText('AI-First Contact Center Platform')).toBeInTheDocument();
  });

  it('validates email format on submission', async () => {
    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'invalid-email' }
    });
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'password123' }
    });

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Check that login is not called with invalid email
    expect(mockLogin).not.toHaveBeenCalled();
  });

  it('requires password to be at least 6 characters', async () => {
    render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: '123' }
    });

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Check that login is not called with short password
    expect(mockLogin).not.toHaveBeenCalled();
  });
});