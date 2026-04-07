import os
import re

for root, _, files in os.walk(r'd:\Project Medbook\backend\app'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add Optional import if missing
            if ' | None' in content:
                if 'from typing import Optional' not in content:
                    content = 'from typing import Optional\n' + content
                
                # Replace T | None with Optional[T]
                content = re.sub(r'([A-Za-z0-9_.]+(?:\[.*\])?)\s*\|\s*None', r'Optional[\1]', content)
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
