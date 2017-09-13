#!/usr/bin/env python
from jconfigure import configure


if __name__ == "__main__":
    print(configure(active_profiles=["LCL"], fail_on_parse_error=False))
