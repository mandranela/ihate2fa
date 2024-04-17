# GDEPC

## Как запустить измерение затрачиваемой энергии алгоритмами сжатия

### Билдим docker image 
```bash
docker build -t power_consumption .
```
### Запускаем docker-activity
Находится в корне проекта
```bash
cd docker-activity/example && docker-compose run activity
```
Все измерения кладутся в `docker-activity/example/storage` в файл `output.json`. 

### Запускаем сжатие
```bash
python3 run_power_measure.py
```
Сжатие происходит каждым алгоритмом по очереди, на каждый алгоритм дается 10 минут (можно изменить в скрипте). Скрипт проверяет наличие оставшихся контейнеров и удаляет их, далее поднимает по очереди для каждого алгоритма.

### Собираем и парсим данные

```python
container_names = [f"proto_{compression}" for compression in compression_dict.keys()] + [f"json_{compression}" for compression in compression_dict.keys()]
compression_power_consumption = []
df = pd.read_json('путь_до_файла_с_данными', lines=True)
df = df[df['containerName'].isin(container_names) & ~df['cpuEnergy'].isna() & df['cpuEnergy'] > 0]
df.to_csv('power_consumption.csv', index=False)
```

