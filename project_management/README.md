# Project Management Log - Pac-Man 42

## Team Roles & Responsibilities
* **Sara (saalomar):** Focused on Backend Logic, Game Engine state management, collision algorithms, and external package adaptation via the Adapter Pattern.
* **alaa (alalnusa):** Focused on UI/UX Rendering pipeline, Pygame window management, HUD tracking, and highscore JSON serialization.

## 30-Day Sprint Breakdown
* **Days 1-7:** Repository setup, subject analysis, and `MazeAdapter` integration.
* **Days 8-14:** Decoupling Monolithic loops into separate `GameEngine` and `GameRenderer` modules.
* **Days 15-21:** Implementing Pac-Man controls, autonomous Ghost pathfinding, and power-up states.
* **Days 22-30:** Highscore persistence, strict `mypy` / `flake8` compliance checking, and peer-review cheat code testing.

## Risk Management & Resolutions

### Blocking Point 1: Motion Overhead & Sub-optimal Pathfinding
* **Description:** Initial ghost and Pac-Man movement algorithms triggered erratic path overhead, causing actors to exceed required directional bounds and move inefficiently.
* **Resolution:** Restricted translation trajectories directly onto tile center-points through rigid grid-based coordinate clamping (`Grid-based checking`). This minimized redundant steps and optimized search paths.

### Blocking Point 2: Dynamic Window Size & HUD Clipping
* **Description:** Variations in maze matrices generated procedurally by the third-party `A-Maze-ing` library across levels caused HUD metrics (score, time) to clip or disappear below layout borders.
* **Resolution:** Re-engineered the window canvas to scale dynamically according to map grids (`matrix length * tile_size`) and added a dedicated, permanent 50-pixel buffer layout at the bottom edge strictly reserved for the HUD.