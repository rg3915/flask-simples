# flask-simples

Projeto simples feito em Flask

## Rodando o projeto

```
git clone https://github.com/rg3915/flask-simples.git
mv flask-simples app
cd app
pip install -r requirements.txt

flask db init
flask db migrate

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
exit

flask run -p 5000 -h 0.0.0.0
```

