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

Absorbe lo que sí sube la fidelidad de [Distilly](https://github.com/titanwings/distilly), [Nüwa](https://github.com/alchaincyf/nuwa-skill) y [Cangjie](https://github.com/Yeadon8888/cangjie-skill), y añade las capas que ellos omiten.
<br>
 **pangu-distill.meta-skill** extrae **marcos de pensamiento ejecutables** de cualquier sujeto.

---

**Navegación Rápida**

[Demo](#demo) | [Instalación Rápida](#instalación-rápida) | [Skills publicados](#skills-publicados) | [Casos Clásicos](#casos-clásicos) | [Arquitectura](#arquitectura) | [Estructura del Repositorio](#estructura-del-repositorio) | [Sobre Mí](#sobre-mí)

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

### Usuarios Técnicos

El mismo `SKILL.md` corre en Claude Code, Cursor, Codex y OpenClaw. Solo cambia la ruta de descubrimiento. Ver [host-compatibility.md](references/host-compatibility.md).

```bash
npx skills add wukongnotnull/pangu-distill
```

Después de instalar, dí esto a tu Agent:

```markdown
> Destilar "Largoplacismo"
> Quiero construir un marco de pensamiento de Buffett
```

### Usuarios No Técnicos (Conversacional)

No hay comandos que recordar — solo copia y pega esto a tu Agent:

```
帮我安装这个 skill：https://github.com/wukongnotnull/pangu-distill
```

Después de instalar, dile lo que quieres en lenguaje natural:

```markdown
> Ayúdame a destilar: largoplacismo
> Quiero construir un marco de pensamiento de Buffett
```

## Skills publicados

Skills ya publicados desde pangu-distill:

| Skill | Fuente | Repositorio |
|------|------|------|
| **pangu-deepseek-v4** | DeepSeek-V4 Technical Report | [wukongnotnull/pangu-deepseek-v4](https://github.com/wukongnotnull/pangu-deepseek-v4) |
| **pangu-one-day-life-reset** | *How to fix your entire life in 1 day* | [wukongnotnull/pangu-one-day-life-reset](https://github.com/wukongnotnull/pangu-one-day-life-reset) |

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

Extraer marcos de pensamiento ejecutables de cualquier sujeto: Persona / Contenido / Ideas / Fenómenos / **Yo**.

**4.5 capas** (el límite honesto no es un apéndice) + **extracción de 7 niveles** (primero la historia de origen, las frases al final) + triple verificación + disparadores + pasos de razonamiento + `scripts/run.py` obligatorio + puntuación de fidelidad con dos agentes independientes (≥80, sin autoevaluación).

### Flujo de Ejecución

Aclarar → crear directorio → recolectar con scripts (hasta 7 agentes) → extraer → construir → verificar → tres rondas de refinamiento.

Cada modelo mental necesita historia de origen, evidencia cruzada, disparador, pasos y límite.

### Validación de Calidad

Puerta de proceso: `quality-checklist.md`. Puerta de fábrica: `fidelity-scorecard.md`. El agente que responde y el que puntúa deben ser distintos. Por debajo de 80 no se entrega.

---

## Estructura del Repositorio

```
pangu-distill/
├── SKILL.md
├── .agents/skills/
├── .claude/skills/skill-creator/
├── .claude/skills/skill-vetter/
├── references/
│   ├── host-compatibility.md
│   ├── distillation-methodology.md
│   ├── research-guide.md
│   ├── quality-checklist.md
│   ├── fidelity-scorecard.md
│   ├── output-spec.md
│   ├── anti-patterns.md
│   ├── special-scenarios.md
│   ├── examples/distillation-example.md
│   └── templates/
└── scripts/
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
