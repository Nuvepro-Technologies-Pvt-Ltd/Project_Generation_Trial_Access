## What you will do:

**Problem Statement**  
Scenario-Based Problem Statement for a React-Powered Ingredient Recipe Search Application

Scenario:  
You have just joined Nourishio, a startup specializing in digital solutions for home cooks and food enthusiasts. The current industry trend is toward highly interactive web applications that make everyday tasks—like finding recipes based on available pantry ingredients—more accessible and visually appealing. Your product manager has identified a critical need: many users struggle to figure out what to cook with leftovers or when supplies are limited. Your task is to build the core frontend for an Ingredient-based Recipe Search application.

Your Role:  
As a Frontend Developer specializing in React, you are responsible for delivering a robust, clean, and user-friendly search interface. Your project must allow users to enter a list of ingredients and receive relevant recipes from a third-party recipe API. The focus is on creating a seamless user experience, managing asynchronous data fetching, and designing maintainable, well-structured React components.

Project Objective:  
Develop a minimal, visually clean React web application that enables users to input ingredients, fetches matching recipes from a recipe API, and displays each result with the recipe title, a list of required ingredients, and clear preparation steps. The app must handle loading and error states gracefully and maintain a clear separation of UI concerns using modular React components.

Key Features & Requirements (strictly adhere to these):
- Ingredient input search bar: Users can enter one or more ingredients to search for recipes.
- Fetching recipes via API based on user input: When the search is initiated, your app must fetch recipes from a public API that supports ingredient-based searching (e.g., Edamam, Spoonacular, or mock/fake API).
- Display each recipe with title, list of ingredients, and preparation steps: Results must present this data clearly.
- Minimal clean UI with error/loading states: Show loading indicators during async fetches and user-friendly error messages for failed requests or empty results. The visual style should remain uncluttered and modern.
- Clear separation of concerns in components: Use a modular component structure (e.g., SearchBar, RecipeList, RecipeCard, Loading, ErrorMessage) for maximum maintainability.

Target Learner Profile:
- Skill Level: Beginner to Intermediate JavaScript and frontend developers who have completed basic React tutorials and have some experience with JavaScript ES6+ features, but are new to API integration and professional UI building.
- Assumptions: Learners understand React fundamentals (components, props, state) but have little or no experience with API calls, error handling, UI state management, or component architecture.
- The project is designed as a 2–3 day sprint, suitable for individuals or groups.

Learning Outcomes:
By successfully delivering this project, you will:
- Demonstrate the ability to build a React-based web app that interacts with a third-party API, handling asynchronous operations and updating the UI based on server responses.
- Enhance practical UI/UX skills by designing user interactions, managing input states, and providing clear feedback for loading and error conditions.
- Gain experience in designing, implementing, and testing simple, reusable, and data-driven UI components for a real-world use case.

Project Tasks & Steps:
Over a 2–3 day period, you are expected to:

Day 1:
1. Scaffold a basic React app using Create React App or Vite. Remove unnecessary boilerplate to keep the codebase clean and focused.
2. Implement the Ingredient Input Search Bar as a controlled React component. Users should be able to type comma-separated ingredients and submit the search via a button or "Enter" key.
3. Establish main component structure: at minimum, create SearchBar, RecipeList, RecipeCard, LoadingIndicator, and ErrorMessage components.

Day 2:
4. Integrate an API fetch function in the main App component or a dedicated service. Use Fetch or Axios to request recipes based on the user’s input ingredients. Make sure to handle the API key securely if using a real service, or substitute with a public demo endpoint or hardcoded demo data if needed.
5. Populate RecipeList with a dynamic list of RecipeCard components upon successful fetch. Each RecipeCard must display:
   - The recipe’s title,
   - The full ingredient list,
   - Step-by-step preparation/method instructions (use placeholders if not provided by the API).
6. Add and display UI states:
   - Loading: Show LoadingIndicator while request is pending.
   - Error: Show ErrorMessage if the request fails, if the API returns zero results, or if the input is invalid.
   - Success: Show the fetched list of recipes.
7. Style the application using simple CSS or a preferred UI library—prioritize readability, proper alignment, and an overall clean appearance.

Day 3:
8. Refine component separation and code structure for maintainability—pass data via props, avoid unnecessary logic in UI components, and use functional components/hooks where possible.
9. Conduct basic manual tests:
   - Enter valid and invalid ingredient combinations.
   - Induce API errors (e.g., disconnect from network).
   - Verify that the loading and error states respond correctly.
10. Optional stretch: Refactor for reusability or add UI polish (e.g., responsive layout, small hover effects).
   
Deliverables:
- A GitHub repository containing the complete React project.
- A "README.md" file with a short description, clear setup instructions, and a summary of features implemented.
- Clear documentation within code, especially separating concerns in components and handling props/state.

Success Criteria:
- The app should run locally without errors.
- Users can submit an ingredient list and reliably fetch and view recipes matching the search.
- The user is never left guessing: loading and error states are always clearly presented.
- The codebase demonstrates componentized architecture with clear separation of UI, logic, and data fetching concerns.

Key Technologies and Constraints:
- Use only React (and its ecosystem: hooks, basic state management, CSS-in-JS or plain CSS as desired)
- No backend, routing, or database work—focus strictly on frontend features defined above
- No extraneous features or libraries outside the specified scope

Industry Relevance:  
Solving this challenge mirrors real-world frontend tasks in food-tech and lifestyle applications, where search-driven interfaces and third-party integrations are essential to user satisfaction. Executing this project will solidify your ability to contribute effectively to modern frontend teams.

Stay focused on the defined features, put user experience first, and demonstrate your practical knowledge of React and asynchronous data integration!

---

## What you will learn:

- Understand the process of integrating a third-party recipe API in a React app

- Build simple, clean, and accessible UI components

- Effectively manage local component state and asynchronous data fetching

- Implement robust error and loading states in UI

- Test component and application logic with modern frontend tools


---

## What you need to know:

- Install Node.js and npm

- Basic JavaScript and React knowledge


---

## Modules and Activities:


### 📦 Core React Structure and UI Components


#### ✅ Build the Main Component Structure

**🎯 Goal:**  
Establish a modular React component structure to support a maintainable UI layout.

**🛠 Instructions:**  

- Review the provided project stub to identify where the main application logic should reside.

- Identify and outline the necessary UI components: a search bar for entering ingredients, a recipe list, individual recipe cards, a loading indicator, and an error message display.

- Within the existing folder/file setup, ensure that each component is represented as a functional React component, making use of hooks where applicable.

- Organize the components in a clear hierarchy: the main App component should render the other components as required, passing data via props where necessary.

- Do not implement any business logic or API calls yet—focus solely on creating placeholders for each component and verifying that they render as expected.


**📤 Expected Output:**  
A working single-page React UI skeleton where the SearchBar, RecipeList, RecipeCard, LoadingIndicator, and ErrorMessage components are visible (with placeholder content) in a clear and logical structure.

---

#### ✅ Design a Clean and Accessible Ingredient Search Bar

**🎯 Goal:**  
Implement a controlled search bar component that allows users to enter comma-separated ingredients.

**🛠 Instructions:**  

- Within the SearchBar component, ensure that the input field is controlled by React state, updating with each change the user makes.

- Add a visually clear button or configure the 'Enter' key to trigger a parent-defined search handler.

- Design the search bar with visual clarity in mind—ensure good spacing, accessibility (label association, keyboard navigation), and modern styling consistent with a minimal UI.

- Test the search bar by manually entering sample ingredients and triggering the submit action, ensuring that it correctly updates state and can send the user input to the main app logic.


**📤 Expected Output:**  
A visually clean and fully functional search bar component in React, where ingredient input and submission are managed as a controlled form and can trigger parent actions.

---



### 📦 API Integration and Data-driven UI


#### ✅ Integrate Ingredient-based Recipe Search via API

**🎯 Goal:**  
Connect the application to a public recipe API to fetch recipes based on the user's input ingredients.

**🛠 Instructions:**  

- Within the main App component or a dedicated service file, implement the logic to fetch recipe data from the provided or mock API endpoint using fetch or axios as permitted.

- Ensure user-provided input is validated and formatted as required by the API (e.g., split and trim comma-separated values).

- Handle asynchronous data fetching by updating loading states before starting and after completing the fetch.

- Account for unsuccessful fetches—capture and separately handle error scenarios such as network issues, invalid inputs, or empty results.

- Make sure that the API key (if any) is handled securely and not exposed unnecessarily within the UI code.


**📤 Expected Output:**  
The app fetches data from a recipe API using entered ingredients, properly handles the loading and error states, and stores the results in component state.

---

#### ✅ Display Fetched Recipes with Readable Layout

**🎯 Goal:**  
Render the list of recipes with clear presentation of title, ingredient list, and preparation steps.

**🛠 Instructions:**  

- Populate the RecipeList component with RecipeCard components by mapping over the recipes stored in state.

- For each RecipeCard, display the recipe's title, all the required ingredients, and a clearly formatted list or sequence of preparation steps.

- If the API does not supply preparation steps, use a simple placeholder indicating this data is unavailable.

- Ensure the recipe details are easy to scan and read, using suitable layout and minimal styling that prioritizes clarity.

- Test by running several valid and invalid searches and checking that the display updates appropriately for each set of results.


**📤 Expected Output:**  
A visually clean recipe list, where each recipe is presented as a card with its title, full list of ingredients, and readable preparation steps or an appropriate placeholder.

---



### 📦 User Feedback, UI States, and Final Polish


#### ✅ Implement Loading and Error State Feedback

**🎯 Goal:**  
Provide clear, context-sensitive user feedback for all loading and error scenarios.

**🛠 Instructions:**  

- Within the main App component, manage at least three UI states: idle (ready for input), loading (fetch in progress), and error (API or validation failure).

- Render the LoadingIndicator component prominently during any recipe fetch operation.

- Display the ErrorMessage component with a friendly, specific message any time an API call fails or input is invalid.

- Ensure these feedback states never overlap—only one should be visible at a time—and the user always knows what is happening.


**📤 Expected Output:**  
Dynamic feedback for loading and error conditions, using dedicated components and state logic, so the user is never left uncertain about the application's status.

---

#### ✅ Refine Layout for Readability and Responsive Minimal UI

**🎯 Goal:**  
Polish the user interface to ensure it is responsive, readable, and visually minimal.

**🛠 Instructions:**  

- Apply simple but consistent styles (using CSS or supported UI libraries) to align elements, ensure comfortable spacing, and maintain visual hierarchy.

- Test the layout on different window sizes and make minor responsive adjustments as needed (e.g., flexible margins, stack layout on small screens).

- Avoid visual clutter by limiting the number of colors, borders, and effects; focus on clarity and ease of use.

- Review the overall user flow—from entering ingredients through to recipe display—and make final tweaks for consistency and accessibility.


**📤 Expected Output:**  
A clean, minimal, and responsive UI where all elements are readable, visually aligned, and the app is pleasant to use on both desktop and smaller screens.

---


