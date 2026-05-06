import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import LeadProfile from './LeadProfile';

// Mock the router params
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ id: 'test-lead-id' })
  };
});

// Mock Firebase
vi.mock('../lib/firebase', () => ({
  db: {}
}));
vi.mock('firebase/firestore', () => ({
  doc: vi.fn(),
  collection: vi.fn(),
  onSnapshot: vi.fn(() => vi.fn()), // returns unsubscribe fn
  query: vi.fn(),
  orderBy: vi.fn()
}));

// Mock custom hooks
vi.mock('../hooks/useModule', () => ({
  useModule: () => ({
    mutateAsync: vi.fn(),
    isPending: false
  })
}));

describe('LeadProfile Component', () => {
  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <LeadProfile />
      </BrowserRouter>
    );
  };

  beforeEach(() => {
    // Mock the global fetch
    globalThis.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({}),
      })
    ) as any;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders the Lead Profile header', () => {
    renderComponent();
    expect(screen.getByRole('heading', { name: /Lead Profile/i })).toBeInTheDocument();
  });

  it('renders the navigation tabs', () => {
    renderComponent();
    expect(screen.getByRole('navigation', { name: /Lead profile tabs/i })).toBeInTheDocument();
    
    // Check for specific tabs
    expect(screen.getByText(/overview/i)).toBeInTheDocument();
    expect(screen.getByText(/history/i)).toBeInTheDocument();
    expect(screen.getByText(/optimizer/i)).toBeInTheDocument();
    expect(screen.getByText(/call briefs/i)).toBeInTheDocument();
  });

  it('renders the company overview by default', () => {
    renderComponent();
    expect(screen.getByRole('heading', { name: /Company Overview/i })).toBeInTheDocument();
  });
});
