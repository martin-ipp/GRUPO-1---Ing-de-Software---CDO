# Grupo 1 — Ingeniería de Software

Pipeline ETL orquestado con Apache Airflow, almacenado en PostgreSQL y visualizado en Streamlit.

## Integrantes

- Ippolito Martin
- Gordon Andres
- Damianich Juan Segundo
- Bautista Benedetti

## Arquitectura

```
Google Drive (CSV) → Airflow (Docker) → Python ETL → PostgreSQL → Streamlit
```

---

## Requisitos previos

Instalar en este orden:

- [Git](https://git-scm.com/download/win)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

---

## Instalación (primera vez)

En Git Bash, navegá a la carpeta donde querés trabajar:

```bash
git clone https://github.com/martin-ipp/GRUPO-1---Ing-de-Software---CDO.git
cd GRUPO-1---Ing-de-Software---CDO
```

---

## 👤 Usuario Consumidor

El usuario consumidor solo necesita ver el dashboard. No requiere conocimientos técnicos ni acceder a Airflow.

### 1. Levantar el entorno

Asegurate de que Docker Desktop esté abierto y corriendo, luego ejecutá en Git Bash:

```bash
docker compose up -d
```

### 2. Ver el dashboard

Abrí el navegador y navegá a:

```
http://localhost:8501
```

Eso es todo. El dashboard muestra los datos más recientes cargados en la base de datos.

### 3. Apagar el entorno

```bash
docker compose down
```

---

## 🛠️ Usuario Desarrollador

El desarrollador tiene acceso completo al entorno — puede ejecutar el pipeline, ver logs y modificar el código.

### 1. Levantar el entorno

Asegurate de que Docker Desktop esté abierto y corriendo:

```bash
docker compose up -d
```

Airflow queda disponible en http://localhost:8080  
Usuario: `admin` | Contraseña: `admin`

Dashboard Streamlit en http://localhost:8501

### 2. Ejecutar el pipeline

En la interfaz de Airflow, buscá el DAG `pipeline_ventas` y hacé clic en **Trigger DAG** ▶.

El pipeline ejecuta en orden:

1. `crear_tablas` — crea la base de datos y las tablas en PostgreSQL si no existen
2. `extract` — descarga el CSV actualizado desde Google Drive automáticamente
3. `transform` — limpia y normaliza los datos
4. `aggregate` — genera resumen de ventas por categoría
5. `load` — carga los datos agregados en PostgreSQL

No es necesario configurar ningún archivo de datos manualmente — el pipeline lo hace solo.

### 3. Apagar el entorno

```bash
docker compose down
```

---

## Estructura del proyecto

```
GRUPO-1---Ing-de-Software---CDO/
├── dags/
│   └── pipeline_dag.py        # DAG principal de Airflow
├── data/
│   ├── raw/                   # CSV descargado automáticamente (no se sube a GitHub)
│   └── processed/             # Archivos intermedios generados (no se suben a GitHub)
├── etl/
│   ├── extract.py             # Descarga el CSV desde Google Drive
│   ├── transform.py           # Limpieza y normalización
│   ├── aggregate.py           # Agregación por categoría
│   ├── setup_db.py            # Crea la base de datos y las tablas
│   └── load.py                # Carga en PostgreSQL
├── streamlit/
│   ├── Dockerfile             # Imagen Docker de Streamlit
│   └── dashboard.py           # Dashboard interactivo
├── sandbox/                   # Scripts de prueba y experimentación
├── tests/                     # Tests unitarios
├── .gitignore
├── docker-compose.yml
├── requirements.txt           # Librerías Python
└── README.md
```

---

## Convención de commits (desarrolladores)

| Prefijo | Uso |
|---|---|
| `feat:` | nueva funcionalidad |
| `fix:` | corrección de bug |
| `docs:` | cambios en documentación |
| `refactor:` | mejora de código sin cambiar funcionalidad |