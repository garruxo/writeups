# 💳 Facturación de Google Play — guía de puesta en marcha

Esta app ya trae integrada la **facturación de Google Play** (plugin `cordova-plugin-purchase`).
Lo que hace el código ya está listo; lo que falta son los pasos que **solo puedes hacer tú**
en tu cuenta de Google (crear el producto y la cuenta de pagos). Aquí van en orden.

> ⚖️ **Importante (política de Google Play):** el contenido digital dentro de la app
> (Premium: animaciones, retos, temas, especialidades) **debe cobrarse con Google Play Billing**.
> No se puede usar un sistema de pago propio ni cobrar por fuera: eso incumple la política y
> retiran la app. El **código de desbloqueo** que ya tiene la app es solo para pruebas/regalos,
> no para vender.

---

## 1 · Qué hace ya el código

- **Plugin**: el workflow añade `cordova-plugin-purchase@13` al compilar (paso nuevo en `build-apk.yml`).
- **Producto**: la app registra un producto con ID **`mapa_premium`** (tipo *no consumible* = compra única de por vida).
- **Flujo**: al comprar y verificar la compra → se activa Premium (`localStorage 'mapa-premium-ok'='1'`)
  y se actualiza la interfaz. Botones **💳 Comprar Premium** y **♻️ Restaurar compra** en la pantalla Premium.
- **En navegador** (sin plugin): los botones avisan de que la compra es desde la app; sigue valiendo el código.

Si cambias el ID del producto, edita `PRODUCT_ID` en el `<script>` de facturación de `app/index.html`
(**debe coincidir** con el ID en Play Console).

---

## 2 · Lo que tienes que hacer en Google (una vez)

### a) Cuenta de desarrollador
1. Alta en **Google Play Console** (pago único de 25 $): https://play.google.com/console
2. Crea la **app** (nombre, idioma, etc.).

### b) Cuenta de pagos (merchant)
3. En Play Console → **Pagos / Payments profile**: crea el perfil de pagos (datos fiscales/bancarios).
   Sin esto no se pueden vender productos.

### c) Crear el producto Premium
4. Play Console → tu app → **Monetizar → Productos → Productos integrados en la aplicación** (in-app products).
5. **Crear producto**:
   - **ID de producto**: `mapa_premium`  ← exactamente igual que en el código.
   - Nombre y descripción (ej. "Premium — contenido y personalización exclusivos").
   - **Precio** (ej. 2,99 €).
   - Estado: **Activo**.

> ¿Prefieres **suscripción** (mensual) en vez de pago único? Dilo y cambio el código a
> `PAID_SUBSCRIPTION` con su ID; el resto es igual.

### d) Firmar la app para producción
6. El APK actual está firmado con una **clave de depuración** (para probar). Para publicar y vender,
   sube la app con **Play App Signing** (Play Console → Configuración → Integridad de la app).
   Google gestiona la clave de firma de producción.

### e) Probar la compra sin pagar
7. Play Console → **Configuración → Pruebas de licencia**: añade tu correo como **tester de licencia**.
8. Sube el APK/AAB a un **track de pruebas** (interna) e instala desde ese canal.
9. Con ese correo, la compra de `mapa_premium` aparece como **prueba** (no te cobran) y puedes
   validar que se activa el Premium y que **Restaurar compra** funciona.

---

## 3 · Checklist rápida

- [ ] Cuenta de Play Console creada y app dada de alta.
- [ ] Perfil de pagos (merchant) configurado.
- [ ] Producto `mapa_premium` creado, con precio y **Activo**.
- [ ] App firmada con Play App Signing para producción.
- [ ] Tester de licencia añadido y compra de prueba OK.
- [ ] (Opcional) ¿suscripción en vez de pago único? avísame y lo cambio.

---

## 4 · Notas técnicas

- El build de depuración compila con el plugin sin configuración extra. Para validación de recibos
  en servidor (opcional, mayor seguridad anti-fraude) se necesita un backend; para empezar no hace falta.
- El permiso `com.android.vending.BILLING` lo añade el plugin automáticamente.
- Mantén el **mismo ID de aplicación** (`com.garruxo.mapajunior`) entre el APK y Play Console.
