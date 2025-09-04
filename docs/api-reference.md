# API Reference

## Overview

This document provides an overview of the API endpoints available in the TNBarMenu project. The API is used to manage and generate weekly menus for the bar of the Telecom Nancy school.

## Endpoints

### `GET /getMealList`

- **Description**: Retrieves the list of available meals.
- **Response**: A JSON array containing meal objects with `name` and `image` properties.

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
