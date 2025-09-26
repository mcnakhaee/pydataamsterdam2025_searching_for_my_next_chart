# Searching for My Next Chart 📊

Hey there! This repo contains all the code and resources from my talk at **PyData Amsterdam 2025** about building an intelligent chart search system.

## What's This About?

Ever found yourself scrolling endlessly through data visualization galleries, trying to find *that perfect chart* for your data story? Yeah, me too. That's why I built this AI-powered search system that helps you discover the right visualization by simply describing what you want to show.

## What's Inside

This demo combines several cool technologies:

- **🤖 AI-powered search** using OpenAI's function calling to understand what you're looking for
- **🔍 Vector search** with Weaviate to find semantically similar visualizations  
- **🎨 Multi-modal search** across chart types, colors, layouts, and purposes
- **⚡ Smart filtering** that combines semantic search with structured filters

## The Magic

Instead of browsing through hundreds of charts, just tell the system things like:
- "Show me charts for comparing proportions"
- "I need a dark background visualization"
- "Find scatter plots with trend lines"
- "Charts that show time series data"

The system understands your intent and finds relevant examples from a curated collection of data visualizations.

## Tech Stack

- **Python** for the backend logic
- **Weaviate** for vector storage and semantic search
- **OpenAI API** for natural language understanding
- **Chainlit** for the web interface (deployed on Heroku)

## Running Locally

You'll need to set up your environment variables for the various APIs used (OpenAI, Weaviate, etc.). Check the code for the specific variables needed.

## The Talk

This was presented at PyData Amsterdam 2025, exploring how AI can make data visualization discovery more intuitive and efficient.

---

*Built with ❤️ for the data viz community*