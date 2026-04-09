from fpdf import FPDF

class AuditPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "LlanoPay - Auditoria Completa", align="R")
        self.ln(4)
        self.set_draw_color(0, 150, 136)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(0, 120, 110)
        self.cell(0, 12, title)
        self.ln(8)
        self.set_draw_color(0, 150, 136)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(50, 50, 50)
        self.cell(0, 10, title)
        self.ln(8)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def table_header(self, cols, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(0, 150, 136)
        self.set_text_color(255, 255, 255)
        for i, col in enumerate(cols):
            self.cell(widths[i], 8, col, border=1, fill=True, align="C")
        self.ln()

    def table_row(self, cols, widths, fill=False):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        if fill:
            self.set_fill_color(240, 248, 247)
        else:
            self.set_fill_color(255, 255, 255)
        max_h = 6
        # Calculate max height needed
        for i, col in enumerate(cols):
            lines = self.multi_cell(widths[i], 6, col, border=0, dry_run=True, output="LINES")
            h = len(lines) * 6
            if h > max_h:
                max_h = h
        x_start = self.get_x()
        y_start = self.get_y()
        for i, col in enumerate(cols):
            self.set_xy(x_start + sum(widths[:i]), y_start)
            self.multi_cell(widths[i], 6, col, border=1, fill=fill, new_x="RIGHT", new_y="TOP")
        self.set_y(y_start + max_h)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        x = self.get_x()
        self.cell(6, 6, "-")
        self.multi_cell(0, 6, text)
        self.ln(1)

    def status_badge(self, text, color="green"):
        colors = {
            "green": (46, 125, 50),
            "red": (198, 40, 40),
            "yellow": (245, 166, 35),
            "orange": (230, 126, 34),
        }
        r, g, b = colors.get(color, (100, 100, 100))
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(r, g, b)
        self.cell(0, 6, text)
        self.ln(5)


def generate():
    pdf = AuditPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ===================== PORTADA =====================
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(0, 120, 110)
    pdf.cell(0, 15, "LLANOPAY", align="C")
    pdf.ln(18)
    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "Auditoria Completa de Proyecto", align="C")
    pdf.ln(12)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 10, "Billetera Digital Regional - Llanos Orientales de Colombia", align="C")
    pdf.ln(20)
    pdf.set_draw_color(0, 150, 136)
    pdf.set_line_width(1)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Estado actual: 55/100 (Etapa de Desarrollo)", align="C")
    pdf.ln(8)
    pdf.cell(0, 8, "Fecha: Abril 2026", align="C")
    pdf.ln(8)
    pdf.cell(0, 8, "Stack: Django 5.1 + Flutter 3.x + PostgreSQL + Redis + Celery", align="C")

    # ===================== SECCION 1: CRITICO =====================
    pdf.add_page()
    pdf.section_title("1. CRITICO - Bloquea Lanzamiento")
    pdf.body_text("Sin resolver estos puntos, la aplicacion NO puede salir a produccion:")

    critico = [
        ["1", "Integracion SMS real (Twilio/AWS SNS)", "OTP se muestra en el JSON del API, no se envia por SMS", "CRITICO"],
        ["2", "Push Notifications (FCM/APNs)", "Stubs con print(), no llegan notificaciones", "CRITICO"],
        ["3", "HTTPS/TLS", "No hay SSL redirect, ni cookies seguras, ni HSTS", "CRITICO"],
        ["4", "DEBUG=False en produccion", "DEBUG=True por defecto, filtra info sensible", "CRITICO"],
        ["5", "Quitar OTP de respuestas del API", "Codigo OTP se devuelve en el JSON", "CRITICO"],
        ["6", "Blockchain real", "BlockchainService no implementado, web3 importado pero no usado", "CRITICO"],
        ["7", "Encriptar datos sensibles", "Cedulas, emails, datos KYC en texto plano en la DB", "CRITICO"],
        ["8", "Pasarela de pagos (PSE, Nequi)", "No hay forma de cargar saldo desde fuentes externas", "CRITICO"],
    ]
    w = [8, 52, 85, 25]
    pdf.table_header(["#", "Que Falta", "Estado Actual", "Nivel"], w)
    for i, row in enumerate(critico):
        pdf.table_row(row, w, fill=(i % 2 == 0))

    # ===================== SECCION 2: SEGURIDAD =====================
    pdf.add_page()
    pdf.section_title("2. Seguridad - Vulnerabilidades Actuales")

    seguridad = [
        ["CORS permite todo en desarrollo", "Whitelist de dominios especificos"],
        ["Sin SSL pinning en Flutter", "Implementar certificate pinning en Dio"],
        ["Sin autenticacion biometrica", "local_auth esta instalado pero no integrado"],
        ["Sin proteccion brute-force en login/OTP", "Rate limiting por endpoint sensible"],
        ["Logs exponen tokens y passwords", "Desactivar LogInterceptor en produccion"],
        ["Sin firma de requests (HMAC)", "Proteccion contra tampering"],
        ["Sin idempotency keys", "Riesgo de transferencias duplicadas"],
        ["Token refresh race condition", "Cola de requests durante refresh"],
        ["WebSocket sin SSL pinning", "Usar WSS con certificados validados"],
        ["MasterWallet singleton", "Punto unico de falla, sin multi-sig"],
    ]
    w2 = [90, 90]
    pdf.table_header(["Problema", "Solucion"], w2)
    for i, row in enumerate(seguridad):
        pdf.table_row(row, w2, fill=(i % 2 == 0))

    # ===================== SECCION 3: FUNCIONALIDADES =====================
    pdf.add_page()
    pdf.section_title("3. Funcionalidades Faltantes")

    features = [
        ["Modo offline en Flutter (Hive/SQLite)", "Alto", "Sin internet no funciona nada"],
        ["Verificacion de identidad real (Truora)", "Alto", "KYC solo sube docs, no los valida"],
        ["Pagos con codigo QR", "Alto", "Estandar en billeteras digitales"],
        ["Historial de auditoria financiero", "Alto", "Obligatorio para compliance"],
        ["Exportar datos (Habeas Data Colombia)", "Alto", "Derecho del usuario por ley"],
        ["Politica de privacidad en la app", "Alto", "Requerimiento legal"],
        ["Recuperacion de contrasena", "Medio", "Flujo no implementado"],
        ["Multi-idioma real", "Medio", "Configurado pero no implementado"],
        ["Dashboard admin web completo", "Bajo", "Django admin es suficiente por ahora"],
        ["Deteccion de fraude (ML)", "Bajo", "Para fase avanzada"],
    ]
    w3 = [75, 20, 85]
    pdf.table_header(["Feature", "Impacto", "Detalle"], w3)
    for i, row in enumerate(features):
        pdf.table_row(row, w3, fill=(i % 2 == 0))

    # ===================== SECCION 4: INFRAESTRUCTURA =====================
    pdf.add_page()
    pdf.section_title("4. Infraestructura y DevOps")

    infra = [
        ["Monitoreo (Sentry, DataDog)", "Detectar errores en produccion"],
        ["Health checks endpoints", "Verificar que el servicio esta vivo"],
        ["Backups automaticos de la DB", "Disaster recovery"],
        ["CI/CD (GitHub Actions)", "Deploy automatico"],
        ["Load testing", "Saber cuantos usuarios soporta"],
        ["Redis en produccion", "Cache esta en memoria local actualmente"],
        ["PostgreSQL en produccion", "SQLite no escala para fintech"],
        ["Metricas Prometheus/Grafana", "Dashboards de rendimiento"],
        ["Logs estructurados (JSON)", "Analisis y busqueda de errores"],
        ["Replicacion de base de datos", "Alta disponibilidad"],
    ]
    w4 = [85, 95]
    pdf.table_header(["Que Falta", "Para Que"], w4)
    for i, row in enumerate(infra):
        pdf.table_row(row, w4, fill=(i % 2 == 0))

    # ===================== SECCION 5: PERMISOS FLUTTER =====================
    pdf.ln(10)
    pdf.section_title("5. Permisos Flutter (Android/iOS)")

    permisos = [
        ["Internet", "Configurado", "OK"],
        ["Camara (KYC, QR)", "Paquete instalado", "Falta integrar QR"],
        ["Ubicacion", "geolocator instalado", "OK"],
        ["Biometria", "local_auth instalado", "NO INTEGRADO"],
        ["Notificaciones push", "No configurado", "Falta Firebase"],
        ["Almacenamiento seguro", "flutter_secure_storage", "OK"],
    ]
    w5 = [45, 55, 80]
    pdf.table_header(["Permiso", "Estado", "Nota"], w5)
    for i, row in enumerate(permisos):
        pdf.table_row(row, w5, fill=(i % 2 == 0))

    # ===================== SECCION 6: ESTADO DE MODULOS =====================
    pdf.add_page()
    pdf.section_title("6. Estado de Modulos del Backend")

    modulos = [
        ["accounts (Auth/KYC)", "90%", "JWT, OTP, perfil, KYC - Bien implementado"],
        ["wallet (Billetera)", "90%", "Balances COP+LLO, transacciones atomicas"],
        ["transfers (Transferencias)", "85%", "P2P, comisiones, limites, OTP para montos altos"],
        ["crypto (Criptomonedas)", "40%", "Modelos OK, blockchain NO implementado"],
        ["marketplace (Comercios)", "50%", "Modelos completos, vistas incompletas"],
        ["microcredit (Microcredito)", "80%", "Score crediticio, productos, pagos"],
        ["notifications", "45%", "WebSocket OK, SMS/Push son stubs"],
        ["web_dashboard", "10%", "Solo un stub"],
    ]
    w6 = [55, 18, 107]
    pdf.table_header(["Modulo", "Avance", "Detalle"], w6)
    for i, row in enumerate(modulos):
        pdf.table_row(row, w6, fill=(i % 2 == 0))

    # ===================== SECCION 7: FLUTTER FRONTEND =====================
    pdf.ln(10)
    pdf.sub_title("Estado del Frontend Flutter")
    pdf.body_text("26 pantallas implementadas, 7 BLoCs, 7 modelos, arquitectura solida.")

    flutter = [
        ["Arquitectura BLoC", "100%", "Patron bien aplicado"],
        ["Pantallas de Auth", "95%", "Splash, login, registro, OTP"],
        ["Pantallas de Wallet", "90%", "Balance, historial, detalle"],
        ["Pantallas de Transfers", "85%", "Enviar, confirmar, historial"],
        ["Pantallas de Crypto", "70%", "Llanocoin, deposito"],
        ["Pantallas Marketplace", "65%", "Listado, detalle comercios"],
        ["Pantallas Microcredito", "75%", "Solicitud, listado"],
        ["Seguridad (biometria)", "10%", "Paquete instalado, no integrado"],
        ["Modo offline", "0%", "No implementado"],
    ]
    w7 = [55, 18, 107]
    pdf.table_header(["Componente", "Avance", "Detalle"], w7)
    for i, row in enumerate(flutter):
        pdf.table_row(row, w7, fill=(i % 2 == 0))

    # ===================== SECCION 8: ROADMAP =====================
    pdf.add_page()
    pdf.section_title("7. Roadmap de Implementacion")

    pdf.sub_title("Semana 1 - Seguridad Critica")
    pdf.bullet("SMS real para OTP (Twilio o AWS SNS)")
    pdf.bullet("Quitar OTP de las respuestas del API")
    pdf.bullet("Configurar HTTPS, cookies seguras, HSTS")
    pdf.bullet("DEBUG=False y CORS restringido en produccion")
    pdf.bullet("Rate limiting por endpoint sensible")
    pdf.ln(3)

    pdf.sub_title("Semana 2-3 - Integraciones Core")
    pdf.bullet("Push notifications con Firebase (FCM)")
    pdf.bullet("Autenticacion biometrica en Flutter")
    pdf.bullet("Pasarela de pagos (PSE, Nequi, tarjetas)")
    pdf.bullet("Encriptacion de datos sensibles en la DB")
    pdf.bullet("SSL certificate pinning en Flutter")
    pdf.ln(3)

    pdf.sub_title("Mes 1 - Completar Features")
    pdf.bullet("Blockchain integration en testnet")
    pdf.bullet("Pagos con codigo QR")
    pdf.bullet("Auditoria financiera (audit trail)")
    pdf.bullet("Tests unitarios al 80%+ de cobertura")
    pdf.bullet("Verificacion de identidad (Truora/Onfido)")
    pdf.ln(3)

    pdf.sub_title("Mes 2 - Infraestructura")
    pdf.bullet("Monitoreo con Sentry + metricas Prometheus")
    pdf.bullet("CI/CD con GitHub Actions")
    pdf.bullet("Load testing y capacity planning")
    pdf.bullet("Modo offline en Flutter")
    pdf.bullet("Backups automaticos de la base de datos")
    pdf.ln(3)

    pdf.sub_title("Mes 3 - Lanzamiento")
    pdf.bullet("Penetration testing por terceros")
    pdf.bullet("Compliance colombiano (Habeas Data, SFC)")
    pdf.bullet("Deteccion de fraude basica")
    pdf.bullet("App Store / Play Store submission")
    pdf.bullet("Documentacion operacional completa")

    # ===================== SECCION 9: DINERO REAL =====================
    pdf.add_page()
    pdf.section_title("8. Manejo de Dinero Real - Estrategia Completa")

    pdf.body_text(
        "Para que LlanoPay maneje dinero real (COP y cripto), se necesitan integraciones "
        "con proveedores financieros regulados. A continuacion se detalla cada opcion:"
    )
    pdf.ln(3)

    pdf.sub_title("8.1 Entrada/Salida de Pesos (COP)")
    pdf.body_text(
        "El usuario necesita poder cargar y retirar pesos colombianos de su billetera. "
        "Opciones disponibles:"
    )

    fiat = [
        ["PSE (ACH Colombia)", "Transferencia bancaria directa desde cualquier banco colombiano. "
         "Requiere contrato con ACH Colombia o un agregador como PayU, Wompi o ePayco. "
         "Comision: 0.5-1.5% por transaccion. Es el metodo mas usado en Colombia.", "RECOMENDADO"],
        ["Wompi (by Bancolombia)", "Pasarela de pagos colombiana. Soporta PSE, tarjetas, Nequi, "
         "Bancolombia. API REST moderna. Sandbox disponible. Comision: ~2.5% tarjeta, "
         "~$3,400 COP fijo PSE. Facil integracion.", "RECOMENDADO"],
        ["PayU Colombia", "Pasarela consolidada en LATAM. Soporta PSE, tarjetas, efectivo "
         "(Efecty, Baloto). API REST. Comision: 2.99% + $900 COP. Requiere cuenta empresarial.", "BUENA OPCION"],
        ["ePayco", "Pasarela colombiana. PSE, tarjetas, Daviplata, Nequi. API REST. "
         "Comision: desde 2.69% + IVA. Dashboard completo.", "BUENA OPCION"],
        ["Nequi API (Bancolombia)", "Integracion directa con Nequi para push-payments. "
         "Los usuarios pagan desde su Nequi. API limitada, requiere acuerdo comercial.", "COMPLEMENTO"],
        ["Daviplata API (Davivienda)", "Similar a Nequi pero con Davivienda. API menos madura. "
         "Requiere acuerdo comercial.", "COMPLEMENTO"],
        ["Efecty / Baloto / SuRed", "Pago en efectivo en puntos fisicos. Usuario recibe un "
         "codigo, paga en tienda, saldo se acredita. Via PayU o ePayco.", "EFECTIVO"],
    ]
    w_fiat = [38, 120, 22]
    pdf.table_header(["Proveedor", "Descripcion", "Nivel"], w_fiat)
    for i, row in enumerate(fiat):
        pdf.table_row(row, w_fiat, fill=(i % 2 == 0))

    pdf.add_page()
    pdf.sub_title("8.2 Criptomonedas - Rampas On/Off")
    pdf.body_text(
        "Para convertir entre COP y cripto (y viceversa), se necesitan rampas fiat-cripto:"
    )

    crypto_providers = [
        ["Bitso", "Exchange mexicano con presencia en Colombia. API completa para trading, "
         "depositos y retiros. Soporta BTC, ETH, USDT, XRP. Rampa fiat COP disponible. "
         "Licencia en Colombia. Comision: 0.1-0.6%. "
         "Uso: Billetera custodial + trading + on/off ramp.", "RECOMENDADO"],
        ["Circle (USDC)", "Emisor de USDC (stablecoin respaldada 1:1 con USD). API para "
         "crear billeteras, enviar/recibir USDC, convertir a fiat. Ideal para remesas "
         "y pagos internacionales. Circle Programmable Wallets permite crear wallets "
         "per-user sin que manejen llaves privadas.", "RECOMENDADO"],
        ["MoonPay", "Widget embebible para comprar cripto con tarjeta/transferencia. "
         "Soporta Colombia (COP). El usuario compra BTC/ETH/USDT directo. "
         "Comision: 3.5-4.5%. Facil integracion (iframe/SDK).", "FACIL"],
        ["Transak", "Similar a MoonPay. Widget para on-ramp. Soporta COP via PSE. "
         "Comision: 1-5%. SDK para Flutter disponible. KYC integrado.", "FACIL"],
        ["Binance Pay API", "API de Binance para pagos cripto. Permite recibir pagos "
         "en cripto y liquidar en COP. Gran liquidez. Requiere cuenta Business.", "ALTERNATIVA"],
        ["Ramp Network", "On-ramp global. SDK embebible. Soporta multiples paises. "
         "KYC integrado. Comision: 2.5-3%.", "ALTERNATIVA"],
    ]
    w_crypto = [30, 125, 25]
    pdf.table_header(["Proveedor", "Descripcion", "Nivel"], w_crypto)
    for i, row in enumerate(crypto_providers):
        pdf.table_row(row, w_crypto, fill=(i % 2 == 0))

    pdf.add_page()
    pdf.sub_title("8.3 Billeteras Custodiales vs No-Custodiales")
    pdf.body_text(
        "Hay dos modelos para manejar las criptomonedas de los usuarios:"
    )

    custody = [
        ["Custodial (Recomendado)", "LlanoPay controla las llaves privadas. El usuario no "
         "necesita saber de blockchain. Mas simple para el usuario. Requiere: "
         "seguro, auditoria, cumplimiento regulatorio. Proveedores: Fireblocks, "
         "Circle Programmable Wallets, BitGo, Bitso Custody."],
        ["No-Custodial", "El usuario controla sus llaves privadas. Mas seguro en teoria "
         "pero el usuario puede perder acceso si pierde la seed phrase. No requiere "
         "custodia regulada. Mas complejo en UX. Proveedores: WalletConnect, "
         "MetaMask SDK."],
        ["Hibrido (MPC)", "Multi-Party Computation. La llave se divide entre el usuario "
         "y el servidor. Ni uno ni otro pueden firmar solo. Mejor seguridad y UX. "
         "Proveedores: Fireblocks MPC, Zengo, Lit Protocol."],
    ]
    w_cust = [42, 138]
    pdf.table_header(["Modelo", "Descripcion"], w_cust)
    for i, row in enumerate(custody):
        pdf.table_row(row, w_cust, fill=(i % 2 == 0))

    pdf.ln(8)
    pdf.sub_title("8.4 Arquitectura Recomendada para Dinero Real")
    pdf.bullet("CAPA 1 - Fiat (COP): Wompi o PayU como pasarela principal para PSE, tarjetas y Nequi")
    pdf.bullet("CAPA 2 - Cripto On/Off Ramp: Bitso API para compra/venta de cripto con COP")
    pdf.bullet("CAPA 3 - Stablecoin: Circle USDC para pagos internacionales y remesas")
    pdf.bullet("CAPA 4 - Custodia: Circle Programmable Wallets (custodial) para cripto del usuario")
    pdf.bullet("CAPA 5 - Token propio (LLO): Smart contract ERC-20 en Polygon para Llanocoin")
    pdf.bullet("CAPA 6 - Liquidez: Pool de liquidez LLO/USDC en DEX o manejado internamente")

    pdf.ln(5)
    pdf.sub_title("8.5 Flujo Completo: Usuario Carga Dinero")
    pdf.bullet("1. Usuario abre la app y selecciona 'Cargar Saldo'")
    pdf.bullet("2. Elige metodo: PSE, tarjeta, Nequi, efectivo o cripto")
    pdf.bullet("3. Si elige PSE/tarjeta: Wompi procesa el pago y notifica via webhook")
    pdf.bullet("4. Backend recibe webhook, valida firma, acredita COP en wallet del usuario")
    pdf.bullet("5. Si quiere comprar LLO: COP se convierte a LLO al tipo de cambio interno")
    pdf.bullet("6. Si quiere comprar BTC/ETH: Se usa Bitso API para ejecutar la orden")
    pdf.bullet("7. Cripto se deposita en la wallet custodial del usuario (Circle)")
    pdf.bullet("8. Para retirar: proceso inverso, Wompi dispersa a cuenta bancaria")

    pdf.ln(5)
    pdf.sub_title("8.6 Regulacion Colombiana")
    pdf.body_text(
        "Para operar con dinero real en Colombia se necesita:"
    )
    pdf.bullet("Registro ante la Superintendencia Financiera de Colombia (SFC) o alianza con entidad vigilada")
    pdf.bullet("Cumplimiento SARLAFT (prevencion lavado de activos y financiacion del terrorismo)")
    pdf.bullet("Programa de Conocimiento del Cliente (KYC) robusto")
    pdf.bullet("Reportes a la UIAF (Unidad de Informacion y Analisis Financiero)")
    pdf.bullet("Cumplimiento Ley 1581 de 2012 (Habeas Data / proteccion de datos personales)")
    pdf.bullet("Sandbox regulatorio de la SFC: permite operar temporalmente mientras se obtiene licencia")
    pdf.bullet("Contrato con operador de pagos autorizado si no se tiene licencia propia")

    pdf.ln(5)
    pdf.sub_title("8.7 Costos Estimados de Integracion")
    costos = [
        ["Wompi (pasarela fiat)", "$0 setup, 2.5% por tx tarjeta, $3,400 PSE"],
        ["Bitso API (cripto)", "$0 setup, 0.1-0.6% por trade"],
        ["Circle (USDC/wallets)", "Gratis hasta 1,000 wallets, luego enterprise"],
        ["MoonPay/Transak (on-ramp)", "3.5-4.5% por compra cripto"],
        ["Fireblocks (custodia MPC)", "Desde $500 USD/mes (enterprise)"],
        ["Twilio (SMS OTP)", "$0.0075 USD por SMS a Colombia"],
        ["Firebase (Push)", "Gratis hasta 10K notificaciones/dia"],
        ["Servidor produccion (AWS/GCP)", "Desde $50-200 USD/mes"],
        ["Dominio + SSL", "$10-50 USD/ano"],
        ["Asesor legal/regulatorio", "Variable, $2,000-10,000 USD"],
    ]
    w_cost = [70, 110]
    pdf.table_header(["Servicio", "Costo"], w_cost)
    for i, row in enumerate(costos):
        pdf.table_row(row, w_cost, fill=(i % 2 == 0))

    # ===================== SECCION 10: RESUMEN =====================
    pdf.add_page()
    pdf.section_title("9. Resumen Ejecutivo")

    pdf.body_text(
        "LlanoPay es una plataforma fintech bien arquitectada con logica de negocio sofisticada "
        "(transferencias P2P, microcredito, marketplace, cripto). El codigo esta bien organizado, "
        "usa frameworks modernos (Django 5.1, Flutter 3.x) e implementa patrones correctos "
        "(BLoC, atomicidad, tareas async)."
    )
    pdf.ln(3)

    pdf.sub_title("Puntuacion por Area")
    scores = [
        ["Autenticacion", "90%"],
        ["Autorizacion", "80%"],
        ["Validacion de datos", "75%"],
        ["Manejo de errores", "60%"],
        ["Seguridad", "50%"],
        ["Testing", "70%"],
        ["Monitoreo", "20%"],
        ["Documentacion", "40%"],
        ["DevOps", "60%"],
        ["Compliance", "30%"],
        ["Rendimiento", "50%"],
        ["Disaster Recovery", "10%"],
    ]
    ws = [100, 80]
    pdf.table_header(["Area", "Puntuacion"], ws)
    for i, row in enumerate(scores):
        pdf.table_row(row, ws, fill=(i % 2 == 0))

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 120, 110)
    pdf.cell(0, 10, "Puntuacion General: 55/100 (Etapa de Desarrollo)", align="C")
    pdf.ln(12)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, "Esfuerzo estimado para produccion: 6-8 semanas (equipo 3-4 devs)")
    pdf.ln(10)

    pdf.body_text(
        "La base de codigo demuestra alta calidad de desarrollo y seria una excelente "
        "base para un servicio fintech regional una vez que se resuelvan las brechas "
        "criticas de seguridad, integraciones y operaciones."
    )

    # Save
    output_path = r"C:\Users\HOME\PycharmProjects\llanopay\Auditoria_LlanoPay_2026.pdf"
    pdf.output(output_path)
    print(f"PDF generado: {output_path}")

if __name__ == "__main__":
    generate()
