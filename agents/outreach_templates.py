"""
LinkedIn Outreach Templates — Klik Energy · Mercado No Regulado Colombia
Templates personalizados por cargo para agendar demos.

Tokens de personalización:
  {nombre}   → Primer nombre del contacto
  {empresa}  → Nombre de la empresa
  {ciudad}   → Ciudad de la empresa
  {sector}   → Sector industrial
  {cargo}    → Cargo del contacto

Etapas: connection | primer_mensaje | followup_1 | followup_2 | demo_request
Roles:  mantenimiento | planta | general | operaciones | financiero
"""

from typing import Optional

# ── Mapeo de cargos a roles de template ───────────────────────────────────────

ROLE_KEYWORDS = {
    "mantenimiento": [
        "mantenimiento", "maintenance", "facilities", "confiabilidad",
        "reliability", "activos", "assets", "instrumentación",
    ],
    "planta": [
        "planta", "producción", "produccion", "manufactura", "plant",
        "manufacturing", "fabricación", "fabricacion", "proceso",
    ],
    "operaciones": [
        "operaciones", "operations", "coo", "operativo", "logística",
        "logistica", "supply chain", "cadena", "abastecimiento",
    ],
    "financiero": [
        "financiero", "finanzas", "finance", "cfo", "tesorería",
        "tesoreria", "presupuesto", "budget", "contralor", "controller",
    ],
    "general": [
        "general", "gerente general", "ceo", "presidente", "director ejecutivo",
        "country manager", "managing director", "vp", "vicepresidente",
    ],
}


def get_role_category(title: str) -> str:
    title_lower = title.lower()
    for role, keywords in ROLE_KEYWORDS.items():
        if any(kw in title_lower for kw in keywords):
            return role
    return "general"


# ── Templates por etapa y rol ──────────────────────────────────────────────────

TEMPLATES: dict[str, dict[str, list[dict]]] = {

    # ── SOLICITUD DE CONEXIÓN (max 300 chars) ─────────────────────────────────
    "connection": {
        "mantenimiento": [
            {
                "id": "conn_mant_01", "tone": "directo",
                "text": (
                    "Hola {nombre}, veo que lideras mantenimiento en {empresa}. "
                    "En Klik Energy acompañamos a plantas industriales a reducir "
                    "costos energéticos en el mercado no regulado. "
                    "¿Te parece si conectamos? Tengo algo concreto para compartirte."
                ),
            },
            {
                "id": "conn_mant_02", "tone": "técnico",
                "text": (
                    "Hola {nombre}, trabajo con directores de mantenimiento en {sector} "
                    "para optimizar contratos de energía en el mercado no regulado. "
                    "En {empresa} podrían ver un ahorro real. ¿Conectamos?"
                ),
            },
            {
                "id": "conn_mant_03", "tone": "casual",
                "text": (
                    "Hola {nombre}, gestionar la energía de una planta tiene sus retos. "
                    "En Klik Energy tenemos un modelo que ya está funcionando en empresas "
                    "como {empresa} en {ciudad}. ¿Conectamos para compartirte los números?"
                ),
            },
        ],
        "planta": [
            {
                "id": "conn_plan_01", "tone": "directo",
                "text": (
                    "Hola {nombre}, en Klik Energy trabajamos con directores de planta "
                    "en {sector} para reducir el costo energético por unidad producida. "
                    "¿Conectamos? Tengo datos concretos de {ciudad} que te pueden interesar."
                ),
            },
            {
                "id": "conn_plan_02", "tone": "ROI",
                "text": (
                    "Hola {nombre}, veo que diriges operaciones en {empresa}. "
                    "En el mercado no regulado, plantas similares en {sector} "
                    "han reducido su factura energética hasta un 15%. "
                    "¿Te parece si conversamos?"
                ),
            },
            {
                "id": "conn_plan_03", "tone": "referencial",
                "text": (
                    "Hola {nombre}, otras plantas de {sector} en Colombia ya eligieron "
                    "a Klik Energy como comercializador en el mercado no regulado. "
                    "Me gustaría mostrarte qué lograron. ¿Conectamos?"
                ),
            },
        ],
        "general": [
            {
                "id": "conn_gen_01", "tone": "ejecutivo",
                "text": (
                    "Hola {nombre}, en Klik Energy ayudamos a empresas industriales "
                    "a transformar su factura eléctrica en una ventaja competitiva "
                    "en el mercado no regulado. Creo que {empresa} califica. ¿Conectamos?"
                ),
            },
            {
                "id": "conn_gen_02", "tone": "estratégico",
                "text": (
                    "Hola {nombre}, muchas empresas de {sector} en {ciudad} "
                    "están migrando al mercado no regulado y ahorrando entre 8-15% "
                    "en energía. Me gustaría mostrarte el modelo. ¿Te parece si conectamos?"
                ),
            },
            {
                "id": "conn_gen_03", "tone": "directo",
                "text": (
                    "Hola {nombre}, soy de Klik Energy. Ayudamos a gerentes generales "
                    "del sector industrial a reducir OPEX con energía más competitiva. "
                    "¿Conectamos para compartirte algo concreto sobre {empresa}?"
                ),
            },
        ],
        "operaciones": [
            {
                "id": "conn_oper_01", "tone": "eficiencia",
                "text": (
                    "Hola {nombre}, en Klik Energy optimizamos el componente energético "
                    "del costo operativo para empresas de {sector} en el mercado no regulado. "
                    "Creo que tiene sentido conectarnos. ¿Te parece?"
                ),
            },
            {
                "id": "conn_oper_02", "tone": "KPI",
                "text": (
                    "Hola {nombre}, el costo de energía puede representar hasta el 30% "
                    "del OPEX en plantas industriales. En Klik Energy lo bajamos. "
                    "¿Conectamos para ver si aplica para {empresa}?"
                ),
            },
            {
                "id": "conn_oper_03", "tone": "directo",
                "text": (
                    "Hola {nombre}, trabajamos con directores de operaciones en {sector} "
                    "para reducir la factura energética en el mercado no regulado. "
                    "{empresa} en {ciudad} podría calificar. ¿Hablamos?"
                ),
            },
        ],
        "financiero": [
            {
                "id": "conn_fin_01", "tone": "ROI",
                "text": (
                    "Hola {nombre}, ¿sabías que empresas de {sector} con demanda similar "
                    "a {empresa} están reduciendo su factura eléctrica hasta 15% "
                    "en el mercado no regulado? En Klik Energy lo hacemos posible. ¿Conectamos?"
                ),
            },
            {
                "id": "conn_fin_02", "tone": "presupuesto",
                "text": (
                    "Hola {nombre}, en Klik Energy ayudamos a CFOs del sector industrial "
                    "a reducir el gasto energético sin inversión de capital. "
                    "¿Te parece si conectamos? Tengo números que te pueden interesar."
                ),
            },
            {
                "id": "conn_fin_03", "tone": "OPEX",
                "text": (
                    "Hola {nombre}, la energía eléctrica es uno de los mayores rubros "
                    "del OPEX industrial. En el mercado no regulado se puede controlar. "
                    "¿Conectamos para ver qué aplica para {empresa}?"
                ),
            },
        ],
    },

    # ── PRIMER MENSAJE (post-conexión) ────────────────────────────────────────
    "primer_mensaje": {
        "mantenimiento": [
            {
                "id": "pm_mant_01", "tone": "técnico",
                "text": (
                    "Hola {nombre}, gracias por conectar.\n\n"
                    "Trabajo con directores de mantenimiento en el sector {sector} "
                    "para resolver algo que probablemente ya tienes en el radar: "
                    "la factura eléctrica de {empresa}.\n\n"
                    "Si {empresa} consume más de 0.1 MW de demanda, tiene la opción de "
                    "elegir su comercializador de energía en el mercado no regulado. "
                    "Esto significa tarifas más competitivas, contratos a medida y "
                    "mejor calidad en la atención de fallas.\n\n"
                    "¿Tienen ya evaluado esto o aún están en mercado regulado? "
                    "Con gusto te comparto cómo lo están haciendo otras plantas "
                    "de {sector} en {ciudad}."
                ),
            },
            {
                "id": "pm_mant_02", "tone": "problema-solución",
                "text": (
                    "Hola {nombre}, un gusto conectar.\n\n"
                    "Sé que para mantenimiento, la energía eléctrica es crítica: "
                    "la calidad de la señal afecta directamente equipos, vida útil "
                    "y paradas no programadas.\n\n"
                    "En Klik Energy, además de ofrecerte tarifas más competitivas "
                    "en el mercado no regulado, tienes acceso a un gestor de cuenta "
                    "dedicado para atender incidentes con el operador de red "
                    "más rápido que en el mercado regulado.\n\n"
                    "¿Tienes 20 minutos esta semana para que te muestre cómo funciona "
                    "con un caso real de {sector} en {ciudad}?"
                ),
            },
            {
                "id": "pm_mant_03", "tone": "valor-inmediato",
                "text": (
                    "Hola {nombre}, gracias por aceptar.\n\n"
                    "Voy directo al punto: si {empresa} tiene una demanda eléctrica "
                    "mayor a 0.1 MW, puede elegir libremente su comercializador de energía. "
                    "La mayoría de plantas industriales en {sector} que han hecho ese cambio "
                    "han visto entre 8% y 15% de reducción en su factura eléctrica.\n\n"
                    "Para mantenimiento, eso también se traduce en acceso prioritario "
                    "a datos de consumo en tiempo real y mejor respuesta ante variaciones "
                    "de tensión.\n\n"
                    "¿Vale la pena explorar esto para {empresa}? "
                    "Puedo hacer el diagnóstico inicial sin costo."
                ),
            },
        ],
        "planta": [
            {
                "id": "pm_plan_01", "tone": "productividad",
                "text": (
                    "Hola {nombre}, gracias por conectar.\n\n"
                    "Como director de planta en {empresa}, sabes que la energía "
                    "es uno de los insumos más importantes y menos controlables. "
                    "En el mercado no regulado eso cambia.\n\n"
                    "Con Klik Energy puedes negociar tarifas según tu perfil de consumo, "
                    "con mayor previsibilidad en el costo por unidad producida. "
                    "Plantas de {sector} similares en {ciudad} ya lo están haciendo "
                    "y han mejorado su margen operativo.\n\n"
                    "¿Estarías disponible esta semana para una llamada de 20 minutos "
                    "donde te muestro los números reales?"
                ),
            },
            {
                "id": "pm_plan_02", "tone": "benchmark",
                "text": (
                    "Hola {nombre}, un placer conectar.\n\n"
                    "Muchas plantas de {sector} en Colombia ya migraron al mercado "
                    "no regulado y están pagando entre 8% y 15% menos por kilovatio. "
                    "El requisito: demanda mayor a 0.1 MW, que probablemente {empresa} cumple.\n\n"
                    "Lo que hace diferente a Klik Energy es el acompañamiento: "
                    "te ayudamos a analizar tu curva de carga, negociar el contrato "
                    "y gestionar la relación con el operador de red.\n\n"
                    "¿Puedo enviarte un análisis preliminar de {empresa} "
                    "basado en el sector y el consumo estimado?"
                ),
            },
            {
                "id": "pm_plan_03", "tone": "simple",
                "text": (
                    "Hola {nombre}, gracias por conectar.\n\n"
                    "Una pregunta directa: ¿ya está {empresa} en el mercado no regulado de energía?\n\n"
                    "Si no, probablemente está pagando más de lo que debería. "
                    "En Klik Energy le ayudamos a empresas de {sector} a hacer "
                    "esa transición de forma sencilla y sin riesgo operativo.\n\n"
                    "Si te interesa, puedo compartirte un caso de una planta de {sector} "
                    "en {ciudad} con resultados concretos. ¿Te va bien esta semana?"
                ),
            },
        ],
        "general": [
            {
                "id": "pm_gen_01", "tone": "estratégico",
                "text": (
                    "Hola {nombre}, gracias por conectar.\n\n"
                    "Le quiero compartir algo que está impactando la competitividad "
                    "de varias empresas del sector {sector} en Colombia.\n\n"
                    "Las que han migrado al mercado no regulado de energía están reduciendo "
                    "su costo eléctrico entre 8% y 15%, lo que en plantas de mediana y "
                    "gran escala representa millones de pesos al año en OPEX.\n\n"
                    "En Klik Energy acompañamos ese proceso de principio a fin: "
                    "diagnóstico, negociación del contrato y gestión continua.\n\n"
                    "¿Tiene 20 minutos esta semana para explorar si {empresa} "
                    "puede beneficiarse de esto?"
                ),
            },
            {
                "id": "pm_gen_02", "tone": "peers",
                "text": (
                    "Hola {nombre}, un placer.\n\n"
                    "Varias empresas de {sector} en {ciudad} ya tomaron la decisión "
                    "de cambiar de comercializador de energía al mercado no regulado. "
                    "El resultado: mejor tarifa, mayor previsibilidad y atención personalizada.\n\n"
                    "Como líder de {empresa}, sé que cada punto de reducción en OPEX "
                    "tiene un impacto directo en los resultados del negocio.\n\n"
                    "¿Vale la pena que sus equipos evalúen esta opción? "
                    "Con mucho gusto le preparo un estimado inicial sin compromiso."
                ),
            },
            {
                "id": "pm_gen_03", "tone": "conciso",
                "text": (
                    "Hola {nombre}, gracias por conectar.\n\n"
                    "Directo al punto: si {empresa} tiene demanda eléctrica superior "
                    "a 0.1 MW, tiene derecho a elegir su comercializador y negociar "
                    "tarifas en el mercado no regulado.\n\n"
                    "En Klik Energy hacemos que ese proceso sea simple y rentable. "
                    "Empresas similares en el sector {sector} han visto retornos "
                    "reales desde el primer mes de contrato.\n\n"
                    "¿Le puedo enviar un análisis de 2 páginas adaptado a {empresa}?"
                ),
            },
        ],
        "operaciones": [
            {
                "id": "pm_oper_01", "tone": "OPEX",
                "text": (
                    "Hola {nombre}, gracias por conectar.\n\n"
                    "La energía eléctrica puede representar entre el 15% y el 30% "
                    "del OPEX en plantas de {sector}. Es uno de los pocos costos "
                    "variables que se puede controlar con la estrategia correcta.\n\n"
                    "En Klik Energy trabajamos con directores de operaciones para "
                    "migrar al mercado no regulado y negociar tarifas a medida "
                    "del perfil de consumo de cada planta.\n\n"
                    "¿Tiene {empresa} evaluado esto? Me gustaría mostrarte cómo "
                    "lo están haciendo otras operaciones en {ciudad}."
                ),
            },
            {
                "id": "pm_oper_02", "tone": "métricas",
                "text": (
                    "Hola {nombre}, un gusto conectar.\n\n"
                    "Sé que para operaciones, los KPIs energéticos son críticos: "
                    "costo por kWh, factor de potencia, demanda pico, eficiencia "
                    "por línea de producción.\n\n"
                    "En el mercado no regulado, tienes más herramientas para gestionarlos. "
                    "Klik Energy te da acceso a datos de consumo en tiempo real, "
                    "alertas de demanda y asesoría técnica continua, además de "
                    "tarifas más competitivas.\n\n"
                    "¿Hablamos esta semana? Te muestro el modelo con un caso real."
                ),
            },
            {
                "id": "pm_oper_03", "tone": "simple",
                "text": (
                    "Hola {nombre}, gracias por conectar.\n\n"
                    "Una pregunta concreta: ¿están gestionando activamente "
                    "el costo energético en {empresa} o es un costo que simplemente llega?\n\n"
                    "En el mercado no regulado se puede negociar, optimizar y predecir. "
                    "En Klik Energy acompañamos a equipos de operaciones a hacer "
                    "esa transición sin afectar la continuidad del proceso.\n\n"
                    "¿Te parece si lo revisamos juntos? 20 minutos son suficientes."
                ),
            },
        ],
        "financiero": [
            {
                "id": "pm_fin_01", "tone": "ROI",
                "text": (
                    "Hola {nombre}, gracias por conectar.\n\n"
                    "Tengo un dato que probablemente te interesa: empresas del sector "
                    "{sector} con un perfil de consumo similar al de {empresa} "
                    "están reduciendo su gasto eléctrico entre 8% y 15% al migrar "
                    "al mercado no regulado de energía.\n\n"
                    "En Klik Energy gestionamos todo el proceso: análisis de viabilidad, "
                    "negociación del contrato y acompañamiento continuo. "
                    "Sin inversión de capital y con impacto desde el primer mes.\n\n"
                    "¿Tiene sentido que lo revisemos? Puedo preparar un estimado "
                    "de ahorro para {empresa} en 48 horas."
                ),
            },
            {
                "id": "pm_fin_02", "tone": "presupuesto",
                "text": (
                    "Hola {nombre}, un gusto conectar.\n\n"
                    "Como responsable financiero en {empresa}, sé que cada línea "
                    "del OPEX importa. La energía eléctrica suele ser una de las más "
                    "difíciles de reducir... hasta que se migra al mercado no regulado.\n\n"
                    "Con Klik Energy, empresas de {sector} en {ciudad} han logrado "
                    "ahorros reales sin inversión, sin cambios en infraestructura "
                    "y con contratos flexibles.\n\n"
                    "¿Puedo enviarte un análisis de impacto en el P&L de {empresa}? "
                    "No toma más de 20 minutos revisarlo juntos."
                ),
            },
            {
                "id": "pm_fin_03", "tone": "capex-cero",
                "text": (
                    "Hola {nombre}, gracias por aceptar.\n\n"
                    "Le propongo algo concreto: en Klik Energy hacemos un diagnóstico "
                    "gratuito de la factura eléctrica de {empresa} para determinar "
                    "si califica para el mercado no regulado y cuánto podría ahorrar.\n\n"
                    "Normalmente esto toma 20 minutos de conversación y una factura "
                    "de energía reciente. Sin compromiso, sin costo, sin cambios "
                    "en la operación.\n\n"
                    "¿Le parece que lo agendamos esta semana?"
                ),
            },
        ],
    },

    # ── SEGUIMIENTO 1 (3-5 días después) ─────────────────────────────────────
    "followup_1": {
        "mantenimiento": [
            {
                "id": "fu1_mant_01", "tone": "soft",
                "text": (
                    "Hola {nombre}, quería hacer seguimiento a mi mensaje anterior.\n\n"
                    "Entiendo que el día a día de mantenimiento es intenso. "
                    "Por eso te dejo esto breve: si {empresa} tiene una demanda "
                    "eléctrica mayor a 0.1 MW, puede estar pagando más de lo necesario.\n\n"
                    "¿Tienes 15 minutos esta semana para explorar los números?"
                ),
            },
            {
                "id": "fu1_mant_02", "tone": "valor",
                "text": (
                    "Hola {nombre}, siguiendo el hilo de mi mensaje.\n\n"
                    "Te comparto un dato rápido: una planta de {sector} en Colombia "
                    "ahorró $180M COP anuales al migrar al mercado no regulado "
                    "con Klik Energy. La demanda era similar a la de {empresa}.\n\n"
                    "¿Vale la pena que revisemos si aplica para ustedes?"
                ),
            },
            {
                "id": "fu1_mant_03", "tone": "pregunta",
                "text": (
                    "Hola {nombre}, ¿tuviste oportunidad de ver mi mensaje?\n\n"
                    "Una pregunta directa: ¿quién en {empresa} toma las decisiones "
                    "sobre el contrato de energía eléctrica? "
                    "Si no eres tú, con gusto me dices con quién hablar. "
                    "Si eres tú, me encantaría mostrarte lo que tenemos para {sector}."
                ),
            },
        ],
        "planta": [
            {
                "id": "fu1_plan_01", "tone": "benchmark",
                "text": (
                    "Hola {nombre}, retomo mi mensaje anterior.\n\n"
                    "Esta semana estuvimos con una planta de {sector} en {ciudad} "
                    "que redujo su costo energético en un 12% al migrar con Klik Energy. "
                    "El proceso tomó 3 semanas sin interrumpir operaciones.\n\n"
                    "¿Tiene sentido revisarlo para {empresa}?"
                ),
            },
            {
                "id": "fu1_plan_02", "tone": "simple",
                "text": (
                    "Hola {nombre}, solo quería confirmar si recibiste mi mensaje.\n\n"
                    "Lo resumo en una pregunta: ¿{empresa} ya está en el mercado "
                    "no regulado de energía, o todavía están en el regulado?\n\n"
                    "Con esa respuesta ya sé si puedo ayudarte o no. ¿Me cuentas?"
                ),
            },
            {
                "id": "fu1_plan_03", "tone": "recurso",
                "text": (
                    "Hola {nombre}, un seguimiento rápido.\n\n"
                    "Te dejo este dato por si es útil: en Colombia, toda empresa "
                    "con demanda mayor a 0.1 MW puede elegir su comercializador "
                    "de energía en el mercado no regulado. Muchas plantas de "
                    "{sector} aún no lo saben.\n\n"
                    "Si quieres saber si {empresa} califica, me cuentas y lo revisamos."
                ),
            },
        ],
        "general": [
            {
                "id": "fu1_gen_01", "tone": "ejecutivo",
                "text": (
                    "Hola {nombre}, un seguimiento breve.\n\n"
                    "Sé que el tiempo es escaso. Por eso lo dejo en una pregunta: "
                    "¿{empresa} tiene evaluado su contrato de energía eléctrica "
                    "en los últimos 12 meses?\n\n"
                    "Si no, probablemente hay una oportunidad de ahorro sin explorar. "
                    "¿Me da 15 minutos para mostrársela?"
                ),
            },
            {
                "id": "fu1_gen_02", "tone": "caso",
                "text": (
                    "Hola {nombre}, retomo mi mensaje anterior.\n\n"
                    "Una empresa de {sector} similar a {empresa} redujo "
                    "su factura eléctrica anual en $240M COP al migrar "
                    "al mercado no regulado con Klik Energy.\n\n"
                    "¿Vale la pena explorar si {empresa} puede lograr algo similar?"
                ),
            },
            {
                "id": "fu1_gen_03", "tone": "directo",
                "text": (
                    "Hola {nombre}, ¿es un buen momento?\n\n"
                    "Quiero saber si la optimización del costo energético "
                    "es una prioridad en {empresa} este año. "
                    "Si lo es, creo que Klik Energy puede contribuir de forma "
                    "concreta. Si no, respeto totalmente.\n\n"
                    "¿Qué me dices?"
                ),
            },
        ],
        "operaciones": [
            {
                "id": "fu1_oper_01", "tone": "KPI",
                "text": (
                    "Hola {nombre}, siguiendo el hilo.\n\n"
                    "Un dato que puede ser relevante para tus KPIs: en el mercado "
                    "no regulado, los contratos pueden incluir cláusulas de precio "
                    "fijo por períodos definidos, lo que mejora la previsibilidad "
                    "del OPEX energético en {empresa}.\n\n"
                    "¿Hablamos esta semana?"
                ),
            },
            {
                "id": "fu1_oper_02", "tone": "simple",
                "text": (
                    "Hola {nombre}, seguimiento rápido.\n\n"
                    "¿La factura eléctrica de {empresa} es algo que tienen activamente "
                    "en la mira, o es un costo que llega fijo cada mes?\n\n"
                    "En el mercado no regulado hay más control. Klik Energy lo hace simple. "
                    "¿Me das 15 minutos para mostrarte cómo?"
                ),
            },
            {
                "id": "fu1_oper_03", "tone": "oferta",
                "text": (
                    "Hola {nombre}, retomo el contacto.\n\n"
                    "Te ofrezco algo concreto: un diagnóstico gratuito del "
                    "perfil energético de {empresa} para ver si hay oportunidad "
                    "de ahorro en el mercado no regulado. "
                    "Solo necesito 20 minutos y una factura de energía reciente.\n\n"
                    "¿Lo agendamos?"
                ),
            },
        ],
        "financiero": [
            {
                "id": "fu1_fin_01", "tone": "P&L",
                "text": (
                    "Hola {nombre}, siguiendo el hilo de mi mensaje.\n\n"
                    "Un punto concreto: el ahorro promedio para empresas de {sector} "
                    "que migran al mercado no regulado con Klik Energy es del 10-15% "
                    "de la factura eléctrica anual. Para {empresa}, eso podría "
                    "traducirse en un impacto real en el P&L.\n\n"
                    "¿Tiene sentido revisarlo con su equipo?"
                ),
            },
            {
                "id": "fu1_fin_02", "tone": "riesgo",
                "text": (
                    "Hola {nombre}, un seguimiento rápido.\n\n"
                    "Sé que cambiar de comercializador puede sonar a riesgo. "
                    "Por eso en Klik Energy ofrecemos contratos con período de "
                    "prueba y salida flexible. La seguridad del suministro "
                    "está garantizada por el operador de red, no por el comercializador.\n\n"
                    "¿Hablamos para despejar esa duda?"
                ),
            },
            {
                "id": "fu1_fin_03", "tone": "urgencia",
                "text": (
                    "Hola {nombre}, un último seguimiento.\n\n"
                    "Las condiciones del mercado no regulado varían. "
                    "Los mejores contratos se consiguen cuando la empresa no "
                    "está en urgencia de renovación. Si {empresa} tiene contrato "
                    "vigente con el regulado, este es el momento de evaluar opciones.\n\n"
                    "¿Me da 15 minutos esta semana?"
                ),
            },
        ],
    },

    # ── SEGUIMIENTO 2 (7-10 días después) ────────────────────────────────────
    "followup_2": {
        "mantenimiento": [
            {
                "id": "fu2_mant_01", "tone": "cierre",
                "text": (
                    "Hola {nombre}, este es mi último mensaje para no ser invasivo.\n\n"
                    "Si en algún momento {empresa} quiere evaluar su contrato "
                    "de energía en el mercado no regulado, aquí estaré. "
                    "Klik Energy trabaja con empresas de {sector} en {ciudad} "
                    "y los resultados han sido consistentes.\n\n"
                    "Quedo a tu disposición. ¡Éxitos!"
                ),
            },
            {
                "id": "fu2_mant_02", "tone": "recurso",
                "text": (
                    "Hola {nombre}, antes de cerrar el ciclo te dejo un recurso:\n\n"
                    "Hicimos una guía rápida para directores de mantenimiento sobre "
                    "cómo evaluar si su empresa puede migrar al mercado no regulado "
                    "sin afectar la continuidad operativa.\n\n"
                    "¿Te la envío? Es de libre uso y sin compromiso."
                ),
            },
        ],
        "planta": [
            {
                "id": "fu2_plan_01", "tone": "cierre",
                "text": (
                    "Hola {nombre}, entiendo que el momento puede no ser el ideal.\n\n"
                    "Dejo la puerta abierta: si en los próximos meses evalúan "
                    "el contrato de energía de {empresa}, me encantaría ser parte "
                    "de esa conversación. Klik Energy tiene experiencia en "
                    "plantas de {sector} en {ciudad}.\n\n"
                    "¡Mucho éxito en la operación!"
                ),
            },
            {
                "id": "fu2_plan_02", "tone": "timing",
                "text": (
                    "Hola {nombre}, un mensaje final.\n\n"
                    "¿No es el momento ahora? Perfecto. "
                    "¿Cuándo vence el contrato de energía actual de {empresa}? "
                    "Con gusto te contacto 2-3 meses antes para que tengan "
                    "tiempo de evaluar opciones sin presión.\n\n"
                    "¿Me lo dices y te programo para ese momento?"
                ),
            },
        ],
        "general": [
            {
                "id": "fu2_gen_01", "tone": "cierre",
                "text": (
                    "Hola {nombre}, este es mi último seguimiento.\n\n"
                    "Si la optimización del costo energético entra en la agenda "
                    "de {empresa} en algún momento, Klik Energy estará aquí. "
                    "Trabajamos con empresas líderes de {sector} en Colombia "
                    "y los resultados hablan solos.\n\n"
                    "¡Éxitos en el liderazgo de {empresa}!"
                ),
            },
            {
                "id": "fu2_gen_02", "tone": "referencia",
                "text": (
                    "Hola {nombre}, cerrando el ciclo.\n\n"
                    "Si le interesa, con gusto le pongo en contacto con un par "
                    "de gerentes de {sector} que ya trabajan con Klik Energy. "
                    "Nada como una referencia directa para tomar una decisión informada.\n\n"
                    "¿Le interesa esa conversación?"
                ),
            },
        ],
        "operaciones": [
            {
                "id": "fu2_oper_01", "tone": "cierre",
                "text": (
                    "Hola {nombre}, último mensaje de mi parte.\n\n"
                    "Cuando en {empresa} estén listos para revisar el componente "
                    "energético del OPEX, Klik Energy puede hacer ese análisis "
                    "en menos de una semana. Sin costo y sin compromiso.\n\n"
                    "Quedo disponible. ¡Éxitos en la operación!"
                ),
            },
        ],
        "financiero": [
            {
                "id": "fu2_fin_01", "tone": "cierre",
                "text": (
                    "Hola {nombre}, cierro el ciclo con este mensaje.\n\n"
                    "Si en algún momento {empresa} quiere hacer el ejercicio de "
                    "cuantificar el ahorro potencial en energía eléctrica, "
                    "Klik Energy lo hace gratis y en 48 horas.\n\n"
                    "Quedo a su disposición. ¡Que les vaya muy bien!"
                ),
            },
            {
                "id": "fu2_fin_02", "tone": "timing",
                "text": (
                    "Hola {nombre}, un mensaje final.\n\n"
                    "Le dejo una pregunta para cuando sea el momento: "
                    "¿cuándo vence el contrato de energía actual de {empresa}?\n\n"
                    "Si me lo indica, agendo un contacto 90 días antes para que "
                    "tengan tiempo de evaluar opciones con calma. "
                    "Sin presión. Solo planeación."
                ),
            },
        ],
    },

    # ── SOLICITUD DE DEMO ─────────────────────────────────────────────────────
    "demo_request": {
        "mantenimiento": [
            {
                "id": "demo_mant_01", "tone": "directo",
                "text": (
                    "Hola {nombre}, basado en nuestra conversación, creo que vale la pena "
                    "que hablemos en detalle.\n\n"
                    "Te propongo una llamada de 30 minutos donde:\n"
                    "• Revisamos la factura actual de {empresa}\n"
                    "• Calculamos el ahorro estimado en el mercado no regulado\n"
                    "• Te explico cómo funciona el cambio sin afectar operaciones\n\n"
                    "¿Qué día te queda bien esta semana o la próxima? "
                    "Puedo adaptarme a tu horario."
                ),
            },
            {
                "id": "demo_mant_02", "tone": "agenda",
                "text": (
                    "Hola {nombre}, ¿podemos agendar 30 minutos esta semana?\n\n"
                    "Quiero mostrarte con números reales cómo otras plantas de "
                    "{sector} en {ciudad} están optimizando su costo energético "
                    "con Klik Energy en el mercado no regulado.\n\n"
                    "¿El martes o el jueves te quedan bien? "
                    "Manejo la hora que prefieras."
                ),
            },
        ],
        "planta": [
            {
                "id": "demo_plan_01", "tone": "valor-claro",
                "text": (
                    "Hola {nombre}, quisiera mostrarte algo concreto.\n\n"
                    "En 30 minutos puedo presentarte:\n"
                    "• Cómo {empresa} puede migrar al mercado no regulado\n"
                    "• El ahorro estimado basado en el perfil del sector {sector}\n"
                    "• Casos reales de plantas en {ciudad} con Klik Energy\n\n"
                    "¿Agendamos una llamada esta semana?"
                ),
            },
        ],
        "general": [
            {
                "id": "demo_gen_01", "tone": "ejecutivo",
                "text": (
                    "Hola {nombre}, le propongo algo directo.\n\n"
                    "Una reunión de 30 minutos con el equipo de Klik Energy "
                    "donde revisamos el potencial de ahorro para {empresa} "
                    "y respondemos todas las preguntas sobre el mercado no regulado.\n\n"
                    "Sin compromiso. Solo información para tomar una buena decisión.\n\n"
                    "¿Le parece bien esta semana o la próxima?"
                ),
            },
            {
                "id": "demo_gen_02", "tone": "breve",
                "text": (
                    "Hola {nombre}, una pregunta concreta:\n\n"
                    "¿Podemos agendar 30 minutos para que el equipo de Klik Energy "
                    "le muestre el potencial de ahorro energético para {empresa}?\n\n"
                    "¿Qué día le funciona?"
                ),
            },
        ],
        "operaciones": [
            {
                "id": "demo_oper_01", "tone": "técnico",
                "text": (
                    "Hola {nombre}, creo que ya tenemos suficiente contexto "
                    "para hacer algo útil.\n\n"
                    "¿Podemos agendar 30 minutos donde revisamos:\n"
                    "• El perfil de consumo de {empresa}\n"
                    "• Las opciones en el mercado no regulado\n"
                    "• El impacto estimado en el OPEX\n\n"
                    "¿Qué día tienes disponible esta semana?"
                ),
            },
        ],
        "financiero": [
            {
                "id": "demo_fin_01", "tone": "ROI",
                "text": (
                    "Hola {nombre}, le propongo una reunión de trabajo de 30 minutos.\n\n"
                    "En ese tiempo, el equipo de Klik Energy le presenta:\n"
                    "• Análisis de ahorro potencial para {empresa}\n"
                    "• Modelo financiero del impacto en el OPEX anual\n"
                    "• Condiciones del contrato y opciones de precio\n\n"
                    "¿Le parece bien esta semana?"
                ),
            },
            {
                "id": "demo_fin_02", "tone": "concreto",
                "text": (
                    "Hola {nombre}, ¿le parece bien que agendemos 30 minutos?\n\n"
                    "Prepararé un estimado de ahorro específico para {empresa} "
                    "antes de la reunión, para que no sea una conversación genérica "
                    "sino algo accionable desde el primer minuto.\n\n"
                    "¿Qué día tiene disponible?"
                ),
            },
        ],
    },
}


# ── Función de selección de template ──────────────────────────────────────────

def select_template(
    contact: dict,
    stage: str,
    variant: int = 0,
) -> Optional[dict]:
    title = contact.get("title", "")
    role = get_role_category(title)
    stage_templates = TEMPLATES.get(stage, {})
    role_templates = stage_templates.get(role, stage_templates.get("general", []))

    if not role_templates:
        return None

    idx = variant % len(role_templates)
    return role_templates[idx]


def personalize(template: dict, contact: dict) -> str:
    text = template["text"]
    nombre = contact.get("name", "").split()[0] if contact.get("name") else "estimado/a"
    sector = contact.get("sector", contact.get("ciiu", "industrial"))

    replacements = {
        "{nombre}":  nombre,
        "{empresa}": contact.get("company_name", contact.get("name", "su empresa")),
        "{ciudad}":  contact.get("company_city", contact.get("city", "Colombia")),
        "{sector}":  sector,
        "{cargo}":   contact.get("title", "su cargo"),
    }
    for token, value in replacements.items():
        text = text.replace(token, value)
    return text.strip()


def generate_sequence(contact: dict, variants: tuple[int, ...] = (0, 0, 0, 0, 1)) -> list[dict]:
    stages = ["connection", "primer_mensaje", "followup_1", "followup_2", "demo_request"]
    delays_days = [0, 1, 4, 9, 0]
    sequence = []

    for i, (stage, delay) in enumerate(zip(stages, delays_days)):
        variant = variants[i] if i < len(variants) else 0
        tmpl = select_template(contact, stage, variant)
        if not tmpl:
            continue
        text = personalize(tmpl, contact)
        sequence.append({
            "stage":        stage,
            "stage_label":  stage.replace("_", " ").title(),
            "delay_days":   delay,
            "template_id":  tmpl["id"],
            "tone":         tmpl.get("tone", ""),
            "message":      text,
            "char_count":   len(text),
            "status":       "queued",
            "sent_at":      None,
        })
    return sequence
