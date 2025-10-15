# API Reference

## Overview

This document provides an overview of the API endpoints available in the TNBarMenu project. The API is used to manage and generate weekly menus for the bar of the Telecom Nancy school.

## Endpoints

### `GET /getMealList`

- **Description**: Retrieves the list of available meals.
- **Response**: A JSON array containing meal objects with `name` and `image` properties.

### `POST /addSandwich`

- **Description**: Adds a new sandwich to the meal list and optionally uploads its image.
- **Request**: Accepts form-data or JSON with the following fields:
  - `name` (required): Display name of the sandwich.
  - `image` (optional if `imageFile` provided): Image code used when generating menus.
  - `frenchDescription` (optional): French description shown in the admin UI.
  - `englishDescription` (optional): English description; defaults to the French description.
  - `isVegetarian` (optional): Boolean flag indicating whether the sandwich is vegetarian.
  - `imageFile` (optional): Uploaded image file; converted to PNG and stored in `Sandwichlogo`.
- **Persistence**: Basic sandwich metadata is stored in `mealList.json`; ingredient descriptions are appended to `ingredients.json`.
- **Response**: On success returns HTTP `201` with a JSON object containing a `message`, the meal entry, and the stored ingredient metadata. Validation errors return HTTP `400` with a JSON message, while conflicts return HTTP `409`.

### `GET /getLastMenu`

- **Description**: Retrieves the last generated menu.
- **Response**: A JSON object containing the menu data, including headers and content for each day.

### `GET /generateImages`

- **Description**: Generates images based on the provided menu options.
- **Query Parameters**:
  - `menu`: A string representing the CLI command for generating the menu images.
- **Response**: A JSON object containing the URLs of the generated images (`horizontal` and `vertical`).

### `GET /getMailingText`

- **Description**: Retrieves the text for the mailing preview.
- **Response**: A JSON object containing the mailing text.

### `GET /horizontalMenu`

- **Description**: Retrieves the horizontal menu image.
- **Query Parameters**:
  - `epoch`: A timestamp representing the version of the image.
- **Response**: The horizontal menu image.

### `GET /verticalMenu`

- **Description**: Retrieves the vertical menu image.
- **Query Parameters**:
  - `epoch`: A timestamp representing the version of the image.
- **Response**: The vertical menu image.
