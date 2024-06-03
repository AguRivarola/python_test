# Simple Python Api

Python Api con lectura de variables de entorno y CI/CD para el deploy automatizado de la imagen en AWS ECR e instanciado un servicio en ECS actualizando la task por cada push en las ramas "development" y "testing". 

## Technologies
- Python 3.12
- FastApi
- Uvicorn
- Docker
- Github Actions
- AWS ECR
- AWS ECS EC2

## Prerequisites
### Local development:
- Instalar `Python 3.12` o superior.
- Instalar `pip`.
``` bash
python -m venv py_api
source py_api/Scripts/Activate
pip install fastapi uvicorn python-dotenv
pip freeze > requirements.txt
uvicorn main:app --reload --port=80
```
- Instalar  `Docker` o `Docker Desktop` en caso de querer validar la creacion de la imagen.
```bash
docker build -t python_api .
docker run -dp 80:80 --name py_app python_api
```
### AWS 
- Tener cuenta de AWS
- Un usuario IAM con los permisos necesarios (para interactual con ECR y ECS) y las `access key` del mismo. 
- Crear un Repositorio privado en ECR
- Crear un `cluster`, una `task definition` utilizando EC2 instances y un `service` del tipo "launch type EC2" en ECS
- Obtener el json de la `task definition` y cargarlo en el archivo `.aws/skeleton.json`


## App 
La app esta desarrollada con python y fastapi, la cual consiste en los siguientes archivos para su funcionamiento:
- main.py
- .env
- requirements.txt

La app consiste de un endpoint en la raiz ("/") en el cual muestra un mensaje en formato json
```json
{
    "message":"Hello World from ${{enviroment}}"
}
```
Siendo "enviroment" la variable que se lee del archivo `.env`.

El archivo "requirements.txt" se obtiene del comando `pip freeze > requirements.txt`, el cual deja plasmada las dependencias para poder facilitar la dockerizacion del proyecto.

## Dependencias e Imagen 
### Instalar dependencias y construccion de imagen de la aplicacion:
Para esto utilizamos los archivos mencionados anteriormente y los relacionados con docker para generar la imagen, los cuales son el `Dockerfile` y el `.dockerignore`.

En el `.dockerignore` declaramos todos loa archivos que no vamos a necesitar en el contenedor, para que la imagene quede optimizada en cuanto a peso.

En el `Dockerfile` vamos a declarar los pasos para generar una imagen con todas sus dependencias, haciendo uso del archivo `requirements.txt` a través del comando `pip install -r requirements.txt`, el cual permite tener las mismas dependencias en el docker que las que se utilizan en el ambiente virtual del desarrollo local y asegurando la homogeneidad entre los ambientes.

## Ci/Cd (Github Actions)
Vamos a tener un archivo con reglas generales para ambas ramas:

- `ecs_deploy.yml`:  Ambos tendran los mismos "stages" pero se cambiara el tag de docker dependiendo de a que rama se haya commiteado (al pushear a `development` y  `testing`).

### Stages de `.github\workflows\ecs_deploy.yml`

- `Checkout`:

Se obtienen los ultimos cambios de la rama

- `Configure AWS credentials`:

Se van a dejar las credenciales cargadas en los secrets del  repo configuradas,tiene que pertenecer a un usuario en la region del cluster con las suficientes policies de IAM para realizar el push al ECR y actualizar el servicio de ECS. 

- `Login to Amazon ECR`:

Con las credenciales configuradas en el paso anterior, nos vamos a loguear en el repository

- `Build, tag, and push image to Amazon ECR`:

En este paso se settea la variable `enviroment` con el valor del ambiente acorde a la rama en el archivo `.env`, se buildea la imagen de docker utilizando el `Dockerfile` en el cual se instalan las dependencias como mencionamos anteriormente y se pushea esta imagen al Registry para disponibilizarla actualizada. 
Se generan 2 tags, uno con el SHA para poder realizar un rollback en caso de ser necesario y una con el nombre de la rama, el cual se va a actualizar con los ultimos cambios de la rama. (Este tag se guarda para utilizarlo en el siguiente paso)

- `Fill in the new image ID in the Amazon ECS task definition`:

Se genera el "task definition" en base a el archivo `.aws/skeleton.json`, actualizando el valor de la imagen con el tag obtenido del paso anterior.

- `Deploy Amazon ECS task definition`:

Se cambia el "task definition", actualizando la task en una nueva version para que pueda correrse como servicio el cual detecta el cambio y se deploya automaticamente, dejando disponible la nueva version con el enviroment y los cambios acorde a la rama en la que se pusheo originalmente.

# Pruebas y validacion

Para probar los cambios en la aplicacion acorde a la rama, deberiamos realizar un cambio en el siguiente archivo:
- `main.py` 

En el cual podriamos modificar el mensaje de salida del endpoint para poder verificar que este se actualice:
```python
return {"message": "Hello World from "+ enviroment}
```
Podrian agregar nuevas claves y valores, cambiar el valor de la clave `message` o cambiar directamente el contenido del `return` (siempre validando que el valor de la variable `enviroment` este presente en el mimso).

Para validar el correcto funcionamiento del mismo, deberiamos ver el impacto del cambio una vez hayan corrido correctamente las actions en:
http://ec2-34-215-212-147.us-west-2.compute.amazonaws.com/
