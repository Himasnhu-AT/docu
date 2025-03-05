# Pull Request Guidelines

This document outlines the process for submitting and reviewing pull requests for Docu.

## Creating a Pull Request

1. **Fork and Clone**: Start by forking the repository and cloning it locally

2. **Create a Branch**: Create a branch for your changes

   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Make Changes**: Implement your changes, following the [code style guidelines](./code-style)

4. **Write Tests**: Add tests for your changes to ensure they work correctly

5. **Run Tests**: Make sure all tests pass before submitting

   ```bash
   pytest
   ```

6. **Commit Changes**: Use clear and descriptive commit messages

   ```bash
   git commit -m "Add feature: detailed description of changes"
   ```

7. **Push Changes**: Push your changes to your fork

   ```bash
   git push origin feature/my-new-feature
   ```

8. **Create Pull Request**: Open a pull request on GitHub with a clear title and description

## Pull Request Template

When creating a pull request, please include:

- **Title**: A clear and descriptive title
- **Description**: Details of what was changed and why
- **Related Issues**: Link to any related issues
- **Testing**: How you tested your changes
- **Checklist**:
  - [ ] Added tests
  - [ ] Updated documentation
  - [ ] Code follows style guidelines
  - [ ] All tests pass

## Review Process

1. At least one maintainer will review each pull request
2. Feedback may be provided and changes requested
3. Once approved, a maintainer will merge the pull request

## After Merge

After your pull request is merged:

1. Delete your branch
2. Update your local master/main branch
3. Start a new branch for any further changes

Thank you for contributing to Docu!

```

```
