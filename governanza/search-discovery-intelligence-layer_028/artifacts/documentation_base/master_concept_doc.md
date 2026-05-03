# Master Concept Document — Search / Discovery Intelligence Layer

Motor ID: motor_028

## purpose
Search / Discovery Intelligence Layer sostiene una busqueda continua, disciplinada y trazable de fuentes candidatas para el framework. Usa el registro de fuentes existente, la taxonomia canonica y las senales de refresh para detectar huecos de cobertura, formular consultas reproducibles y proponer candidatos de fuente para evaluacion posterior. Su salida no es evidencia incorporada al sistema, sino inteligencia de descubrimiento con provenance suficiente para decidir si una fuente debe revisarse, registrarse o descartarse.

## what_it_does
- Recibe perfiles de fuentes registradas, taxonomias canonicas y senales de obsolescencia o cambio.
- Identifica temas, entidades, jurisdicciones, periodos o tipos de fuente con cobertura insuficiente.
- Construye planes de busqueda con consultas, filtros, idioma, alcance temporal, motivo de busqueda y restricciones de derechos conocidas.
- Registra candidatos de fuente con url, titulo, editor, tipo de fuente, dominio taxonomico, razon de descubrimiento, timestamp y metodo usado.
- Emite paquetes de descubrimiento para revision por Source Registry + Rights Engine y para priorizacion operativa.

## what_it_does_not_do
- No descarga, parsea ni ingiere contenido de la fuente; eso corresponde al motor de ingesta.
- No crea registros finales de fuente ni perfiles de derechos; solo propone candidatos para el motor_008.
- No normaliza datos, resuelve identidad, evalua calidad del dataset ni cura bibliotecas.
- No decide que una fuente es evidencia valida, autorizada o apta para uso analitico.
- No sustituye a Source Change Detection / Refresh Intelligence; consume sus senales para orientar nuevas busquedas.

## why_it_exists
El sistema necesita una capa que convierta huecos de cobertura y senales de stale data en trabajo de descubrimiento trazable. Sin este motor, la busqueda de nuevas fuentes quedaria como actividad manual o dispersa, sin lineage, sin criterios reproducibles y con alto riesgo de duplicar fuentes ya conocidas. Existe separado porque Source Registry gobierna fuentes ya declaradas, Refresh Intelligence detecta cambios en fuentes conocidas, y este motor cubre el espacio anterior a la admision: encontrar, justificar y documentar fuentes candidatas.
