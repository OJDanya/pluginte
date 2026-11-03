"""Load packaged instructions for customer communication; never persist prompts."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

def handle(event):
    if event.get('hook_event_name') != 'UserPromptSubmit':
        return {}
    prompt = event.get('prompt', '')
    if not isinstance(prompt, str):
        return {}
    audience = re.search(r'\b(?:клиент\w*|заказчик\w*|покупател\w*|партн[её]р\w*|customer\w*|client\w*)\b', prompt, re.I)
    communication = re.search(r'\b(?:ответ\w*|отвеч\w*|напиш\w*|напис\w*|письм\w*|сообщени\w*|переписк\w*|общени\w*|сформулир\w*|reply|respond\w*|email\w*|message\w*)\b', prompt, re.I)
    if not (audience and communication):
        return {}
    skill = ROOT / 'skills' / 'business-reply' / 'SKILL.md'
    body = skill.read_text(encoding='utf-8').split('---', 2)[-1].strip()
    return {
        'systemMessage': 'Корпоративный хук 0.5: загружен business-reply.',
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': 'Для текущего запроса об общении с клиентом загружены инструкции business-reply. Применяй их к деловому ответу. Если пользователь обсуждает сам плагин или не просит составлять ответ, не создавай письмо от себя. Сообщи кратко в ходе работы: «Инструкции делового ответа загружены корпоративным хуком 0.5». Не включай эту отметку в текст для клиента.\n\n' + body
        }
    }

if __name__ == '__main__':
    try:
        result = handle(json.load(sys.stdin))
    except (ValueError, OSError, AttributeError):
        result = {'systemMessage': 'Корпоративный хук: инструкции не загружены из-за ошибки.'}
    print(json.dumps(result, ensure_ascii=True))
