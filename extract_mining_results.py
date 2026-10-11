#!/usr/bin/env python3
import sys, json, re

for line in sys.stdin:
    data = json.loads(line.strip())
    agent_id = data.get('agentId')
    result = data.get('result', '')

    if agent_id == 'ade0bb258071ad767':
        continue  # Scout result, not a mining result

    # Check if result contains JSON
    if result.strip().startswith('{'):
        try:
            parsed = json.loads(result)
            with open(f'/home/igor/Projects/hyprmac/mining_{agent_id}.json', 'w') as f:
                json.dump(parsed, f, indent=2)
            print(f'Saved {agent_id}')
        except:
            print(f'{agent_id}: Invalid JSON')
    elif '```json' in result:
        json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                with open(f'/home/igor/Projects/hyprmac/mining_{agent_id}.json', 'w') as f:
                    json.dump(parsed, f, indent=2)
                print(f'Saved {agent_id}')
            except:
                print(f'{agent_id}: Invalid JSON in code block')
        else:
            print(f'{agent_id}: No JSON code block found')
    else:
        print(f'{agent_id}: No JSON found (text result)')