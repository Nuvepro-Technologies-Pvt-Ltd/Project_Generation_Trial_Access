## What you will do:

**Problem Statement**  
Problem Statement: Building a Responsive To-Do List Productivity Web Application (Scenario-Based)

Scenario — Industry Challenge in Productivity
You are a Junior Frontend Developer who has just joined "EfficientlyYou," a rapidly growing productivity SaaS startup. The company's mission is to empower users to seamlessly manage their daily tasks and increase day-to-day productivity through an easy-to-use, responsive to-do list web app. Amidst increased remote work and scattered task management tools, EfficientlyYou seeks to deliver a focused solution that helps users stay on top of their goals, minimize distractions, and quickly adapt to shifting priorities. As part of your first assignment, you are tasked with creating an interactive, productivity-focused to-do list web application using React. The app must make it intuitive for users to manage their tasks from any device and foster a modern digital workspace.

Project Objective:
Design and implement, within a 1-week sprint, a robust, user-friendly to-do list web application using React that will allow users to create, view, update, and delete their tasks, mark tasks as completed, edit tasks efficiently, clear single or all items, and filter their list based on active/completed/all status—all while ensuring a responsive interface for mobile and desktop users.

Deliverables:
A complete React-based web application repository (with installation and run instructions), and a short written summary explaining your component design decisions and test coverage.

Feature Requirements (Strictly Adhere To):

- Create, read, update, and delete (CRUD) to-do items
- Mark to-do items as completed
- Edit existing to-do items (inline or via modal)
- Delete single or all to-do items
- Display lists based on: active, completed, or all items
- Basic responsive design (mobile/tablet/desktop-friendly, using CSS or a UI framework)

Learning Outcomes:
This project is specifically designed for Beginner to Intermediate Full Stack Developers (assumed familiar with JavaScript, npm, and basic React concepts). Completing the assignment will demonstrate:

- Practical React app building skills: Develop a working web app tool using React functional components and hooks.
- Understanding of component-based UI design: Break down features into reusable, maintainable React components.
- Hands-on CRUD operations integration: Implement full CRUD lifecycle management of tasks using state and props.
- Front-end testing basics: Write at least one simple test per main UI component (using Jest/React Testing Library or similar; e.g., rendering and task creation).

Project Execution Plan
(This plan structures the 1-week timeline and matches your experience level.)

Day 1: Setup and Component Planning
- Initialize a new React app (using Create React App or Vite).
- Design your component hierarchy (e.g., App, ToDoList, ToDoItem, ToDoFilter, ToDoInput).
- Create static component files and basic layout.

Day 2: Implement Core CRUD Functionality
- Develop the ToDoList and ToDoItem components.
- Add state management for tasks (using useState/useReducer).
- Implement "create," "read," and "delete" functionality for to-do items.

Day 3: Update, Edit, and Completion Features
- Add editing of existing to-do items (double-click to edit or an 'Edit' button).
- Implement "mark as completed" functionality (toggle checkbox/icon).
- Style completed items differently for clear visual distinction.

Day 4: Filtering and Bulk Actions
- Add filter buttons/tabs to switch between active, completed, and all to-do views.
- Implement "delete all" functionality and support for deleting completed items only.

Day 5: Basic Responsive Design
- Apply a CSS solution (plain CSS, CSS Modules, or a framework like Bootstrap/Tailwind) for layout and responsiveness.
- Ensure the app looks and works well on mobile and desktop screens.

Day 6: Front-End Testing
- Set up a basic test suite (using Jest and React Testing Library or similar).
- Write simple tests for main components: rendering, adding, marking, and deleting items.

Day 7: Review, Documentation, and Submission
- Refactor code for clarity, comment important logic, and ensure all listed features work.
- Write a concise summary (1-2 paragraphs) explaining your component design and test approach.
- Add clear installation and run instructions to the README.

Evaluation Rubric (Self-Checklist)
- All required features are present and function as described.
- Codebase is structured with clear, reusable components.
- The UI is responsive and accessible.
- At least one test per main component passes.
- Code quality (formatting, naming, comments).
- README includes install/run steps and a design summary.

Assumptions & Target Audience Alignment:
You are at a beginner to intermediate level, comfortable with JS, npm, and basic React development. No backend setup is required (local state only). The design and features fit the real-world needs of productivity enthusiasts and remote workers seeking to optimize their daily workflow with a straightforward digital task organizer.

Technology Focus:
- Web Application Development (Frontend only)
- React with functional components, hooks, and basic state management
- CSS (your choice of implementation)
- Optional: One testing library for component/unit tests

Key Constraints:
- Do not add features beyond the specified set.
- Keep the project self-contained (no backend, no API).
- Do not implement authentication, user management, or non-productivity features.
- Focus all effort on delivering the best possible productivity to-do list web app with a modern, responsive frontend and reliable core functionality.

By completing this challenge, you will:
- Build practical skills in React development from scratch (installation to deployment).
- Cement your understanding of component-based architecture and props/state flows.
- Master CRUD operations in the context of a productivity tool.
- Practice best practices for UI testing and build confidence for future full-stack projects.

This project simulates an authentic industry scenario and will prepare you to contribute meaningfully to productivity-focused web applications while reinforcing all essential web frontend skills for your level.

---

## What you will learn:

- Build a functional interactive frontend web app with React

- Apply state management and React hooks in a real scenario

- Design and compose reusable UI components

- Integrate basic UI testing strategies for React apps

- Develop basic CRUD user interaction flows


---

## What you need to know:

- Node.js (v16+)

- npm or yarn package manager

- Code editor (Visual Studio Code recommended)

- Basic command line skills


---

## Modules and Activities:


### 📦 Core To-Do List Functionality: Adding, Editing, Deleting, and Marking Tasks


#### ✅ Add a New To-Do Item

**🎯 Goal:**  
Demonstrate the ability to add a new task to the to-do list using controlled input in a React functional component.

**🛠 Instructions:**  

- Open the main to-do list interface in the provided React project.

- Locate the task input field above or within the to-do list.

- Type a descriptive task (such as 'Complete React assignment') into the input.

- Submit the new task by pressing Enter or clicking the 'Add' button.

- Verify that the new task now visibly appears at the top or bottom of your to-do list.


**📤 Expected Output:**  
A new to-do item is added and appears in the list. The input field clears after submission.

---

#### ✅ Edit and Update an Existing To-Do Item

**🎯 Goal:**  
Show the ability to efficiently modify the text/content of an existing task.

**🛠 Instructions:**  

- In your displayed to-do list, select an existing task that you wish to change.

- Initiate editing using either a double-click on the task text or by clicking the provided 'Edit' button/icon.

- Modify the task content by typing new text in the provided editing field.

- Confirm the update using the save or confirmation control.

- Ensure that the edited to-do now shows the updated content in the main list.


**📤 Expected Output:**  
The selected to-do item is updated and immediately displays the new text, replacing the previous content.

---

#### ✅ Delete an Individual To-Do Item

**🎯 Goal:**  
Demonstrate the ability to remove a specific task from the to-do list.

**🛠 Instructions:**  

- Find any to-do item in your list that you wish to delete.

- Click the delete or remove icon/button associated with that specific to-do item.

- Confirm the action if prompted.

- Visually verify that the deleted task is no longer present in the list.


**📤 Expected Output:**  
The selected to-do item is fully removed from the list with no trace in the current UI.

---

#### ✅ Mark a To-Do as Completed or Active

**🎯 Goal:**  
Show that you can toggle a to-do item's completion status and provide clear visual distinction between states.

**🛠 Instructions:**  

- For any to-do item in your list, find the completion checkbox or toggle control.

- Click the control to mark the item as completed.

- Check that the completed task appears visually distinct (e.g., grayed out or with a strikethrough effect).

- Now, toggle the item back to active (uncompleted) by clicking the same control again.

- Confirm that the item reverts to its normal, active appearance.


**📤 Expected Output:**  
Tasks can be toggled between completed and active states, with evident visual feedback reflecting their current status.

---



### 📦 Bulk Actions and To-Do List Views: Clearing and Filtering Tasks


#### ✅ Clear All Completed To-Do Items

**🎯 Goal:**  
Demonstrate ability to bulk-delete all completed tasks without affecting active ones.

**🛠 Instructions:**  

- Mark at least two tasks as completed and verify their completed status.

- Locate and activate the control labeled 'Clear Completed' or similar.

- Confirm the action if asked.

- Check the list to ensure that all completed tasks have been removed, but active tasks remain.


**📤 Expected Output:**  
All completed to-dos are removed from the list, while all active to-dos persist without change.

---

#### ✅ Filter To-Dos by Status: All, Active, Completed

**🎯 Goal:**  
Demonstrate the ability to view tasks based on their completion status using filtering UI controls.

**🛠 Instructions:**  

- Create a set of tasks and mark some as completed, leaving others as active.

- Locate filter buttons or tabs labeled 'All', 'Active', and 'Completed' below or above the list.

- Click the 'Active' filter and verify that only uncompleted (active) tasks are displayed.

- Switch to the 'Completed' filter to display only completed tasks.

- Return to the 'All' filter to see the entire list.


**📤 Expected Output:**  
Switching filters reliably displays only the relevant tasks: all, only active, or only completed, according to the selected view.

---


