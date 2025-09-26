# JavaScript Strategy Scripts

This directory contains externalized JavaScript code for survey automation strategies.

## Overview

All JavaScript code has been moved from Python files to separate `.js` files for better maintainability, debugging, and reusability.

## Files

### Core Strategy Scripts

- **`matrix_strategy.js`** - Matrix question filling with specific rating level (A1-A7)
- **`matrix_random_strategy.js`** - Matrix questions with random rating selection (A5/A6/A7)
- **`input_strategy.js`** - Text/number input field filling
- **`radio_strategy.js`** - Radio button selection by label text matching
- **`checkbox_strategy.js`** - Checkbox selection by indices
- **`barrier_free_inclusion.js`** - Special inclusion strategy (A1 for barrier-free, A6 for others)

### Function Format

Each script exports a function that can be called from Python:

```javascript
function executeStrategyName(parameters) {
    // Strategy implementation
    return {
        // Results object
    };
}
```

## Usage

JavaScript files are loaded and executed via `JavaScriptLoader` utility:

```python
from src.utils.javascript_loader import JavaScriptLoader

js_loader = JavaScriptLoader()
result = js_loader.execute_script(
    driver,
    'script_name',
    'functionName',
    parameter1,
    parameter2
)
```

## Benefits of Externalization

1. **Better Maintainability** - JavaScript code is separate from Python logic
2. **Easier Debugging** - JavaScript can be tested independently in browser console
3. **Code Reusability** - Scripts can be shared across different Python components
4. **Version Control** - JavaScript changes are clearly visible in diffs
5. **IDE Support** - Better syntax highlighting and error detection for JavaScript

## Integration

All scripts are integrated into `SmartPlaybackSystem` through the `JavaScriptLoader` utility. The system automatically loads the appropriate script for each strategy pattern.