# Grupo 1 — Ingeniería de Software

Pipeline ETL orquestado con Apache Airflow, almacenado en PostgreSQL y visualizado en Streamlit.

## Integrantes

- (completar con nombres del grupo)

## Arquitectura

```
Google Drive (CSV) → Airflow (Docker) → Python ETL → PostgreSQL → Streamlit
```

## Requisitos previos

Instalar en este orden:

- [Git](https://git-scm.com/download/win)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Astro CLI](https://docs.astronomer.io/astro/cli/install-cli) — en Windows ejecutar en PowerShell como administrador:

```powershell
winget install -e --id Astronomer.Astro
```

## Instalación y configuración (primera vez)

### 1. Clonar el repositorio

En Git Bash, navegá a la carpeta donde querés trabajar:

```bash
git clone https://github.com/martin-ipp/GRUPO-1---Ing-de-Software---CDO.git
cd GRUPO-1---Ing-de-Software---CDO
```

### 2. Levantar el entorno

Asegurate de que Docker Desktop esté abierto y corriendo, luego ejecutá en Git Bash:

```bash
astro dev start
```

Airflow queda disponible en http://localhost:8080  
Usuario: `admin` | Contraseña: `admin`

### 3. Ejecutar el pipeline

En la interfaz de Airflow, buscá el DAG `pipeline_ventas` y hacé clic en **Trigger DAG** ▶.

El pipeline ejecuta en orden:

1. `crear_tablas` — crea la base de datos y las tablas en PostgreSQL si no existen
2. `extract` — descarga el CSV actualizado desde Google Drive automáticamente
3. `transform` — limpia y normaliza los datos
4. `aggregate` — genera resumen de ventas por categoría
5. `load` — carga los datos transformados en PostgreSQL

No es necesario descargar ni configurar ningún archivo de datos manualmente — el pipeline lo hace solo.

---

## Flujo de trabajo diario con Git

Antes de empezar a trabajar, siempre traer los últimos cambios:

```bash
git pull origin main
```

Para subir cambios, trabajar siempre en una rama propia:

```bash
git checkout -b feature/nombre-de-tu-tarea
# ... hacés tus cambios ...
git add .
git commit -m "feat: descripción clara del cambio"
git push origin feature/nombre-de-tu-tarea
```

Luego abrís un **Pull Request** en GitHub hacia `main` para que el equipo revise antes de mergear.

## Convención de commits

| Prefijo | Uso |
|---|---|
| `feat:` | nueva funcionalidad |
| `fix:` | corrección de bug |
| `docs:` | cambios en documentación |
| `refactor:` | mejora de código sin cambiar funcionalidad |

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
│   └── dashboard.py           # Dashboard interactivo
├── sandbox/                   # Scripts de prueba y experimentación
├── tests/                     # Tests unitarios
├── .gitignore
├── docker-compose.override.yml
├── Dockerfile
├── requirements.txt           # Librerías Python
└── README.md
```

---

## Apagar el entorno

```bash
astro dev stop
```