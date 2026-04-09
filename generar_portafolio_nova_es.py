from fpdf import FPDF


class PortfolioPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(75, 0, 130)
            self.cell(0, 8, "NovaPay | Billetera Digital Global", align="R")
            self.ln(4)
            self.set_draw_color(75, 0, 130)
            self.set_line_width(0.4)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(75, 0, 130)
        self.cell(0, 14, title)
        self.ln(10)
        self.set_draw_color(75, 0, 130)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(50, 50, 50)
        self.cell(0, 10, title)
        self.ln(9)

    def body(self, text):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6.5, text)
        self.ln(3)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(60, 60, 60)
        self.cell(6, 6.5, "-")
        self.multi_cell(0, 6.5, text)
        self.ln(1)

    def highlight_box(self, text):
        self.set_fill_color(245, 240, 255)
        self.set_draw_color(75, 0, 130)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(75, 0, 130)
        y = self.get_y()
        self.rect(10, y, 190, 14, style="DF")
        self.set_xy(15, y + 3)
        self.cell(0, 8, text)
        self.ln(18)

    def table_header(self, cols, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(75, 0, 130)
        self.set_text_color(255, 255, 255)
        for i, col in enumerate(cols):
            self.cell(widths[i], 8, col, border=1, fill=True, align="C")
        self.ln()

    def table_row(self, cols, widths, fill=False):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        if fill:
            self.set_fill_color(245, 240, 255)
        else:
            self.set_fill_color(255, 255, 255)
        max_h = 6
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


def generate():
    pdf = PortfolioPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ==================== PORTADA ====================
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 48)
    pdf.set_text_color(75, 0, 130)
    pdf.cell(0, 20, "NOVAPAY", align="C")
    pdf.ln(22)
    pdf.set_draw_color(75, 0, 130)
    pdf.set_line_width(2)
    pdf.line(50, pdf.get_y(), 160, pdf.get_y())
    pdf.ln(14)
    pdf.set_font("Helvetica", "", 17)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "La Billetera Digital Global", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 12)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "Envia dinero a cualquier lugar. Paga lo que sea.", align="C")
    pdf.ln(7)
    pdf.cell(0, 8, "Cripto, moneda local y mucho mas.", align="C")
    pdf.ln(30)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, "Portafolio de Startup", align="C")
    pdf.ln(7)
    pdf.cell(0, 7, "Abril 2026", align="C")
    pdf.ln(7)
    pdf.cell(0, 7, "Documento Confidencial", align="C")

    # ==================== VISION ====================
    pdf.add_page()
    pdf.section_title("Vision")
    pdf.body(
        "NovaPay es una billetera digital de nueva generacion construida para un mundo "
        "sin fronteras. Creemos que el dinero debe moverse tan libremente como la informacion. "
        "Sin fronteras, sin demoras, sin exclusion. Ya seas un freelancer en Lagos recibiendo "
        "pagos de Nueva York, una familia en Manila enviando remesas desde Dubai, o un comerciante "
        "en Bogota aceptando pagos en cripto, NovaPay es tu centro financiero unico."
    )
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(75, 0, 130)
    pdf.cell(0, 10, "Mision")
    pdf.ln(9)
    pdf.body(
        "Brindar acceso universal a servicios financieros para cada persona en el planeta, "
        "sin importar su ubicacion, ingresos o estado bancario. Combinamos lo mejor de las "
        "finanzas tradicionales con el poder de blockchain para crear un ecosistema financiero "
        "verdaderamente inclusivo."
    )

    pdf.ln(3)
    pdf.highlight_box("  Una app. Todas las monedas. Todos los paises. Cero barreras.")

    # ==================== EL PROBLEMA ====================
    pdf.add_page()
    pdf.section_title("El Problema")

    pdf.body(
        "El sistema financiero global esta fragmentado, es costoso y excluye a miles de millones. "
        "A pesar de los avances tecnologicos, los servicios financieros basicos siguen siendo "
        "inaccesibles para una porcion masiva de la poblacion mundial:"
    )
    pdf.ln(3)

    pdf.sub_title("Exclusion Financiera Global")
    pdf.bullet("1,400 millones de adultos en el mundo no tienen cuenta bancaria (Banco Mundial 2024)")
    pdf.bullet("Las comisiones de remesas promedian 6.2% globalmente - costando $48,000 millones USD/ano en comisiones")
    pdf.bullet("Las transferencias internacionales toman 3-5 dias habiles por banca tradicional")
    pdf.bullet("Las comisiones por conversion de moneda van del 2 al 8% segun el corredor")
    pdf.bullet("El 76% del Africa Subsahariana y el 65% del Sudeste Asiatico estan sub-bancarizados")
    pdf.bullet("Pequenos comerciantes en mercados emergentes pagan 3-5% por procesamiento de tarjetas")
    pdf.bullet("Freelancers en paises en desarrollo pierden 5-10% en plataformas de pago internacionales")

    pdf.ln(3)
    pdf.sub_title("Las Soluciones Actuales se Quedan Cortas")
    pdf.bullet("Bancos: Costosos, lentos, requieren presencia fisica, excluyen a usuarios de bajos ingresos")
    pdf.bullet("PayPal/Wise: Limitados en mercados emergentes, comisiones altas para montos pequenos")
    pdf.bullet("Billeteras cripto: Demasiado complejas para usuarios comunes, sin integracion fiat")
    pdf.bullet("Dinero movil (M-Pesa): Regional, sin funcionalidad transfronteriza, sin cripto, sin credito")
    pdf.bullet("Neobancos (Revolut, N26): Enfocados en mercados desarrollados, alcance global limitado")

    pdf.ln(3)
    pdf.highlight_box("  $150 billones USD se mueven transfronterizamente al ano. Capturamos el segmento desatendido.")

    # ==================== LA SOLUCION ====================
    pdf.add_page()
    pdf.section_title("La Solucion")

    pdf.body(
        "NovaPay es una billetera digital global todo-en-uno que unifica monedas fiat, "
        "criptomonedas y servicios financieros en una sola aplicacion. "
        "Disponible en mas de 180 paises desde el primer dia via smartphone."
    )
    pdf.ln(3)

    features = [
        ["Billetera Multi-Moneda", "Administra mas de 50 monedas fiat y 20+ criptomonedas "
         "en una sola billetera. Conversion en tiempo real a tasas interbancarias. Sin comisiones "
         "ocultas. Soporta USD, EUR, GBP, COP, MXN, NGN, PHP, INR, BRL y mas."],
        ["Transferencias Globales Instantaneas", "Envia dinero a cualquier persona, en cualquier lugar, "
         "en segundos. Transferencias P2P por numero de celular, email o usuario. Pagos "
         "internacionales se liquidan en menos de 60 segundos via blockchain. Comisiones desde 0.3%."],
        ["Trading y Custodia Cripto", "Compra, vende y guarda Bitcoin, Ethereum, USDC y 20+ tokens. "
         "Custodia de grado institucional con seguro. Gana rendimiento en stablecoins. "
         "Conversion fluida de fiat a cripto."],
        ["NovaCoin (NOVA)", "Token de utilidad nativo que impulsa el ecosistema. Gana NOVA por "
         "transacciones, referidos y staking. Usa NOVA para descuentos en comisiones, "
         "funciones premium y recompensas en comercios. Tokenomics deflacionario."],
        ["Pagos a Comercios", "Acepta pagos de cualquier usuario NovaPay en el mundo via codigo QR, "
         "link de pago o API. Liquida en moneda local o cripto. "
         "Comisiones 60% mas bajas que el procesamiento tradicional de tarjetas."],
        ["Microprestamos", "Score crediticio impulsado por IA basado en historial de transacciones. "
         "Microprestamos desde $10 hasta $10,000 USD equivalentes. Aprobacion instantanea. "
         "Prestamos colateralizados con activos cripto."],
        ["Tarjetas Virtuales y Fisicas", "Emite tarjetas Visa/Mastercard virtuales al instante. Gasta tu "
         "saldo NovaPay donde se acepten tarjetas. Tarjeta fisica disponible "
         "en 50+ paises. Compatible con Apple Pay y Google Pay."],
        ["Pagos de Servicios y Recargas", "Paga servicios, facturas, recargas moviles en 100+ paises. "
         "Programa pagos recurrentes. Divide cuentas con amigos. "
         "Gana cashback en NOVA en cada pago."],
    ]
    w = [38, 142]
    pdf.table_header(["Funcion", "Descripcion"], w)
    for i, row in enumerate(features):
        pdf.table_row(row, w, fill=(i % 2 == 0))

    # ==================== PROPUESTA DE VALOR ====================
    pdf.add_page()
    pdf.section_title("Propuesta de Valor")

    pdf.sub_title("Para Usuarios")
    pdf.bullet("Abre una cuenta en 90 segundos solo con tu numero de celular")
    pdf.bullet("Envia $200 USD a otro pais por $0.60 (vs $12.40 promedio de la industria)")
    pdf.bullet("Mantiene multiples monedas y convierte a tasas de cambio reales")
    pdf.bullet("Accede a credito basado en tu comportamiento financiero, no en tu codigo postal")
    pdf.bullet("Gana ingresos pasivos en stablecoins (4-8% APY)")
    pdf.bullet("Una app reemplaza: cuenta bancaria + servicio de remesas + exchange cripto + app de pagos")

    pdf.ln(4)
    pdf.sub_title("Para Comercios")
    pdf.bullet("Acepta pagos de 180+ paises sin necesidad de hardware")
    pdf.bullet("Comisiones desde 0.8% (vs 2.9-3.5% de Stripe/PayPal)")
    pdf.bullet("Liquidacion instantanea en moneda local, cripto o stablecoins")
    pdf.bullet("Programa de lealtad integrado via recompensas NovaCoin")
    pdf.bullet("API y plugins para integracion e-commerce (Shopify, WooCommerce)")
    pdf.bullet("Dashboard de analitica con datos de ventas en tiempo real")

    pdf.ln(4)
    pdf.sub_title("Para Freelancers y Trabajadores Remotos")
    pdf.bullet("Recibe pagos de clientes en todo el mundo sin demoras de conversion")
    pdf.bullet("Factura en cualquier moneda, recibe en cualquier moneda")
    pdf.bullet("Retira a cuenta bancaria local, dinero movil o billetera cripto")
    pdf.bullet("Reportes de transacciones listos para impuestos por pais")

    pdf.ln(4)
    pdf.sub_title("Para Empresas")
    pdf.bullet("Desembolso de nomina a 180+ paises en un solo clic")
    pdf.bullet("Gestion de tesoreria con soporte multi-moneda y stablecoins")
    pdf.bullet("Integracion KYC/AML lista para cumplimiento regulatorio")
    pdf.bullet("Solucion de billetera white-label disponible")

    # ==================== MODELO DE NEGOCIO ====================
    pdf.add_page()
    pdf.section_title("Modelo de Negocio")

    pdf.body(
        "NovaPay genera ingresos a traves de fuentes diversificadas, asegurando resiliencia "
        "y crecimiento compuesto a medida que la base de usuarios escala:"
    )
    pdf.ln(3)

    modelo = [
        ["Comisiones por Transaccion", "0.3% a 1.5% por transaccion segun tipo y volumen. "
         "Transferencias P2P: 0.3-0.5%. Internacionales: 0.5-1.0%. "
         "Pagos a comercios: 0.8-1.5%. Precios por volumen para empresas."],
        ["Spread Cambiario", "0.3-0.8% de spread en conversiones de moneda. Tasas interbancarias + "
         "pequeno margen. Competitivo con Wise (0.4-1.5%) y muy por debajo de bancos (2-5%). "
         "Fuente de ingresos de alta frecuencia."],
        ["Comisiones Trading Cripto", "0.1-0.5% por operacion cripto. Menor que Coinbase (1.5%) y "
         "competitivo con Binance (0.1%). Modelo de comision maker/taker. "
         "Descuentos por volumen para traders activos."],
        ["Intereses de Prestamos", "8-24% TAE en microprestamos (varia por mercado y riesgo). "
         "Prestamos colateralizados con cripto al 5-12% TAE. "
         "Margen neto de interes: 4-10% despues del costo de capital."],
        ["Staking y Rendimiento", "Participacion en rendimiento de productos stablecoin. Usuarios ganan "
         "4-8% APY, NovaPay gana 1-3% de comision de gestion. Optimizacion DeFi."],
        ["Ecosistema NovaCoin", "1% de comision en compra/venta de NOVA. Mecanismo de quema de tokens "
         "crea deflacion. Alianzas empresariales para programas de recompensas."],
        ["Suscripciones Premium", "NovaPay Pro: $9.99/mes - cero comisiones en transferencias, limites "
         "mas altos, soporte prioritario, productos de rendimiento exclusivos. "
         "NovaPay Business: $29.99/mes - API avanzada, analitica, cuentas de equipo."],
        ["Ingresos por Tarjetas", "Comisiones interchange en transacciones con tarjeta (0.5-1.5%). "
         "Participacion de ingresos con red Visa/Mastercard. "
         "Comisiones de emision de tarjeta en mercados selectos."],
        ["B2B / White-Label", "Licenciamiento empresarial para soluciones white-label. "
         "Comisiones de acceso API para procesamiento de pagos. "
         "Integraciones personalizadas para bancos y fintechs."],
    ]
    w_mod = [38, 142]
    pdf.table_header(["Fuente de Ingreso", "Detalle"], w_mod)
    for i, row in enumerate(modelo):
        pdf.table_row(row, w_mod, fill=(i % 2 == 0))

    # ==================== MERCADO ====================
    pdf.add_page()
    pdf.section_title("Oportunidad de Mercado")

    pdf.sub_title("TAM (Mercado Total Direccionable)")
    pdf.body(
        "Mercado global de pagos digitales: $11.6 billones USD (2025), proyectado $19.9 billones "
        "para 2028. Mercado global de remesas: $860,000 millones USD (2025). "
        "Capitalizacion global del mercado cripto: $2.8 billones USD. "
        "TAM combinado: $15+ billones USD en volumen de transacciones anuales."
    )

    pdf.sub_title("SAM (Mercado Disponible)")
    pdf.body(
        "Pagos digitales en mercados emergentes: $3.2 billones USD. "
        "Remesas transfronterizas a LATAM, Africa, Asia: $540,000 millones USD. "
        "Trading cripto minorista en mercados objetivo: $180,000 millones USD. "
        "SAM: $3.9 billones USD en volumen direccionable."
    )

    pdf.sub_title("SOM (Mercado Objetivo Inicial)")
    pdf.body(
        "Objetivo inicial: LATAM (Colombia, Mexico, Brasil) + Africa Occidental (Nigeria, Ghana) + "
        "Sudeste Asiatico (Filipinas, Indonesia). "
        "Meta ano 3: $2,500 millones USD en volumen de transacciones anuales. "
        "A 0.8% de tasa promedio = $20 millones USD de ingreso anual."
    )

    pdf.ln(3)
    pdf.highlight_box("  $15 billones USD de TAM creciendo al 15% CAGR. Empezamos donde otros no llegan.")

    pdf.ln(3)
    pdf.sub_title("Panorama Competitivo")
    comp = [
        ["PayPal / Venmo", "Global", "Confianza de marca, red de comercios", "Comisiones altas, limitado en mercados emergentes, sin custodia cripto"],
        ["Wise", "Global", "Bajas comisiones FX, transparencia", "Sin cripto, sin prestamos, sin pagos a comercios, sin recompensas"],
        ["Revolut", "Europa+", "Multi-moneda, cripto, tarjetas", "Limitado en Africa/LATAM/Asia, retos regulatorios"],
        ["Binance / Coinbase", "Global", "Liquidez cripto, marca", "Sin billetera fiat, UX compleja, sin remesas, sin prestamos"],
        ["M-Pesa", "Africa", "Lider en dinero movil, offline", "Solo regional, sin cripto, sin funcionalidad transfronteriza"],
        ["NovaPay", "Global", "Todo-en-uno: fiat + cripto + prestamos + tarjetas + recompensas. "
         "Construido para mercados emergentes primero. 0.3% comisiones.", "Marca nueva, requiere traccion inicial"],
    ]
    w_comp = [28, 18, 62, 72]
    pdf.table_header(["Jugador", "Alcance", "Fortaleza", "Debilidad"], w_comp)
    for i, row in enumerate(comp):
        pdf.table_row(row, w_comp, fill=(i % 2 == 0))

    # ==================== FLUJO DE DINERO ====================
    pdf.add_page()
    pdf.section_title("Como se Mueve el Dinero en NovaPay")

    pdf.body(
        "NovaPay orquesta el movimiento de dinero a traves de socios financieros regulados. "
        "Nunca mantenemos fondos de clientes directamente - se mantienen en cuentas segregadas "
        "con socios bancarios licenciados y custodios asegurados."
    )
    pdf.ln(3)

    pdf.sub_title("Rampas Fiat de Entrada/Salida (Por Region)")
    fiat = [
        ["Latinoamerica", "PSE, SPEI, PIX, OXXO", "Transferencias bancarias, billeteras moviles, redes de efectivo. "
         "Socios: Wompi, PayU, Mercado Pago, dLocal."],
        ["Africa", "Dinero movil, transferencia bancaria", "M-Pesa, MTN MoMo, Airtel Money, Chipper Cash. "
         "Socios: Flutterwave, Paystack, dLocal."],
        ["Sudeste Asiatico", "GCash, GrabPay, transferencia", "Billeteras moviles, debito directo, OTC. "
         "Socios: Xendit, PayMongo, dLocal."],
        ["Europa", "SEPA, Open Banking, tarjetas", "Transferencias SEPA instantaneas, open banking PSD2. "
         "Socios: Stripe, Adyen, TrueLayer."],
        ["Norteamerica", "ACH, tarjetas debito/credito", "Transferencias bancarias, vinculacion via Plaid. "
         "Socios: Stripe, Plaid, Synapse."],
        ["Medio Oriente", "Transferencia, casas de cambio", "Integracion bancaria local, retiro en efectivo. "
         "Socios: Checkout.com, Tabby, dLocal."],
        ["Efectivo Global", "Redes de deposito en efectivo", "200,000+ puntos de recaudo en el mundo. "
         "Socios: Efecty, OXXO, 7-Eleven, Paxful."],
    ]
    w_fiat = [30, 42, 108]
    pdf.table_header(["Region", "Metodos", "Detalles"], w_fiat)
    for i, row in enumerate(fiat):
        pdf.table_row(row, w_fiat, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.sub_title("Infraestructura Cripto")
    crypto = [
        ["Liquidez y Trading", "Bitso, Binance, Kraken", "Agregacion multi-exchange para mejores precios. "
         "Pools de liquidez profundos. Soporta 20+ tokens."],
        ["Stablecoins", "Circle (USDC), Tether (USDT)", "Tokens anclados al dolar para remesas y ahorro. "
         "Liquidacion on-chain en segundos."],
        ["Custodia", "Fireblocks, BitGo", "Custodia MPC de grado institucional con seguro de $250M USD. "
         "Certificacion SOC 2 Tipo II. Almacenamiento frio + tibio."],
        ["Widgets On-Ramp", "MoonPay, Transak, Ramp", "Compra/venta de cripto integrada con metodos de pago locales. "
         "KYC integrado. 180+ paises soportados."],
        ["Redes Blockchain", "Polygon, Ethereum, Solana, Base", "Soporte multi-cadena para transacciones de bajo costo. "
         "Token NOVA desplegado en Polygon para eficiencia de gas."],
        ["Rendimiento DeFi", "Aave, Compound, Yearn", "Estrategias automatizadas de rendimiento en stablecoins. "
         "Productos con score de riesgo para usuarios. Solo protocolos auditados."],
    ]
    w_crypto = [32, 46, 102]
    pdf.table_header(["Capa", "Socios", "Detalles"], w_crypto)
    for i, row in enumerate(crypto):
        pdf.table_row(row, w_crypto, fill=(i % 2 == 0))

    # ==================== FLUJO DE USUARIO ====================
    pdf.add_page()
    pdf.sub_title("Recorrido Completo del Usuario")
    pdf.body("Como un usuario interactua con NovaPay desde el registro hasta el uso diario:")
    pdf.ln(2)
    pdf.bullet("1. REGISTRO: Descarga la app, ingresa su celular, verifica via SMS OTP (90 segundos)")
    pdf.bullet("2. KYC: Escanea documento de identidad + selfie para verificacion completa (automatizado, 2-5 min)")
    pdf.bullet("3. FONDEAR: Agrega dinero via transferencia bancaria, tarjeta, dinero movil o deposito en efectivo")
    pdf.bullet("4. MANTENER: Saldo visible en moneda local + cripto. Vista multi-moneda.")
    pdf.bullet("5. ENVIAR: Transfiere a cualquier persona por celular/email/usuario. Instantaneo. Desde 0.3%.")
    pdf.bullet("6. PAGAR: Escanea QR en comercios, paga en linea o usa tarjeta virtual/fisica")
    pdf.bullet("7. CONVERTIR: Intercambia entre monedas fiat a tasas interbancarias (0.3% spread)")
    pdf.bullet("8. TRADEAR: Compra/vende cripto directamente desde la app. Ejecucion instantanea.")
    pdf.bullet("9. GANAR: Haz staking de stablecoins al 4-8% APY. Gana NOVA en cada transaccion.")
    pdf.bullet("10. PEDIR PRESTAMO: Solicita microprestamo basado en historial. Aprobacion instantanea.")
    pdf.bullet("11. RETIRAR: Retira a cuenta bancaria, dinero movil o billetera cripto")

    pdf.ln(5)
    pdf.sub_title("Costos de Transaccion para el Usuario")
    costos = [
        ["Transferencia P2P domestica", "GRATIS (hasta $500 USD/mes)", "0.3% despues del tier gratuito"],
        ["Transferencia internacional", "0.5% (promedio $1 en $200)", "vs $12.40 promedio industria"],
        ["Conversion de moneda", "0.3% spread", "vs 2-5% en bancos"],
        ["Compra/venta cripto", "0.5%", "vs 1.5% en Coinbase"],
        ["Pago a comercio", "GRATIS para compradores", "0.8-1.5% al comercio"],
        ["Pago con tarjeta", "GRATIS", "Interchange lo paga el comercio"],
        ["Retiro en cajero", "2 gratis/mes", "$1.50 despues del tier gratuito"],
        ["Pago de servicios", "GRATIS", "Varia segun proveedor"],
        ["Rendimiento stablecoin", "Sin costo al usuario", "NovaPay gana 1-3% comision de gestion"],
        ["Microprestamo", "8-24% TAE", "Basado en score de riesgo"],
    ]
    w_cost = [50, 55, 75]
    pdf.table_header(["Operacion", "Costo al Usuario", "Notas"], w_cost)
    for i, row in enumerate(costos):
        pdf.table_row(row, w_cost, fill=(i % 2 == 0))

    # ==================== REGULACION ====================
    pdf.add_page()
    pdf.section_title("Estrategia Regulatoria")

    pdf.body(
        "NovaPay adopta un enfoque de cumplimiento primero. Nos asociamos con entidades "
        "licenciadas en cada jurisdiccion y buscamos nuestras propias licencias a medida que "
        "escalamos. Nuestra estrategia regulatoria esta disenada para entrada rapida al mercado "
        "manteniendo cumplimiento total."
    )
    pdf.ln(3)

    reg = [
        ["Estados Unidos", "MSB (FinCEN) + MTLs estatales", "Registro como Money Services Business. Licencias de "
         "transmisor de dinero estado por estado. Alianza con socio bancario licenciado inicialmente."],
        ["Union Europea", "Licencia EMI (toda la UE)", "Licencia de Institucion de Dinero Electronico bajo PSD2. "
         "Pasaportable en 27 paises de la UE. Cumplimiento MiCA para cripto."],
        ["Reino Unido", "Licencia E-Money FCA", "Registro ante Financial Conduct Authority. "
         "Registro cripto bajo FCA. Sandbox disponible."],
        ["Colombia", "Licencia SEDPE SFC", "Sandbox de la Superintendencia Financiera. Cumplimiento SARLAFT. "
         "Reportes UIAF. Alianza con banco local."],
        ["Mexico", "Licencia IFPE CNBV", "Cumplimiento de Ley Fintech. Registro CNBV "
         "para pagos electronicos. Operaciones cripto autorizadas."],
        ["Brasil", "Institucion de Pago BCB", "Autorizacion del Banco Central do Brasil. Integracion PIX. "
         "Registro CVM para operaciones cripto."],
        ["Nigeria", "Licencia PSB CBN", "Licencia de Banco de Servicios de Pago del Banco Central de Nigeria. "
         "Registro SEC para activos digitales."],
        ["Filipinas", "Licencia EMI BSP", "Registro ante Bangko Sentral ng Pilipinas. "
         "Licencia de Exchange de Moneda Virtual."],
        ["AML/KYC Global", "Cumplimiento FATF", "Cumplimiento Travel Rule. Integracion Chainalysis para "
         "monitoreo blockchain. KYC por niveles (Basico/Verificado/Premium)."],
    ]
    w_reg = [30, 40, 110]
    pdf.table_header(["Jurisdiccion", "Licencia", "Detalles"], w_reg)
    for i, row in enumerate(reg):
        pdf.table_row(row, w_reg, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.sub_title("Niveles de KYC (Global)")
    kyc = [
        ["Nivel 0 - Basico", "Solo celular + email", "Limite $200/mes. Solo P2P. Sin cripto.", "Instantaneo"],
        ["Nivel 1 - Verificado", "Documento de identidad + selfie", "Limite $5,000/mes. Todas las funciones. Cripto habilitado.", "< 5 min"],
        ["Nivel 2 - Mejorado", "Prueba de direccion + fuente de fondos", "Limite $50,000/mes. Limites mayores. Acceso a prestamos.", "< 24 hrs"],
        ["Nivel 3 - Premium", "Debida diligencia mejorada completa", "Sin limites. Funciones empresariales. Soporte prioritario.", "< 48 hrs"],
    ]
    w_kyc = [28, 48, 75, 19]
    pdf.table_header(["Nivel", "Requisitos", "Beneficios", "Tiempo"], w_kyc)
    for i, row in enumerate(kyc):
        pdf.table_row(row, w_kyc, fill=(i % 2 == 0))

    # ==================== PLAN DE TRACCION ====================
    pdf.add_page()
    pdf.section_title("Estrategia de Salida al Mercado")

    pdf.sub_title("Fase 1: Fundacion (Meses 1-6)")
    pdf.bullet("Lanzamiento en Colombia y Mexico (cabeza de playa LATAM)")
    pdf.bullet("Funciones core: billetera, transferencias P2P, rampa fiat, cripto basico")
    pdf.bullet("Alianza con 500 comercios en Bogota, CDMX, Villavicencio")
    pdf.bullet("Programa de embajadores universitarios en 20 universidades")
    pdf.bullet("Programa de referidos: $5 USD en NOVA por cada usuario referido")
    pdf.bullet("Meta: 50,000 usuarios registrados, 15,000 MAU")

    pdf.ln(3)
    pdf.sub_title("Fase 2: Expansion LATAM (Meses 7-12)")
    pdf.bullet("Expansion a Brasil (integracion PIX), Argentina, Peru, Chile")
    pdf.bullet("Lanzamiento del token NovaCoin (NOVA) con recompensas de staking")
    pdf.bullet("Lanzamiento de microprestamos en Colombia y Mexico")
    pdf.bullet("Despliegue de tarjeta Visa virtual en todo LATAM")
    pdf.bullet("Corredores de remesas: EEUU-Mexico, EEUU-Colombia, Espana-LATAM")
    pdf.bullet("Meta: 300,000 usuarios, 100,000 MAU, $50M volumen mensual")

    pdf.ln(3)
    pdf.sub_title("Fase 3: Africa y Asia (Meses 13-18)")
    pdf.bullet("Lanzamiento en Nigeria, Ghana, Kenia (Africa) y Filipinas, Indonesia (Asia)")
    pdf.bullet("Integracion de dinero movil (M-Pesa, MTN MoMo, GCash)")
    pdf.bullet("Corredores de remesas: EAU-Filipinas, UK-Nigeria, EEUU-India")
    pdf.bullet("Despliegue de tarjeta fisica en los 10 mercados principales")
    pdf.bullet("Productos de rendimiento DeFi para tenedores de stablecoins")
    pdf.bullet("Meta: 1M usuarios, 400K MAU, $200M volumen mensual")

    pdf.ln(3)
    pdf.sub_title("Fase 4: Escala Global (Meses 19-24)")
    pdf.bullet("Lanzamiento en UE y UK con licencias EMI/FCA")
    pdf.bullet("Solucion B2B white-label para bancos y fintechs")
    pdf.bullet("Gestion de nomina y tesoreria empresarial")
    pdf.bullet("Deteccion de fraude y score crediticio impulsados por IA")
    pdf.bullet("Meta: 3M usuarios, 1.2M MAU, $1,000M volumen mensual, rentabilidad")

    # ==================== PROYECCIONES ====================
    pdf.add_page()
    pdf.section_title("Proyecciones Financieras")

    pdf.sub_title("Proyeccion de Crecimiento a 3 Anos")
    proy = [
        ["Usuarios registrados", "50,000", "500,000", "3,000,000"],
        ["Usuarios activos mensuales (MAU)", "15,000", "200,000", "1,200,000"],
        ["Transacciones mensuales", "75,000", "2,000,000", "15,000,000"],
        ["Volumen transado mensual", "$5M USD", "$200M USD", "$2,500M USD"],
        ["Valor promedio por transaccion", "$67 USD", "$100 USD", "$167 USD"],
        ["Ingreso comisiones/mes", "$25K USD", "$1.2M USD", "$12.5M USD"],
        ["Ingreso spread FX/mes", "$5K USD", "$400K USD", "$5M USD"],
        ["Ingreso trading cripto/mes", "$2K USD", "$200K USD", "$3M USD"],
        ["Ingreso intereses prestamos/mes", "$0", "$150K USD", "$2.5M USD"],
        ["Ingreso suscripciones/mes", "$1K USD", "$100K USD", "$1.5M USD"],
        ["Ingreso interchange tarjetas/mes", "$0", "$80K USD", "$1M USD"],
        ["Ingreso total mensual", "$33K USD", "$2.1M USD", "$25.5M USD"],
        ["Ingreso total anual", "$400K USD", "$25.2M USD", "$306M USD"],
        ["Costos operativos mensuales", "$150K USD", "$1.4M USD", "$15M USD"],
        ["Resultado neto mensual", "-$117K USD", "$700K USD", "$10.5M USD"],
        ["Margen bruto", "-", "67%", "59%"],
        ["Mercados activos", "2", "8", "25+"],
        ["Comercios afiliados", "500", "10,000", "100,000"],
    ]
    w_proy = [55, 35, 45, 45]
    pdf.table_header(["Metrica", "Ano 1", "Ano 2", "Ano 3"], w_proy)
    for i, row in enumerate(proy):
        pdf.table_row(row, w_proy, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.highlight_box("  Punto de equilibrio: Mes 16. Flujo de caja positivo en el Mes 20.")

    # ==================== NOVACOIN ====================
    pdf.add_page()
    pdf.section_title("NovaCoin (NOVA) - Economia del Token")

    pdf.body(
        "NovaCoin (NOVA) es el token de utilidad nativo del ecosistema NovaPay. "
        "Alinea incentivos entre usuarios, comercios y la plataforma mientras "
        "crea un poderoso efecto de red."
    )
    pdf.ln(3)

    pdf.sub_title("Utilidad del Token")
    pdf.bullet("Descuentos en comisiones: Paga comisiones con NOVA y obtiene 50% de descuento")
    pdf.bullet("Recompensas de staking: Haz staking de NOVA para ganar rendimiento adicional (8-15% APY)")
    pdf.bullet("Recompensas en comercios: Gana cashback en NOVA en compras (1-5%)")
    pdf.bullet("Gobernanza: Vota sobre funciones de la plataforma y estructuras de comisiones")
    pdf.bullet("Acceso premium: Haz staking de NOVA para desbloquear funciones premium sin suscripcion")
    pdf.bullet("Colateral para prestamos: Usa NOVA como colateral para microprestamos")

    pdf.ln(3)
    pdf.sub_title("Distribucion del Token")
    dist = [
        ["Recompensas y Airdrops", "30%", "300,000,000", "Distribuidos en 5 anos a usuarios"],
        ["Equipo y Asesores", "20%", "200,000,000", "Vesting 4 anos, cliff 1 ano"],
        ["Tesoreria y Operaciones", "15%", "150,000,000", "Desarrollo de plataforma y operaciones"],
        ["Inversionistas (Seed + Serie A)", "15%", "150,000,000", "Vesting 2 anos, cliff 6 meses"],
        ["Liquidez y Market Making", "10%", "100,000,000", "Pools de liquidez DEX y CEX"],
        ["Fondo del Ecosistema", "10%", "100,000,000", "Grants, alianzas, integraciones"],
    ]
    w_dist = [50, 15, 35, 80]
    pdf.table_header(["Asignacion", "%", "Tokens", "Notas"], w_dist)
    for i, row in enumerate(dist):
        pdf.table_row(row, w_dist, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.body(
        "Suministro total: 1,000,000,000 NOVA (fijo). Mecanismo deflacionario: 20% de "
        "las comisiones de la plataforma se usan para recomprar y quemar NOVA trimestralmente. "
        "Desplegado en Polygon para comisiones de gas bajas y transacciones rapidas."
    )

    # ==================== EQUIPO ====================
    pdf.add_page()
    pdf.section_title("Equipo Necesario")

    pdf.body(
        "NovaPay requiere un equipo de clase mundial que abarque fintech, blockchain, "
        "cumplimiento regulatorio y crecimiento. Roles clave para el equipo fundador:"
    )
    pdf.ln(3)

    equipo = [
        ["CEO / Co-Fundador", "Vision, levantamiento de capital, alianzas, estrategia", "Background en fintech o pagos. Red LATAM + global."],
        ["CTO / Co-Fundador", "Arquitectura, seguridad, infraestructura, liderazgo tecnico", "Escalo plataforma fintech. Experiencia en blockchain."],
        ["VP de Ingenieria", "Liderazgo de equipos backend, mobile, DevOps", "Construyo sistemas de pago de alta disponibilidad."],
        ["Director de Cumplimiento", "Licencias, KYC/AML, relaciones regulatorias", "Experiencia multi-jurisdiccion en cumplimiento fintech."],
        ["Director de Producto", "UX/UI, investigacion de usuario, priorizacion de funciones", "Productos fintech de consumo. Experiencia en mercados emergentes."],
        ["CMO (Director de Marketing)", "Estrategia de marca, posicionamiento, PR, contenido, pauta", "Construyo marca fintech global. Experiencia en campanas para mercados emergentes."],
        ["Director de Crecimiento", "Adquisicion de usuarios, alianzas, viral loops", "Crecio app fintech/consumo a 1M+ usuarios."],
        ["Director de Cripto", "Economia de tokens, DeFi, custodia, operaciones blockchain", "Construyo o lidero exchange cripto o protocolo DeFi."],
        ["Director de Riesgos", "Prevencion de fraude, score crediticio, modelado de riesgo", "Gestion de riesgo financiero. Experiencia en ML/IA."],
        ["Gerentes de Pais", "Operaciones locales, alianzas, cumplimiento", "Uno por mercado. Red local profunda."],
        ["Lider de Soporte", "Operaciones de soporte multilingue 24/7", "Escalo soporte para producto financiero."],
    ]
    w_eq = [38, 60, 82]
    pdf.table_header(["Rol", "Responsabilidad", "Perfil Ideal"], w_eq)
    for i, row in enumerate(equipo):
        pdf.table_row(row, w_eq, fill=(i % 2 == 0))

    # ==================== INVERSION ====================
    pdf.add_page()
    pdf.section_title("Inversion")

    pdf.sub_title("Ronda Seed: $2.5M USD")
    pdf.body(
        "Estamos levantando una ronda seed de $2.5M USD para construir el producto, asegurar "
        "las licencias iniciales y lanzar en nuestros dos primeros mercados (Colombia y Mexico)."
    )
    pdf.ln(3)

    inv = [
        ["Desarrollo de producto (12 meses)", "$800,000", "Equipo de ingenieria, infraestructura, auditorias de seguridad"],
        ["Licencias y Legal", "$400,000", "Aplicaciones MSB, SEDPE, IFPE. Asesoria legal en 4 jurisdicciones."],
        ["Equipo (12 meses)", "$700,000", "Equipo core de 12-15 personas en ingenieria, cumplimiento, ops"],
        ["Marketing y Adquisicion", "$300,000", "Campanas de lanzamiento, programa de referidos, red de embajadores"],
        ["Infraestructura y Operaciones", "$150,000", "Cloud, SMS, custodia, comisiones de setup de procesadores"],
        ["Capital de Trabajo y Reserva", "$150,000", "Colchon operativo, contingencias, manejo de flotante"],
        ["TOTAL RONDA SEED", "$2,500,000", "Runway de 18 meses hasta hitos de Serie A"],
    ]
    w_inv = [52, 25, 103]
    pdf.table_header(["Categoria", "Monto", "Detalle"], w_inv)
    for i, row in enumerate(inv):
        pdf.table_row(row, w_inv, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.sub_title("Hitos para Serie A (Mes 18)")
    pdf.bullet("300,000+ usuarios registrados en LATAM")
    pdf.bullet("$50M+ en volumen de transacciones mensuales")
    pdf.bullet("$2M+ ARR (Ingreso Anual Recurrente)")
    pdf.bullet("Licencias aseguradas en 3+ jurisdicciones")
    pdf.bullet("NovaCoin lanzado y usado activamente por 50,000+ tenedores")
    pdf.bullet("Camino a rentabilidad demostrado")

    pdf.ln(3)
    pdf.sub_title("Serie A Proyectada: $15-25M USD")
    pdf.body(
        "Los fondos de Serie A aceleraran la expansion a Africa y Sudeste Asiatico, "
        "lanzaran el programa de tarjeta fisica, construiran la cartera de prestamos "
        "y buscaran licencia EMI en la UE/UK."
    )

    # ==================== HERRAMIENTAS ====================
    pdf.add_page()
    pdf.section_title("Socios y Proveedores Clave")

    pdf.body(
        "NovaPay aprovecha proveedores de primer nivel para entregar una experiencia "
        "financiera global sin fisuras:"
    )
    pdf.ln(3)

    herr = [
        ["Procesamiento de Pagos", "Stripe, Adyen, dLocal", "Procesamiento global de tarjetas y transferencias"],
        ["Pagos LATAM", "Wompi, PayU, Mercado Pago", "PSE, SPEI, PIX, metodos locales"],
        ["Pagos Africa", "Flutterwave, Paystack", "Dinero movil, transferencias, tarjetas"],
        ["Pagos Asia", "Xendit, PayMongo", "GCash, GrabPay, bancos locales"],
        ["Exchange Cripto", "Bitso, Binance, Kraken", "Agregacion de liquidez multi-exchange"],
        ["Stablecoins", "Circle (USDC)", "Moneda digital anclada al dolar"],
        ["Custodia Cripto", "Fireblocks, BitGo", "Custodia MPC con seguro"],
        ["On-Ramp Cripto", "MoonPay, Transak", "Compra cripto con metodos de pago locales"],
        ["Emision de Tarjetas", "Marqeta, Visa DPS", "Programas de tarjetas virtuales y fisicas"],
        ["Verificacion de Identidad", "Onfido, Truora, Jumio", "KYC global con documento + biometria"],
        ["Monitoreo Blockchain", "Chainalysis, Elliptic", "Cumplimiento AML para transacciones cripto"],
        ["SMS y Comunicaciones", "Twilio, AWS SNS", "OTP, notificaciones, comunicaciones con clientes"],
        ["Notificaciones Push", "Firebase, OneSignal", "Notificaciones moviles en tiempo real"],
        ["Infraestructura Cloud", "AWS, Google Cloud", "Multi-region, alta disponibilidad"],
        ["Monitoreo y Seguridad", "Sentry, DataDog, Cloudflare", "Tracking de errores, rendimiento, proteccion DDoS"],
        ["Socios Bancarios", "Bancos regionales por mercado", "Cuentas segregadas, custodia fiat"],
    ]
    w_herr = [40, 45, 95]
    pdf.table_header(["Categoria", "Proveedor", "Uso"], w_herr)
    for i, row in enumerate(herr):
        pdf.table_row(row, w_herr, fill=(i % 2 == 0))

    # ==================== POR QUE AHORA ====================
    pdf.add_page()
    pdf.section_title("Por Que Ahora?")

    pdf.bullet("La penetracion de smartphones en mercados emergentes supero el 75% en 2025")
    pdf.bullet("Infraestructura de pago en tiempo real (PIX, UPI, SPEI) ya disponible en mercados clave")
    pdf.bullet("La regulacion MiCA en la UE proporciona un marco cripto claro por primera vez")
    pdf.bullet("El mercado de stablecoins alcanzo $180,000M USD, probando demanda de dolares digitales")
    pdf.bullet("El trabajo remoto creo 200M+ freelancers transfronterizos que necesitan soluciones de pago")
    pdf.bullet("Los bancos tradicionales estan cerrando sucursales - reduccion del 30% desde 2020")
    pdf.bullet("Gen Z y millennials (60% de poblacion en mercados emergentes) son mobile-first")
    pdf.bullet("APIs de open banking ahora disponibles en LATAM, Africa y Asia")

    pdf.ln(5)
    pdf.sub_title("Por Que Gana NovaPay")
    pdf.bullet("MERCADOS EMERGENTES PRIMERO: Construido para los 1,400M sin banco, no como idea secundaria")
    pdf.bullet("TODO-EN-UNO: Una sola app reemplaza 5+ productos financieros")
    pdf.bullet("CRIPTO-NATIVO: Rails blockchain para transferencias internacionales instantaneas y baratas")
    pdf.bullet("ALINEADO POR TOKEN: NovaCoin crea efectos de red virales y retencion de usuarios")
    pdf.bullet("UNIT ECONOMICS: Positivos a $100 USD de saldo promedio por usuario")
    pdf.bullet("LISTO REGULATORIAMENTE: Enfoque de cumplimiento primero, no cumplimiento despues")

    # ==================== CIERRE ====================
    pdf.add_page()
    pdf.ln(35)
    pdf.set_font("Helvetica", "B", 48)
    pdf.set_text_color(75, 0, 130)
    pdf.cell(0, 20, "NOVAPAY", align="C")
    pdf.ln(22)
    pdf.set_draw_color(75, 0, 130)
    pdf.set_line_width(2)
    pdf.line(50, pdf.get_y(), 160, pdf.get_y())
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 15)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "La Billetera Digital Global", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 12)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "Una app. Todas las monedas. Todos los paises.", align="C")
    pdf.ln(25)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(75, 0, 130)
    pdf.cell(0, 10, "Levantando: Ronda Seed de $2.5M USD", align="C")
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Contacto: hola@novapay.io", align="C")
    pdf.ln(7)
    pdf.cell(0, 8, "Web: www.novapay.io", align="C")
    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, "Confidencial - Preparado para inversionistas - Abril 2026", align="C")

    # Save
    output_path = r"C:\Users\HOME\PycharmProjects\llanopay\Portafolio_NovaPay_Global_ES_2026.pdf"
    pdf.output(output_path)
    print(f"PDF generado: {output_path}")


if __name__ == "__main__":
    generate()
