#!/usr/bin/env bash
# exit on error
set -o errexit

# Chrome'u indiriyoruz
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Chrome'u kuruyoruz
apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb

# Python kütüphanelerini kuruyoruz
pip install -r requirements.txt