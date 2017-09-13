#!/usr/bin/env python
import json
from jconfigure import configure


if __name__ == "__main__":
    print(json.dumps(configure(), indent=2))
