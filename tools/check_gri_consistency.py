#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI↔TSRS ve SDG↔GRI uyumluluk denetimi (CLI)
"""

import logging
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from gri.gri_reporting import GRIReporting

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    rep = GRIReporting()
    result = rep.check_consistency()
    logging.info(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
