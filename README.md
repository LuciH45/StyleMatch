# 🛒 StyleMatch: Tienda virtual de ropa con asistente de estilo integrado 

## 📥 Clonar el repositorio usando Git

Asegúrate de tener **Git** instalado antes de realizar este paso.

Abre la consola y escribe el siguiente comando:

```
git clone https://github.com/LuciH45/StyleMatch.git
```
## 🔐 Crear archivo .env y agregar la API Key de Gemini

Antes de ejecutar el proyecto, debes crear un archivo llamado `.env` en la raíz del proyecto y agregar tu clave de API de Gemini 

* El modo de obtención es mediante la página: https://aistudio.google.com/welcome?utm_source=google&utm_medium=cpc&utm_campaign=FY25-global-DR-gsem-BKWS-1710442&utm_content=text-ad-none-any-DEV_c-CRE_736763515403-ADGP_Hybrid%20%7C%20BKWS%20-%20EXA%20%7C%20Txt-Gemini%20(Growth)-Gemini%20API%20Key-KWID_2337809406845-kwd-2337809406845&utm_term=KW_google%20api%20key%20for%20gemini-ST_google%20api%20key%20for%20gemini&gclsrc=aw.ds&gad_source=1&gad_campaignid=22311566089&gbraid=0AAAAACn9t65Bf0gsDsCM3ZSLH_VPE6Maq&gclid=CjwKCAiA_orJBhBNEiwABkdmjNFRXkz9_ajp7Gm0YkWuPhwI6tbIxwC9YFLI5N3AmarGSp5jQAgLOxoCwjMQAvD_BwE.

El archivo `.env` debe contener solo esta línea: 

```
GEMINI_API_KEY="TU_GEMINI_KEY_AQUÍ"
```
## 🐍 Instalar Python y pip

Antes de continuar, asegúrate de tener instalados **Python** y **pip** en tu equipo.

## 📚 Instalar las librerías necesarias

Abre la carpeta donde se encuentra el proyecto utilizando el comando `cd` después de clonar. Luego, instala las dependencias ejecutando:

```
pip install -r requirements.txt
```

## 🚀 Ejecutar el servidor local

Después de instalar las librerías, abre la consola en la carpeta del proyecto y ejecuta uno de los siguientes comandos:

```
py manage.py runserver
```

ó

```
python manage.py runserver
```


## 🌐 Usar StyleMatch

Una vez que el servidor esté corriendo, accede a la siguiente dirección para usar StyleMatch:

[http://localhost:8000](http://localhost:8000)

## Ingreso de usuario para la app
Para entrar a la aplicación debe usar la siguiente información de usuario:

- **Usuario:** juancaciguz
- **Contraseña:** 123
