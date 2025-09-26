# Testing Guide for Valuebell Transcriber

## Overview

This document explains the testing strategy for the Valuebell Transcriber project, including baseline tests before modularization and ongoing testing during refactoring.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── unit/
│   ├── __init__.py
│   └── test_utility_functions.py  # Unit tests for individual functions
├── integration/
│   ├── __init__.py
│   ├── test_current_app.py        # Tests for current monolithic structure
│   └── test_main_processing.py    # End-to-end workflow tests
├── fixtures/
│   ├── sample_transcript.json     # Sample data for testing
│   └── expected_outputs/          # Expected output files
└── manual/
    └── README.md                  # Manual testing procedures
```

## Running Tests

### Quick Validation (No Dependencies Required)
```bash
python3 scripts/validate_functions.py
```
This validates core functions without requiring external dependencies.

### Full Test Suite (Requires Dependencies)
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest -m "not slow"        # Skip slow tests
```

### Manual Testing
See `tests/manual/README.md` for instructions on testing with real APIs and user interaction.

## Test Categories

### Unit Tests (`tests/unit/`)
- Test individual functions in isolation
- Use mocking for external dependencies
- Fast execution, no network calls
- Focus on edge cases and error handling

**Example functions tested:**
- `detect_file_source()`
- `convert_dropbox_to_direct()`
- `get_word_attr()`
- `format_txt_timestamp()`
- `format_srt_time()`

### Integration Tests (`tests/integration/`)
- Test complete workflows
- Mock external APIs (ElevenLabs, file downloads)
- Test file processing end-to-end
- Validate output formats

**Example workflows tested:**
- JSON transcript processing
- Audio file transcription (mocked)
- File download orchestration
- Error handling scenarios

### Manual Tests (`tests/manual/`)
- Tests requiring real API keys
- UI interaction testing
- Performance testing with large files
- Real-world scenario validation

## Test Fixtures and Mocking

### Shared Fixtures (`tests/conftest.py`)
- `temp_dir`: Temporary directory for test files
- `sample_elevenlabs_response`: Mock API response data
- `mock_elevenlabs_client`: Mocked ElevenLabs client
- `mock_subprocess`: Mocked ffmpeg/ffprobe calls
- `mock_requests`: Mocked HTTP requests
- `sample_audio_file`: Test audio file

### Mock Strategy
- **ElevenLabs API**: Mock all transcription calls
- **File Downloads**: Mock HTTP requests and file operations
- **FFmpeg**: Mock subprocess calls for audio processing
- **File System**: Use temporary directories for all file operations

## Validation Results

✅ **Baseline Validation Completed**
- 29 core function tests passed
- Test structure validated
- Ready for modularization

### Functions Validated
- File source detection (8 test cases)
- Dropbox URL conversion (5 test cases)
- Word attribute extraction (6 test cases)
- Timestamp formatting (10 test cases)

## Testing During Modularization

### Phase 1: Extract Module
1. Move code to new module
2. Update imports in tests
3. Run affected tests
4. Verify behavior unchanged

### Phase 2: Integration Testing
1. Test module interfaces
2. Verify end-to-end workflows
3. Check error propagation
4. Validate output consistency

### Phase 3: Regression Testing
1. Run complete test suite
2. Compare outputs with baseline
3. Performance benchmarking
4. Manual smoke testing

## Continuous Integration Recommendations

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r requirements-test.txt
    - run: pytest --cov=. --cov-report=xml
    - run: python3 scripts/validate_functions.py
```

## Test Coverage Goals

- **Unit Tests**: >90% coverage of utility functions
- **Integration Tests**: All major workflows covered
- **Error Handling**: All error paths tested
- **Edge Cases**: Boundary conditions validated

## Best Practices

1. **Test First**: Write tests before refactoring
2. **Small Changes**: Test after each small modification
3. **Mock External**: Never call real APIs in automated tests
4. **Clean Up**: Use temporary directories, clean up test files
5. **Document**: Keep test documentation updated

## Known Limitations

- Some tests require specific environment setup
- External dependencies may need manual installation
- Performance tests require large test files
- UI tests require manual validation

## Next Steps

1. ✅ Baseline tests created and validated
2. 🔄 **Ready to begin modularization**
3. ⏳ Module-by-module refactoring with tests
4. ⏳ Final integration testing
5. ⏳ Performance validation