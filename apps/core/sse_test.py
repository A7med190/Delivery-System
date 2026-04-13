import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.core.sse import broadcast_sse

async def test_sse():
    print('Testing SSE broadcast...')
    await broadcast_sse('test_channel', 'test_event', {'message': 'Hello from SSE!'})
    print('SSE test complete')

if __name__ == '__main__':
    import asyncio
    asyncio.run(test_sse())
