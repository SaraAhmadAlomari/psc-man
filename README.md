*This activity has been created as part of the 42 curriculum by alalnusa, saalomar.*

# Description

Pac-Man 42 is a modern, modular, and object-oriented recreation of the classic 1980 Namco arcade game, developed in Python 3.10+ using Pygame. The project features dynamic maze generation using an external package, a persistent highscore tracking system, customizable JSON configurations, an interactive HUD, and built-in developer cheat tools designed specifically for peer review validation

# Instructions

## Installation

Clone the repository:

```bash
git clone <repository_url>
cd <project_directory>
```

Install dependencies (if applicable):

```bash
make install
```

## Execution

To run the project:

```bash
make run
```

or manually:

```bash
python3 main.py config.json
```

## Debug Mode

To run in debug mode:

```bash
make debug
```

## Code Quality

To run linters and static analysis tools:

```bash
make lint
make lint-strict
```

# Configuration

The project uses a JSON configuration file (`config.json`) to control runtime behavior.

Example structure:

```json
{
  "window_width": 800,
  "window_height": 600,
  "cell_size": 20,
  "maze_width": 25,
  "maze_height": 25,
  "difficulty": "medium"
}
```

### Default Values

If no configuration file is provided, the system will use default values defined in the configuration module.

# Highscore

The highscore system stores player performance data such as score, time, or completion metrics.

Scores are saved locally in a persistent file (e.g., `highscores.json`).
Constraints: User nicknames are limited to a maximum of 10 characters (alphanumeric and spaces only).
Display: It updates and isolates the Top 10 performance profiles which render directly onto the Main Menu UI.
This approach was chosen for simplicity, portability, and ease of testing without requiring external databases.

# Maze Generation

The structural layout of each map is generated using an external assigned A-Maze-ing package.

Integration Rule: The package is integrated completely as-is without any direct modifications.

Adaptability: Our codebase utilizes an Adapter pattern (MazeAdapter) to cleanly translate the external tool's interface into a layout digestible by our Pygame layout engine.

Corridor Generation: The generator parameters explicitly enforce PERFECT = False to introduce multi-path loops and Pac-Man compatible corridors instead of strict trees.

Seed Logic: The first level initiates using a fixed configuration seed (42), while subsequent maps generate procedurally with randomized seeds to maintain dynamic difficulty.

# Implementation

The project is implemented using a modular architecture:

* **Core Engine**: Handles game loop, updates, and state management.
* **Renderer**: Responsible for drawing the maze, player, and UI elements.
* **Configuration Module**: Parses and validates JSON config files.
* **Highscore Manager**: Handles saving and loading leaderboard data.
* **Maze Module**: Integrates A-Maze-ing package and converts output.

This separation of concerns ensures maintainability and scalability.

# General Software Architecture

main.py: The centralized bootstrapper. It parses configurations, initializes assets, and boots the controller.

src/game_engine.py: The central nervous system. Manages state machines (menu, playing, paused, name_entry), delta clocks, path updates, and collision detections.

src/renderer.py: The dedicated graphics pipeline. Handles drawing functions, vector math for grids, lines, color mappings, menus, text layouts, and overlay screens.

src/entities.py: Defines structural classes for actors (PacMan, Ghost) implementing distinct state attributes (e.g., standard, frightened, dead).

## Project Management
This project was systematically engineered over a focused **30-day (1-month)** operational cycle using an agile team matrix.
* **Artifacts & Logs:** Comprehensive execution timelines, risk mitigation logs, and team responsibilities are explicitly structured within the dedicated [/project_management](./project_management) subdirectory.

# Resources

## References

* 42 Curriculum Documentation
* Python Official Documentation: [https://docs.python.org/](https://docs.python.org/)
* JSON Schema Guide: [https://json-schema.org/](https://json-schema.org/)
* A-Maze-ing package documentation (if applicable)

## AI Usage

AI tools were used to:

* Improve documentation clarity and formatting
* Provide suggestions for architecture and section organization
* Debug and explain configuration and implementation concepts
AI was not used to replace core implementation logic but to support documentation and understanding of the project structure.
