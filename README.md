# TNBarMenu

## Introduction

TNBarMenu is a project created for the communication of the bar of the Telecom Nancy school. It allows the bar to generate and display weekly menus, including meal options and other relevant information. The project is now **fully frontend-based**, with all computation done in the browser using HTML/CSS for menu rendering. No backend server is required!

## Features

- **Frontend-Only Architecture**: All menu generation and rendering happens in the browser
- **HTML/CSS Menu Rendering**: Beautiful menu layouts using browser rendering engine
- **localStorage Persistence**: Custom sandwiches and menu data stored locally
- **No Image Export Needed**: Menus are rendered directly in HTML/CSS, ready for screenshots
- **Customizable Layouts**: Vertical and horizontal menu layouts with configurable styles
- **Email Text Generation**: Automatic generation of mailing list text with ingredient information

## Installation

To set up the project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Ozraam/TNBarMenu.git
   cd TNBarMenu
   ```

2. Install dependencies:
   ```bash
   npm install
   # or if you have Bun installed
   bun install
   ```

3. Start the development server:
   ```bash
   npm run dev
   # or with Bun
   bun run dev
   ```

4. Open the app in your browser:
   ```bash
   npm run dev -- --open
   # or with Bun
   bun run dev --open
   ```

## Usage

### Creating Menus

1. Open the application in your browser
2. Use the customization panel to add meals and text for each day
3. Click "Generate Images" to render the menu
4. Click on the rendered menu to download it as PNG

### Adding Custom Sandwiches

1. Navigate to the "New Sandwich" page
2. Fill in the sandwich details:
   - Name
   - Image code (or upload an image)
   - French and English descriptions
   - Mark as vegetarian if applicable
3. Submit the form
4. Your custom sandwich will be available in the meal selector

### Keyboard Shortcuts

- `Ctrl+K` (or `Cmd+K` on Mac): Open command palette for quick meal selection

## Building for Production

To create a production version of your app:

```bash
npm run build
# or with Bun
bun run build
```

You can preview the production build with:

```bash
npm run preview
# or with Bun
bun run preview
```

## Docker Deployment

Build and run with Docker:

```bash
docker-compose up -d
```

The application will be available at `http://localhost:3000`.

## Data Storage

All data is stored locally in the browser:
- **Static Data**: Meal lists, ingredients, and style configuration from `/static` folder
- **Custom Data**: Custom sandwiches and menu configurations in browser localStorage
- **No Backend Required**: Everything runs client-side

## Contributing

We welcome contributions to the TNBarMenu project! If you would like to contribute, please follow these guidelines:

1. Fork the repository and create a new branch for your feature or bugfix.
2. Make your changes and ensure that the project builds and runs correctly.
3. Submit a pull request with a clear description of your changes and the problem they solve.

