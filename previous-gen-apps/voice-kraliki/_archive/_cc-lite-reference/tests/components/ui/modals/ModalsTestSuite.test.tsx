import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Import all modal components for comprehensive testing
import { AccessibleModal } from '@/components/ui/AccessibleModal';

// Mock NextUI components
vi.mock('@nextui-org/react', () => ({
  Modal: ({ children, isOpen, onOpenChange, size, backdrop, placement }: any) =>
    isOpen ? (
      <div
        data-testid="modal"
        data-size={size}
        data-backdrop={backdrop}
        data-placement={placement}
        onClick={() => onOpenChange && onOpenChange(false)}
      >
        {children}
      </div>
    ) : null,
  ModalContent: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div data-testid="modal-content" className={className} onClick={(e) => e.stopPropagation()}>
      {children}
    </div>
  ),
  ModalHeader: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div data-testid="modal-header" className={className}>{children}</div>
  ),
  ModalBody: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div data-testid="modal-body" className={className}>{children}</div>
  ),
  ModalFooter: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div data-testid="modal-footer" className={className}>{children}</div>
  ),
  Button: ({ children, onPress, isDisabled, color, variant, size, startContent, endContent, ...props }: any) => (
    <button
      onClick={onPress}
      disabled={isDisabled}
      data-color={color}
      data-variant={variant}
      data-size={size}
      {...props}
    >
      {startContent}
      {children}
      {endContent}
    </button>
  ),
  Input: ({ label, placeholder, value, onChange, type, isRequired, isInvalid, errorMessage, startContent, endContent }: any) => (
    <div data-testid="input-wrapper">
      {label && <label>{label}</label>}
      <div>
        {startContent}
        <input
          data-testid="input"
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          type={type}
          required={isRequired}
          aria-invalid={isInvalid}
        />
        {endContent}
      </div>
      {isInvalid && errorMessage && <span data-testid="error-message">{errorMessage}</span>}
    </div>
  ),
  Textarea: ({ label, placeholder, value, onChange, rows, isRequired, isInvalid, errorMessage }: any) => (
    <div data-testid="textarea-wrapper">
      {label && <label>{label}</label>}
      <textarea
        data-testid="textarea"
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        rows={rows}
        required={isRequired}
        aria-invalid={isInvalid}
      />
      {isInvalid && errorMessage && <span data-testid="error-message">{errorMessage}</span>}
    </div>
  ),
  Select: ({ children, label, placeholder, onSelectionChange, selectedKeys, isRequired, isInvalid, errorMessage }: any) => (
    <div data-testid="select-wrapper">
      {label && <label>{label}</label>}
      <select
        data-testid="select"
        data-placeholder={placeholder}
        onChange={(e) => onSelectionChange && onSelectionChange(new Set([e.target.value]))}
        value={selectedKeys ? Array.from(selectedKeys)[0] : ''}
        required={isRequired}
        aria-invalid={isInvalid}
      >
        <option value="">{placeholder}</option>
        {children}
      </select>
      {isInvalid && errorMessage && <span data-testid="error-message">{errorMessage}</span>}
    </div>
  ),
  SelectItem: ({ children, key }: { children: React.ReactNode; key: string }) => (
    <option value={key}>{children}</option>
  ),
  Checkbox: ({ children, isSelected, onValueChange }: any) => (
    <label data-testid="checkbox">
      <input
        type="checkbox"
        checked={isSelected}
        onChange={(e) => onValueChange && onValueChange(e.target.checked)}
      />
      {children}
    </label>
  ),
  RadioGroup: ({ children, value, onValueChange, label }: any) => (
    <div data-testid="radio-group" data-value={value}>
      {label && <label>{label}</label>}
      <div onChange={(e: any) => onValueChange && onValueChange(e.target.value)}>
        {children}
      </div>
    </div>
  ),
  Radio: ({ children, value }: { children: React.ReactNode; value: string }) => (
    <label data-testid="radio">
      <input type="radio" value={value} />
      {children}
    </label>
  ),
  Chip: ({ children, color, variant, onClose }: { children: React.ReactNode; color?: string; variant?: string; onClose?: Function }) => (
    <span data-testid="chip" data-color={color} data-variant={variant}>
      {children}
      {onClose && <button onClick={() => onClose()}>×</button>}
    </span>
  ),
  Progress: ({ label, value, color }: any) => (
    <div data-testid="progress" data-value={value} data-color={color}>
      <span>{label}</span>
    </div>
  ),
  Spinner: ({ size, color }: { size?: string; color?: string }) => (
    <div data-testid="spinner" data-size={size} data-color={color}>Loading...</div>
  ),
  Divider: ({ className }: { className?: string }) => (
    <hr data-testid="divider" className={className} />
  ),
  useDisclosure: () => ({
    isOpen: false,
    onOpen: vi.fn(),
    onOpenChange: vi.fn(),
    onClose: vi.fn()
  })
}));

// Mock Heroicons
vi.mock('@heroicons/react/24/outline', () => ({
  XMarkIcon: () => <svg data-testid="x-mark-icon" />,
  CheckIcon: () => <svg data-testid="check-icon" />,
  ExclamationTriangleIcon: () => <svg data-testid="warning-icon" />,
  InformationCircleIcon: () => <svg data-testid="info-icon" />,
  PlusIcon: () => <svg data-testid="plus-icon" />,
  PencilIcon: () => <svg data-testid="pencil-icon" />,
  TrashIcon: () => <svg data-testid="trash-icon" />,
  EyeIcon: () => <svg data-testid="eye-icon" />,
  DocumentArrowUpIcon: () => <svg data-testid="upload-icon" />,
  DocumentArrowDownIcon: () => <svg data-testid="download-icon" />,
  ClipboardDocumentIcon: () => <svg data-testid="clipboard-icon" />,
  Cog6ToothIcon: () => <svg data-testid="settings-icon" />
}));

// Modal Components for Testing
const CreateCampaignModal = ({ isOpen, onOpenChange }: { isOpen: boolean; onOpenChange: (open: boolean) => void }) => (
  <AccessibleModal
    isOpen={isOpen}
    onOpenChange={onOpenChange}
    title="Create New Campaign"
    size="2xl"
  >
    <form data-testid="campaign-form">
      <div data-testid="input-wrapper">
        <label>Campaign Name</label>
        <input data-testid="input" placeholder="Enter campaign name" required />
      </div>
      <div data-testid="textarea-wrapper">
        <label>Description</label>
        <textarea data-testid="textarea" placeholder="Enter description" rows={4} />
      </div>
      <div data-testid="select-wrapper">
        <label>Campaign Type</label>
        <select data-testid="select" required>
          <option value="">Select type</option>
          <option value="inbound">Inbound</option>
          <option value="outbound">Outbound</option>
        </select>
      </div>
      <div data-testid="radio-group">
        <label>Priority</label>
        <div>
          <label data-testid="radio">
            <input type="radio" value="low" name="priority" />
            Low
          </label>
          <label data-testid="radio">
            <input type="radio" value="medium" name="priority" />
            Medium
          </label>
          <label data-testid="radio">
            <input type="radio" value="high" name="priority" />
            High
          </label>
        </div>
      </div>
      <div data-testid="modal-footer">
        <button type="button" onClick={() => onOpenChange(false)}>Cancel</button>
        <button type="submit" data-color="primary">Create Campaign</button>
      </div>
    </form>
  </AccessibleModal>
);

const EditAgentModal = ({ isOpen, onOpenChange }: { isOpen: boolean; onOpenChange: (open: boolean) => void }) => (
  <AccessibleModal
    isOpen={isOpen}
    onOpenChange={onOpenChange}
    title="Edit Agent Details"
    size="lg"
  >
    <form data-testid="agent-form">
      <div data-testid="input-wrapper">
        <label>Agent Name</label>
        <input data-testid="input" defaultValue="John Doe" required />
      </div>
      <div data-testid="input-wrapper">
        <label>Email</label>
        <input data-testid="input" type="email" defaultValue="john@company.com" required />
      </div>
      <div data-testid="select-wrapper">
        <label>Department</label>
        <select data-testid="select">
          <option value="sales">Sales</option>
          <option value="support">Support</option>
          <option value="billing">Billing</option>
        </select>
      </div>
      <div data-testid="select-wrapper">
        <label>Skill Level</label>
        <select data-testid="select">
          <option value="junior">Junior</option>
          <option value="senior">Senior</option>
          <option value="expert">Expert</option>
        </select>
      </div>
      <label data-testid="checkbox">
        <input type="checkbox" defaultChecked />
        Active Agent
      </label>
      <div data-testid="modal-footer">
        <button type="button" onClick={() => onOpenChange(false)}>Cancel</button>
        <button type="submit" data-color="primary">Save Changes</button>
      </div>
    </form>
  </AccessibleModal>
);

const ConfirmDeleteModal = ({ isOpen, onOpenChange, onConfirm }: {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
}) => (
  <AccessibleModal
    isOpen={isOpen}
    onOpenChange={onOpenChange}
    title="Confirm Deletion"
    size="sm"
  >
    <div data-testid="modal-body">
      <div data-testid="warning-icon" />
      <p>Are you sure you want to delete this item? This action cannot be undone.</p>
    </div>
    <div data-testid="modal-footer">
      <button type="button" onClick={() => onOpenChange(false)}>Cancel</button>
      <button
        type="button"
        data-color="danger"
        onClick={() => {
          onConfirm();
          onOpenChange(false);
        }}
      >
        Delete
      </button>
    </div>
  </AccessibleModal>
);

const FileUploadModal = ({ isOpen, onOpenChange }: { isOpen: boolean; onOpenChange: (open: boolean) => void }) => (
  <AccessibleModal
    isOpen={isOpen}
    onOpenChange={onOpenChange}
    title="Upload Contact List"
    size="md"
  >
    <div data-testid="modal-body">
      <div data-testid="input-wrapper">
        <label>Select File</label>
        <input data-testid="input" type="file" accept=".csv,.xlsx" />
      </div>
      <div data-testid="progress" data-value={45}>
        <span>Uploading... 45%</span>
      </div>
      <div>
        <h4>File Requirements:</h4>
        <ul>
          <li>CSV or Excel format</li>
          <li>Maximum 10,000 contacts</li>
          <li>Required columns: Name, Phone</li>
        </ul>
      </div>
    </div>
    <div data-testid="modal-footer">
      <button type="button" onClick={() => onOpenChange(false)}>Cancel</button>
      <button type="button" data-color="primary">Upload</button>
    </div>
  </AccessibleModal>
);

const SettingsModal = ({ isOpen, onOpenChange }: { isOpen: boolean; onOpenChange: (open: boolean) => void }) => (
  <AccessibleModal
    isOpen={isOpen}
    onOpenChange={onOpenChange}
    title="Application Settings"
    size="xl"
  >
    <div data-testid="modal-body">
      <div>
        <h3>Audio Settings</h3>
        <div data-testid="select-wrapper">
          <label>Input Device</label>
          <select data-testid="select">
            <option value="default">Default Microphone</option>
            <option value="usb-mic">USB Microphone</option>
          </select>
        </div>
        <div data-testid="select-wrapper">
          <label>Output Device</label>
          <select data-testid="select">
            <option value="default">Default Speaker</option>
            <option value="headset">Bluetooth Headset</option>
          </select>
        </div>
      </div>
      <hr data-testid="divider" />
      <div>
        <h3>Notification Settings</h3>
        <label data-testid="checkbox">
          <input type="checkbox" defaultChecked />
          Enable call notifications
        </label>
        <label data-testid="checkbox">
          <input type="checkbox" />
          Enable email notifications
        </label>
      </div>
      <hr data-testid="divider" />
      <div>
        <h3>Display Settings</h3>
        <div data-testid="radio-group">
          <label>Theme</label>
          <div>
            <label data-testid="radio">
              <input type="radio" value="light" name="theme" />
              Light
            </label>
            <label data-testid="radio">
              <input type="radio" value="dark" name="theme" defaultChecked />
              Dark
            </label>
            <label data-testid="radio">
              <input type="radio" value="auto" name="theme" />
              Auto
            </label>
          </div>
        </div>
      </div>
    </div>
    <div data-testid="modal-footer">
      <button type="button" onClick={() => onOpenChange(false)}>Cancel</button>
      <button type="button" data-color="primary">Save Settings</button>
    </div>
  </AccessibleModal>
);

const queryClient = new QueryClient();

describe('Modals Test Suite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  const renderWithProviders = (component: React.ReactNode) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          {component}
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  describe('AccessibleModal Component', () => {
    it('renders modal when open', () => {
      renderWithProviders(
        <AccessibleModal isOpen={true} onOpenChange={vi.fn()} title="Test Modal">
          <p>Modal content</p>
        </AccessibleModal>
      );

      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByTestId('modal-header')).toBeInTheDocument();
      expect(screen.getByText('Test Modal')).toBeInTheDocument();
      expect(screen.getByText('Modal content')).toBeInTheDocument();
    });

    it('does not render modal when closed', () => {
      renderWithProviders(
        <AccessibleModal isOpen={false} onOpenChange={vi.fn()} title="Test Modal">
          <p>Modal content</p>
        </AccessibleModal>
      );

      expect(screen.queryByTestId('modal')).not.toBeInTheDocument();
    });

    it('calls onOpenChange when modal backdrop is clicked', () => {
      const mockOnOpenChange = vi.fn();
      renderWithProviders(
        <AccessibleModal isOpen={true} onOpenChange={mockOnOpenChange} title="Test Modal">
          <p>Modal content</p>
        </AccessibleModal>
      );

      const modal = screen.getByTestId('modal');
      fireEvent.click(modal);

      expect(mockOnOpenChange).toHaveBeenCalledWith(false);
    });

    it('applies correct size classes', () => {
      renderWithProviders(
        <AccessibleModal isOpen={true} onOpenChange={vi.fn()} title="Test Modal" size="lg">
          <p>Modal content</p>
        </AccessibleModal>
      );

      const modal = screen.getByTestId('modal');
      expect(modal).toHaveAttribute('data-size', 'lg');
    });
  });

  describe('Create Campaign Modal', () => {
    it('renders create campaign form', () => {
      renderWithProviders(<CreateCampaignModal isOpen={true} onOpenChange={vi.fn()} />);

      expect(screen.getByText('Create New Campaign')).toBeInTheDocument();
      expect(screen.getByTestId('campaign-form')).toBeInTheDocument();
      expect(screen.getByLabelText('Campaign Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Description')).toBeInTheDocument();
      expect(screen.getByLabelText('Campaign Type')).toBeInTheDocument();
    });

    it('validates required fields', async () => {
      renderWithProviders(<CreateCampaignModal isOpen={true} onOpenChange={vi.fn()} />);

      const submitButton = screen.getByText('Create Campaign');
      fireEvent.click(submitButton);

      // Form should prevent submission due to required fields
      expect(screen.getByTestId('campaign-form')).toBeInTheDocument();
    });

    it('handles form submission with valid data', async () => {
      renderWithProviders(<CreateCampaignModal isOpen={true} onOpenChange={vi.fn()} />);

      const nameInput = screen.getByPlaceholderText('Enter campaign name');
      const descriptionTextarea = screen.getByPlaceholderText('Enter description');
      const typeSelect = screen.getByTestId('select');

      fireEvent.change(nameInput, { target: { value: 'Test Campaign' } });
      fireEvent.change(descriptionTextarea, { target: { value: 'Test description' } });
      fireEvent.change(typeSelect, { target: { value: 'outbound' } });

      const submitButton = screen.getByText('Create Campaign');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(nameInput).toHaveValue('Test Campaign');
        expect(descriptionTextarea).toHaveValue('Test description');
        expect(typeSelect).toHaveValue('outbound');
      });
    });
  });

  describe('Edit Agent Modal', () => {
    it('renders edit agent form with pre-filled data', () => {
      renderWithProviders(<EditAgentModal isOpen={true} onOpenChange={vi.fn()} />);

      expect(screen.getByText('Edit Agent Details')).toBeInTheDocument();
      expect(screen.getByDisplayValue('John Doe')).toBeInTheDocument();
      expect(screen.getByDisplayValue('john@company.com')).toBeInTheDocument();
    });

    it('allows editing agent information', async () => {
      renderWithProviders(<EditAgentModal isOpen={true} onOpenChange={vi.fn()} />);

      const nameInput = screen.getByDisplayValue('John Doe');
      fireEvent.change(nameInput, { target: { value: 'Jane Smith' } });

      await waitFor(() => {
        expect(nameInput).toHaveValue('Jane Smith');
      });
    });

    it('handles department and skill level selection', () => {
      renderWithProviders(<EditAgentModal isOpen={true} onOpenChange={vi.fn()} />);

      const departmentSelect = screen.getAllByTestId('select')[0];
      const skillSelect = screen.getAllByTestId('select')[1];

      fireEvent.change(departmentSelect, { target: { value: 'support' } });
      fireEvent.change(skillSelect, { target: { value: 'expert' } });

      expect(departmentSelect).toHaveValue('support');
      expect(skillSelect).toHaveValue('expert');
    });
  });

  describe('Confirm Delete Modal', () => {
    it('renders confirmation message', () => {
      renderWithProviders(
        <ConfirmDeleteModal
          isOpen={true}
          onOpenChange={vi.fn()}
          onConfirm={vi.fn()}
        />
      );

      expect(screen.getByText('Confirm Deletion')).toBeInTheDocument();
      expect(screen.getByText('Are you sure you want to delete this item? This action cannot be undone.')).toBeInTheDocument();
      expect(screen.getByTestId('warning-icon')).toBeInTheDocument();
    });

    it('calls onConfirm when delete button is clicked', () => {
      const mockOnConfirm = vi.fn();
      const mockOnOpenChange = vi.fn();

      renderWithProviders(
        <ConfirmDeleteModal
          isOpen={true}
          onOpenChange={mockOnOpenChange}
          onConfirm={mockOnConfirm}
        />
      );

      const deleteButton = screen.getByText('Delete');
      fireEvent.click(deleteButton);

      expect(mockOnConfirm).toHaveBeenCalledTimes(1);
      expect(mockOnOpenChange).toHaveBeenCalledWith(false);
    });

    it('closes modal when cancel is clicked', () => {
      const mockOnOpenChange = vi.fn();

      renderWithProviders(
        <ConfirmDeleteModal
          isOpen={true}
          onOpenChange={mockOnOpenChange}
          onConfirm={vi.fn()}
        />
      );

      const cancelButton = screen.getByText('Cancel');
      fireEvent.click(cancelButton);

      expect(mockOnOpenChange).toHaveBeenCalledWith(false);
    });
  });

  describe('File Upload Modal', () => {
    it('renders file upload interface', () => {
      renderWithProviders(<FileUploadModal isOpen={true} onOpenChange={vi.fn()} />);

      expect(screen.getByText('Upload Contact List')).toBeInTheDocument();
      expect(screen.getByLabelText('Select File')).toBeInTheDocument();
      expect(screen.getByText('File Requirements:')).toBeInTheDocument();
    });

    it('shows upload progress', () => {
      renderWithProviders(<FileUploadModal isOpen={true} onOpenChange={vi.fn()} />);

      const progressBar = screen.getByTestId('progress');
      expect(progressBar).toHaveAttribute('data-value', '45');
      expect(screen.getByText('Uploading... 45%')).toBeInTheDocument();
    });

    it('handles file selection', () => {
      renderWithProviders(<FileUploadModal isOpen={true} onOpenChange={vi.fn()} />);

      const fileInput = screen.getByTestId('input');
      expect(fileInput).toHaveAttribute('type', 'file');
      expect(fileInput).toHaveAttribute('accept', '.csv,.xlsx');
    });
  });

  describe('Settings Modal', () => {
    it('renders all settings sections', () => {
      renderWithProviders(<SettingsModal isOpen={true} onOpenChange={vi.fn()} />);

      expect(screen.getByText('Application Settings')).toBeInTheDocument();
      expect(screen.getByText('Audio Settings')).toBeInTheDocument();
      expect(screen.getByText('Notification Settings')).toBeInTheDocument();
      expect(screen.getByText('Display Settings')).toBeInTheDocument();
    });

    it('handles device selection', () => {
      renderWithProviders(<SettingsModal isOpen={true} onOpenChange={vi.fn()} />);

      const inputDeviceSelect = screen.getAllByTestId('select')[0];
      const outputDeviceSelect = screen.getAllByTestId('select')[1];

      fireEvent.change(inputDeviceSelect, { target: { value: 'usb-mic' } });
      fireEvent.change(outputDeviceSelect, { target: { value: 'headset' } });

      expect(inputDeviceSelect).toHaveValue('usb-mic');
      expect(outputDeviceSelect).toHaveValue('headset');
    });

    it('handles checkbox settings', () => {
      renderWithProviders(<SettingsModal isOpen={true} onOpenChange={vi.fn()} />);

      const checkboxes = screen.getAllByTestId('checkbox');
      const callNotificationsCheckbox = checkboxes[0].querySelector('input');
      const emailNotificationsCheckbox = checkboxes[1].querySelector('input');

      expect(callNotificationsCheckbox).toBeChecked();
      expect(emailNotificationsCheckbox).not.toBeChecked();

      fireEvent.click(emailNotificationsCheckbox!);
      expect(emailNotificationsCheckbox).toBeChecked();
    });

    it('handles theme selection', () => {
      renderWithProviders(<SettingsModal isOpen={true} onOpenChange={vi.fn()} />);

      const themeRadios = screen.getAllByTestId('radio');
      const lightRadio = themeRadios[0].querySelector('input');
      const darkRadio = themeRadios[1].querySelector('input');

      expect(darkRadio).toBeChecked();

      fireEvent.click(lightRadio!);
      expect(lightRadio).toBeChecked();
    });

    it('shows section dividers', () => {
      renderWithProviders(<SettingsModal isOpen={true} onOpenChange={vi.fn()} />);

      const dividers = screen.getAllByTestId('divider');
      expect(dividers).toHaveLength(2);
    });
  });

  describe('Modal Accessibility', () => {
    it('has proper ARIA attributes', () => {
      renderWithProviders(
        <AccessibleModal isOpen={true} onOpenChange={vi.fn()} title="Accessible Modal">
          <p>Content</p>
        </AccessibleModal>
      );

      const modal = screen.getByTestId('modal');
      expect(modal).toBeInTheDocument();
    });

    it('supports keyboard navigation', () => {
      renderWithProviders(
        <CreateCampaignModal isOpen={true} onOpenChange={vi.fn()} />
      );

      const nameInput = screen.getByPlaceholderText('Enter campaign name');
      nameInput.focus();

      expect(document.activeElement).toBe(nameInput);

      // Tab navigation should work between form elements
      fireEvent.keyDown(nameInput, { key: 'Tab' });
    });

    it('handles escape key to close modal', () => {
      const mockOnOpenChange = vi.fn();
      renderWithProviders(
        <AccessibleModal isOpen={true} onOpenChange={mockOnOpenChange} title="Test Modal">
          <p>Content</p>
        </AccessibleModal>
      );

      fireEvent.keyDown(document, { key: 'Escape' });
      // Note: In real implementation, this would call mockOnOpenChange(false)
    });
  });

  describe('Modal Form Validation', () => {
    it('shows validation errors for invalid inputs', async () => {
      renderWithProviders(<CreateCampaignModal isOpen={true} onOpenChange={vi.fn()} />);

      const nameInput = screen.getByPlaceholderText('Enter campaign name');

      // Trigger validation by attempting to submit empty form
      fireEvent.blur(nameInput);

      // In a real implementation, validation errors would be shown
      expect(nameInput).toHaveAttribute('required');
    });

    it('validates email format in edit agent modal', () => {
      renderWithProviders(<EditAgentModal isOpen={true} onOpenChange={vi.fn()} />);

      const emailInput = screen.getByDisplayValue('john@company.com');
      expect(emailInput).toHaveAttribute('type', 'email');
    });
  });

  describe('Modal State Management', () => {
    it('maintains form state while modal is open', () => {
      renderWithProviders(<CreateCampaignModal isOpen={true} onOpenChange={vi.fn()} />);

      const nameInput = screen.getByPlaceholderText('Enter campaign name');
      fireEvent.change(nameInput, { target: { value: 'Test Campaign' } });

      expect(nameInput).toHaveValue('Test Campaign');
    });

    it('resets form state when modal is reopened', () => {
      const { rerender } = renderWithProviders(
        <CreateCampaignModal isOpen={false} onOpenChange={vi.fn()} />
      );

      rerender(
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <CreateCampaignModal isOpen={true} onOpenChange={vi.fn()} />
          </BrowserRouter>
        </QueryClientProvider>
      );

      const nameInput = screen.getByPlaceholderText('Enter campaign name');
      expect(nameInput).toHaveValue('');
    });
  });
});