import telebot
import mph
import random
from matplotlib import pyplot as plt
from working_with_model import run_model
from pathlib import WindowsPath
import jpype
import time

bot = telebot.TeleBot('1749257***SENSORED***A5U7Fi0PA') #вставить сюда токен, полученный через @botfather
mph.discovery.search_Windows = lambda: [{'name': '5.5', #здесь и ниже: указать данные установленной версии Comsol
                                         'major': 5,
                                         'minor': 5,
                                         'patch': 0,
                                         'build': 359,
                                         'root': WindowsPath('C:/Program Files/COMSOL/COMSOL55/Multiphysics'), #указать путь к главной папке "Multiphysics"
                                         'jvm': WindowsPath('C:/Program Files/COMSOL/COMSOL55/Multiphysics/java/win64/jre/bin/server/jvm.dll'), #указать путь к файлу jvm.dll
                                         'server': [WindowsPath('C:/Program Files/COMSOL/COMSOL55/Multiphysics/bin/win64/comsol'), #указать путь к файлу запуска Comsol
                                                    'mphserver']}]
client = mph.start()
print('Started')
models = dict()
plt.ioff()


def parse_pset(pset):
    return {
            line.split('=')[0].strip(): line.split('=')[1].strip() 
            for line in pset.split('\n') 
            if '=' in line
            }


def new_run(message):
    msg = message
    model = client.load(models[msg.chat.id])
    psets = message.text.split('&&&')
    for pset in psets:
        params = parse_pset(pset)
        print(params)
        for p in params.keys():
            model.parameter(p, params[p])
        ps = pset.replace("\n", ", ")
        bot.send_message(message.chat.id, f'Running set {ps}')
        lambdas, res = run_model(model)
        pstring = '_'.join([params[k].split('[')[0] for k in sorted(params.keys())])
        filename = f'{models[msg.chat.id]}_{pstring}'
        plt.cla()
        plt.plot(lambdas, res)
        plt.savefig('tmp.jpg')
        bot.send_photo(message.chat.id, open('tmp.jpg', 'rb').read())
        filename=filename.replace("/","_div_")
        with open(filename+'.txt', 'w') as f:
            for a, b in zip(lambdas, res):
                f.write(f'{a} {b}\n')
        bot.send_document(message.chat.id, open(filename+'.txt', 'rb').read(), caption=str(filename+'.txt'))


@bot.message_handler(commands=['new'])
def handle_new(msg):
    try:
        print('new')
        model = client.load(models[msg.chat.id])
        bot.reply_to(msg, f'''Send me your parameters like this:\n<code>b=5[mm]\nc=3[s]</code>
The parameters in the model:
<code>{model.parameters()}</code>.
If you want to have several parameter sets, separate them with &&&''',
                parse_mode='HTML')
        bot.register_next_step_handler(msg, new_run)
    except Exception as e:
        print(e)


@bot.message_handler(func=lambda message: message.text.lower().startswith('model:') or message.document is not None)
def select_model(msg):
    if msg.text.lower().startswith('model:'):
        models[msg.chat.id] = msg.text.lower().removeprefix('model:').strip()
        print('Setting model')
        bot.send_message(msg.chat.id, 'Ok')
    else:
        bot.send_message(msg.chat.id, 'Ooops, something went wrong')

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(30)
