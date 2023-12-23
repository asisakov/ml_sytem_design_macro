
# Команды helm установки базовых сервисов

## ingress nginx
```
helm --kubeconfig ~/.kube/testcom upgrade -i --namespace ingress-nginx --create-namespace ingress-nginx ingress-nginx
helm --kubeconfig ~/.kube/testcom diff upgrade -f secrets.yaml  --namespace system compredict-cluster cluster
```

## Docker registry
```
helm --kubeconfig ~/.kube/testcom upgrade -i --namespace  registry --create-namespace registry registry
helm --kubeconfig ~/.kube/testcom diff upgrade  --namespace  registry  registry registry
```

# Установка раннеров


По [quick start guide](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners-with-actions-runner-controller/quickstart-for-actions-runner-controller) ставятся два helm релиза. Один в пространстве arc (или arc-system) - это собственно оператор, второй в пространстве arc-runners. В arc-runners фактически задаются template для запуска подов и указывается к какому именно проекту относятся раннеры.

Чарты, указанные в гайде, сделаны в виде dependency, файлы values вытащены из скачанных `helm dep update` архивов, весь yaml запрятан в название dependency.

Запуск helm

```
helm --kubeconfig ~/.kube/testcom diff upgrade -i --namespace arc arc arc
helm --kubeconfig ~/.kube/testcom diff upgrade -f arc-runners/values.petr.yaml  --namespace arc-runners arc-runners arc-runners

helm --kubeconfig ~/.kube/testcom diff upgrade -f arc-runners/values.aisakov.yaml  --namespace github-runners compredict-runners arc-runners
```

## Использоваине kubernetes

По умолчанию runner использует docker, в новых кластерах это не работает, т.к. runtime containerd. Чтобы раннер использовал kubernetes для создания подов с произвольными образами необходимо следующее:

* Обеспечить CSI dynamic storage
* Указать containerMode.type=kubernetes
* Указать соответствующий storage class

Всё это указывается в файле arc-runner/values.yaml

По-поводу containerMode.type = kubernetes есть два источника: маленький [мануал](https://github.com/actions/actions-runner-controller/blob/master/docs/deploying-alternative-runners.md#runner-with-k8s-jobs) в проекте arc и [статья](https://some-natalie.dev/blog/kaniko-in-arc/)

### CSI

В качестве csi выбран тестовый [csi-driver-host-path](https://github.com/kubernetes-csi/csi-driver-host-path/blob/master/docs/deploy-1.17-and-later.md), который не рекомендован к использованию в проде и работает только в single node, но вообще-то нам это как раз подходит.

Данные по факту хранятся в `/var/lib/csi-hostpath-data -> /data/csi-hostpath-data`

#### Скрипт установки

Немного изменённый скрипт установки CRD и собственно драйвера. Указана конкретная версия snapshotter и пофикшены пути к crd.

```
# Change to the latest supported snapshotter version
SNAPSHOTTER_VERSION=v6.3.2

alias kubectl="kubectl --kubeconfig ~/.kube/testcom"

# Apply VolumeSnapshot CRDs
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/${SNAPSHOTTER_VERSION}/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/${SNAPSHOTTER_VERSION}/client/config/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/${SNAPSHOTTER_VERSION}/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml

# Create snapshot controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/${SNAPSHOTTER_VERSION}/deploy/kubernetes/snapshot-controller/rbac-snapshot-controller.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/${SNAPSHOTTER_VERSION}/deploy/kubernetes/snapshot-controller/setup-snapshot-controller.yaml
```


### Проблема с правами доступа

При возникновении ошибки `Error: Access to the path /home/runner/_work/_tool is denied` нужно либо указать правильный fsGroup, либо с помощью initContainer'а поправить права доступа.

Взято [отсюда](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners-with-actions-runner-controller/troubleshooting-actions-runner-controller-errors#error-access-to-the-path-homerunner_work_tool-is-denied)

### Настройка workflow подов и кроличья нора

Поды с произвольными image создаются, однако при этом они не наследуют никакие настройки template.spec из values, например imagePullSecrets или монтированные каталоги и т.д. И соответственно являются практически бесполезными, во всяком случае, использовать кастомный image или секрет не выйдет.
При этом оказалось, что дефолтный image kaniko (а только с его помощью можно что-либо собрать в кластере) криво работает с actions/checkout.

Копание в коде показало, при создании job подов используется некий параметр [extensions](https://github.com/actions/runner-container-hooks/blob/main/packages/k8s/src/k8s/index.ts#L65), который в свою очередь читается из переменной  `export const ENV_HOOK_TEMPLATE_PATH = 'ACTIONS_RUNNER_CONTAINER_HOOK_TEMPLATE'`, поиск последней вывел на [совет](https://github.com/actions/actions-runner-controller/issues/2890#issuecomment-1746353393) разработчика как кастомизировать создаваемые поды. Этот процесс описан в [документе](https://github.com/actions/runner-container-hooks/blob/main/docs/adrs/0096-hook-extensions.md) с непонятным статусом.
Но на момент прочтения этот документ соответствовал коду.

В конечном итоге, кастомизация подов сводится к следующим шагам

* Объявить кастомный yaml, начиная со слова spec
```
spec:
  containers:
    - name: "$job"
      volumeMounts:
        - name: runners-secrets
          mountPath: /etc/runners-secrets
  volumes:
        - name: runners-secrets
          secret:
            secretName: runners-secrets
  imagePullSecrets:
    - name: registry-compredict
```

При этом, название "$job" зарезерировано и значит, что параметры этого контейнера будут перекрывать параметры собственно контейнера выполняющего работу.
Остальные параметры в spec переопределяют или дополняют (volumes, containers, ...) параметры пода.

* Монтировать созданный yaml в контейнер раннера (например через configmap и volume в arc-runners/values.yaml)

* Указать путь к yaml в переменной `ACTIONS_RUNNER_CONTAINER_HOOK_TEMPLATE`

Вот так вот "просто" можно сделать из буханки троллейбус...



# Github actions

https://docs.github.com/en/actions/using-workflows/manually-running-a-workflow


# Ограничения

https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners-with-actions-runner-controller/using-actions-runner-controller-runners-in-a-workflow

You cannot use labels to target runners created by ARC. You can only use the installation name of the runner scale set that you specified during the installation or by defining the value of the runnerScaleSetName field in your values.yaml file. For more information, see "Deploying runner scale sets with Actions Runner Controller."


# Создание fine grained токена

Для создания токена нужно зайти в Profile -> Settings -> Developer Settings (в самом низу слева) -> Personal Access Tokens -> Fine-grained token -> Нажать кнопку Generate new Token (справа)

В появившейся форме нужно назвать как-то токен, чтобы потом можно было вспомнить для чего он, например, `ml_design_runner`

Выбрать срок действия, желательно чтобы не закончился до того как проект станет неактуальным )

В Repository Access выбрать "Only Selected Repositories".

Выбрать из списка репку с проектом `ml_system_design_macro`.

В разделе Permissions -> Repository Permissions для Administration указать Read and write.

Будет написано Repository permissions: 2 selected (одна всегда выбрана).

Затем нажать "Generate token" и отдать появившийся токен мне.

## Обновление токена

Если токен истёк, то после обновления секрета нужно удалить соответствующий под `*-listener` в пространстве arc. Другими способоами прочитать новый токен оно не может.
