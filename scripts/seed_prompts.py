#!/usr/bin/env python3
"""
Database seeding script for default prompts.
Run this after database migration to populate default prompts.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.db.session import get_db_session
from app.ai.prompt_service import PromptService
from app.db.models import User

async def seed_default_prompts():
    """Seed the database with default prompts"""

    # Get the first admin user or create a system user
    async for session in get_db_session():
        try:
            # Try to get an admin user
            result = await session.execute(
                "SELECT id FROM users WHERE role = 'admin' LIMIT 1"
            )
            admin_user = result.fetchone()

            if not admin_user:
                # Create a system user if no admin exists
                result = await session.execute(
                    "INSERT INTO users (email, hashed_password, role, is_active) "
                    "VALUES ('system@learning-ai-platform.com', 'system', 'admin', true) "
                    "RETURNING id"
                )
                system_user_id = result.fetchone()[0]
            else:
                system_user_id = admin_user[0]

            # Create system user object
            system_user = User(id=system_user_id, email="system@learning-ai-platform.com", role="admin")

            # Default prompts
            default_prompts = [
                {
                    "name": "rag_system_default",
                    "content": "Answer using only the provided context. If the answer is not in context, say you do not know based on the uploaded documents.",
                    "prompt_type": "system"
                },
                {
                    "name": "rag_system",
                    "content": "Answer using the provided context. If the answer is not in context, use your general knowledge but note that it's not from the provided sources.",
                    "prompt_type": "system"
                },
                {
                    "name": "chat_system",
                    "content": "You are a helpful AI assistant. Provide accurate and helpful responses to user queries.",
                    "prompt_type": "system"
                }
            ]

            for prompt_data in default_prompts:
                # Check if prompt already exists
                existing = await PromptService.get_active_prompt(session, prompt_data["name"], prompt_data["prompt_type"])
                if not existing:
                    await PromptService.create_prompt(session, prompt_data, system_user)
                    print(f"Created prompt: {prompt_data['name']}")
                else:
                    print(f"Prompt already exists: {prompt_data['name']}")

            await session.commit()
            print("Default prompts seeded successfully!")

        except Exception as e:
            print(f"Error seeding prompts: {e}")
            await session.rollback()
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(seed_default_prompts())
