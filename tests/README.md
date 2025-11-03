# Test Suite Documentation

This directory contains comprehensive test suites for the Roopkala Jewellers Billing System.

## Test Files

### 1. `test_suite.py` - Comprehensive Module Tests

Tests all core modules and functionality without GUI interaction.

**Coverage:**

- Module imports (calculator, database, PDF, label printer)
- Calculator functionality (arithmetic, tax calculations)
- Database operations (CRUD for categories, products, suppliers)
- PDF generator initialization and test PDF creation
- Label printer functionality
- Settings and configuration loading
- Folder structure verification
- Required files verification

**Run:**

```bash
python tests\test_suite.py
```

**Expected Results:** 36/36 tests passed (100%)

### 2. `test_advanced.py` - Business Logic Tests

Tests complex business logic, edge cases, and calculations.

**Coverage:**

- Override total calculations with amount allocation
- Complex multi-item invoices with large amounts
- Database integrity checks
- Edge cases (tiny/large quantities, zero handling)
- Different tax rate calculations (1.5%, 2.5%)
- Rounding behavior verification

**Run:**

```bash
python tests\test_advanced.py
```

**Expected Results:** 6/6 tests passed (100%)

## Running All Tests

From the project root directory:

```bash
# Run basic module tests
python tests\test_suite.py

# Run advanced business logic tests
python tests\test_advanced.py

# Or run both in sequence
python tests\test_suite.py ; python tests\test_advanced.py
```

## Test Results Summary

**Last Test Run:**

- Basic Module Tests: 36/36 passed (100%)
- Advanced Logic Tests: 6/6 passed (100%)
- **Overall: 42/42 tests passed (100%)**

## What Gets Tested

### ✅ Core Functionality

- All arithmetic calculations
- Tax calculations (CGST, SGST)
- Database CRUD operations
- PDF invoice generation
- Settings management

### ✅ Business Logic

- Invoice calculations with multiple items
- Override total feature with amount allocation
- Tax rate handling
- Decimal precision (weights to 3 decimals, money to 2 decimals)
- Rounding behavior

### ✅ Edge Cases

- Tiny quantities (0.001g)
- Large quantities (999.999g)
- Zero values
- Complex decimal amounts
- Reverse calculations (amount → rate)

### ✅ System Integrity

- All required folders exist
- All required files present
- Settings configuration valid
- Database schema intact
- Module imports working

## Known Limitations

1. **GUI Testing**: These tests don't cover GUI interactions. Manual GUI testing required.
2. **Database State**: Tests use the existing database, not a test database.
3. **File Generation**: Test PDFs are generated in the `invoices/` folder.

## Maintenance

- Run tests after any code changes
- Update tests when adding new features
- Keep test coverage above 95%
- Document any test failures

## Notes for Developers

- Tests are designed to run from the project root
- All import paths are relative to the parent directory
- Tests don't modify database data (read-only operations)
- Settings are loaded from `settings.json` in root

## Troubleshooting

**Issue:** Module import errors
**Solution:** Ensure you're running from the project root directory

**Issue:** Settings file not found
**Solution:** Run tests from root: `python tests\test_suite.py`

**Issue:** Database connection failed
**Solution:** Check that `jewelry_management.db` exists or will be created

---

**Last Updated:** November 2, 2025
**Status:** All tests passing ✅
