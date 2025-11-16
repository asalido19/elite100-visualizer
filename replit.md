# Elite 100 Visualizer

## Overview

Elite 100 Visualizer is an interactive data visualization application built with Python Dash. The application analyzes and displays performance data for elite vehicles, allowing users to explore lap times and vehicle characteristics through interactive filtering and real-time visualization. Users can filter vehicles by brand, drivetrain type, and engine configuration to analyze performance patterns across different vehicle categories.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Choice: Dash + Plotly + Bootstrap Components**
- **Problem**: Need for interactive data visualization with minimal JavaScript development
- **Solution**: Dash framework provides a Python-native way to build reactive web applications
- **Rationale**: 
  - Allows full-stack development in Python without writing JavaScript
  - Plotly integration provides rich, interactive visualizations out of the box
  - Dash Bootstrap Components (dbc) offers pre-styled UI elements for professional appearance
- **Trade-offs**: 
  - Pros: Rapid development, Python-only codebase, extensive visualization library
  - Cons: Less flexibility than pure JavaScript frameworks, larger bundle sizes

**Reactive UI Pattern**
- Uses Dash callbacks to update visualizations in real-time based on user filter selections
- Filter inputs (brand, drivetrain, engine type) trigger callback functions that regenerate plots
- State management handled automatically by Dash's callback system

**Custom Styling**
- Custom CSS in `assets/custom.css` for dropdown component styling
- Overrides default Dash Select component styles to ensure readability (black text on white background)
- Z-index management for proper dropdown layering

### Backend Architecture

**Data Processing Layer**
- **Single-file architecture**: All logic contained in `app.py` for simplicity
- **CSV-based data source**: Vehicle performance data stored in `elite100.csv`
- **Pandas for data manipulation**: 
  - Provides efficient data cleaning and filtering operations
  - Handles missing values and data type conversions
  - Enables complex aggregations and transformations

**Time Parsing System**
- **Problem**: Lap times stored in varied string formats (MM:SS.SSS or SS.SSS)
- **Solution**: Custom regex-based parser (`parse_time_to_seconds`) converts all time formats to numeric seconds
- **Implementation**: 
  - Handles both minute:second and second-only formats
  - Converts to float for mathematical operations and plotting
  - Gracefully handles malformed or missing data with NaN values

**Data Cleaning Pipeline**
- Automatic whitespace stripping from column names and string values
- Type detection and conversion for proper data handling
- Applied during initial data load to ensure consistency

### Data Storage

**File-based Storage**
- **Choice**: CSV flat file (`elite100.csv`)
- **Rationale**: 
  - Dataset is static and relatively small (100 entries)
  - No need for database overhead
  - Easy to edit and version control
  - Fast loading for in-memory processing
- **Trade-offs**:
  - Pros: Simple, portable, version-controllable, no server dependencies
  - Cons: Not suitable for large datasets, no concurrent write support, limited query capabilities

**In-Memory Processing**
- Data loaded once at application startup into Pandas DataFrame
- All filtering and aggregations performed in-memory
- Fast response times for interactive operations

### Application Architecture Patterns

**Server-Side Rendering with Client-Side Interactivity**
- Initial page load generates static HTML structure
- User interactions (filter changes) trigger server callbacks
- Server regenerates plot data and sends updates to client
- Plotly handles client-side rendering and interaction (zoom, pan, hover)

**Modular Code Organization** (as evidenced by function structure)
- Data loading and parsing separated into dedicated section
- Time parsing abstracted into reusable function
- Callback decorators keep UI logic separate from business logic

### Deployment Configuration

**Environment Detection**
- **Production Deployment**: Detected via `REPLIT_DEPLOYMENT=1` environment variable
  - Binds to `0.0.0.0:8050` (matches `.replit` port mapping for external port 80)
  - Debug mode disabled for performance and stability
  - Suitable for published apps with health checks
- **Development (Replit Workspace)**: Detected via `REPL_ID` environment variable
  - Binds to `0.0.0.0:5000` (Replit's standard webview port)
  - Debug mode enabled for live reloading and error details
  - Accessible via `.replit.dev` development URL
- **Local Development**: Default when no Replit environment variables present
  - Binds to `127.0.0.1:5000` (localhost)
  - Debug mode enabled for development

**Port Configuration**
- Development uses port 5000 for Replit webview compatibility
- Deployment uses port 8050 as configured in `.replit` file (external port 80)
- Automatic port selection based on environment ensures seamless transitions between development and production

## External Dependencies

### Python Libraries

**Dash (v2.14.2)**
- Core framework for building the web application
- Provides component library and callback system
- Handles routing and server management

**Dash Bootstrap Components (v1.5.0)**
- Pre-built Bootstrap components for Dash
- Provides responsive layout system
- Offers styled dropdowns, cards, and other UI elements

**Plotly (v5.18.0)**
- Interactive visualization library
- Generates JavaScript-based charts from Python
- Supports hover interactions, zooming, and panning

**Pandas (v2.1.3)**
- Data manipulation and analysis
- CSV file reading and parsing
- DataFrame operations for filtering and aggregation

**NumPy (v1.26.2)**
- Numerical computing support
- Handles NaN values in time parsing
- Provides mathematical operations for data transformations

### Static Assets

**Custom CSS**
- Located in `assets/` directory (Dash convention)
- Automatically loaded by Dash at runtime
- Provides dropdown styling overrides for improved UX

### Data Files

**elite100.csv**
- Primary data source containing vehicle performance metrics
- Expected columns include: Brand, Drivetrain, Engine type, lap times
- Consumed during application initialization