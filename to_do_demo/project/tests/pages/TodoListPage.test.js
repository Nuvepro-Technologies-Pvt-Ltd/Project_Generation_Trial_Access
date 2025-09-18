import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import TodoListPage from '../../src/pages/TodoListPage';

// tests/pages/TodoListPage.test.js
// Note: React Testing Library is used with Jest.
describe('TodoListPage - Filter & Core Functionality', () => {
  // Helper to add a task
  async function addTask(taskText) {
    const input = screen.getByPlaceholderText('Enter a new task');
    userEvent.clear(input);
    userEvent.type(input, taskText);
    const btn = screen.getByRole('button', { name: 'Add' });
    userEvent.click(btn);
    await waitFor(() => expect(btn).not.toBeDisabled(), { timeout: 1000 });
  }

  // Helper to add multiple tasks
  async function addTasks(taskArr) {
    for (const t of taskArr) {
      await addTask(t);
    }
  }

  beforeEach(() => {
    render(<TodoListPage />);
  });

  test('renders without crashing and shows empty list message', () => {
    expect(screen.getByTestId('todo-list-page')).toBeInTheDocument();
    expect(screen.getByTestId('empty-list-note')).toHaveTextContent('No tasks to show for this filter.');
  });

  test('adds new tasks and displays in All filter', async () => {
    await addTasks(['A first task', 'A second task']);
    expect(screen.queryByTestId('empty-list-note')).not.toBeInTheDocument();
    expect(screen.getByText('A first task')).toBeInTheDocument();
    expect(screen.getByText('A second task')).toBeInTheDocument();

    // The count summary is correct
    expect(screen.getByText(/2 active, 0 completed tasks/)).toBeInTheDocument();
  });

  test('cannot add empty or whitespace-only task', async () => {
    const input = screen.getByPlaceholderText('Enter a new task');
    const btn = screen.getByRole('button', { name: 'Add' });
    userEvent.type(input, '  ');
    expect(btn).toBeDisabled();
    userEvent.clear(input);
    userEvent.click(btn);
    expect(await screen.findByTestId('input-error')).toHaveTextContent('Please enter a task description.');
  });

  test('toggle completion and filter Active/Completed/All', async () => {
    await addTasks(['Foo', 'Bar', 'Baz']);
    // Mark 'Foo' as completed
    const fooCheckbox = screen.getAllByRole('checkbox')[0];
    fireEvent.click(fooCheckbox);
    // Now filter active
    userEvent.click(screen.getByTestId('filter-btn-active'));
    expect(screen.queryByText('Foo')).not.toBeInTheDocument();
    expect(screen.getByText('Bar')).toBeInTheDocument();
    expect(screen.getByText('Baz')).toBeInTheDocument();
    // Filter completed
    userEvent.click(screen.getByTestId('filter-btn-completed'));
    expect(screen.getByText('Foo')).toBeInTheDocument();
    expect(screen.queryByText('Bar')).not.toBeInTheDocument();
    expect(screen.queryByText('Baz')).not.toBeInTheDocument();
    // Filter all
    userEvent.click(screen.getByTestId('filter-btn-all'));
    expect(screen.getByText('Foo')).toBeInTheDocument();
    expect(screen.getByText('Bar')).toBeInTheDocument();
    expect(screen.getByText('Baz')).toBeInTheDocument();
  });

  test('shows correct item count messaging on filters', async () => {
    await addTasks(['Only active']);
    expect(screen.getByText(/1 active, 0 completed tasks/)).toBeInTheDocument();
    // Mark as completed
    fireEvent.click(screen.getByRole('checkbox'));
    expect(screen.getByText(/0 active, 1 completed tasks/)).toBeInTheDocument();
    // Now filter 'completed'
    userEvent.click(screen.getByTestId('filter-btn-completed'));
    expect(screen.getByText('1 completed task shown')).toBeInTheDocument();
    // Filter to 'active'
    userEvent.click(screen.getByTestId('filter-btn-active'));
    expect(screen.getByText('0 active tasks shown')).toBeInTheDocument();
  });

  test('edge: no tasks for given filter shows empty note', async () => {
    await addTasks(['Alpha']);
    // Alpha is active; mark as complete
    fireEvent.click(screen.getByRole('checkbox'));
    // Now filter to active
    userEvent.click(screen.getByTestId('filter-btn-active'));
    expect(screen.getByTestId('empty-list-note')).toBeInTheDocument();
    // Switch to completed (should see Alpha)
    userEvent.click(screen.getByTestId('filter-btn-completed'));
    expect(screen.queryByTestId('empty-list-note')).not.toBeInTheDocument();
  });

  test('editing task in-place and validating edge cases', async () => {
    await addTask('Edit me');
    // Start edit
    userEvent.click(screen.getByRole('button', { name: 'Edit' }));
    const editInput = screen.getByLabelText('Edit task description');
    userEvent.clear(editInput);
    userEvent.type(editInput, '{space}');
    const saveBtn = screen.getByRole('button', { name: 'Save' });
    expect(saveBtn).toBeDisabled();
    // Try save with empty input
    userEvent.clear(editInput);
    fireEvent.click(saveBtn);
    expect(await screen.findByText('Task description cannot be empty.')).toBeInTheDocument();
    // Type a new description and save
    userEvent.clear(editInput);
    userEvent.type(editInput, 'NewName');
    userEvent.click(saveBtn);
    await waitFor(() => expect(screen.queryByLabelText('Edit task description')).not.toBeInTheDocument(), { timeout: 2000 });
    expect(screen.getByText('NewName')).toBeInTheDocument();
    // Re-open edit by double click on span
    const taskText = screen.getByText('NewName');
    fireEvent.doubleClick(taskText);
    expect(screen.getByLabelText('Edit task description')).toHaveValue('NewName');
    // Cancel edit
    userEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(screen.queryByLabelText('Edit task description')).not.toBeInTheDocument();
  });

  test('delete individual task via modal confirmation', async () => {
    await addTasks(['First', 'Second']);
    const deleteButtons = screen.getAllByRole('button', { name: 'Delete task' });
    userEvent.click(deleteButtons[0]);
    // Modal appears
    expect(screen.getByText('Delete Task')).toBeInTheDocument();
    // Cancel
    userEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(screen.queryByText('Delete Task')).not.toBeInTheDocument();
    // Reopen and confirm delete
    userEvent.click(screen.getAllByRole('button', { name: 'Delete task' })[0]);
    userEvent.click(screen.getByRole('button', { name: 'Delete' }));
    await waitFor(() => expect(screen.queryByText('First')).not.toBeInTheDocument(), { timeout: 2000 });
    expect(screen.getByText('Second')).toBeInTheDocument();
  });

  test('bulk clear completed disables/enables correctly, works and handles modal UX', async () => {
    await addTasks(['c1', 'c2', 'keep-active']);
    // Mark first two as completed
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[0]);
    fireEvent.click(checkboxes[1]);
    // Button should now be enabled
    const btn = screen.getByTestId('clear-completed-btn');
    expect(btn).toBeEnabled();
    // Modal appears and cancellation
    userEvent.click(btn);
    expect(screen.getByText('Clear All Completed Tasks')).toBeInTheDocument();
    userEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(screen.queryByText('Clear All Completed Tasks')).not.toBeInTheDocument();
    // Confirm clear completed
    userEvent.click(screen.getByTestId('clear-completed-btn'));
    userEvent.click(screen.getByRole('button', { name: 'Clear All Completed' }));
    await waitFor(() => expect(screen.queryByText('c1')).not.toBeInTheDocument(), { timeout: 2000 });
    expect(screen.queryByText('c2')).not.toBeInTheDocument();
    expect(screen.getByText('keep-active')).toBeInTheDocument();
    // After clearing, bulk clear should be disabled if no completed tasks left
    expect(screen.getByTestId('clear-completed-btn')).toBeDisabled();
  });

  test('all interactive controls have accessible labels', async () => {
    await addTask('Task A');
    // Filter buttons
    ['all', 'active', 'completed'].forEach(key => {
      expect(screen.getByTestId(`filter-btn-${key}`)).toBeInTheDocument();
    });
    // Edit and delete buttons
    expect(screen.getByRole('button', { name: 'Edit' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Delete task' })).toBeInTheDocument();
    // Checkbox
    expect(screen.getByRole('checkbox')).toHaveAccessibleName('Mark as completed');
  });

  test('performance: UI remains responsive after rapid task additions and deletes', async () => {
    const N = 10;
    const values = Array.from({length: N}, (_, i) => `Task-${i}`);
    await addTasks(values);
    // Delete all in a quick loop
    for (let i = 0; i < N; i++) {
      userEvent.click(screen.getAllByRole('button', { name: 'Delete task' })[0]);
      userEvent.click(screen.getByRole('button', { name: 'Delete' }));
      // Ensure it doesn't stall
      await waitFor(() => expect(screen.queryByText(`Task-${i}`)).not.toBeInTheDocument(), { timeout: 2000 });
    }
    expect(screen.getByTestId('empty-list-note')).toBeInTheDocument();
  });

  // Security: While not a backend app, test input sanitation basics
  test('security: input strips surrounding whitespace, HTML seen as text', async () => {
    await addTask('   trim-me   ');
    expect(screen.getByText('trim-me')).toBeInTheDocument();
    // Input with HTML like <script> doesn't render as HTML
    const htmlText = '<b>Dangerous</b> <script>alert(1)</script>';
    await addTask(htmlText);
    expect(screen.getByText(htmlText)).toBeInTheDocument();
  });

  // Edge: keyboard controls for edit (enter and escape)
  test('editing: enter saves, escape cancels', async () => {
    await addTask('keytest');
    userEvent.click(screen.getByRole('button', { name: 'Edit' }));
    const editInput = screen.getByLabelText('Edit task description');
    userEvent.clear(editInput);
    userEvent.type(editInput, 'bye');
    // Press escape
    fireEvent.keyDown(editInput, { key: 'Escape', code: 'Escape' });
    expect(screen.queryByLabelText('Edit task description')).not.toBeInTheDocument();
    // Re-edit, type, press enter
    userEvent.click(screen.getByRole('button', { name: 'Edit' }));
    const editInput2 = screen.getByLabelText('Edit task description');
    userEvent.clear(editInput2);
    userEvent.type(editInput2, 'greet');
    fireEvent.keyDown(editInput2, { key: 'Enter', code: 'Enter' });
    await waitFor(() => expect(screen.queryByLabelText('Edit task description')).not.toBeInTheDocument(), {timeout:1000});
    expect(screen.getByText('greet')).toBeInTheDocument();
  });

  // Parameterized filter scenarios
  test.each`
    filter          | tasks                        | completes     | expected
    ${'all'}        | ${['A', 'B', 'C']}           | ${[1]}        | ${['A', 'B', 'C']}
    ${'active'}     | ${['D', 'E']}                | ${[0]}        | ${['E']}
    ${'completed'}  | ${['F', 'G', 'H']}           | ${[0,2]}      | ${['F', 'H']}
  `('parameterized: $filter filter shows correct tasks', async ({ filter, tasks, completes, expected }) => {
    await addTasks(tasks);
    // Complete some
    for (const idx of completes) {
      fireEvent.click(screen.getAllByRole('checkbox')[idx]);
    }
    userEvent.click(screen.getByTestId(`filter-btn-${filter}`));
    expected.forEach(txt => expect(screen.getByText(txt)).toBeInTheDocument());
  });

  // Test that after deletion and edit, bulk clear completed still works
  test('correctness after multiple interactions', async () => {
    await addTasks(['persist', 'go', 'leave']);
    // Complete 'leave', edit 'go' to 'gone', delete 'persist'
    fireEvent.click(screen.getAllByRole('checkbox')[2]);
    userEvent.click(screen.getAllByRole('button', {name:'Edit'})[1]);
    const editInput = screen.getByLabelText('Edit task description');
    userEvent.clear(editInput);
    userEvent.type(editInput, 'gone');
    userEvent.click(screen.getByRole('button', {name: 'Save'}));
    userEvent.click(screen.getAllByRole('button', {name: 'Delete task'})[0]);
    userEvent.click(screen.getByRole('button', {name: 'Delete'}));
    await waitFor(() => expect(screen.queryByText('persist')).not.toBeInTheDocument(), { timeout: 2000 });
    userEvent.click(screen.getByTestId('clear-completed-btn'));
    userEvent.click(screen.getByRole('button', { name: 'Clear All Completed' }));
    await waitFor(() => expect(screen.queryByText('leave')).not.toBeInTheDocument(), { timeout: 2000 });
    // Only 'gone' remains
    expect(screen.getByText('gone')).toBeInTheDocument();
  });

  // Async: spinner appears during add, edit, delete, clear completed
  test('loading spinners show during async ops', async () => {
    // Add loading
    const input = screen.getByPlaceholderText('Enter a new task');
    userEvent.type(input, 'Spin');
    const addBtn = screen.getByRole('button', { name: 'Add' });
    userEvent.click(addBtn);
    expect(screen.getByRole('status')).toBeInTheDocument(); // Spinner is role='status'
    await waitFor(() => expect(addBtn).not.toBeDisabled(), { timeout: 1500 });
    // Edit loading
    await addTask('LoadEdit');
    userEvent.click(screen.getByRole('button', { name: 'Edit' }));
    const editInput = screen.getByLabelText('Edit task description');
    userEvent.clear(editInput);
    userEvent.type(editInput, 'XL');
    const saveBtn = screen.getByRole('button', { name: 'Save' });
    userEvent.click(saveBtn);
    expect(screen.getByRole('status')).toBeInTheDocument();
    await waitFor(() => expect(saveBtn).not.toBeDisabled(), { timeout: 1500 });
    // Delete loading
    userEvent.click(screen.getByRole('button', { name: 'Delete task' }));
    userEvent.click(screen.getByRole('button', { name: 'Delete' }));
    expect(screen.getByRole('status')).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByRole('status')).not.toBeInTheDocument(), { timeout: 1500 });
    // Bulk clear completed
    await addTasks(['for-clear']);
    fireEvent.click(screen.getByRole('checkbox'));
    const clearBtn = screen.getByTestId('clear-completed-btn');
    userEvent.click(clearBtn);
    userEvent.click(screen.getByRole('button', { name: 'Clear All Completed' }));
    expect(screen.getByRole('status')).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByRole('status')).not.toBeInTheDocument(), { timeout: 2000 });
  });

  // Stress: large number of tasks does not degrade filter performance
  test('performance: handles many tasks', async () => {
    const many = Array.from({length: 40}, (_, i) => `MassTask${i}`);
    await addTasks(many);
    userEvent.click(screen.getByTestId('filter-btn-completed'));
    expect(screen.getByTestId('empty-list-note')).toBeInTheDocument();
    // Mark some completed
    for (let i = 0; i < many.length; i += 2) {
      fireEvent.click(screen.getAllByRole('checkbox')[i]);
    }
    // Filter to completed
    userEvent.click(screen.getByTestId('filter-btn-completed'));
    for (let i = 0; i < many.length; i += 2) {
      expect(screen.getByText(`MassTask${i}`)).toBeInTheDocument();
    }
    // Check active filter
    userEvent.click(screen.getByTestId('filter-btn-active'));
    for (let i = 1; i < many.length; i += 2) {
      expect(screen.getByText(`MassTask${i}`)).toBeInTheDocument();
    }
  });
});