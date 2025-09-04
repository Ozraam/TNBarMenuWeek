# User Guide

## Overview

This user guide provides instructions on how to use the TNBarMenu project to generate and manage weekly menus for the bar of the Telecom Nancy school.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Bun](https://bun.sh/)
- [Git](https://git-scm.com/)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Ozraam/TNBarMenu.git
   cd TNBarMenu
   ```

2. Install dependencies:
   ```bash
   bun install
   ```

3. Start the development server:
   ```bash
   bun run dev
   ```

4. Open the app in your browser:
   ```bash
   bun run dev --open
   ```

## Using the Application

### Customizing the Menu

1. Open the application in your browser.
2. Use the interface to customize the weekly menu. You can add meal options, specify text for each day, and generate images for the menus.
3. Click the "Generate Images" button to create the menu images.

### Viewing the Menu

1. After generating the images, you can view the horizontal and vertical menu images in the application.
2. You can also preview the mailing text for the menu.

### Saving the Menu

1. To save the generated menu images, click on the images in the application. The images will be downloaded to your device.

## Troubleshooting

### Common Issues

- **Issue**: The development server does not start.
  - **Solution**: Ensure you have installed all dependencies by running `bun install`. Check for any error messages in the terminal and resolve them.

- **Issue**: The menu images are not generated.
  - **Solution**: Ensure the backend server is running and accessible. Check the console for any error messages and resolve them.

## Support

If you encounter any issues or have questions, please open an issue on the [GitHub repository](https://github.com/Ozraam/TNBarMenu/issues).

## Contributing

We welcome contributions to the TNBarMenu project! If you would like to contribute, please follow these guidelines:

1. Fork the repository and create a new branch for your feature or bugfix.
2. Make your changes and ensure that the project builds and runs correctly.
3. Submit a pull request with a clear description of your changes and the problem they solve.

