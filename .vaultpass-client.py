#!/usr/bin/env python3
import os
import sys

envvar_vault_pass = "VAULT_PASSWORD"

if os.environ.get(envvar_vault_pass) is not None and os.environ.get(envvar_vault_pass) != "":
    print(os.environ[envvar_vault_pass])
else:
    print("ERROR: '" + envvar_vault_pass + "' is not set in environment")
    sys.exit(1)
