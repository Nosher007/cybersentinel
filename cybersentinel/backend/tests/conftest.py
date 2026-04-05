"""
Shared test configuration.
Sets ENVIRONMENT=test before any app module is imported,
so rate limiters and other env-dependent features are disabled.
"""
import os

os.environ["ENVIRONMENT"] = "test"
