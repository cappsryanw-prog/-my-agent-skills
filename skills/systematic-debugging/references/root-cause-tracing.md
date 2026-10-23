# Root Cause Tracing

Load this when an error shows up deep in a call chain and it isn't clear where the bad value came from.

## Why trace backward

Errors usually appear far from their cause. A file lands in the wrong folder, a query runs against the wrong table, a total comes out negative. The line that failed is just where the bad value finally did damage. Fixing that line hides the symptom and leaves every other path that uses the bad value still broken.

## The steps

1. **Write down the symptom exactly.** "Report saved to the project root instead of `output/`."
2. **Find the line that directly caused it.** The call that wrote the file, sent the request, or did the math.
3. **Look at the values it received.** Print them right before that line. Here, the output path was an empty string, which the file API treats as "current directory".
4. **Ask who passed that value, and repeat.** Follow the call chain up one level at a time: the save function got it from the report builder, which got it from the settings loader.
5. **Stop at the origin.** The place where the value was first created wrong. Here, the settings loader read `OUTPUT_DIR` before the config file was loaded, so it got an empty default.
6. **Fix at the origin.** Load config before reading it, and make the loader fail loudly if `OUTPUT_DIR` is empty instead of returning `""`.

## When you can't trace by reading

Add temporary instrumentation right before the risky operation:

- Log the inputs, the working directory, and the relevant environment variables
- Log a stack trace, so you can see every caller (`new Error().stack` in JavaScript, `traceback.print_stack()` in Python)
- In test runs, write to stderr; some test runners and loggers hide normal output
- Log *before* the operation, not only after it fails

Run once, filter the output for your marker, and read which caller and which input produce the bad value. Remove the instrumentation once the cause is found.

## Finding which test causes it

If something goes wrong only when the full test suite runs (a stray file appears, shared data gets modified), run the test files one at a time and check for the side effect after each. The first file after which it appears is the polluter. Most runners can also run tests in a fixed order or a single file, which makes this quick to script.

## After the fix: guard the layers

Once the root cause is fixed, consider adding a check at each layer the bad value passed through, so a different path can't recreate the bug:

- **Entry point:** reject empty or invalid input where it enters (a function argument, a form field, a config value)
- **Business logic:** check the value makes sense for this operation before using it
- **Environment guard:** refuse dangerous operations in the wrong context (for example, refuse to write outside a temp folder while tests are running)
- **Logging:** record enough context that the next investigation is short

Not every bug needs all four. Add the guards that would have caught this bug sooner, and test that each one actually triggers.
