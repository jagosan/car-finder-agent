# Gemini CLI Constraints

This document outlines specific operational constraints for the Gemini CLI agent.

## Sudo Permissions

The agent is explicitly forbidden from executing commands with `sudo`. Any required `sudo` operations will be performed manually by the user.

## Python Package Installation

When attempting to install Python packages, the `pip` command may not be directly available in the agent's environment, resulting in a "command not found" error. To successfully install Python packages, use the `python3 -m pip install` command instead of `pip install`.

## Tooling and Authentication Hints

To improve efficiency and avoid repeating mistakes, this `GEMINI.md` file should be continuously updated with hints and best practices regarding authentication, tool calling, and common operational procedures. This includes, but is not limited to, `gcloud` authentication, `kubectl` usage, and Docker commands.