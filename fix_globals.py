#!/usr/bin/env python3
"""Fix: Add SERPER_API_KEY and FASTINDEX_API_KEY to Inject Globals node"""
import json

with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

# Find Inject Globals node
for node in wf['nodes']:
    if 'Inject Globals' in node.get('name', ''):
        code = node['parameters']['jsCode']
        
        # Add SERPER_API_KEY and FASTINDEX_API_KEY after SPEEDYINDEX_API_KEY
        old = "SPEEDYINDEX_API_KEY: $vars.SPEEDYINDEX_API_KEY || '',\n  TELEGRAM_BOT_TOKEN:"
        new = "SPEEDYINDEX_API_KEY: $vars.SPEEDYINDEX_API_KEY || '',\n  SERPER_API_KEY: $vars.SERPER_API_KEY || '',\n  FASTINDEX_API_KEY: $vars.FASTINDEX_API_KEY || '',\n  TELEGRAM_BOT_TOKEN:"
        
        if old in code:
            code = code.replace(old, new)
            node['parameters']['jsCode'] = code
            print('✅ Updated Inject Globals node')
        else:
            print('❌ Pattern not found in Inject Globals')
            print('Current code snippet:')
            idx = code.find('SPEEDYINDEX')
            if idx >= 0:
                print(code[idx:idx+200])
        break

with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2)

# Verify
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)
    
for node in wf['nodes']:
    if 'Inject Globals' in node.get('name', ''):
        code = node['parameters']['jsCode']
        if 'SERPER_API_KEY' in code and 'FASTINDEX_API_KEY' in code:
            print('✅ Verified: Both keys present in Inject Globals')
        else:
            print('❌ Verification failed')
