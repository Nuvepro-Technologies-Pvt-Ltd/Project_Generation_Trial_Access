import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/extend-expect';
import TodoListPage from '../TodoListPage';

// Comprehensive test suite for TodoListPage (React - Jest + RTL)
// Tests cover: task adding, validation, toggling complete/active, editing, deleting, modals, edge & error cases

// Helper to add task
async function addTask(taskText) {
  const input = screen.getByPlaceholderText('Enter a new task');
  await userEvent.clear(input);
  await userEvent.type(input, taskText);
  const addBtn = screen.getByRole('button', { name: /add/i });
  await userEvent.click(addBtn);
  // Wait for loading to finish (simulated API)
  await waitFor(() => expect(addBtn).not.toBeDisabled());
}

describe('TodoListPage Component', () => {
  beforeEach(() => {
    render(<TodoListPage />);
  });

  test('should render the main container and empty message', () => {
    // Renders main title
    expect(screen.getByTestId('todo-list-page')).toBeInTheDocument();
    expect(screen.getByText('To-Do List')).toBeInTheDocument();
    // Shows empty state
    expect(screen.getByTestId('empty-list-note')).toHaveTextContent('No tasks yet. Add your first one!');
  });

  test('should not allow adding empty task and displays error', async () => {
    const addBtn = screen.getByRole('button', { name: /add/i });
    expect(addBtn).toBeDisabled();

    // Try to add by pressing submit with empty input
    const form = screen.getByRole('form');
    fireEvent.submit(form);
    expect(await screen.findByTestId('input-error')).toHaveTextContent('Please enter a task description.');

    // Input non-space then space only
    const input = screen.getByPlaceholderText('Enter a new task');
    await userEvent.type(input, '   ');
    expect(addBtn).toBeDisabled();
  });

  test('should add a new task and clear the input', async () => {
    await addTask('Buy milk');
    expect(screen.queryByTestId('empty-list-note')).not.toBeInTheDocument();
    expect(screen.getByText('Buy milk')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter a new task')).toHaveValue('');
  });

  test('should toggle task as completed and then active', async () => {
    await addTask('Call Mom');
    // Checkbox is unchecked on add
    const checkbox = screen.getByRole('checkbox', { name: /mark as completed/i });
    expect(checkbox).not.toBeChecked();
    // Complete task
    await userEvent.click(checkbox);
    expect(checkbox).toBeChecked();
    // Visual strike-through on description
    const taskDesc = screen.getByText('Call Mom');
    expect(taskDesc).toHaveStyle({ textDecoration: 'line-through', color: '#888', opacity: '0.7' });
    // Checkbox aria-label changes
    expect(checkbox).toHaveAttribute('aria-label', 'Mark as active');
    // Set back to active
    await userEvent.click(checkbox);
    expect(checkbox).not.toBeChecked();
    expect(checkbox).toHaveAttribute('aria-label', 'Mark as completed');
    expect(taskDesc).not.toHaveStyle('text-decoration: line-through');
  });

  test('should allow editing a task and validation of empty edit value', async () => {
    await addTask('Read a book');
    const editBtn = screen.getByRole('button', { name: /edit task/i });
    await userEvent.click(editBtn);
    // Edit input appears
    const editInput = screen.getByLabelText('Edit task description');
    expect(editInput).toHaveValue('Read a book');
    // Try to save empty edit
    await userEvent.clear(editInput);
    const saveBtn = screen.getByRole('button', { name: /save/i });
    await userEvent.click(saveBtn);
    expect(screen.getByText('Task description cannot be empty.')).toBeInTheDocument();
    // Enter new text
    await userEvent.type(editInput, 'Learn Jest');
    expect(saveBtn).not.toBeDisabled();
    await userEvent.click(saveBtn);
    // Wait for loading
    await waitFor(() => expect(screen.getByText('Learn Jest')).toBeInTheDocument());
    expect(screen.queryByText('Read a book')).not.toBeInTheDocument();
  });

  test('should edit task on double-click description', async () => {
    await addTask('Walk dog');
    const taskDesc = screen.getByText('Walk dog');
    fireEvent.doubleClick(taskDesc);
    expect(screen.getByLabelText('Edit task description')).toBeInTheDocument();
  });

  test('editing can be cancelled with Escape or Cancel button', async () => {
    await addTask('Finish homework');
    const editBtn = screen.getByRole('button', { name: /edit task/i });
    await userEvent.click(editBtn);
    const editInput = screen.getByLabelText('Edit task description');
    // Cancel with Escape
    fireEvent.keyDown(editInput, { key: 'Escape' });
    expect(editInput).not.toBeInTheDocument();

    // Open edit again, cancel with button
    await userEvent.click(editBtn);
    const cancelBtn = screen.getByRole('button', { name: /cancel/i });
    await userEvent.click(cancelBtn);
    expect(screen.queryByLabelText('Edit task description')).not.toBeInTheDocument();
  });

  test('should support editing by pressing Enter', async () => {
    await addTask('Go jogging');
    await userEvent.click(screen.getByRole('button', { name: /edit task/i }));
    const editInput = screen.getByLabelText('Edit task description');
    await userEvent.clear(editInput);
    await userEvent.type(editInput, 'Morning run');
    fireEvent.keyDown(editInput, { key: 'Enter' });
    await waitFor(() => expect(screen.getByText('Morning run')).toBeInTheDocument());
  });

  test('should open and cancel delete confirmation modal', async () => {
    await addTask('Test delete');
    const deleteBtn = screen.getByRole('button', { name: /delete task/i });
    await userEvent.click(deleteBtn);
    // Modal is visible
    expect(screen.getByText('Delete Task')).toBeInTheDocument();
    // Clicking cancel closes modal
    await userEvent.click(screen.getByRole('button', { name: /cancel/i }));
    expect(screen.queryByText('Delete Task')).not.toBeInTheDocument();
  });

  test('should delete a task after confirmation', async () => {
    await addTask('Delete me');
    expect(screen.getByText('Delete me')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /delete task/i }));
    expect(screen.getByText('Delete Task')).toBeInTheDocument();
    const confirmBtn = screen.getByRole('button', { name: /^delete$/i });
    await userEvent.click(confirmBtn);
    // Simulate loading and removal
    await waitFor(() => expect(screen.queryByText('Delete me')).not.toBeInTheDocument());
  });

  test('should maintain correct completed/active style through all operations', async () => {
    await addTask('First');
    await addTask('Second');
    const [first, second] = screen.getAllByRole('checkbox');

    // Mark first complete
    await userEvent.click(first);
    expect(screen.getAllByRole('checkbox')[0]).toBeChecked();
    // Edit the completed task and assert style persists
    await userEvent.click(screen.getAllByRole('button', { name: /edit task/i })[0]);
    const editInput = screen.getByLabelText('Edit task description');
    await userEvent.clear(editInput);
    await userEvent.type(editInput, 'First updated');
    await userEvent.click(screen.getByRole('button', { name: /save/i }));
    await waitFor(() => expect(screen.getByText('First updated')).toBeInTheDocument());
    // Still completed
    expect(screen.getAllByRole('checkbox')[0]).toBeChecked();
    const [updatedDesc] = screen.getAllByText(/First updated/);
    expect(updatedDesc).toHaveStyle('text-decoration: line-through');
  });

  test('should handle tasks with long text or special characters', async () => {
    const longText = 'A'.repeat(200) + ' \u2603 ~!@#$%^&*()_+';
    await addTask(longText);
    expect(screen.getByText(longText)).toBeInTheDocument();
    // Mark completed and ensure rendering
    await userEvent.click(screen.getByRole('checkbox'));
    expect(screen.getByRole('checkbox')).toBeChecked();
  });

  test('should be able to quickly add multiple tasks and mark them completed independently', async () => {
    await addTask('Alpha');
    await addTask('Beta');
    await addTask('Gamma');
    const checkboxes = screen.getAllByRole('checkbox');
    // Mark second and third completed
    await userEvent.click(checkboxes[1]);
    await userEvent.click(checkboxes[2]);
    expect(checkboxes[0]).not.toBeChecked();
    expect(checkboxes[1]).toBeChecked();
    expect(checkboxes[2]).toBeChecked();
  });

  test('should support accessibility: all buttons and inputs have appropriate labels', () => {
    expect(screen.getByLabelText('Task Description')).toBeInTheDocument();
    // Add a task for more checks
    addTask('Do laundry');
    expect(screen.getByLabelText(/mark as completed/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /edit task/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /delete task/i })).toBeInTheDocument();
  });

  // Asynchronous/atomicity/performance isn't directly testable due to setTimeout mocks (simulate reasonable behavior)
  // Could use Jest fake timers if needed for more advanced cases
});

// Note: This suite provides high coverage, including validation, edge cases (long text), disabled states, and UI feedback/ARIA, essential for real-world production apps.