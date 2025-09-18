// src/pages/TodoListPage.js
import React, { useState } from 'react';
import { Container, Row, Col, Form, Button, ListGroup, Alert, Spinner, InputGroup, Modal, ButtonGroup } from 'react-bootstrap';

/**
 * Main To-Do List Page: supports adding, editing, deleting, toggling completed,
 * filtering by All/Active/Completed, and bulk-clearing completed tasks.
 */
const FILTERS = {
  all: {
    label: 'All',
    predicate: () => true,
  },
  active: {
    label: 'Active',
    predicate: task => !task.completed,
  },
  completed: {
    label: 'Completed',
    predicate: task => !!task.completed,
  },
};

const TodoListPage = () => {
  // Task state
  const [taskInput, setTaskInput] = useState('');
  const [tasks, setTasks] = useState([]); // [{id, description, completed}]
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState('');
  // Editing state
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [editError, setEditError] = useState('');
  const [editLoading, setEditLoading] = useState(false);
  // Deleting state
  const [deleteId, setDeleteId] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  // Bulk clear completed state
  const [showClearCompletedModal, setShowClearCompletedModal] = useState(false);
  const [clearCompletedLoading, setClearCompletedLoading] = useState(false);
  const [clearCompletedError, setClearCompletedError] = useState('');
  // Filtering state
  const [filter, setFilter] = useState('all'); // 'all' | 'active' | 'completed'

  // --- Add New Task ---
  const handleInputChange = (e) => {
    setTaskInput(e.target.value);
    if (error) setError('');
  };
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!taskInput.trim()) {
      setError('Please enter a task description.');
      return;
    }
    setAdding(true);
    setTimeout(() => {
      setTasks(prevTasks => [...prevTasks, {
        id: Date.now(),
        description: taskInput.trim(),
        completed: false
      }]);
      setTaskInput('');
      setAdding(false);
    }, 500);
  };

  // --- Edit Task Logic ---
  const handleStartEdit = (task) => {
    setEditingId(task.id);
    setEditValue(task.description);
    setEditError('');
  };
  const handleEditInputChange = (e) => {
    setEditValue(e.target.value);
    if (editError) setEditError('');
  };
  const handleSaveEdit = (task) => {
    if (!editValue.trim()) {
      setEditError('Task description cannot be empty.');
      return;
    }
    setEditLoading(true);
    setTimeout(() => {
      setTasks(prevTasks =>
        prevTasks.map(t =>
          t.id === task.id ? { ...t, description: editValue.trim() } : t
        )
      );
      setEditingId(null);
      setEditValue('');
      setEditError('');
      setEditLoading(false);
    }, 500);
  };
  const handleCancelEdit = () => {
    setEditingId(null);
    setEditValue('');
    setEditError('');
  };
  const handleTaskDoubleClick = (task) => {
    handleStartEdit(task);
  };
  const handleEditKeyDown = (e, task) => {
    if (e.key === 'Enter') {
      handleSaveEdit(task);
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  // --- Delete Logic ---
  const handleShowDeleteModal = (taskId) => {
    setDeleteId(taskId);
  };
  const handleCloseDeleteModal = () => {
    setDeleteId(null);
    setDeleteLoading(false);
  };
  const handleConfirmDelete = () => {
    setDeleteLoading(true);
    setTimeout(() => {
      setTasks(prev => prev.filter(t => t.id !== deleteId));
      handleCloseDeleteModal();
    }, 500);
  };

  // --- Toggle Complete ---
  const handleToggleComplete = (taskId) => {
    setTasks(prevTasks =>
      prevTasks.map(t =>
        t.id === taskId ? { ...t, completed: !t.completed } : t
      )
    );
  };

  // --- Bulk Clear Completed Logic ---
  const handleShowClearCompletedModal = () => {
    setClearCompletedError('');
    setShowClearCompletedModal(true);
  };
  const handleCloseClearCompletedModal = () => {
    setShowClearCompletedModal(false);
    setClearCompletedLoading(false);
    setClearCompletedError('');
  };
  const handleConfirmClearCompleted = () => {
    setClearCompletedLoading(true);
    setTimeout(() => {
      setTasks(prev => prev.filter(t => !t.completed));
      setShowClearCompletedModal(false);
      setClearCompletedLoading(false);
    }, 700);
  };

  // --- Filter Tabs/Buttons ---
  const filteredTasks = tasks.filter(FILTERS[filter].predicate);
  const completedCount = tasks.filter(t => t.completed).length;
  const totalCount = tasks.length;
  const activeCount = tasks.filter(t => !t.completed).length;

  return (
    <Container data-testid="todo-list-page" className="py-4" style={{ maxWidth: '550px' }}>
      <Row>
        <Col>
          <h2 className="mb-4">To-Do List</h2>

          {/* --- Add New Task Form --- */}
          <Form onSubmit={handleSubmit} className="mb-3" autoComplete="off">
            <Form.Group controlId="formNewTask">
              <Form.Label visuallyHidden>Add Task</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter a new task"
                value={taskInput}
                onChange={handleInputChange}
                disabled={adding}
                aria-label="Task Description"
                autoFocus
              />
            </Form.Group>
            <div className="d-flex mt-2">
              <Button type="submit" variant="primary" disabled={adding || !taskInput.trim()}>
                {adding ? <Spinner size="sm" animation="border" /> : 'Add'}
              </Button>
            </div>
          </Form>
          {error && (
            <Alert variant="danger" data-testid="input-error" className="py-2">
              {error}
            </Alert>
          )}

          {/* ------ Filter Buttons (All/Active/Completed) ------ */}
          <div className="d-flex justify-content-center mb-2" data-testid="filter-buttons">
            <ButtonGroup>
              {Object.keys(FILTERS).map(key => (
                <Button
                  key={key}
                  variant={filter === key ? 'primary' : 'outline-primary'}
                  onClick={() => setFilter(key)}
                  data-testid={`filter-btn-${key}`}
                >
                  {FILTERS[key].label}
                </Button>
              ))}
            </ButtonGroup>
          </div>
          {/* --- subtext about items size by filter --- */}
          <div className="small text-muted mb-2 text-center">
            {filter === 'all' && totalCount > 0 && (
              <>{activeCount} active, {completedCount} completed tasks</>
            )}
            {filter === 'active' && (
              <>{activeCount} active task{activeCount !== 1 ? 's' : ''} shown</>
            )}
            {filter === 'completed' && (
              <>{completedCount} completed task{completedCount !== 1 ? 's' : ''} shown</>
            )}
          </div>

          {/* ------ To-Do List ------ */}
          <ListGroup>
            {filteredTasks.length === 0 ? (
              <ListGroup.Item data-testid="empty-list-note" className="text-muted">No tasks to show for this filter.</ListGroup.Item>
            ) : (
              filteredTasks.map(task => (
                <ListGroup.Item
                  key={task.id}
                  className="d-flex align-items-start justify-content-between"
                  style={{
                    background: task.completed ? '#f8f9fa' : 'white',
                  }}
                >
                  {/* Checkbox to toggle completion */}
                  <Form.Check
                    type="checkbox"
                    className="me-2 mt-1"
                    checked={!!task.completed}
                    onChange={() => handleToggleComplete(task.id)}
                    aria-label={task.completed ? "Mark as active" : "Mark as completed"}
                    tabIndex={0}
                  />
                  {/* Edit Mode or static view */}
                  {editingId === task.id ? (
                    <div className="flex-grow-1">
                      <Form.Group controlId={`edit-task-${task.id}`} className="mb-0">
                        <InputGroup>
                          <Form.Control
                            type="text"
                            value={editValue}
                            onChange={handleEditInputChange}
                            onKeyDown={e => handleEditKeyDown(e, task)}
                            autoFocus
                            disabled={editLoading}
                            aria-label="Edit task description"
                          />
                          <Button
                            variant="success"
                            onClick={() => handleSaveEdit(task)}
                            disabled={editLoading || !editValue.trim()}
                          >
                            {editLoading ? <Spinner size="sm" animation="border" /> : 'Save'}
                          </Button>
                          <Button
                            variant="outline-secondary"
                            onClick={handleCancelEdit}
                            disabled={editLoading}
                          >
                            Cancel
                          </Button>
                        </InputGroup>
                        {editError && (
                          <div className="text-danger small pt-1">{editError}</div>
                        )}
                      </Form.Group>
                    </div>
                  ) : (
                    <>
                      {/* Task description visually distinct if completed */}
                      <span
                        style={{
                          cursor: 'pointer',
                          textDecoration: task.completed ? 'line-through' : 'none',
                          color: task.completed ? '#888' : 'inherit',
                          opacity: task.completed ? 0.7 : 1
                        }}
                        className="flex-grow-1"
                        title="Double-click to edit"
                        onDoubleClick={() => handleTaskDoubleClick(task)}
                        tabIndex={0}
                      >
                        {task.description}
                      </span>
                      <div className="d-flex">
                        <Button
                          variant="outline-primary"
                          size="sm"
                          className="ms-2"
                          onClick={() => handleStartEdit(task)}
                          aria-label="Edit task"
                        >
                          Edit
                        </Button>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          className="ms-2"
                          onClick={() => handleShowDeleteModal(task.id)}
                          aria-label="Delete task"
                        >
                          Delete
                        </Button>
                      </div>
                    </>
                  )}
                </ListGroup.Item>
              ))
            )}
          </ListGroup>

          {/* ------- Bulk 'Clear Completed' Button ------- */}
          <div className="mt-3 text-center">
            <Button
              variant="outline-secondary"
              onClick={handleShowClearCompletedModal}
              disabled={completedCount === 0 || clearCompletedLoading || tasks.length === 0}
              data-testid="clear-completed-btn"
            >
              {clearCompletedLoading ? <Spinner size="sm" animation="border" /> : 'Clear Completed'}
            </Button>
            {completedCount > 0 && (
              <span className="ms-2 small text-muted" data-testid="completed-count">
                {completedCount} completed {completedCount === 1 ? 'task' : 'tasks'}
              </span>
            )}
          </div>

          {/* Modal: Confirm Bulk Clear Completed */}
          <Modal show={showClearCompletedModal} onHide={handleCloseClearCompletedModal} centered backdrop="static">
            <Modal.Header closeButton>
              <Modal.Title>Clear All Completed Tasks</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              Are you sure you want to remove <b>all completed tasks</b> ({completedCount}) from your list? This cannot be undone and will <span className="text-primary">not affect active tasks</span>.
              {clearCompletedError && (
                <Alert variant="danger" className="mt-3">{clearCompletedError}</Alert>
              )}
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={handleCloseClearCompletedModal} disabled={clearCompletedLoading}>
                Cancel
              </Button>
              <Button variant="danger" onClick={handleConfirmClearCompleted} disabled={clearCompletedLoading}>
                {clearCompletedLoading ? (
                  <Spinner size="sm" animation="border" />
                ) : 'Clear All Completed'}
              </Button>
            </Modal.Footer>
          </Modal>

          {/* Modal: Confirm Delete single item */}
          <Modal show={deleteId !== null} onHide={handleCloseDeleteModal} centered backdrop="static">
            <Modal.Header closeButton>
              <Modal.Title>Delete Task</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              Are you sure you want to delete this task? This action cannot be undone.
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={handleCloseDeleteModal} disabled={deleteLoading}>
                Cancel
              </Button>
              <Button variant="danger" onClick={handleConfirmDelete} disabled={deleteLoading}>
                {deleteLoading ? <Spinner size="sm" animation="border" /> : 'Delete'}
              </Button>
            </Modal.Footer>
          </Modal>
        </Col>
      </Row>
    </Container>
  );
};

export default TodoListPage;
