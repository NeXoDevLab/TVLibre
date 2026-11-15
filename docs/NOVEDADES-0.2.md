# TVLibre 0.2

[Índice](../README.md) · [Compatibilidad](COMPATIBILIDAD.md) · [Restauración](RESTAURACION.md)

## Inicio 1.10 en español

dumbtv mejora los reintentos de Home, la vuelta desde suspensión, el foco y alineación de
cuadrículas, el acceso a Appstore y el arranque en Fire OS 6. En Opciones puedes cambiar la
posición de las filas, activar Todas las apps, seleccionar paquetes de iconos instalados,
elegir iconos y exportar home.conf al directorio multimedia. La biblioteca de títulos y
los fondos se configuran con archivos locales; siguen siendo funciones opcionales.
Consulta los formatos de [biblioteca y fondos de upstream](https://github.com/humblemuzzu/dumbtv/tree/b35f3ade7b92d03357ce191844525b3448e57285/launcher).
No se activa un filtro DNS, una VPN ni descargas de imágenes al instalar el launcher.
La supervisión de personalDNSfilter está desactivada por defecto: solo se configura
expresamente en Opciones, y desactivarla detiene la supervisión, no la VPN de otra app.

El APK español 1.10-es conserva el certificado de 1.6-es publicado por TVLibre. Actualiza
con el instalador verificado de [Launchers](LAUNCHERS.md), que conserva una copia del APK
previo y utiliza actualización normal. Una compilación propia o la versión oficial puede
tener otra firma: no se sustituye desinstalando automáticamente. La entrada histórica
`dumbtv-es-1.6` permanece en el catálogo para identificar el APK anterior.

## Reparar un componente conservando el historial

`com.amazon.storm.lightning.tutorial` contiene la pantalla de emparejamiento del mando móvil.
Está protegido desde 0.2 y ya no se propone como limpieza. Las protecciones también incluyen
componentes de entradas Amlogic, HbbTV, sintonizador, CI+ y ajustes. No se habilitan de forma
masiva paquetes que ya estaban desactivados por el sistema o por la persona.

Si una limpieza anterior desactivó el componente de emparejamiento, diagnostícalo y genera
un plan que nombre expresamente el paquete. Ejemplo con una dirección de documentación:

```bash
python3 tvlibre.py --serial 192.0.2.10:5555 repair-plan --packages com.amazon.storm.lightning.tutorial --out state/repair.json
python3 tvlibre.py --serial 192.0.2.10:5555 apply --plan state/repair.json --yes
```

La reparación guarda el estado previo exacto y utiliza los mismos comandos verify/restore
con el backup.json que imprime. Solo admite componentes protegidos instalados, nombrados
expresamente y deshabilitados. Mantiene las restricciones de modelo, SDK y usuario.
Los diarios antiguos que incluyan este tutorial todavía permiten verificación y restauración;
no pueden reutilizarse como planes para deshabilitarlo de nuevo.

## Diagnóstico y respaldos

```bash
python3 tvlibre.py devices
python3 tvlibre.py analyze --inventory state/inventory.json
python3 tvlibre.py --serial 192.0.2.10:5555 find-backups --directory state
python3 tvlibre.py --adb-server-port 5038 --serial 192.0.2.10:5555 doctor
```

El análisis de inventarios funciona sin conectar al TV. Distingue candidatos del perfil,
paquetes protegidos deshabilitados y paquetes desconocidos; no declara que un nombre sea
telemetría. El catálogo documenta fuentes y modelos informados por terceros: sus informes
no equivalen a pruebas de TVLibre ni habilitan perfiles Amazon en Android TV o Google TV.

La búsqueda compara identidad estable, firmware y usuario, y encuentra diarios aunque el
router cambie la IP. No muestra como restaurables los planes, registros de instalación o
diarios incompatibles. La restauración vuelve a validar la identidad y los cambios posteriores.

En macOS un servidor ADB heredado puede fallar con «No route to host» aunque el puerto del
TV responda. `--adb-server-port 5038` utiliza otro servidor sin interrumpir las conexiones del
predeterminado. No cambia permisos de macOS ni acepta los diálogos ADB del televisor.

## Accesibilidad y validación

Android puede activar accessibility_enabled al añadir Guard. El diario registra ese posible
efecto antes de escribir y acepta únicamente ese cambio dependiente, manteniendo el rechazo
de cambios ajenos. Un corte después de añadir el servicio sigue teniendo registro de recuperación.

Se ejecutan simulaciones Python de cortes, conflictos, reparación, copias e identidad, pruebas
Java de upstream, compilación Android, comprobación de recursos españoles y firma del APK.
La versión 0.2 no se ha aplicado en un televisor durante su desarrollo; no se atribuyen a ella
las pruebas físicas anteriores. Voz, casting, reproducción y firmware nuevo requieren pruebas
en el dispositivo correspondiente.
