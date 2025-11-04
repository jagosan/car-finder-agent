# Gemini CLI Constraints

This document outlines specific operational constraints for the Gemini CLI agent.

## Sudo Permissions

The agent is explicitly forbidden from executing commands with `sudo`. Any required `sudo` operations will be performed manually by the user.

## Python Package Installation

When attempting to install Python packages, the `pip` command may not be directly available in the agent's environment, resulting in a "command not found" error. To successfully install Python packages, use the `python3 -m pip install` command instead of `pip install`.

## Tooling and Authentication Hints

To improve efficiency and avoid repeating mistakes, this `GEMINI.md` file should be continuously updated with hints and best practices regarding authentication, tool calling, and common operational procedures. This includes, but is not limited to, `gcloud` authentication, `kubectl` usage, and Docker commands.

## Project Workflow

- Always read `spec.md` and give a summary of what we have accomplished so far, and what the next steps are.
- Provide an update after a maximum of 1 minute for any long-running operations.
- Be rigorous in your debugging and always create a plan before trying to make incremental progress based on assumptions.
- Always provide an estimate of the time an operation is expected to take, and provide updates for any operation that is expected to take more than a minute.
- Never overwrite `captains-log.md`. It is intended to be a log of activities for posterity. Always append new entries to the log.