# Directory Tree Generator (DirViz)

A modern, user-friendly GUI application for generating and visualizing directory tree structures with an intuitive interface and theme support.

## Features

- **Intuitive File Browser**: Easily select directories from your file system
- **Interactive Tree View**: Hierarchical representation with checkboxes for easy selection
- **Selective Visualization**: Include or exclude specific files and directories
- **Custom Tree Generation**: Create formatted directory trees with proper indentation and branch characters
- **Light & Dark Themes**: Built-in theme support for comfortable viewing in any environment
- **Copy to Clipboard**: One-click copying of generated tree structures
- **Responsive UI**: Modern Qt-based interface with status feedback

## Installation

### Prerequisites

- Python 3.6 or higher
- PySide6

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/Arivald8/DirViz.git
   cd DirViz
   ```

2. Install dependencies:
   ```bash
   pip install PySide6
   ```

3. Run the application:
   ```bash
   python dirviz.py
   ```

## Usage

1. **Select a Directory**: Click the "Browse" button to choose a root directory
2. **Customize Selection**: Check/uncheck files and directories in the tree view
   - Use "Select All" or "Deselect All" buttons for quick selection
   - Parent directories automatically show partial selection when some children are selected
3. **Generate Tree**: Click "Generate Tree" to create a text representation
4. **Copy Result**: Use "Copy to Clipboard" to copy the generated tree
5. **Switch Themes**: Toggle between light and dark themes via the View menu

## Example Output

```
my_project/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
└── tests/
    ├── __init__.py
    └── test_main.py
```

## Development

The application is built with PySide6, a modern Python binding for the Qt framework. The codebase is organized as follows:

- `dirviz.py`: Main application file containing the UI and logic
- Directory visualization uses standard ASCII characters for compatibility
- Theme support with QPalette for consistent dark/light modes
- Settings persistence via QSettings

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

## Acknowledgments

- Built with [PySide6](https://wiki.qt.io/Qt_for_Python) (Qt for Python)
- Inspired by command-line tree utilities with added GUI convenience

---

Made with ❤️ by Arivald8
