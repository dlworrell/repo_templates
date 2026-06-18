# PROJECT_NAME

PROJECT_DESCRIPTION

This is the C23 library repository template.

## Repository Type

Template: c_library
Template version: 0.1.0

## Intended Use

Use this template for portable C libraries built with CMake and tested with CTest.

## Standard Contents

- README.md
- LICENSE
- CHANGELOG.md
- CONTRIBUTING.md
- SECURITY.md
- CODE_OF_CONDUCT.md
- CMakeLists.txt
- include/
- src/
- tests/
- examples/
- docs/
- cmake/
- .github/

## Build

```sh
cmake -S . -B build -G Ninja
cmake --build build
ctest --test-dir build
```

## License

LICENSE_NAME
