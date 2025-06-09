from typing import Text, Optional, List
import json
from app.bot.memory.models import State
from app.bot.memory import MemorySaver
from app.database_postgres import postgres_db


class MemorySaverPostgreSQL(MemorySaver):
    """
    MemorySaverPostgreSQL implements the MemorySaver interface for PostgreSQL/Supabase.
    """

    def __init__(self):
        self.db = postgres_db

    async def save(self, thread_id: Text, state: State):
        """Save conversation state to PostgreSQL"""
        state_dict = state.to_dict()
        
        query = '''
            INSERT INTO chat_states (thread_id, state_data)
            VALUES ($1, $2)
        '''
        
        await self.db.execute(query, thread_id, json.dumps(state_dict))

    async def get(self, thread_id: Text) -> Optional[State]:
        """Get the latest conversation state for a thread"""
        query = '''
            SELECT state_data FROM chat_states 
            WHERE thread_id = $1 
            ORDER BY created_at DESC 
            LIMIT 1
        '''
        
        result = await self.db.fetchval(query, thread_id)
        
        if result:
            if isinstance(result, str):
                state_data = json.loads(result)
            else:
                state_data = result
            return State.from_dict(state_data)
        return None

    async def get_all(self, thread_id: Text) -> List[State]:
        """Get all conversation states for a thread"""
        query = '''
            SELECT state_data FROM chat_states 
            WHERE thread_id = $1 
            ORDER BY created_at DESC
        '''
        
        results = await self.db.fetch(query, thread_id)
        
        states = []
        for row in results:
            state_data = row['state_data']
            if isinstance(state_data, str):
                state_data = json.loads(state_data)
            states.append(State.from_dict(state_data))
        
        return states

    async def clear(self, thread_id: Text):
        """Clear all states for a thread"""
        query = 'DELETE FROM chat_states WHERE thread_id = $1'
        await self.db.execute(query, thread_id)