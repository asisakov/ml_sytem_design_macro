# ML System Design Doc - [RU]
## Дизайн ML системы - \<Commodities price prediction\> \<MVP\> \<0.1\>                                                                                                         

### 1. Цели и предпосылки 
#### 1.1. Зачем идем в разработку продукта?  

Бизнес-цель - Улучшение процесса принятия экономических решений за счет применения прогнозов по макроэкономическим данным. Применение возможно следующим образом:
- Планировние складских запасов с учетом повышения цен на сырье;
- Покупка фьючерсов на определенные commodity с учетом дальнейшего роста цены;
- Оценка бюджетных средств по операционным расходам на мероприятия, связанные с материалами, завязанными на сырье;
- Расчет стресс-сценариев по оценке.

Какие улучшения принятия экономических решений предполагаются с разработкой системы автоматического прогнозирования мировых цен на товары широкого потребления:
- Высокая скорость получения прогнозов с заданной точностью;
- Возможность получить доверительный интервал на полученное предсказание;
- Интерпретируемость полученного результата;
- Визуализация прогноза и удобство его применения.

#### 1.2. Бизнес-требования и ограничения  

- Краткое описание БТ и ссылки на детальные документы с бизнес-требованиями `Product Owner`
    - Основной задачей в бизнес-требовании является "разработка платформы для предсказания фьючерсов на товары широкого потребления". При этом в документе предложена детализация получаемого прогноза. Планируется получить прогноз на 14 дней вперед с ежедневной разбивкой. Ценой актива считать цену закрытия, либо среднюю цену закрытия за все часы торгов в данный день. Ссылка на документ ТУТ.
- Бизнес-ограничения
    - Также со стороны `Product Owner` представлены бюджетные ограничения, сроки разработки, тестирования и пилотирования продукта. Этап разработки и исследований планируется завершить за 4 месяца. Пилотированию и тестам планируется уделить 2 месяца. Согласованный бюджет реализации проекта - 1000000 руб. Требуемая точность готового продукта - максимальное абсолютное процентное отклонение не более 5% на горизонте прогноза 1 неделя и не более 10% на горизонте прогноза 14 дней. Ссылка на документ ТУТ.
- Что мы ожидаем от конкретной итерации `Product Owner`.
    - Ожидания от конкретной итерации - получить рабочий прототип платформы, демонстрирующий базовую функциональность: возможность получить необходимое предсказание и сравнить его с фактом на графике.
- Описание бизнес-процесса пилота, насколько это возможно - как именно мы будем использовать модель в существующем бизнес-процессе? `Product Owner`
    - В рамках пилотного проекта, платформа для применения прогноза будет интегрирована в существующий процесс финансовой аналитики промышленных индустрий. Пользователи смогут в 2 клика получить необходимую информацию и на ее основе принимать экономические решения. Далее пользователь системы будет оставлять обратную связь о применении платформы в бизнес-задачах.
- Критерии успеха пилота:
    - Не менее 50% пользователей платформы отмечают полезность продукта.
    - Системой пользуются не менее 5 человек в день.
    - Полученная точность прогноза соответствует заявленной.
-  Возможные пути развития проекта `Product Owner`:
    -  Добавление новых инструментов и моделей в нынешний прогноз (обогащение прогноза).
    -  Добавление возможности тестировать торговые стратегии.
    -  Подготовка API для возможности применять результат прогнозирования в сторонних продуктах.

#### 1.3. Что входит в скоуп проекта/итерации, что не входит   

- На закрытие каких БТ подписываемся в данной итерации `Data Scientist`
    - Требование P001: Подготовка прогноза на 14 дней вперед (подневно) ежедневно.
    - Требование P002: Обеспечение точности прогноза на 7 дней - 5%, на 14 дней - 10% в терминах максимального процентного отклонения от факта.
    - Требование P003: Сбор и подготовка данных по заданным активам.
    - Требование P004: Мониторинг и поддержка модели.
    - Требование P005: Создание платформы для возможности визуализировать подготовленный прогноз.
    - Требование P006: Формирование отчета о разработке модели.
- Описание результата с точки зрения качества кода и воспроизводимости решения `Data Scientist`
    - Ожидается, что код, разработанный `Data Scientist`, будет высокого качества, с хорошей документацией и комментариями для обеспечения читаемости и понимания другими разработчиками. Решение должно быть воспроизводимым, с возможностью повторного обучения модели на новых данных. Ожидается, что в отчете о разработке будет описан воспроизводимый процесс подготовки модели.
- Что не будет закрыто `Data Scientist`
    - ?
- Описание планируемого технического долга (что оставляем для дальнейшей продуктивизации) `Data Scientist`
    - Подготовка API для возможности применять результат прогнозирования в сторонних продуктах.

#### 1.4. Предпосылки решения  

- Используемые блоки данных: Для получения прогноза необходимо получить данные из открытых источников. Достаточной является информация о цене зыкрытия актива в определенный промежуток времени с частотностью наблюдений не менее 1 сутки.
- Горизонт прогноза: Горизонт прогноза составляет 14 дней (Бизнес-требование). Отсчет горизонта идет от дня прогнозирования. Например, если прогноз был рассчитан 15 января 2024, то первым днем прогноза считается именно день 15 января 2024.
- Запрос бизнеса и обоснование: Запрос на разработку системы прогнозирования цены закрытия актива на следующие 14 дней является отражением необходимости ускорения принятия эффективных экономических решений.
- Законодательные ограничения: При разработке системы будут учитываться законодательные ограничения. Следовательно, любые предсказания, полученные на выходе из моделей не являются индивидуеальной инвестиционной рекомендацией.


#### 1.5. Затраты на реализацию решения  

- Зарплаты разработчиков и исследователей, занимающихся созданием и внедрением моделей машинного обучения для прогноза
- Затраты на получение данных и их хранение
- Затраты на обслуживание и мониторинг прогнозных моделей
- Затраты на вычислительные ресурсы, включая сервера или облачные вычисления

 
#### 1.6. Что считаем за результат (Definition of Done)

- Существует локальная платформа с ограниченным доступом для заинтересованных в прогнозе лиц.
- Продукт предоставляет ежедневно обновляемый прогноз по ценам на фьючерсы определенных товаров широкого потребления на 14 дней вперед.
- Пользователи системы имеют возможность увидеть и загрузить все рассчитанные прогнозы, а также сравнить их с фактическими наблюдениями.

### 2. Методология `Data Scientist`     

#### 2.1. Постановка задачи  

- Данная задача относится к классу `прогнозирование временных рядов`.
- В конкретном случае рассматривается следующая постановка:
    - Даны исторические наблюдения за ценами нескольких активов ежедневно за последние 2 года.
    - Следует построить прогноз на 14 дней вперед с применением моделей машинного обучения
    - Итоговая точность должна составить не менее 5% MAPE на временном промежутке 7 дней и 10% MAPE на временном промежутке 14 дней.
    - Следует подготовить платформу для визуализации полученного прогноза с целью обеспечения удобного пользования.
- Декомпозиция задач (3 микросервиса - 3 гланых задачи):
    1. Загрузка данных и хранение:
        1.1. Выбрать источник данных
        1.2. Выбрать тип базы данных
        1.3. Настроить удаленный хостинг базы данных
        1.4. Указать частоту обновления данных
        1.5. Подготовть схему хранения данных
        1.6. Создать роли для доступа к таблицам 

    2. Подготовка предсказательных моделей:
        2.1. Генерация и отбор признаков
        2.2. Выбор моделей для прогнозирования
        2.3. Хостинг моделей на сервере
        2.4. Подготовить таблицу для записи результата моделей
        2.5. Расчет метрик качества прогнозов
        2.6. * Интерпретация полученных прогнозов

    3. Платформа визуализации прогноза
        3.1. Выбор фреймфорка для визуализации
        3.2. Частотность обновления данных
        3.3. Хостинг платформы с визуализацией
        3.4. UI-дизайн визуализации и схема пользовательских действий

#### 2.2. Блок-схема решения  

- Блок-схема для основного MVP с ключевыми этапами решения задачи `Data Scientist`:
![block_scheme](https://github.com/asisakov/ml_sytem_design_macro/assets/43218578/fce80106-7baa-4944-bda0-fc04514f36c3)

#### 2.3. Этапы решения задачи `Data Scientist`  

 *Этап 1 - Согласование бизнес-требований.*  

- Согласование бизнес-требований перед разработкой является важнейшей задачей, которая гарантирует успешное выполнение проекта. Здесь важно определить конечные цели и задачи проекта для выстраивания правильной стратегии разработки. Также это позволяет учесть все требования и пожелания заказчика, что повышает вероятность соответствия конечного продукта с ожиданиями. Данный этап предотвращает возможные проблемы и несоответствия в постановке задач. Например, заранее можно договориться об ожиданиях от модели и предостеречь, какие метрики возможно получить при данной постановке задачи. Наконец, правильное согласование бизнес-требований позволяет оптимизировать сроки и бюджет проекта, так как позволяет избежать лишних телодвижений заранее.

 *Этап 2 - Сбор данных.*  

- Данные собираются с сервиса Yahoo Finance. Данная платформа предоставляет возможность получать актуальные данные об активах (фьючерсах), необходимых для тренировки предиктивной модели. Источник считается достоверным, что немаловажно, поскольку точность и надежность данных являются ключевыми факторами для разработки таких инструментов. Также существует возможность получать данные в реальном времени с небольшим лагом, что особенно полезно при разработке моделей, требующих актуальной информации для прогнозирования будущих событий. Для надежности решения также принято решение складывать все входные данные в базу данных с частотой 1 раз в сутки. 
  
- Схема входных данных  
  
| date  | ticker | value |
| ------------- | ------------- | ------------- |
| '2023-12-20 07:00:00' | 'ALI=F '  | 2183 |
| ...  | ...  | ... |
 
- На выходе имеем входные данные за промежуток времени не менее 2 лет. Данный этап позволяет нам получать свежие данные с платформы Yahoo Finance. Также в случае недоступности сервиса есть возможность обратиться к историческим данным для обучения моделей.

 *Этап 3 - Подготовка данных*

- Применительно ко временным рядам на данном этапе можно выделить 2 подзадачи:
    - Обработка данных: работа с пропусками, очистка от выбросов
    - Генерация новых признаков.
- В финансовых данных пропуски имеют под собой важную составляющую - в случае отсутствия торгов цена закрытия актива имеет цену, равную цене закрытия за прошлый период торгов при нулеовом объеме совершенных сделок. В случае отсутствия цены закрытия актива можно предположить, что торги на бирже в данный момент были приостановлены. С точки зрения постановки задачи важна оценка цен в следующие торговые периоды. Следовательно, пропуски в данных при данной постановке задаче можно очистить.
- При работе с выбросами важно учитыать доменную составляющую. В конкретной задаче выбросы играют немаловажную роль, так как они и могут являться катализаторами принятия экономических решений. Поэтому на данном этапе работа с выбросами не производится.
- Для генерации признаков во временных рядах можно рассмотреть следующие техники:
    - Лаги (стоимость алюминия T-lag времени назад)
    - Скользящее среднее с окном N (средняя стоимость в промежутке от T-N до T), а также стандартное отклонение в скользящем окне
    - Преобразования над полученными признаками (монотонные - например, e^x, и не монотонные - например, x^2)
    - Разбиение на тренд и сезонность (например, достать тренд моделью Prophet)
    - Деление/умножение/разность/сумма фичей между собой (std(N=3)/std(N=10))
    - Для линейных моделей можно также применять кодирование признаков, (например, MTE - mean target encoding)
    - Признаки, относящиеся ко времени (сколько дней до праздника, выходной день или будний)
- В данной задаче наибольший вклад в точность внесли признаки, основанные на лагах, тренде и сезонности. Также были важны временные признаки.

 *Этап 4 - Отбор моделей и признаков*

- На данном этапе также можно выделить 2 подзадачи, однако они работают в комбинации друг с другом:
    - Отбор наиважнейших признаков
    - Выбор наилучшей модели
- При генерации большого количества признаков с использованием техник, описанных выше, мы сталкиваемся проблемами переобучения, взаимокорреляции, а также большого количества ресурсов, расходуемых на расчет большого количества признаков. Для отбора наиболее важных признаков предложены следующие методы:
    - L1 регуляризация
    - PCA для снижения размерности пространства
    - RFE (recursive feature elimination) для повторяющегося отбора признаков
    - Feature importance (permutation, SHAP, split (for GB), entropy (for GB), mutual info) ->  пошаговый отбор признаков на основе важности в обученной модели
    - Проверка на статистическую значимость коэффициентов при признаке для линейной регрессии
    - Проверка на взаимокорреляцию признаков друг с другом и на корреляцию с целевой переменной
    - Проверка по критериям VIF, PSI
- Следует отметить, что данные методы используются только вместе с определенными моделями. При этом, при разработке намеренно отказались от PCA для обеспечения интерпретируемости моделей.
- Среди моделей были рассмотрены:
    - Baseline - последнее наблюдение
    - Holt-Winters Model - экспоненциальное сглаживание для тренда, сезонности и отклонений
    - ARIMA - скользящее среднее с лагами и разностями
    - XGBOOST - градиентный бустинг с обучением на отклонениях
    - Prophet - аддитивная модель, основанная на максимизации правдоподобия предсказания следующих N значений
- Пайплайн разработки моделей можно представить в виде следующей схемы:
![train_pipeline](https://github.com/asisakov/ml_sytem_design_macro/assets/43218578/0018d5d1-b0a9-426b-8739-695fd8d51750)

- Для сравнения моделей применялись тренировочная и отложенная выборки.
- Целевая переменная - 14 следующих значений цены актива от даты предсказания.
- Метрика качества - MAPE для возможности сравнивать эффективность моделей для активов, имеющих разные порядки формирования стоимости.
- Целевая метрика качества - не более 5% на первых 7 периодах прогноза, не более 10% для 14 периодов прогноза.
- Полученные признаки и прогнозы обязательно валидируются на совмествных встречах с заказчиками.

 *Этап 5 - Подготовка лучшей модели для инференса*

- Итоговой моделью выбран Prophet, пайплайн реализован в библиотеке ETNA.
- Следует учесть некоторые особенности применения данной модели:
    - Есть возможность интерпретации прогноза
    - Отсутствует надобность отдельно готовить признаки, кроме признаков, отвечающих за праздники и внешних регрессоров
    - В библиотеке реализована кросс-валидация из коробки, что позволяет вызовом одной функции получить дтелаьный отчет
    - Высокая вероятность переобучиться, если не ограничивать количество параметров
- Данные для инференса собираются из таблицы, лежащей в базе данных и описанной на этапе 2.
- Частота формирования прогноза - 1 раз в сутки (1 раз в час).
- Горизонт прогноза - 14 дней (14 часов), гранулярность - дни (часы).
- Риск повышенной чувствительности модели к выбросам отсутствует.
- На выходе формируется таблица со следующей схемой:

| forecast_date  | ticker | value | model  | interval | run_date |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| '2023-12-20 08:00:00' | 'ALI=F ' | 2185 | 'Prophet' | 14 | '2023-12-20 07:15:00' |
| ...  | ...  | ... | ...  | ...  | ... |

- Схему процесса можно представить следующим образом:
![inference_pipeline](https://github.com/asisakov/ml_sytem_design_macro/assets/43218578/0642ce1f-d137-4834-bf39-8e88b7b586cc)

 *Этапы 6 и 7*
 
Описание техники **для каждого этапа** должно включать описание **отдельно для MVP** и **отдельно для бейзлайна**:  

- Описанный здесь дизайн-документ является отчетом о проведенной разработке модели
- Пилотирование модели описано в главе 3.  
  
### 3. Подготовка пилота  

Пилот представляет собой тестирование готовой модели в реальной среде с применением мониторинга и аналитикой
  
#### 3.1. Способ оценки пилота  
  
*Входные данные*:
- Оценка достоверности полученных данных путем сравнения с другимим источниками
- Валидация данных с проверкой соответствия типа данных и их заполненности

*Модель предсказания цены актива*:
- Оценка метрики качества (MAPE) на пилоте и ее стабильность по сравнению с train и oot выборками
- Оценка доли отклонений более 10% в одном прогнозном ряде
- Оценка волатильности предсказаний модели по отношению к волатильности фактических значений целевой переменной

*Надежность системы*:
- Оценка доли успешно выполненных расчетов
- Оценка времени доступности системы

*Ресурсные затраты*:
- Оценка времени для обучения модели и времени получения прогноза
- Оценка затраченных ресурсов в виде мощностей и памяти
  
#### 3.2. Что считаем успешным пилотом  
  
*Точность прогноза*:
- Точность прогноза соответствует заранее согласованным в бизнес-требованиях условиям: максимальное абсолютное процентное отклонение не более 5% на горизонте прогноза 1 неделя и не более 10% на горизонте прогноза 14 дней

*Время инференса*:
- Время тренировки модели и получения прогноза составляет не более 1 часа

*Стабильность прогноза*:
- Метрика качества (MAPE) на пилоте отклоняется не более чем на 10% по сравнению с train выборкой и не более, чем на 15% по сравнению с oot выборкой

*Доступность прогноза*:
- Сервис доступен более 99.99% времени
  
#### 3.3. Подготовка пилота  
  
*Эксперимент с MVP*:

CPU: 4 ядра с тактовой частотой 3 ГГц
RAM: 4 ГБ
Срок эксперимента: 01.11.23 - 31.12.23

*Продуктовая эксплуатация*:
CPU: 4 ядра с тактовой частотой 3 ГГц
RAM: 4 ГБ

### 4. Внедрение production системы  
  
#### 4.1. Архитектура решения   
  
- Функциональная архитектура решения расположена на схеме ниже:
![deploy_scheme](https://github.com/asisakov/ml_sytem_design_macro/assets/43218578/bb67430c-8764-4b2e-ac5d-1420a1849861)
- Расшифровка компонент:
    - "Yahoo Finance" - сервис для загрузки данных по различным финансовым активам
    - "Downloader" - микросервис, выполняющий загрузку данных с "Yahoo Finance" с последующим сохранением в базу данных
    - "ClickHouse" - база данных
    - "Forecast" - микросервис, который выдает прогноз цен актива на ближайшие 14 дней с разбивкой по дням
    - "Streamlit UI" - микросервис для визуализации прогноза
    - "Web Client" - веб-клиент на стороне потребителя
  
#### 4.2. Описание инфраструктуры и масштабируемости 
  
Для реализации проекта по прогнозу цены актива отсутствует явная необходимость иметь доступ к высокопроизводительным вычислительным мощностям. В качестве вычилительных ресурсов применяется удаленный сервер со следующими характеристиками: 4 ядра CPU высокой производительности, 4 Гб RAM. Обеспечение масштабируемости возможно за счет выполнения задачи асинхронными потоками, а также на разных машинах. При неустойчивости серверных вычислений есть возможность быстро рассчитать прогноз на локальной машине.

База данных `ClickHouse` развернута на удаленном сервере без партицирования, шардирования и создания реплик. Так как нет необходимости в высокой производительности, при этом  средняя частота обращения к базе данных составляет не более 2 раз в сутки. Кластер баз данных расположен на локальном сервере со следующими характеристиками: 4 ядра CPU, 4 Гб RAM, 2 ТБ дисковое пространство. Масштабируемость можно рассмотреть в виде увеличения дискового пространства.
  
#### 4.3. Требования к работе системы  
  
- Сервис обеспечивает результат прогнозирования не более чем за 1 час с момента пуска процесса1

- Пропускная способность сервиса составляет 100 Мбит/секунду, средняя задержка при работе с веб-клиентом составляет  менее 50 миллисекунд. 
  
#### 4.4. Безопасность системы  
  
Потенциальная уязвимость системы для сервиса может быть связана с возможностью проникновения в базу данных, либо получение параметров модели. Например, есть потенциальная возможность узнать предсказания модели постороннему человеку, что может привести к осведомленности о потенциальных экономических решениях компании. Для предотвращения такой уязвимости системы, заказчик может использовать дополнительные методы обеспечения безопасности сервиса, например, сделать двойную аутентификацию при пользовании сервисом.
  
#### 4.5. Безопасность данных   
  
Для обеспечения безопасности данных в системе идентификации личности по фото необходимо соблюдать требования GDPR и других законов, регулирующих защиту персональных данных. Это включает в себя:

1. Сбор и обработку персональных данных только с согласия пользователя.

2. Хранение персональных данных в зашифрованном виде на защищенных серверах.

3. Ограничение доступа к персональным данным только для авторизованных лиц, работающих в системе.

4. Уведомление пользователей о всех изменениях в политике конфиденциальности и правилах обработки персональных данных.

5. Предоставление пользователям права на удаление своих персональных данных из системы.

Также необходимо регулярно проводить аудит безопасности системы для выявления возможных уязвимостей и принятия мер по их устранению. 
  
#### 4.6. Издержки  
  
Расчётные издержки на обслуживание системы в месяц включают в себя только затраты на оборудование - это аренда серверов для запуска микросервисов. Затраты на программное обеспечение являются нулевыми, так как сервис строится на открытом ПО. Затраты на техническое обслуживание системы и серверов составят оплату труда при чатсичной (10%) занятости команды, состоящей из одного `Data Scientist` и одного `DevOps`.
  
#### 4.5. Integration points  
  
Возможность интеграционых взаимодействий с другими системами в инфраструктуре заказчика рассматривается как продолжение проекта.
  
#### 4.6. Риски  
  
При разработке и внедрении сервиса следует учитывать следующие риски и неопределенности:

1. Риск данных: возможность получить неверные данные, либо проблемы с сервисом поставки данных.

2. Модельный риск: Деградация модели из-за изменений в данных, что может потребовать за собой дообучение, перенастройку, либо вывод модели из эксплуатации.

3. Нарушение безопасности: система может стать объектом кибератак или злоумышленных действий, что может привести к утечкам данных или нарушению работы сервиса.

4. Ограниченный функционал: система может не обладать достаточными возможностями для снижения финансовых рисков.

5. Низкая скорость работы: система может работать медленнее, чем необходимо, при существенном росте объема обрабатываемых данных, что может негативно сказаться на пользовательском опыте.

Для уменьшения рисков и неопределенностей тестирование системы проводится на различных наборах данных, также проводится еженедельный мониторинг модели с составлением отчетности. С другой стороны, необходимо обеспечивать высокий уровень безопасности и конфиденциальности, а также сотрудничать с юридическими экспертами для обеспечения соответствия сервиса законодательству.

