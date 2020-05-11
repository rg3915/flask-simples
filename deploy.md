## Criar servidor

## Configurar conexão ssh

## Criar um usuário

```
adduser deploy

ls /home

su -

usermod -aG sudo deploy
```

Agora saia do servidor e entre com o nome do novo usuário

```
ssh deploy@IP
```

## Configurando acesso via ssh

```
su -
cd /home/deploy
mkdir .ssh
touch .ssh/authorized_keys
```

E coloque sua chave ssh pública lá dentro.

Depois faça

```
chown -R deploy:deploy /home/deploy/.ssh
```

Ao sair novamente do servidor, você pode entrar com

```
ssh deploy@IP
```

## Atualizar o servidor

```
sudo apt update
sudo apt upgrade
```

## Crie alguns alias dentro do `~/.bashrc`

```
alias l='clear; ls -lF'
alias rm='rm -i'
alias h=history
alias python=python3
alias pip=pip3
# Git
alias g='git'
alias gp='git push origin HEAD'
```

E faça `source ~/.bashrc`

### Vim

Se quiser configure seu `~/.vimrc` para usar 4 espaços.

https://stackoverflow.com/questions/234564/tab-key-4-spaces-and-auto-indent-after-curly-braces-in-vim/234578#234578

Eu gosto de deixar minha configuração assim:

```
set encoding=utf-8
set number          " show line numbers
set expandtab       " use spaces instead of tabs
set autoindent      " autoindent based on line above
set smartindent     " smarter indent for C-like languages
set shiftwidth=4    " when using Shift + > or <
set softtabstop=4   " in insert mode
set tabstop=4       " set the space occupied by a regular tab
```

Eu tenho um `.vimrc` mais completo em

https://gist.github.com/rg3915/57b489c1751c384b3ad614c492478df0

## Instalando pyenv

...


## Instalando pipenv

...


## Clonando um projeto Flask

```
pip install flask

git clone https://github.com/rg3915/flask-simples.git
```

Renomeie a pasta para `app`.

```
mv flask-simples app
```

Para rodar a aplicação digite

```
flask run -p 5000 -h 0.0.0.0
```

Se der erro, e se você tiver instalado sem virtualenv, seu flask estará na pasta

```
~/.local/bin/
```

Então entre em `~/.bashrc` e digite

```
export PATH="/home/deploy/.local/bin/:$PATH"
```

E faça

```
source ~/.bashrc
```

Dai rode novamente

```
flask run -p 5000 -h 0.0.0.0
```

Já pra acessar a página

```
IP:5000
```

## Instalando o gunicorn

```
pip install gunicorn
```

Se você fez o clone ele já está no requirements.txt.

Para rodar a aplicação com gunicorn faça

```
gunicorn -b 0.0.0.0:5000 -w 4 app:app
```

Onde `-b` é o bind de acesso.

O primeiro `app` é o nome do arquivo. E o segundo `app` é a variável de instância.


## Instalando o nginx

```
sudo apt install -y nginx
```

Para verificar se o nginx está rodando

```
systemctl status nginx
```

Para ativar um novo serviço do nginx no Linux, pra voltar a funcionar mesmo que a máquina seja reiniciada.

```
sudo systemctl enable nginx
```

```
cd /etc/nginx
l
cd sites-available
cat default
```

Crie um novo arquivo `webapp`

```
vim /etc/nginx/sites-available/webapp

server {
    listen 80;
    server_name 127.0.0.1;
    charset utf-8;

    location / { 
        proxy_pass http://127.0.0.1:5000;
        access_log /home/deploy/logs/nginx-access.log;
    }

    location /static {
        alias /home/deploy/app/static;
    }
}
```

Agora vamos criar o link simbólico em `sites-enabled`

```
cd /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/webapp /etc/nginx/sites-enabled/
```

E se quiser, pode remover o `default`

```
rm /etc/nginx/sites-available/default
rm /etc/nginx/sites-enabled/default
```

### Reiniciar o nginx

Antes você pode testar o nginx com o comando

```
sudo nginx -t
```

Reiniciando

```
sudo service nginx restart
```

Rode a aplicação novamente com

```
gunicorn -b 0.0.0.0:5000 -w 4 app:app
```

E acesse a aplicação, ou

```
curl 0.0.0.0:5000
```

### Monitorando o log do nginx



```
# /etc/nginx/sites-available/webapp
...
access_log /home/deploy/logs/nginx-access.log;
...
```

```
tail -f /home/deploy/logs/nginx-access.log
```

Para conferir se os arquivos estáticos estão passando pelo nginx inspecione elementos no navegador

```
Response Headers
Server: nginx/1.16.1 (Ubuntu)
```

## Migração

```
pip install flask-migrate
```

A esta altura nosso `app.py` deve estar assim:

```python
# app.py
from flask import Flask, render_template


app = Flask(__name__)
app.config["ENV"] = "production"


@app.route("/")
def home():
    return render_template("index.html")
```

Agora façamos:

```python
# app.py
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["ENV"] = "production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)
Migrate(app, db)


class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))


@app.route("/")
def home():
    return render_template("index.html")
```

```
flask db init
flask db migrate
flask db upgrade
```

```
flask shell
>>>
from app import db, Track
track = Track()
track.name = "Track One"
db.session.add(track)
db.session.commit()
track = Track()
track.name = "Track Two"
db.session.add(track)
db.session.commit()
```

E em `index.html`, faça

```html
# index.html
...
  <ul>
    {% for track in tracks %}
      <li>{{ track.name }}</li>
    {% endfor %}
  </ul>
...
```

E edite um pouco mais em `app.py`

```python
...
@app.route("/")
def home():
    tracks = Track.query.all()
    return render_template("index.html", tracks=tracks)
```

Rode novamente o `gunicorn`

```
gunicorn -b 0.0.0.0:5000 -w 4 app:app
```


## Supervisor

```
sudo apt install -y supervisor
```

```
cd /etc/supervisor/conf.d

sudo vim webapp.conf


[program:webapp]
user=deploy
directory=/home/deploy/app
command=/home/deploy/.local/bin/gunicorn -b 0.0.0.0:5000 -w 4 app:app
autostart=true
autorestart=true
stderr_logfile=/home/deploy/app/logs/webapp.err.log
stdout_logfile=/home/deploy/app/logs/webapp.out.log
```

```
sudo supervisorctl status
sudo systemctl status supervisor    # gerenciar processos no Linux
sudo systemctl enable supervisor    # ativar o supervisor no servidor
sudo supervisorctl reread           # relê os arquivos de configuração do supervisor
sudo supervisorctl update           # atualiza
sudo service supervisor restart webapp
sudo systemctl status
sudo supervisorctl status
```

Se der algum erro é porque você esqueceu de colocar o `user=deploy` em `webapp.conf`.

E

```
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart webapp
sudo supervisorctl status
```

```
lsof -i :5000
```

Seu deploy está pronto.

