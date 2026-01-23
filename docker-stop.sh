#!/bin/bash

# Docker Stop Script for Network Architecture Design System

echo "=============================================================================="
echo "Stopping Network Architecture Design System"
echo "=============================================================================="
echo ""

# Stop all containers
echo "Stopping containers..."
docker-compose down

echo ""
echo "✓ All containers stopped"
echo ""
echo "To remove volumes as well, run:"
echo "  docker-compose down -v"
echo ""
