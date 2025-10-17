# Gemini CLI Constraints

This document outlines specific operational constraints for the Gemini CLI agent.

## Sudo Permissions

The agent is explicitly forbidden from executing commands with `sudo`. Any required `sudo` operations will be performed manually by the user.
