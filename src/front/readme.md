# Как запускать

```
python -m venv v
# Команду активации virtualenv надо запускаь в каждом терминале, где планируется запуск streamlit
. v/bin/activate
pip install -r requirements_lock.txt
```

Создать файл .env

```
CLICKHOUSE_PORT=443
CLICKHOUSE_HOST=ch.compredict.xyz
CLICKHOUSE_USER=***
CLICKHOUSE_PASSWORD=***
```


## Запуск сервера

```
. v/bin/activate
streamlit run main.py
```


streamlit сам по себе не падает, даже если python скрипт внутри упал (возможно это dev режим)
