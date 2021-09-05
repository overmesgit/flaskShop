#!/bin/bash
mypy -m app
coverage run -m pytest
coverage report