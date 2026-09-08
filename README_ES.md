<div align="center">

# pangu-distill.meta-skill

<br>

> **Destilar todo en marcos de pensamiento ejecutables** <br>

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-orange.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/skills.sh-Compatible-green)](https://skills.sh)

<br>

**Pangu (el Creador), después de abrir el cielo y la tierra, sintió que el mundo estaba solo,** <br>
**Moldeó personas del barro amarillo, les sopló vida,** <br>
**Resultado: Las personas de barro ahora dominan el mundo.**

<br>

Inspirado por [colleague.skill](https://github.com/titanwings/colleague-skill) y [Nuwa.skill](https://github.com/titanwings/colleague-skill), destilando marcos de pensamiento de figuras famosas, difuntos y élites.
<br>
 **pangu-distill.meta-skill** extrae **marcos de pensamiento ejecutables** de cualquier sujeto.

---

**Navegación Rápida**

[Demo](#demo) | [Instalación Rápida](#instalación-rápida) | [Casos Clásicos](#casos-clásicos) | [Arquitectura](#arquitectura) | [Estructura del Repositorio](#estructura-del-repositorio) | [Sobre Mí](#sobre-mí)

<br>

**Otros Idiomas**

[中文](README.md) · [English](README_EN.md) · [日本語](README_JA.md) · [한국어](README_KO.md)

<br>


</div>

---

## Demo

Destilar el largoplacismo extrae no solo "persistencia," sino un marco cognitivo ejecutable:

```
Usuario    ❯ Destilar "Largoplacismo"

Pangu      ❯ 【Fase 1 en progreso】
            ✓ Recolección de seis corrientes completa (obras/entrevistas/crítica/decisiones/línea de tiempo/similares)
            ✓ Verificación triple del modelo mental aprobada
            ✓ Destilación completa

            Producción: "Largoplacismo · Marco de Pensamiento"

            Modelos Mentales Centrales:
            ① Pensamiento compuesto: persistir como amigo del tiempo, disfrutar el crecimiento exponencial
            ② Enfoque a largo plazo: ignorar fluctuaciones a corto plazo, concentrarse en valor a largo plazo
            ③ Perseverancia: no rendirse en tiempos difíciles

            ADN de Expresión:
            - Alta certeza: "obviamente," "debe," "sin duda"
            - Pocas frases de transición, rara vez usar "pero"
            - Muletillas: "amigo del tiempo," "lento es rápido"
```

---

## Instalación Rápida

### Método 1: Usuarios Técnicos (Línea de Comando)

Instalar directamente con npx:

```bash
npx skills add wukongnotnull/pangu-distill
```

Después de instalar, dí esto a tu Agent:

```markdown
> Destilar "Largoplacismo"
> Quiero construir un marco de pensamiento de Buffett
```

### Método 2: Usuarios No Técnicos (Conversacional)

No hay comandos que recordar — solo copia y pega esto a tu Agent:

```
帮我安装这个 skill：https://github.com/wukongnotnull/pangu-distill
```

Después de instalar, dile lo que quieres en lenguaje natural:

```markdown
> Ayúdame a destilar: largoplacismo
> Quiero construir un marco de pensamiento de Buffett
```

## Casos Clásicos

Estas 13 figuras son casos de destilación planificados. Los Skills terminados **aún no se han publicado**:

### 💰 Inversión / Negocios

| Persona | Dominio | Estado |
|------|---------|------------------|
| **Naval** | Riqueza / Apalancamiento / Filosofía de Vida | Aún no publicado |
| **Munger** | Inversión / Modelos Mentales / Inversión | Aún no publicado |
| **Zhang Xuefeng** | Educación / Planificación de Carrera / Movilidad de Clase | Aún no publicado |

### 🚀 Startup / Producto

| Persona | Dominio | Estado |
|------|---------|------------------|
| **Paul Graham** | Startups / Escritura / Producto / Filosofía de Vida | Aún no publicado |
| **Zhang Yiming** | Producto / Organización / Globalización / Talento | Aún no publicado |
| **Steve Jobs** | Producto / Diseño / Estrategia | Aún no publicado |
| **Elon Musk** | Ingeniería / Costo / Principios Primeros | Aún no publicado |

### 🤖 IA / Tecnología

| Persona | Dominio | Estado |
|------|---------|------------------|
| **Karpathy** | IA / Ingeniería / Educación / Código Abierto | Aún no publicado |
| **Ilya Sutskever** | Seguridad IA / Scaling / Gusto de Investigación | Aún no publicado |

### 🎬 Creación de Contenido

| Persona | Dominio | Estado |
|------|---------|------------------|
| **MrBeast** | Creación de Contenido / Metodología de YouTube | Aún no publicado |

### 🎯 Comunicación / Poder

| Persona | Dominio | Estado |
|------|---------|------------------|
| 🔥**Trump** | Negociación / Poder / Comunicación / Predicción de Comportamiento | Aún no publicado |

### 🧠 Pensamiento / Aprendizaje

| Persona | Dominio | Estado |
|------|---------|------------------|
| **Feynman** | Aprendizaje / Enseñanza / Pensamiento Científico | Aún no publicado |
| **Taleb** | Riesgo / Antifragilidad / Incertidumbre | Aún no publicado |

---

## Arquitectura

### Capacidad Principal

Extraer marcos de pensamiento ejecutables de cualquier sujeto, produciendo Skills de Persona / Contenido / Ideas / Fenómenos.

### Flujo de Ejecución

#### Fase 1: Destilación

**Paso 1: Recolección de Información**

3 Agentes recolectan en paralelo (modo maestro-esclavo):

| Agente | Responsabilidad | Archivo de Salida |
|-------|------|---------|
| Master (Recolector de Materiales) | Obras centrales + Línea de tiempo | `01-writings.md`, `06-timeline.md` |
| Analyst A | Podcasts/Entrevistas + ADN de Expresión | `02-conversations.md`, `03-expression-dna.md` |
| Analyst B | Crítica + Decisiones Importantes + Similares | `04-limitations.md`, `05-decisions.md`, `07-similar-objects.md` |

**Paso 2: Extracción del Marco**

- **Verificación Triple del Modelo Mental**:
  - Verificación 1: Reproducción cruzada (≥2 campos diferentes)
  - Verificación 2: Poder generativo (puede inferir posiciones en nuevas preguntas)
  - Verificación 3: Exclusividad (no es lo que cualquier persona inteligente pensaría)
  - Pasa 3 → Modelo mental; Pasa 1-2 → Heurística de decisión

- **Cuantificación del ADN de Expresión**: Huellas dactilares de oraciones, etiquetas de estilo, palabras tabú y muletillas

- **Manejo de Contradicciones**: Contradicciones temporales → registrar trayectoria de evolución; Contradicciones de dominio → registrar por campo; Tensiones esenciales → definir explícitamente como tensiones centrales

**Paso 3: Construcción del Skill**

3-7 modelos mentales + 5-10 heurísticas de decisión + ADN de Expresión + Valores y Anti-patrones + Límites honestos

### Validación de Calidad

Probar con 3 preguntas que la persona respondió públicamente — la dirección debe coincidir. Ante una pregunta nueva no cubierta por el Skill, el marco debe inferir una postura coherente.

---

## Estructura del Repositorio

```
pangu-distill/
├── SKILL.md                           # pangu-distill en sí
├── references/
│   ├── quality-checklist.md            # Lista de verificación de calidad
│   ├── special-scenarios.md           # Manejo de escenarios especiales
│   ├── examples/                       # Ejemplos de destilación
│   │   └── distillation-example.md    # Ejemplo de destilación (Largoplacismo)
│   └── templates/                       # Plantillas de Skill
│       ├── README.md                  # Índice de plantillas
│       ├── person-skill-template.md   # Plantilla de destilación tipo persona D1
│       ├── content-skill-template.md  # Plantilla de destilación tipo contenido D2
│       ├── idea-skill-template.md     # Plantilla de destilación tipo idea D3
│       └── phenomenon-skill-template.md # Plantilla de destilación tipo fenómeno D4
└── scripts/                            # Módulo de búsqueda Python
    ├── search/                         # Tubería de búsqueda
    ├── crawl/                          # Rastreo web
    └── transcribe/                     # Transcripción de audio/video
```

---

## Sobre Mí

**Wukong Feikong Ye** — Fundador de AI Dao, desarrollador independiente, YouTuber.

| Plataforma         | Enlace                                                                         |
| ------------ | ---------------------------------------------------------------------------- |
| 🌐  Sitio Web    | [waytoai.cn](https://waytoai.cn)                                                |
| 𝕏  Twitter   | [悟空非空也](https://x.com/wukongnotnull)                                   |
| 📺  BiliBili       | [悟空非空也](https://space.bilibili.com/456634391)                              |
| ▶️  YouTube   | [悟空非空也](https://www.youtube.com/@wukongnotnull)                        |
| 📕  XiaoHongShu    | [悟空非空也](https://www.xiaohongshu.com/user/profile/5ca89c2f000000001100952b) |
| 💬  WeChat    | Busca「悟空非空也」o escanea el código QR abajo ↓                                            |

<img src="./images/wechat-qrcode.jpg" alt="Código QR de WeChat" width="360">

---

<div align="center">

Apache-2.0 license © [悟空非空也](https://github.com/wukongnotnull)

</div>
