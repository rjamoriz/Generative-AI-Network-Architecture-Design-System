#!/bin/bash

# Docker Logs Script for Network Architecture Design System

SERVICE=${1:-all}

if [ "$SERVICE" = "all" ]; then
    echo "Showing logs for all services (Ctrl+C to exit)..."
    docker-compose logs -f
else
    echo "Showing logs for $SERVICE (Ctrl+C to exit)..."
    docker-compose logs -f $SERVICE
fi
