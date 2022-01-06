import telepot
import json
import requests

from django.template.loader import render_to_string
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

TelegramBot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)

def parse_user_repos(name):
    response = requests.get('https://api.github.com/users/' + name + '/repos')
    repos = response.json()
    return repos

def send_repos_info(repos):
    public_repos = [repo for repo in repos if repo['private'] is False]
    public_repos_count = len(public_repos)
    private_repos = [repo for repo in repos if repo['private'] is True]
    private_repos_count = len(private_repos)
    return render_to_string('repos.md', {'public_repos_count': public_repos_count, 'private_repos_count': private_repos_count})

def display_repos_count(name):
    repos = parse_user_repos(name)
    return send_repos_info(repos)

def display_help():
    return render_to_string('help.md')

class CommandReceiveView(View):
    def get_func(self, cmd):
        commands = {
            '/start': display_help,
            '/help': display_help
        }
        if (len(cmd) > 1):
            commands['/repos'] = display_repos_count
        func = commands.get(cmd[0].lower())
        return func

    def send_msg(self, cmd):
        cmd0 = cmd[0].lower()
        if (cmd0 == '/start'):
            string = display_help()
        elif (cmd0 == '/help'):
            string = display_help()
        elif (cmd0 == '/repos' and len(cmd) > 1):
            string = display_repos_count(cmd[1])
        else:
            string = 'Wrong command'
        return string

    def post(self, request, bot_token):
        if bot_token != settings.TELEGRAM_BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            chat_id = payload['message']['chat']['id']
            cmd = payload['message'].get('text').split(' ')
            result = self.send_msg(cmd)
            TelegramBot.sendMessage(chat_id, result, parse_mode='Markdown')
        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
